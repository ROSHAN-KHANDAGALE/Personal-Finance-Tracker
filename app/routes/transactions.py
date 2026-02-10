from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get(
    "/",
    response_model=list[TransactionResponse],
    status_code=status.HTTP_200_OK,
)
def get_transactions(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    List transactions for the current user only.
    """
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == user_id)
        .all()
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
def get_transaction_by_id(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Get a single transaction, ensuring it belongs to the current user.
    """
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.user_id == user_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Create a transaction for the current user.
    """
    transaction = models.Transaction(
        user_id=user_id,
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


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
def update_transaction(
    transaction_id: UUID,
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Update a transaction owned by the current user.
    """
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.user_id == user_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    transaction.date = payload.date
    transaction.type = payload.type
    transaction.category = payload.category
    transaction.amount = payload.amount
    transaction.payment_mode = payload.payment_mode

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Delete a transaction owned by the current user.
    """
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.user_id == user_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    db.delete(transaction)
    db.commit()

