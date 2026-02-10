import math
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Debt


def calculate_savings_plan(
    db: Session,
    user_id: UUID,
    free_cash: float,
    target_amount: float,
):
    """
    Savings planner for a single user.

    Monthly saving power = free_cash + total EMI
    where total EMI is the sum of all current EMI obligations
    (both fixed and flexible debts with an emi_amount).
    """
    # EMI that will be freed once this user's debts are cleared
    emi_rows = (
        db.query(Debt.emi_amount)
        .filter(
            Debt.user_id == user_id,
            Debt.emi_amount.isnot(None),
        )
        .all()
    )
    # Normalize to float to avoid Decimal/float mixing
    total_emi = float(sum((e[0] or 0) for e in emi_rows))

    monthly_saving_power = float(free_cash) + total_emi

    if monthly_saving_power <= 0:
        return {
            "status": "not_possible",
            "message": "No saving capacity available",
        }

    months_required = math.ceil(target_amount / monthly_saving_power)

    return {
        "status": "possible",
        "target_amount": round(target_amount, 2),
        "monthly_saving_power": round(monthly_saving_power, 2),
        "months_required": months_required,
    }
