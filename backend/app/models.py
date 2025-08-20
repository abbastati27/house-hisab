from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


FUND_VALUES = ("CASH", "ONLINE_A", "ONLINE_Y")
TXN_TYPES = ("CONTRIBUTION", "INCOME", "EXPENSE", "TRANSFER")


class Person(Base):
    __tablename__ = "people"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="person")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class FundBalance(Base):
    __tablename__ = "fund_balances"

    fund: Mapped[str] = mapped_column(String, primary_key=True)
    balance_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "txn_type IN ('CONTRIBUTION','INCOME','EXPENSE','TRANSFER')",
            name="ck_txn_type",
        ),
        CheckConstraint("amount_paise > 0", name="ck_amount_positive"),
        CheckConstraint(
            "fund_from IN ('CASH','ONLINE_A','ONLINE_Y') OR fund_from IS NULL",
            name="ck_fund_from",
        ),
        CheckConstraint(
            "fund_to IN ('CASH','ONLINE_A','ONLINE_Y') OR fund_to IS NULL",
            name="ck_fund_to",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    txn_type: Mapped[str] = mapped_column(String, nullable=False)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    posting: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    fund_from: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fund_to: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    person_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("people.id"))
    category_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("categories.id"))

    party: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    person: Mapped[Optional[Person]] = relationship(back_populates="transactions")
    category: Mapped[Optional[Category]] = relationship(back_populates="transactions")
