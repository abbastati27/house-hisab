from __future__ import annotations

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Transaction, FundBalance, Category, Person
from ..schemas import SummaryReportOut, TopEntry

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/summary", response_model=SummaryReportOut)
def summary(posting: bool = True, db: Session = Depends(get_db)):
    sum_contrib = db.execute(
        select(func.coalesce(func.sum(Transaction.amount_paise), 0)).where(
            Transaction.posting == posting, Transaction.txn_type == "CONTRIBUTION"
        )
    ).scalar_one()
    sum_income = db.execute(
        select(func.coalesce(func.sum(Transaction.amount_paise), 0)).where(
            Transaction.posting == posting, Transaction.txn_type == "INCOME"
        )
    ).scalar_one()
    sum_expense = db.execute(
        select(func.coalesce(func.sum(Transaction.amount_paise), 0)).where(
            Transaction.posting == posting, Transaction.txn_type == "EXPENSE"
        )
    ).scalar_one()

    funds = db.execute(select(FundBalance)).scalars().all()
    stored_total = sum(f.balance_paise for f in funds)

    discrepancy = stored_total - (sum_contrib + sum_income - sum_expense)

    return SummaryReportOut(
        total_contributions=sum_contrib,
        total_income=sum_income,
        total_expenses=sum_expense,
        stored_total_funds=stored_total,
        discrepancy=discrepancy,
    )


@router.get("/top-categories", response_model=list[TopEntry])
def top_categories(limit: int = 8, posting: bool = True, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Transaction.category_id, Category.name, func.sum(Transaction.amount_paise).label("total"))
        .join(Category, Category.id == Transaction.category_id)
        .where(Transaction.posting == posting, Transaction.txn_type == "EXPENSE")
        .group_by(Transaction.category_id, Category.name)
        .order_by(func.sum(Transaction.amount_paise).desc())
        .limit(limit)
    ).all()
    return [TopEntry(id=cid, name=name, total_paise=total) for cid, name, total in rows]


@router.get("/top-people", response_model=list[TopEntry])
def top_people(limit: int = 8, posting: bool = True, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Transaction.person_id, Person.name, func.sum(Transaction.amount_paise).label("total"))
        .join(Person, Person.id == Transaction.person_id)
        .where(Transaction.posting == posting, Transaction.txn_type == "CONTRIBUTION")
        .group_by(Transaction.person_id, Person.name)
        .order_by(func.sum(Transaction.amount_paise).desc())
        .limit(limit)
    ).all()
    return [TopEntry(id=pid, name=name, total_paise=total) for pid, name, total in rows]


@router.get("/export.csv")
def export_csv(scope: str = "transactions", posting: bool = True, db: Session = Depends(get_db)):
    buf = io.StringIO()
    writer = csv.writer(buf)
    if scope == "transactions":
        writer.writerow(["id","txn_type","amount_paise","date","posting","fund_from","fund_to","person_id","category_id","party","notes"])
        rows = db.execute(select(Transaction).where(Transaction.posting == posting).order_by(Transaction.date)).scalars().all()
        for t in rows:
            writer.writerow([t.id, t.txn_type, t.amount_paise, t.date.isoformat(), int(t.posting), t.fund_from, t.fund_to, t.person_id, t.category_id, (t.party or ""), (t.notes or "")])
    elif scope == "people":
        writer.writerow(["id","name"])
        for p in db.execute(select(Person).order_by(Person.name)).scalars().all():
            writer.writerow([p.id, p.name])
    elif scope == "categories":
        writer.writerow(["id","name"])
        for c in db.execute(select(Category).order_by(Category.name)).scalars().all():
            writer.writerow([c.id, c.name])
    else:
        writer.writerow(["error"]) ; writer.writerow(["unknown scope"])  # simple guard
    return Response(content=buf.getvalue(), media_type="text/csv")
