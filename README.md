### House Hisab — Three‑Fund Ledger

Prereqs: Python 3.11+, Node 18+

Backend (FastAPI + SQLite)
- cd backend
- python -m venv .venv && source .venv/bin/activate
- pip install -r requirements.txt
- uvicorn app.main:app --reload --port 8000
- Seed once (optional): python -m backend.seed.load_seed

Frontend (Next.js)
- cd frontend
- npm install
- echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
- npm run dev

APIs
- GET http://localhost:8000/api/v1/funds
- POST http://localhost:8000/api/v1/transactions

Note: Stored balances are authoritative and updated by SQLite triggers for posting transactions.
