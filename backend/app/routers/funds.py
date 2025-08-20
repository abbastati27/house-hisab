from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import FundBalance
from ..schemas import FundBalancesOut, FundBalancesPatch

router = APIRouter(prefix="/api/v1/funds", tags=["funds"])


@router.get("", response_model=FundBalancesOut)
def get_funds(db: Session = Depends(get_db)):
    rows = db.execute(select(FundBalance)).scalars().all()
    balance_map = {r.fund: r.balance_paise for r in rows}
    cash = balance_map.get("CASH", 0)
    oa = balance_map.get("ONLINE_A", 0)
    oy = balance_map.get("ONLINE_Y", 0)
    total = cash + oa + oy
    return {"cash": cash, "online_a": oa, "online_y": oy, "total": total}


@router.patch("", response_model=FundBalancesOut)
def patch_funds(payload: FundBalancesPatch, db: Session = Depends(get_db)):
    for fund_key, field in (("CASH", "cash"), ("ONLINE_A", "online_a"), ("ONLINE_Y", "online_y")):
        value = getattr(payload, field)
        if value is not None:
            fb = db.get(FundBalance, fund_key)
            if not fb:
                fb = FundBalance(fund=fund_key, balance_paise=0)
                db.add(fb)
            fb.balance_paise = value
    db.commit()
    return get_funds(db)
