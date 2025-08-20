from __future__ import annotations

import json
from pathlib import Path
import sys
from datetime import date

# Ensure the backend root (containing the 'app' package) is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from app.db import SessionLocal, Base, engine
from app.models import FundBalance, Person, Category, Transaction


def load_seed(seed_path: str | None = None) -> None:
    Base.metadata.create_all(bind=engine)
    # Resolve seed path
    if seed_path is None:
        seed_path = str(BACKEND_ROOT / "seed" / "seed.json")
    p = Path(seed_path)
    if not p.is_absolute():
        p = (BACKEND_ROOT / p).resolve()
    data = json.loads(p.read_text())

    with SessionLocal() as db:
        # fund balances
        for row in data.get("fund_balances", []):
            fb = db.get(FundBalance, row["fund"]) or FundBalance(fund=row["fund"], balance_paise=0)
            fb.balance_paise = int(row["balance_paise"])  # authoritative
            db.add(fb)
        # people
        for row in data.get("people", []):
            if not db.get(Person, row["id"]):
                db.add(Person(id=row["id"], name=row["name"]))
        # categories
        for row in data.get("categories", []):
            if not db.get(Category, row["id"]):
                db.add(Category(id=row["id"], name=row["name"]))
        db.commit()
        # transactions (non-posting historical)
        for row in data.get("transactions", []):
            if not db.get(Transaction, row["id"]):
                d = row["date"]
                d_py = date.fromisoformat(d) if isinstance(d, str) else d
                db.add(Transaction(
                    id=row["id"],
                    txn_type=row["txn_type"],
                    amount_paise=int(row["amount_paise"]),
                    date=d_py,
                    posting=bool(row["posting"]),
                    fund_from=row.get("fund_from"),
                    fund_to=row.get("fund_to"),
                    person_id=row.get("person_id"),
                    category_id=row.get("category_id"),
                    party=row.get("party"),
                    notes=row.get("notes"),
                ))
        db.commit()


if __name__ == "__main__":
    load_seed()
