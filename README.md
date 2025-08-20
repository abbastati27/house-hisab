### House Hisab — Three‑Fund Ledger

Tech stack
- Backend: FastAPI + SQLAlchemy + SQLite (stored balances with triggers)
- Frontend: Next.js (App Router) + React + Tailwind + TanStack Query

Quick start (serves UI from the backend)
- cd backend
- python -m venv .venv && source .venv/bin/activate
- pip install -r requirements.txt
- python seed/load_seed.py   # optional: seeds balances, people, categories, and historical txns
- uvicorn app.main:app --reload --port 8000
- Open http://localhost:8000 (UI) • APIs under http://localhost:8000/api/v1/*

Frontend build (static export)
- cd frontend
- npm install
- npm run build  # outputs static site to frontend/out
- The backend auto-serves `frontend/out` at /

Developer mode (optional separate frontend dev server)
- cd frontend
- npm install
- echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
- npm run dev
- Open http://localhost:3000

Key endpoints
- GET /api/v1/funds
- POST /api/v1/transactions
- GET /api/v1/reports/summary?posting=false  # seed is non‑posting, so posting=false shows totals

Notes
- Stored balances are authoritative (maintained by SQLite triggers) and not recomputed from history.
- Edit route (static export compatible): `/transactions/edit?id=TXN_ID`.
