# app/services/planner_service.py
from sqlalchemy.orm import Session

from app.db.models import Transaction, Debt
from app.services.debt_simulator import DebtItem, simulate_debt_clearance


def calculate_financial_summary(db: Session):
    # Total Income
    income_rows = (
        db.query(Transaction.amount)
        .filter(Transaction.type == "Income")
        .all()
    )
    total_income = sum(i[0] for i in income_rows)

    # Living Expenses (exclude debt-related)
    expense_rows = (
        db.query(Transaction.amount)
        .filter(
            Transaction.type == "Expense",
            Transaction.category.notin_(["Loan", "EMI", "Debt"])
        )
        .all()
    )
    living_expenses = sum(e[0] for e in expense_rows)

    # Mandatory EMI (only non-flexible debts)
    emi_rows = (
        db.query(Debt.emi_amount)
        .filter(Debt.is_flexible.is_(False))
        .all()
    )
    mandatory_emi = sum(e[0] or 0 for e in emi_rows)

    free_cash = total_income - living_expenses - mandatory_emi

    return {
        "total_income": round(total_income, 2),
        "living_expenses": round(living_expenses, 2),
        "mandatory_emi": round(mandatory_emi, 2),
        "free_cash": round(free_cash, 2),
    }


def run_financial_planner(db: Session):
    summary = calculate_financial_summary(db)

    if summary["free_cash"] < 0:
        return {
            "summary": summary,
            "error": "Expenses + EMI exceed income",
        }

    debt_items = []
    debts = db.query(Debt).all()

    for d in debts:
        debt_items.append(
            DebtItem(
                name=d.creditor_name,
                remaining=float(d.remaining_amount),
                emi=float(d.emi_amount) if d.emi_amount is not None else None,
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
