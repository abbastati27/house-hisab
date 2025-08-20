from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Person
from ..schemas import PersonCreate, PersonOut, PersonUpdate

router = APIRouter(prefix="/api/v1/people", tags=["people"])


def _generate_id(name: str) -> str:
    base = "p_" + "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
    return base


@router.get("", response_model=list[PersonOut])
def list_people(db: Session = Depends(get_db)):
    return db.execute(select(Person).order_by(Person.name)).scalars().all()


@router.post("", response_model=PersonOut)
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    pid = payload.id or _generate_id(payload.name)
    if db.get(Person, pid):
        raise HTTPException(status_code=409, detail="person with id already exists")
    p = Person(id=pid, name=payload.name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{person_id}", response_model=PersonOut)
def update_person(person_id: str, payload: PersonUpdate, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="person not found")
    p.name = payload.name
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{person_id}")
def delete_person(person_id: str, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="person not found")
    db.delete(p)
    db.commit()
    return {"ok": True}
