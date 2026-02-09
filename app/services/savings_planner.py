import math
from sqlalchemy.orm import Session
from app.db.models import Debt


def calculate_savings_plan(
    db: Session,
    free_cash: float,
    target_amount: float,
):
    # EMI that will be freed once debts are cleared
    emi_rows = db.query(Debt.emi_amount).all()
    total_emi = sum(e[0] or 0 for e in emi_rows)

    monthly_saving_power = free_cash + total_emi

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
