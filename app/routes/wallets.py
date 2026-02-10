from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.dependencies import get_current_user_id
from app.schemas.wallet import (
    WalletCreate,
    WalletUpdate,
    WalletResponse,
    WalletWithRole,
)
from app.services import wallet_service


router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get(
    "/",
    response_model=list[WalletResponse],
    status_code=status.HTTP_200_OK,
)
def list_wallets(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    List all wallets the current user belongs to.
    """
    return wallet_service.list_wallets_for_user(db, user_id)


@router.post(
    "/",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_wallet(
    payload: WalletCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Create a wallet; the caller becomes the owner.
    """
    wallet = wallet_service.create_wallet(db, owner_id=user_id, payload=payload)
    return wallet


@router.get(
    "/{wallet_id}",
    response_model=WalletWithRole,
    status_code=status.HTTP_200_OK,
)
def get_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    wallet = wallet_service.get_wallet_for_user(db, user_id, wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or access denied",
        )

    role = wallet_service.get_user_role_in_wallet(db, user_id, wallet_id) or "member"
    base = WalletResponse.model_validate(wallet)
    return WalletWithRole(
        **base.model_dump(),
        current_user_role=role,
    )


@router.put(
    "/{wallet_id}",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
def update_wallet(
    wallet_id: UUID,
    payload: WalletUpdate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    wallet = wallet_service.update_wallet(db, user_id, wallet_id, payload)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the wallet owner can update the wallet",
        )
    return wallet


@router.delete(
    "/{wallet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    ok = wallet_service.delete_wallet(db, user_id, wallet_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the wallet owner can delete the wallet",
        )


@router.post(
    "/{wallet_id}/members",
    status_code=status.HTTP_201_CREATED,
)
def add_wallet_member(
    wallet_id: UUID,
    member_user_id: UUID,
    role: str = "member",
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Add or update a member in the wallet.
    Only the owner can call this.
    """
    member = wallet_service.add_member(
        db=db,
        owner_id=user_id,
        wallet_id=wallet_id,
        user_id=member_user_id,
        role=role,
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the wallet owner can manage members",
        )
    return {
        "id": member.id,
        "wallet_id": str(member.wallet_id),
        "user_id": str(member.user_id),
        "role": member.role,
    }


@router.delete(
    "/{wallet_id}/members/{member_user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_wallet_member(
    wallet_id: UUID,
    member_user_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Remove a member from the wallet.
    Only the owner can call this.
    """
    ok = wallet_service.remove_member(
        db=db,
        owner_id=user_id,
        wallet_id=wallet_id,
        user_id=member_user_id,
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the wallet owner can manage members",
        )

