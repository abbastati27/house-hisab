from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Transaction, Person, Category
from ..schemas import TransactionCreate, TransactionOut, TransactionUpdate

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut)
def create_txn(payload: TransactionCreate, db: Session = Depends(get_db)):
    # Upstream schema validation already performed
    tid = payload.id or f"t{(abs(hash((payload.txn_type, payload.amount_paise, payload.date))%10**8)):08d}"
    if db.get(Transaction, tid):
        raise HTTPException(status_code=409, detail="transaction id already exists")
    t = Transaction(
        id=tid,
        txn_type=payload.txn_type,
        amount_paise=payload.amount_paise,
        date=payload.date,
        posting=payload.posting,
        fund_from=payload.fund_from,
        fund_to=payload.fund_to,
        person_id=payload.person_id,
        category_id=payload.category_id,
        party=payload.party,
        notes=payload.notes,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("", response_model=list[TransactionOut])
def list_txns(
    type: Optional[str] = Query(None, alias="type"),
    fund: Optional[str] = None,
    category_id: Optional[str] = None,
    person_id: Optional[str] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
    posting: Optional[bool] = None,
    q: Optional[str] = None,
    page: int = 1,
    db: Session = Depends(get_db),
):
    stmt = select(Transaction)
    conds = []
    if type:
        conds.append(Transaction.txn_type == type)
    if fund:
        conds.append(or_(Transaction.fund_from == fund, Transaction.fund_to == fund))
    if category_id:
        conds.append(Transaction.category_id == category_id)
    if person_id:
        conds.append(Transaction.person_id == person_id)
    if from_date:
        conds.append(Transaction.date >= from_date)
    if to:
        conds.append(Transaction.date <= to)
    if posting is not None:
        conds.append(Transaction.posting == posting)
    if q:
        like = f"%{q}%"
        conds.append(or_(Transaction.notes.like(like), Transaction.party.like(like)))
    if conds:
        stmt = stmt.where(and_(*conds))
    stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(100).offset((page - 1) * 100)
    return db.execute(stmt).scalars().all()


@router.get("/{txn_id}", response_model=TransactionOut)
def get_txn(txn_id: str, db: Session = Depends(get_db)):
    t = db.get(Transaction, txn_id)
    if not t:
        raise HTTPException(status_code=404, detail="transaction not found")
    return t


@router.put("/{txn_id}", response_model=TransactionOut)
def update_txn(txn_id: str, payload: TransactionUpdate, db: Session = Depends(get_db)):
    t = db.get(Transaction, txn_id)
    if not t:
        raise HTTPException(status_code=404, detail="transaction not found")
    # Assign all fields
    t.txn_type = payload.txn_type
    t.amount_paise = payload.amount_paise
    t.date = payload.date
    t.posting = payload.posting
    t.fund_from = payload.fund_from
    t.fund_to = payload.fund_to
    t.person_id = payload.person_id
    t.category_id = payload.category_id
    t.party = payload.party
    t.notes = payload.notes
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{txn_id}")
def delete_txn(txn_id: str, db: Session = Depends(get_db)):
    t = db.get(Transaction, txn_id)
    if not t:
        raise HTTPException(status_code=404, detail="transaction not found")
    db.delete(t)
    db.commit()
    return {"ok": True}
