#!/usr/bin/env python3
"""
🌐 Web Portal (stdlib-only WSGI)
- Tenders portal for multiple professions
- Profession-specific agents auto-bidding
- GDPR-style compliance: consent, privacy-first logging, legal docs
"""
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults
from urllib.parse import parse_qs
from pathlib import Path
import json
import hashlib
import datetime
import os

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
STATIC = BASE / 'static'
TEMPLATES = BASE / 'templates'
LOGS = BASE / 'logs'
LEGAL = BASE / 'legal'

DATA.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

TENDERS_FILE = DATA / 'tenders.json'
PROFESSIONS_FILE = DATA / 'professions.json'
ERASURE_FILE = DATA / 'erasure_requests.json'
AUDIT_LOG = LOGS / 'audit.log'

for p, default in [
    (TENDERS_FILE, {"tenders": [], "bids": []}),
    (PROFESSIONS_FILE, {"professions": [
        "Software Developer", "Designer", "Engineer", "Marketer",
        "Data Scientist", "Translator", "Writer", "Consultant"
    ]}),
    (ERASURE_FILE, {"requests": []}),
]:
    if not p.exists():
        p.write_text(json.dumps(default, indent=2), encoding='utf-8')


def _json_response(start_response, data, status='200 OK', headers=None):
    base_headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
        ('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline';"),
        ('X-Content-Type-Options', 'nosniff'),
        ('Referrer-Policy', 'no-referrer'),
        ('Permissions-Policy', 'geolocation=()'),
        ('Cache-Control', 'no-store')
    ]
    if headers:
        base_headers.extend(headers)
    start_response(status, base_headers)
    return [json.dumps(data).encode('utf-8')]


def _serve_file(start_response, path: Path, content_type='text/plain; charset=utf-8'):
    if not path.exists():
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']
    data = path.read_bytes()
    start_response('200 OK', [
        ('Content-Type', content_type),
        ('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline';"),
        ('X-Content-Type-Options', 'nosniff')
    ])
    return [data]


def _hash_ip(ip: str) -> str:
    return hashlib.sha256((ip or 'unknown').encode('utf-8')).hexdigest()


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


def _audit(event: str, ip: str, extra=None):
    entry = {"ts": _now_iso(), "event": event, "ip_hash": _hash_ip(ip), "data": extra or {}}
    with AUDIT_LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def _load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _save_json(p: Path, obj):
    p.write_text(json.dumps(obj, indent=2), encoding='utf-8')


# Import profession agents (local stdlib logic)
try:
    from profession_agents.agents import AutoBidder
except Exception:
    # Fallback stub
    class AutoBidder:
        @staticmethod
        def generate_bid(profession: str, tender: dict) -> dict:
            return {
                "bidder_name": f"AutoAgent-{profession.replace(' ', '')}",
                "bid_amount": max(100, int(tender.get('budget', 1000) * 0.9)),
                "message": f"Automated proposal for {profession}. We can deliver on time.",
            }


MIME = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
}


def application(environ, start_response):
    setup_testing_defaults(environ)
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    ip = environ.get('REMOTE_ADDR', '')

    # Static and index
    if path == '/':
        return _serve_file(start_response, TEMPLATES / 'index.html', 'text/html; charset=utf-8')
    if path.startswith('/static/'):
        rel = path[len('/static/'):]
        f = STATIC / rel
        return _serve_file(start_response, f, MIME.get(f.suffix, 'application/octet-stream'))

    # Legal docs
    if path.startswith('/legal/'):
        rel = path[len('/legal/'):]
        f = LEGAL / rel
        ctype = 'text/markdown; charset=utf-8'
        return _serve_file(start_response, f, ctype)

    # API endpoints
    if path == '/api/professions' and method == 'GET':
        return _json_response(start_response, _load_json(PROFESSIONS_FILE))

    if path == '/api/tenders':
        if method == 'GET':
            return _json_response(start_response, _load_json(TENDERS_FILE))
        elif method == 'POST':
            length = int(environ.get('CONTENT_LENGTH') or 0)
            body = environ['wsgi.input'].read(length) if length else b''
            try:
                payload = json.loads(body.decode('utf-8'))
            except Exception:
                return _json_response(start_response, {"error": "Invalid JSON"}, '400 Bad Request')
            # Consent required
            if not payload.get('consent'):
                return _json_response(start_response, {"error": "Consent required"}, '400 Bad Request')
            # Minimal PII: only contact_email stored
            tender = {
                "id": f"t_{int(datetime.datetime.utcnow().timestamp())}",
                "title": payload.get('title', '').strip()[:120],
                "description": payload.get('description', '').strip()[:5000],
                "profession": payload.get('profession', ''),
                "budget": float(payload.get('budget', 0) or 0),
                "deadline": payload.get('deadline', '').strip()[:40],
                "contact_email": payload.get('contact_email', '').strip()[:160],
                "created_at": _now_iso(),
            }
            store = _load_json(TENDERS_FILE) or {"tenders": [], "bids": []}
            store.setdefault('tenders', []).append(tender)
            _save_json(TENDERS_FILE, store)
            _audit('tender_create', ip, {"tender_id": tender['id']})
            return _json_response(start_response, {"ok": True, "tender": tender}, '201 Created')

    if path == '/api/bids' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return _json_response(start_response, {"error": "Invalid JSON"}, '400 Bad Request')
        tid = payload.get('tender_id')
        store = _load_json(TENDERS_FILE)
        if not any(t.get('id') == tid for t in store.get('tenders', [])):
            return _json_response(start_response, {"error": "Unknown tender"}, '404 Not Found')
        bid = {
            "tender_id": tid,
            "bidder_name": payload.get('bidder_name', 'anonymous')[:120],
            "bid_amount": float(payload.get('bid_amount', 0) or 0),
            "message": payload.get('message', '')[:2000],
            "created_at": _now_iso(),
        }
        store.setdefault('bids', []).append(bid)
        _save_json(TENDERS_FILE, store)
        _audit('bid_create', ip, {"tender_id": tid})
        return _json_response(start_response, {"ok": True, "bid": bid}, '201 Created')

    if path == '/api/auto_bid' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return _json_response(start_response, {"error": "Invalid JSON"}, '400 Bad Request')
        profession = payload.get('profession')
        tid = payload.get('tender_id')
        store = _load_json(TENDERS_FILE)
        tenders = store.get('tenders', [])
        tender = next((t for t in tenders if t.get('id') == tid), None)
        if not tender:
            return _json_response(start_response, {"error": "Unknown tender"}, '404 Not Found')
        auto = AutoBidder.generate_bid(profession, tender)
        bid = {
            "tender_id": tid,
            "bidder_name": auto['bidder_name'],
            "bid_amount": float(auto['bid_amount']),
            "message": auto['message'][:2000],
            "created_at": _now_iso(),
        }
        store.setdefault('bids', []).append(bid)
        _save_json(TENDERS_FILE, store)
        _audit('auto_bid', ip, {"tender_id": tid, "profession": profession})
        return _json_response(start_response, {"ok": True, "bid": bid}, '201 Created')

    if path == '/api/request_erasure' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return _json_response(start_response, {"error": "Invalid JSON"}, '400 Bad Request')
        email = (payload.get('email') or '').strip()[:160]
        er = _load_json(ERASURE_FILE)
        er.setdefault('requests', []).append({"email": email, "ts": _now_iso()})
        _save_json(ERASURE_FILE, er)
        _audit('gdpr_erasure_request', ip, {"email_hash": hashlib.sha256(email.encode()).hexdigest()})
        return _json_response(start_response, {"ok": True})

    # 404
    start_response('404 Not Found', [('Content-Type', 'application/json')])
    return [json.dumps({"error": "Not Found"}).encode('utf-8')]


def run(host='0.0.0.0', port=8000):
    with make_server(host, port, application) as httpd:
        print(f"Web portal running on http://{host}:{port}")
        httpd.serve_forever()

if __name__ == '__main__':
    run()