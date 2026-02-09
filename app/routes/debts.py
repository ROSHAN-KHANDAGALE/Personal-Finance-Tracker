# app/routes/debts.py
from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.schemas.debt import DebtCreate, DebtResponse

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.get(
    "/",
    response_model=list[DebtResponse],
    status_code=status.HTTP_200_OK,
)
def get_debts(db: Session = Depends(get_db)):
    return db.query(models.Debt).all()


@router.post(
    "/",
    response_model=DebtResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_debt(
    payload: DebtCreate,
    db: Session = Depends(get_db),
):
    USER_ID = UUID("00000000-0000-0000-0000-000000000001")

    debt = models.Debt(
        user_id=USER_ID,
        creditor_name=payload.creditor_name,
        total_amount=payload.total_amount,
        remaining_amount=payload.total_amount,
        emi_amount=payload.emi_amount,
        interest_rate=payload.interest_rate,
        is_flexible=payload.is_flexible,
        priority=payload.priority,
        status="active",
    )

    db.add(debt)
    db.commit()
    db.refresh(debt)

    return debt
