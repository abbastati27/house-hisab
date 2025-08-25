from __future__ import annotations

import os
import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .db import Base, engine, create_triggers_if_missing, SessionLocal
from .models import FundBalance
from .routers import funds, transactions, people, categories, reports


def _get_local_ip() -> str:
    ip = "127.0.0.1"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
    except Exception:
        pass
    return ip


app = FastAPI(title="Three-Fund Ledger", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Ensure all fund rows exist
    with SessionLocal() as db:
        for fund in ("CASH", "ONLINE_A", "ONLINE_Y"):
            if not db.get(FundBalance, fund):
                db.add(FundBalance(fund=fund, balance_paise=0))
        db.commit()
    create_triggers_if_missing()

    # Helpful LAN URL print when running with --host 0.0.0.0
    ip = _get_local_ip()
    port = os.environ.get("PORT", "8000")
    print(f"Open on your LAN: http://{ip}:{port}")


# API routers
app.include_router(funds.router)
app.include_router(transactions.router)
app.include_router(people.router)
app.include_router(categories.router)
app.include_router(reports.router)


# Serve exported frontend
FRONTEND_EXPORT_DIR = Path(__file__).resolve().parents[2] / "frontend" / "out"
if FRONTEND_EXPORT_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_EXPORT_DIR), html=True), name="frontend")


@app.get("/api/v1/health")
def health():
    return {"ok": True}



@app.get("/")
def root():
    return {"message": "Backend is running!"}