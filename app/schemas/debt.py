from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


# -------------------------
# Base Schema
# -------------------------
class DebtBase(BaseModel):
    creditor_name: str
    total_amount: float
    interest_rate: Optional[float] = None

    emi_amount: Optional[float] = None   # NULL = no EMI
    is_flexible: bool = False
    priority: int = 0


# -------------------------
# Create Schema (POST)
# -------------------------
class DebtCreate(DebtBase):
    creditor_name: str
    total_amount: Decimal
    emi_amount: Decimal | None = None
    interest_rate: Decimal | None = None
    is_flexible: bool = False
    priority: int = 0


# -------------------------
# Response Schema
# -------------------------
class DebtResponse(DebtBase):
    id: UUID
    user_id: UUID
    creditor_name: str
    total_amount: Decimal
    remaining_amount: Decimal
    emi_amount: Decimal | None
    interest_rate: Decimal | None
    is_flexible: bool
    priority: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
