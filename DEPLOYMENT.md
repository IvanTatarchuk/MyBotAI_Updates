# Deployment Guide - Web Portal (stdlib-only)

## Quick Start (development)

1. Run the server:
   ```bash
   python3 web_portal/app.py
   ```
2. Open `http://localhost:8000`

## Production (reverse proxy)

- Use a reverse proxy (e.g., Nginx/Apache) to proxy to `127.0.0.1:8000`.
- Enable HTTPS (Let's Encrypt) and HTTP security headers.

Example Nginx:
```nginx
server {
  listen 80;
  server_name example.com;
  location / { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; }
}
```

## Data & Logs

- Data: `web_portal/data/`
- Logs: `web_portal/logs/audit.log`
- Legal docs: `web_portal/legal/`

## Compliance

- Consent banner enabled on UI
- Erasure endpoint: `POST /api/request_erasure { email }`
- Minimal PII, hashed IPs, CSP headers