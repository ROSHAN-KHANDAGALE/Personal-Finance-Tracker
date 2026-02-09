from pydantic import BaseModel
from typing import List


class PaymentItem(BaseModel):
    debt: str
    amount: float


class MonthlyPlan(BaseModel):
    month: int
    payments: List[PaymentItem]


class DebtPlanResponse(BaseModel):
    total_months: int
    monthly_breakdown: List[MonthlyPlan]


class FinancialSummary(BaseModel):
    total_income: float
    living_expenses: float
    mandatory_emi: float
    free_cash: float
