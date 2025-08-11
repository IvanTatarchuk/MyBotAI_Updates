# Deploy on Render (step by step)

1. Repo → GitHub (push aktualnego kodu)
2. W Render.com → New → Blueprint → wskaż repo z `render.yaml`
3. W Environment Variables ustaw:
   - SECRET_KEY: (własny losowy ciąg)
   - VERTICALS: construction,transport,dev
   - BASE_URL: https://twoja‑domena
   - PORT: 8000
4. Deploy → poczekaj aż status będzie Live
5. Ustaw DNS CNAME subdomen (construction/transport/dev) na adres Render
6. Test:
   - GET /healthz → {"status":"ok"}
   - GET /readyz → {"ready":true}
   - UI: / i /admin

Skalowanie
- Change instance → zwiększ RAM/CPU lub worker’y (Gunicorn)
- AutoDeploy: on (z master/main)

Logi i diagnostyka
- Logs → sprawdź start i błędy
- /healthz i /readyz do monitoringu