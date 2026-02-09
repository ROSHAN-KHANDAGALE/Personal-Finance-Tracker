# app/services/debt_simulator.py
from typing import List, Dict, Optional


class DebtItem:
    def __init__(
        self,
        name: str,
        remaining: float,
        emi: Optional[float],
        is_flexible: bool,
        priority: int,
    ):
        self.name = name
        self.remaining = remaining
        self.emi = emi
        self.is_flexible = is_flexible
        self.priority = priority


def simulate_debt_clearance(
    monthly_income: float,
    living_expenses: float,
    debts: List[DebtItem],
) -> Dict:
    # Mandatory EMI
    mandatory_emi = sum(d.emi or 0 for d in debts)

    free_cash = monthly_income - living_expenses - mandatory_emi

    if free_cash < 0:
        return {"error": "Expenses + EMI exceed income"}

    # Higher priority = lower number
    debts = sorted(debts, key=lambda d: d.priority)

    month = 0
    breakdown = []

    while any(d.remaining > 0 for d in debts):
        month += 1
        extra_cash = free_cash

        snapshot = {"month": month, "payments": []}

        for debt in debts:
            if debt.remaining <= 0:
                continue

            # Fixed EMI
            if debt.emi is not None:
                payment = min(debt.emi, debt.remaining)
                debt.remaining -= payment
                snapshot["payments"].append(
                    {"debt": debt.name, "amount": round(payment, 2)}
                )
                continue

            # Flexible debt
            if debt.is_flexible and extra_cash > 0:
                payment = min(extra_cash, debt.remaining)
                debt.remaining -= payment
                extra_cash -= payment
                snapshot["payments"].append(
                    {"debt": debt.name, "amount": round(payment, 2)}
                )

        breakdown.append(snapshot)

        if month > 120:
            break

    return {
        "total_months": month,
        "monthly_breakdown": breakdown,
    }
