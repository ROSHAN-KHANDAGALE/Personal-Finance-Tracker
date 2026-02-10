from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RecurringBase(BaseModel):
    type: str = Field(..., examples=["Income", "Expense"])
    category: str
    amount: float = Field(..., gt=0)
    payment_mode: str | None = None

    frequency: str = Field(
        ...,
        description='One of: "daily", "weekly", "monthly", "yearly"',
    )
    start_date: date
    end_date: date | None = None


class RecurringCreate(RecurringBase):
    """
    Create payload; next_run_date is derived from start_date server-side.
    """


class RecurringUpdate(BaseModel):
    """
    Partial update for recurring transaction.
    """

    type: str | None = None
    category: str | None = None
    amount: float | None = Field(default=None, gt=0)
    payment_mode: str | None = None
    frequency: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class RecurringResponse(RecurringBase):
    id: UUID
    user_id: UUID
    next_run_date: date
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

