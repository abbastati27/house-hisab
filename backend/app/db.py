from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./house_hisab.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_triggers_if_missing() -> None:
    """Create SQLite triggers to keep fund balances in sync with transactions."""
    with engine.begin() as conn:
        # INSERT
        conn.execute(text(
            """
            CREATE TRIGGER IF NOT EXISTS trg_txn_insert
            AFTER INSERT ON transactions
            BEGIN
                UPDATE fund_balances SET balance_paise = balance_paise + NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type IN ('CONTRIBUTION','INCOME') AND fund = NEW.fund_to;

                UPDATE fund_balances SET balance_paise = balance_paise - NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type = 'EXPENSE' AND fund = NEW.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise - NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type = 'TRANSFER' AND fund = NEW.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise + NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type = 'TRANSFER' AND fund = NEW.fund_to;
            END;
            """
        ))

        # UPDATE: reverse OLD if it was posting, then apply NEW if posting
        conn.execute(text(
            """
            CREATE TRIGGER IF NOT EXISTS trg_txn_update
            AFTER UPDATE ON transactions
            BEGIN
                UPDATE fund_balances SET balance_paise = balance_paise - OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type IN ('CONTRIBUTION','INCOME') AND fund = OLD.fund_to;

                UPDATE fund_balances SET balance_paise = balance_paise + OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type = 'EXPENSE' AND fund = OLD.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise + OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type = 'TRANSFER' AND fund = OLD.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise - OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type = 'TRANSFER' AND fund = OLD.fund_to;

                UPDATE fund_balances SET balance_paise = balance_paise + NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type IN ('CONTRIBUTION','INCOME') AND fund = NEW.fund_to;

                UPDATE fund_balances SET balance_paise = balance_paise - NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type = 'EXPENSE' AND fund = NEW.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise - NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type = 'TRANSFER' AND fund = NEW.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise + NEW.amount_paise
                WHERE NEW.posting = 1 AND NEW.txn_type = 'TRANSFER' AND fund = NEW.fund_to;
            END;
            """
        ))

        # DELETE: reverse OLD if posting
        conn.execute(text(
            """
            CREATE TRIGGER IF NOT EXISTS trg_txn_delete
            AFTER DELETE ON transactions
            BEGIN
                UPDATE fund_balances SET balance_paise = balance_paise - OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type IN ('CONTRIBUTION','INCOME') AND fund = OLD.fund_to;

                UPDATE fund_balances SET balance_paise = balance_paise + OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type = 'EXPENSE' AND fund = OLD.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise + OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type = 'TRANSFER' AND fund = OLD.fund_from;

                UPDATE fund_balances SET balance_paise = balance_paise - OLD.amount_paise
                WHERE OLD.posting = 1 AND OLD.txn_type = 'TRANSFER' AND fund = OLD.fund_to;
            END;
            """
        ))
