from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


def _generate_id(name: str) -> str:
    base = "cat_" + "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
    return base


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.execute(select(Category).order_by(Category.name)).scalars().all()


@router.post("", response_model=CategoryOut)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    cid = payload.id or _generate_id(payload.name)
    if db.get(Category, cid):
        raise HTTPException(status_code=409, detail="category with id already exists")
    c = Category(id=cid, name=payload.name)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)):
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="category not found")
    c.name = payload.name
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{category_id}")
def delete_category(category_id: str, db: Session = Depends(get_db)):
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="category not found")
    db.delete(c)
    db.commit()
    return {"ok": True}
