from datetime import date, timedelta
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import RecurringTransaction, Transaction
from app.schemas.recurring import RecurringCreate, RecurringUpdate


def _next_date(current: date, frequency: str) -> date:
    """
    Compute the next run date based on frequency.
    """
    freq = frequency.lower()
    if freq == "daily":
        return current + timedelta(days=1)
    if freq == "weekly":
        return current + timedelta(weeks=1)
    if freq == "monthly":
        # naive month increment
        month = current.month + 1
        year = current.year
        if month > 12:
            month = 1
            year += 1
        day = min(current.day, 28)  # keep simple to avoid invalid dates
        return date(year, month, day)
    if freq == "yearly":
        return date(current.year + 1, current.month, current.day)
    # default: one month
    return current + timedelta(days=30)


def create_recurring(
    db: Session,
    user_id: UUID,
    payload: RecurringCreate,
) -> RecurringTransaction:
    rt = RecurringTransaction(
        user_id=user_id,
        type=payload.type,
        category=payload.category,
        amount=payload.amount,
        payment_mode=payload.payment_mode,
        frequency=payload.frequency,
        start_date=payload.start_date,
        end_date=payload.end_date,
        next_run_date=payload.start_date,
        is_active=True,
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def list_recurring(
    db: Session,
    user_id: UUID,
) -> List[RecurringTransaction]:
    return (
        db.query(RecurringTransaction)
        .filter(RecurringTransaction.user_id == user_id)
        .order_by(RecurringTransaction.created_at.desc())
        .all()
    )


def get_recurring(
    db: Session,
    user_id: UUID,
    recurring_id: UUID,
) -> RecurringTransaction | None:
    return (
        db.query(RecurringTransaction)
        .filter(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id,
        )
        .first()
    )


def update_recurring(
    db: Session,
    user_id: UUID,
    recurring_id: UUID,
    payload: RecurringUpdate,
) -> RecurringTransaction | None:
    rt = get_recurring(db, user_id, recurring_id)
    if not rt:
        return None

    if payload.type is not None:
        rt.type = payload.type
    if payload.category is not None:
        rt.category = payload.category
    if payload.amount is not None:
        rt.amount = payload.amount
    if payload.payment_mode is not None:
        rt.payment_mode = payload.payment_mode
    if payload.frequency is not None:
        rt.frequency = payload.frequency
    if payload.start_date is not None:
        rt.start_date = payload.start_date
        rt.next_run_date = payload.start_date
    if payload.end_date is not None:
        rt.end_date = payload.end_date
    if payload.is_active is not None:
        rt.is_active = payload.is_active

    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def delete_recurring(
    db: Session,
    user_id: UUID,
    recurring_id: UUID,
) -> bool:
    rt = get_recurring(db, user_id, recurring_id)
    if not rt:
        return False

    db.delete(rt)
    db.commit()
    return True


def run_recurring_scheduler(
    db: Session,
    user_id: UUID,
    today: date | None = None,
) -> int:
    """
    Materialize due recurring transactions for a user into Transaction rows.

    Returns number of transactions created.
    """
    if today is None:
        today = date.today()

    due_items = (
        db.query(RecurringTransaction)
        .filter(
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.is_active.is_(True),
            RecurringTransaction.next_run_date <= today,
        )
        .all()
    )

    created_count = 0

    for rt in due_items:
        # Check end_date
        if rt.end_date and rt.next_run_date > rt.end_date:
            rt.is_active = False
            db.add(rt)
            continue

        # Create concrete transaction
        tx = Transaction(
            user_id=user_id,
            date=rt.next_run_date,
            type=rt.type,
            category=rt.category,
            amount=rt.amount,
            payment_mode=rt.payment_mode,
        )
        db.add(tx)
        created_count += 1

        # Move next_run_date forward
        rt.next_run_date = _next_date(rt.next_run_date, rt.frequency)

        # If after advance we're past end_date, deactivate
        if rt.end_date and rt.next_run_date > rt.end_date:
            rt.is_active = False

        db.add(rt)

    if created_count > 0:
        db.commit()

    return created_count

