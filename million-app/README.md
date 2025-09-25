# Million-App

AI-assisted document insight platform (MVP). Upload files and get instant, explainable insights. Built to evolve into enterprise knowledge analysis, compliance checks, and intelligent search — a plausible path to multi-million valuation.

## Folders
- backend: FastAPI service
- frontend: React (Vite + TS)
- ops: deployment scripts

## Local development (without Docker)

Backend:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit API_KEY if desired
uvicorn app.main:app --reload --port 8000
```

Frontend (in a new terminal):
```bash
cd frontend
npm install
cp .env.example .env   # optional; defaults provided
npm run dev
```

Open the app at: http://localhost:5173

## API

- Health: GET http://localhost:8000/health
- Upload & analyze: POST http://localhost:8000/api/upload
  - Headers: `x-api-key: <your_api_key>` (default `dev-secret-key`)
  - Body: multipart form-data with field `file`

## Docker (optional)

If you have Docker:
```bash
docker compose up --build
```

## Positioning & value

- Start as a delightful, fast document analysis assistant that extracts structure, summaries, and risks.
- Land-and-expand to teams with shared workspaces, SOC2-ready logging, and policy checks.
- Clear ROI: save hours per document, reduce compliance risk, unify knowledge search.

## Go-to-market (outline)

- Narrow ICPs: legal ops, vendor due diligence, compliance, customer success runbooks.
- Bottom-up motion: free trial, usage-based pricing, single-tenant upgrades later.
- Integrations: Google Drive, Slack, Notion; export to DOCX/PDF; API for workflows.
