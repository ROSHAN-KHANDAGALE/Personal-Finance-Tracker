from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List


class BudgetCategoryCreate(BaseModel):
    category: str = Field(..., description="Transaction category name")
    limit_amount: Decimal = Field(..., gt=0, description="Spending limit for this category")


class BudgetCategoryResponse(BaseModel):
    id: UUID
    category: str
    limit_amount: Decimal

    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    name: str
    year: int = Field(..., ge=2000, le=3000)
    month: int = Field(..., ge=1, le=12)


class BudgetCreate(BudgetBase):
    categories: List[BudgetCategoryCreate]


class BudgetResponse(BudgetBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    categories: List[BudgetCategoryResponse] = []

    class Config:
        from_attributes = True


class BudgetCategorySummary(BaseModel):
    category: str
    limit_amount: Decimal
    spent: Decimal
    remaining: Decimal
    utilization_percent: float


class BudgetSummary(BaseModel):
    budget: BudgetResponse
    categories: List[BudgetCategorySummary]
    total_limit: Decimal
    total_spent: Decimal
    total_remaining: Decimal

