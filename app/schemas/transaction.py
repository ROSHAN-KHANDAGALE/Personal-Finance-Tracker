from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field


# -------------------------
# Base Schema
# -------------------------
class TransactionBase(BaseModel):
    date: date
    type: str = Field(..., examples=["Income", "Expense"])
    category: str
    amount: float
    payment_mode: str | None = None


# -------------------------
# Create Schema (POST)
# -------------------------
class TransactionCreate(TransactionBase):
    date: date
    type: str
    category: str
    amount: float
    payment_mode: str | None = None


# -------------------------
# Response Schema
# -------------------------
class TransactionResponse(TransactionBase):
    id: UUID
    user_id: UUID
    date: date
    type: str
    category: str
    amount: float
    payment_mode: str | None
    created_at: datetime

    class Config:
        from_attributes = True
