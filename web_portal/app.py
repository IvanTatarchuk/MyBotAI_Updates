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

# New data files
USERS_FILE = DATA / 'users.json'
SESSIONS_FILE = DATA / 'sessions.json'
OTPS_FILE = DATA / 'otps.json'
KYC_FILE = DATA / 'kyc.json'
ESCROWS_FILE = DATA / 'escrows.json'

for p, default in [
    (TENDERS_FILE, {"tenders": [], "bids": []}),
    (PROFESSIONS_FILE, {"professions": [
        "Software Developer", "Designer", "Engineer", "Marketer",
        "Data Scientist", "Translator", "Writer", "Consultant"
    ]}),
    (ERASURE_FILE, {"requests": []}),
    (USERS_FILE, {"users": []}),
    (SESSIONS_FILE, {"sessions": {}}),
    (OTPS_FILE, {"otps": []}),
    (KYC_FILE, {"kyc": []}),
    (ESCROWS_FILE, {"escrows": []}),
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

# Simple cookie parsing

def _parse_cookies(environ):
    cookie = environ.get('HTTP_COOKIE') or ''
    cookies = {}
    for part in cookie.split(';'):
        if '=' in part:
            k, v = part.strip().split('=', 1)
            cookies[k] = v
    return cookies

import os as _os
import secrets as _secrets

def _set_cookie(start_response, headers, name, value, path='/', max_age=86400):
    headers.append(('Set-Cookie', f"{name}={value}; Path={path}; Max-Age={max_age}; HttpOnly; SameSite=Lax"))


def _get_user(environ):
    sessions = _load_json(SESSIONS_FILE).get('sessions', {})
    cookies = _parse_cookies(environ)
    sid = cookies.get('sid')
    if sid and sid in sessions:
        users = _load_json(USERS_FILE).get('users', [])
        uid = sessions[sid]
        return next((u for u in users if u.get('id') == uid), None)
    return None


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
    if path == '/admin':
        return _serve_file(start_response, TEMPLATES / 'admin.html', 'text/html; charset=utf-8')
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

    # Auth endpoints (OTP)
    if path == '/api/auth/request_otp' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return _json_response(start_response, {"error": "Invalid JSON"}, '400 Bad Request')
        email = (payload.get('email') or '').strip().lower()[:160]
        role = (payload.get('role') or 'seller').strip().lower()
        if role not in ('admin','buyer','seller'):
            role = 'seller'
        users = _load_json(USERS_FILE)
        if not any(u.get('email') == email for u in users.get('users', [])):
            users.setdefault('users', []).append({"id": f"u_{int(datetime.datetime.utcnow().timestamp())}", "email": email, "role": role})
            _save_json(USERS_FILE, users)
        code = str(_secrets.randbelow(900000) + 100000)
        otps = _load_json(OTPS_FILE)
        # store hashed code for safety
        otps.setdefault('otps', []).append({"email": email, "code_hash": hashlib.sha256(code.encode()).hexdigest(), "exp": int(datetime.datetime.utcnow().timestamp()) + 600})
        _save_json(OTPS_FILE, otps)
        _audit('otp_request', ip, {"email_hash": hashlib.sha256(email.encode()).hexdigest()})
        # In dev, return the code; in prod, integrate SMTP
        return _json_response(start_response, {"ok": True, "dev_code": code})

    if path == '/api/auth/login' and method == 'POST':
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return _json_response(start_response, {"error": "Invalid JSON"}, '400 Bad Request')
        email = (payload.get('email') or '').strip().lower()[:160]
        code = (payload.get('code') or '').strip()
        otps = _load_json(OTPS_FILE)
        now_ts = int(datetime.datetime.utcnow().timestamp())
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        found = None
        for item in list(otps.get('otps', [])):
            if item.get('email') == email and item.get('code_hash') == code_hash and item.get('exp', 0) >= now_ts:
                found = item
        if not found:
            return _json_response(start_response, {"error": "Invalid or expired code"}, '401 Unauthorized')
        # Create session
        users = _load_json(USERS_FILE)
        user = next((u for u in users.get('users', []) if u.get('email') == email), None)
        sessions = _load_json(SESSIONS_FILE)
        sid = hashlib.sha256((_os.urandom(16)).hex().encode()).hexdigest()
        sessions.setdefault('sessions', {})[sid] = user['id']
        _save_json(SESSIONS_FILE, sessions)
        headers = []
        _set_cookie(start_response, headers, 'sid', sid)
        _audit('login', ip, {"user": user['id']})
        return _json_response(start_response, {"ok": True, "user": user}, headers=headers)

    if path == '/api/auth/whoami' and method == 'GET':
        user = _get_user(environ)
        return _json_response(start_response, {"user": user} if user else {"user": None})

    if path == '/api/auth/logout' and method == 'POST':
        sessions = _load_json(SESSIONS_FILE)
        cookies = _parse_cookies(environ)
        sid = cookies.get('sid')
        if sid and sid in sessions.get('sessions', {}):
            del sessions['sessions'][sid]
            _save_json(SESSIONS_FILE, sessions)
        headers = []
        _set_cookie(start_response, headers, 'sid', 'deleted', max_age=0)
        return _json_response(start_response, {"ok": True}, headers=headers)

    # KYC endpoints
    if path == '/api/kyc/submit' and method == 'POST':
        user = _get_user(environ)
        if not user:
            return _json_response(start_response, {"error": "Auth required"}, '401 Unauthorized')
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return _json_response(start_response, {"error": "Invalid JSON"}, '400 Bad Request')
        entry = {
            "user_id": user['id'],
            "email": user['email'],
            "full_name": (payload.get('full_name') or '')[:160],
            "country": (payload.get('country') or '')[:80],
            "doc_type": (payload.get('doc_type') or '')[:40],
            "doc_id_hash": hashlib.sha256(((payload.get('doc_id') or '')).encode()).hexdigest(),
            "status": "pending",
            "submitted_at": _now_iso(),
        }
        kyc = _load_json(KYC_FILE)
        # replace existing for user
        kyc['kyc'] = [k for k in kyc.get('kyc', []) if k.get('user_id') != user['id']]
        kyc['kyc'].append(entry)
        _save_json(KYC_FILE, kyc)
        _audit('kyc_submit', ip, {"user": user['id']})
        return _json_response(start_response, {"ok": True, "kyc": entry})

    if path == '/api/admin/kyc/approve' and method == 'POST':
        user = _get_user(environ)
        if not user or user.get('role') != 'admin':
            return _json_response(start_response, {"error": "Admin only"}, '403 Forbidden')
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        payload = json.loads(body or b'{}')
        email = (payload.get('email') or '').strip().lower()
        kyc = _load_json(KYC_FILE)
        for rec in kyc.get('kyc', []):
            if rec.get('email') == email:
                rec['status'] = 'approved'
        _save_json(KYC_FILE, kyc)
        _audit('kyc_approve', ip, {"email_hash": hashlib.sha256(email.encode()).hexdigest()})
        return _json_response(start_response, {"ok": True})

    # GDPR export
    if path == '/api/export' and method == 'GET':
        qs = parse_qs(environ.get('QUERY_STRING') or '')
        email = (qs.get('email', [''])[0]).strip().lower()
        users = _load_json(USERS_FILE)
        tenders = _load_json(TENDERS_FILE)
        kyc = _load_json(KYC_FILE)
        esc = _load_json(ESCROWS_FILE)
        user = next((u for u in users.get('users', []) if u.get('email') == email), None)
        data = {
            "user": user,
            "tenders_owned": [t for t in tenders.get('tenders', []) if t.get('contact_email','').lower() == email],
            "bids_by_name": [b for b in tenders.get('bids', []) if b.get('bidder_name','').lower().startswith(email)],
            "kyc": [k for k in kyc.get('kyc', []) if k.get('email') == email],
            "escrows": [e for e in esc.get('escrows', []) if e.get('payer_email') == email or e.get('payee_name','').lower().startswith(email)],
        }
        return _json_response(start_response, data)

    # Tender APIs (existing)
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
                "owner_email": payload.get('contact_email', '').strip()[:160],
                "status": "open",
                "created_at": _now_iso(),
            }
            store = _load_json(TENDERS_FILE) or {"tenders": [], "bids": []}
            store.setdefault('tenders', []).append(tender)
            _save_json(TENDERS_FILE, store)
            _audit('tender_create', ip, {"tender_id": tender['id']})
            return _json_response(start_response, {"ok": True, "tender": tender}, '201 Created')

    # Tender workflow updates
    if path == '/api/tenders/update_status' and method == 'POST':
        user = _get_user(environ)
        if not user:
            return _json_response(start_response, {"error": "Auth required"}, '401 Unauthorized')
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        payload = json.loads(body or b'{}')
        tid = payload.get('tender_id')
        status = payload.get('status')
        store = _load_json(TENDERS_FILE)
        tender = next((t for t in store.get('tenders', []) if t.get('id') == tid), None)
        if not tender:
            return _json_response(start_response, {"error": "Unknown tender"}, '404 Not Found')
        if user.get('role') != 'admin' and tender.get('owner_email','').lower() != user.get('email'):
            return _json_response(start_response, {"error": "Forbidden"}, '403 Forbidden')
        if status not in ('open','under_review','awarded','closed'):
            return _json_response(start_response, {"error": "Bad status"}, '400 Bad Request')
        tender['status'] = status
        _save_json(TENDERS_FILE, store)
        _audit('tender_status', ip, {"tender_id": tid, "status": status})
        return _json_response(start_response, {"ok": True, "tender": tender})

    if path == '/api/tenders/award' and method == 'POST':
        user = _get_user(environ)
        if not user:
            return _json_response(start_response, {"error": "Auth required"}, '401 Unauthorized')
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        payload = json.loads(body or b'{}')
        tid = payload.get('tender_id')
        bidder_name = (payload.get('bidder_name') or '')[:160]
        store = _load_json(TENDERS_FILE)
        tender = next((t for t in store.get('tenders', []) if t.get('id') == tid), None)
        if not tender:
            return _json_response(start_response, {"error": "Unknown tender"}, '404 Not Found')
        if user.get('role') != 'admin' and tender.get('owner_email','').lower() != user.get('email'):
            return _json_response(start_response, {"error": "Forbidden"}, '403 Forbidden')
        tender['awarded_to'] = bidder_name
        tender['status'] = 'awarded'
        _save_json(TENDERS_FILE, store)
        _audit('tender_award', ip, {"tender_id": tid, "bidder": bidder_name})
        return _json_response(start_response, {"ok": True, "tender": tender})

    # Bids existing endpoint unchanged above

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

    # Escrow endpoints (simulated)
    if path == '/api/escrow/create' and method == 'POST':
        user = _get_user(environ)
        if not user:
            return _json_response(start_response, {"error": "Auth required"}, '401 Unauthorized')
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length else b''
        payload = json.loads(body or b'{}')
        tid = payload.get('tender_id')
        amount = float(payload.get('amount') or 0)
        payee = (payload.get('payee_name') or '')[:160]
        esc = _load_json(ESCROWS_FILE)
        escrow = {
            "id": f"e_{int(datetime.datetime.utcnow().timestamp())}",
            "tender_id": tid,
            "payer_email": user['email'],
            "payee_name": payee,
            "amount": amount,
            "state": "created",
            "history": [{"ts": _now_iso(), "event": "created"}],
        }
        esc.setdefault('escrows', []).append(escrow)
        _save_json(ESCROWS_FILE, esc)
        _audit('escrow_create', ip, {"escrow": escrow['id']})
        return _json_response(start_response, {"ok": True, "escrow": escrow})

    def _escrow_transition(eid: str, new_state: str, event: str):
        esc = _load_json(ESCROWS_FILE)
        escrow = next((e for e in esc.get('escrows', []) if e.get('id') == eid), None)
        if not escrow:
            return None
        escrow['state'] = new_state
        escrow.setdefault('history', []).append({"ts": _now_iso(), "event": event})
        _save_json(ESCROWS_FILE, esc)
        return escrow

    if path == '/api/escrow/fund' and method == 'POST':
        payload = json.loads((environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH') or 0)) or b'{}'))
        eid = payload.get('escrow_id')
        esc = _escrow_transition(eid, 'funded', 'funded')
        if not esc: return _json_response(start_response, {"error": "Not found"}, '404 Not Found')
        _audit('escrow_fund', ip, {"escrow": eid})
        return _json_response(start_response, {"ok": True, "escrow": esc})

    if path == '/api/escrow/release' and method == 'POST':
        payload = json.loads((environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH') or 0)) or b'{}'))
        eid = payload.get('escrow_id')
        esc = _escrow_transition(eid, 'released', 'released')
        if not esc: return _json_response(start_response, {"error": "Not found"}, '404 Not Found')
        _audit('escrow_release', ip, {"escrow": eid})
        return _json_response(start_response, {"ok": True, "escrow": esc})

    if path == '/api/escrow/refund' and method == 'POST':
        payload = json.loads((environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH') or 0)) or b'{}'))
        eid = payload.get('escrow_id')
        esc = _escrow_transition(eid, 'refunded', 'refunded')
        if not esc: return _json_response(start_response, {"error": "Not found"}, '404 Not Found')
        _audit('escrow_refund', ip, {"escrow": eid})
        return _json_response(start_response, {"ok": True, "escrow": esc})

    # Admin analytics
    if path == '/api/admin/analytics' and method == 'GET':
        user = _get_user(environ)
        if not user or user.get('role') != 'admin':
            return _json_response(start_response, {"error": "Admin only"}, '403 Forbidden')
        tenders = _load_json(TENDERS_FILE)
        esc = _load_json(ESCROWS_FILE)
        kyc = _load_json(KYC_FILE)
        users = _load_json(USERS_FILE)
        stats = {
            "counts": {
                "tenders": len(tenders.get('tenders', [])),
                "bids": len(tenders.get('bids', [])),
                "escrows": len(esc.get('escrows', [])),
                "users": len(users.get('users', [])),
                "kyc_pending": len([k for k in kyc.get('kyc', []) if k.get('status') == 'pending'])
            },
            "tenders_by_status": {s: len([t for t in tenders.get('tenders', []) if t.get('status') == s]) for s in ('open','under_review','awarded','closed')},
            "escrows_by_state": {s: len([e for e in esc.get('escrows', []) if e.get('state') == s]) for s in ('created','funded','released','refunded')},
        }
        return _json_response(start_response, stats)

    # 404
    start_response('404 Not Found', [('Content-Type', 'application/json')])
    return [json.dumps({"error": "Not Found"}).encode('utf-8')]


def run(host='0.0.0.0', port=8000):
    with make_server(host, port, application) as httpd:
        print(f"Web portal running on http://{host}:{port}")
        httpd.serve_forever()

if __name__ == '__main__':
    run()