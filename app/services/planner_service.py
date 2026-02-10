# app/services/planner_service.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Transaction, Debt
from app.services.debt_simulator import DebtItem, simulate_debt_clearance


def calculate_financial_summary(db: Session, user_id: UUID):
    """
    Compute the financial summary for a single user.

    - Total Income
    - Living Expenses (exclude loan/EMI/debt categories)
    - Mandatory EMI (only fixed-EMI debts, i.e. non-flexible)
    - Free Cash = Income − Living Expenses − Mandatory EMI
    """
    # Total Income
    income_rows = (
        db.query(Transaction.amount)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "Income",
        )
        .all()
    )
    total_income = float(sum(i[0] or 0 for i in income_rows))

    # Living Expenses (exclude loan/EMI/debt categories)
    expense_rows = (
        db.query(Transaction.amount)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "Expense",
            Transaction.category.notin_(["Loan", "EMI", "Debt"]),
        )
        .all()
    )
    living_expenses = float(sum(e[0] or 0 for e in expense_rows))

    # Mandatory EMI (only FIXED_EMI debts => non-flexible)
    emi_rows = (
        db.query(Debt.emi_amount)
        .filter(
            Debt.user_id == user_id,
            Debt.is_flexible.is_(False),
        )
        .all()
    )
    # coerce Numeric/Decimal to float explicitly to avoid type errors
    mandatory_emi = float(sum((e[0] or 0) for e in emi_rows))

    free_cash = float(total_income - living_expenses - mandatory_emi)

    return {
        "total_income": round(float(total_income), 2),
        "living_expenses": round(float(living_expenses), 2),
        "mandatory_emi": round(float(mandatory_emi), 2),
        "free_cash": round(float(free_cash), 2),
    }


def run_financial_planner(db: Session, user_id: UUID):
    """
    High-level planner for a single user:
    - Calculates summary
    - Runs debt clearance simulator
    """
    summary = calculate_financial_summary(db, user_id=user_id)

    if summary["free_cash"] < 0:
        return {
            "summary": summary,
            "error": "Expenses + EMI exceed income",
        }

    debts = (
        db.query(Debt)
        .filter(Debt.user_id == user_id)
        .all()
    )

    debt_items: list[DebtItem] = []
    for d in debts:
        debt_items.append(
            DebtItem(
                name=d.creditor_name,
                remaining=float(d.remaining_amount),
                # Only non-flexible debts are treated as fixed EMI
                emi=float(d.emi_amount)
                if d.emi_amount is not None and not d.is_flexible
                else None,
                is_flexible=d.is_flexible,
                priority=d.priority,
            )
        )

    debt_plan = simulate_debt_clearance(
        monthly_income=summary["total_income"],
        living_expenses=summary["living_expenses"],
        debts=debt_items,
    )

    return {
        "summary": summary,
        "debt_plan": debt_plan,
    }
