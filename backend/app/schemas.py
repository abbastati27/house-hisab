from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator

FUND = Literal["CASH", "ONLINE_A", "ONLINE_Y"]
TXN_TYPE = Literal["CONTRIBUTION", "INCOME", "EXPENSE", "TRANSFER"]


class PersonBase(BaseModel):
    name: str


class PersonCreate(PersonBase):
    id: Optional[str] = None


class PersonUpdate(BaseModel):
    name: str


class PersonOut(PersonBase):
    id: str

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    id: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: str


class CategoryOut(CategoryBase):
    id: str

    class Config:
        from_attributes = True


class FundBalancesOut(BaseModel):
    cash: int
    online_a: int
    online_y: int
    total: int


class FundBalancesPatch(BaseModel):
    cash: Optional[int] = None
    online_a: Optional[int] = None
    online_y: Optional[int] = None


class TransactionBase(BaseModel):
    txn_type: TXN_TYPE
    amount_paise: int
    date: date
    posting: bool = True

    fund_from: Optional[FUND] = None
    fund_to: Optional[FUND] = None

    person_id: Optional[str] = None
    category_id: Optional[str] = None
    party: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount_paise")
    @classmethod
    def amount_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("amount_paise must be > 0")
        return v

    @model_validator(mode="after")
    def validate_semantics(self):
        if not self.posting:
            return self
        t = self.txn_type
        if t in ("CONTRIBUTION", "INCOME"):
            if self.fund_to is None:
                raise ValueError("fund_to required for CONTRIBUTION/INCOME when posting=true")
            if t == "CONTRIBUTION" and not self.person_id:
                raise ValueError("person_id required for CONTRIBUTION when posting=true")
        elif t == "EXPENSE":
            if self.fund_from is None:
                raise ValueError("fund_from required for EXPENSE when posting=true")
            if not self.category_id:
                raise ValueError("category_id required for EXPENSE when posting=true")
        elif t == "TRANSFER":
            if self.fund_from is None or self.fund_to is None:
                raise ValueError("fund_from and fund_to required for TRANSFER when posting=true")
            if self.fund_from == self.fund_to:
                raise ValueError("fund_from and fund_to must differ for TRANSFER")
        return self


class TransactionCreate(TransactionBase):
    id: Optional[str] = None


class TransactionUpdate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    id: str

    class Config:
        from_attributes = True


class SummaryReportOut(BaseModel):
    total_contributions: int
    total_income: int
    total_expenses: int
    stored_total_funds: int
    discrepancy: int


class TopEntry(BaseModel):
    id: Optional[str]
    name: Optional[str]
    total_paise: int
