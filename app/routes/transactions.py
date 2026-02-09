# app/routes/transactions.py
from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get(
    "/",
    response_model=list[TransactionResponse],
    status_code=status.HTTP_200_OK,
)
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    USER_ID = UUID("00000000-0000-0000-0000-000000000001")

    transaction = models.Transaction(
        user_id=USER_ID,
        date=payload.date,
        type=payload.type,
        category=payload.category,
        amount=payload.amount,
        payment_mode=payload.payment_mode,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction
