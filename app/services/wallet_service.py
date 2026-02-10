from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Wallet, WalletMember
from app.schemas.wallet import WalletCreate, WalletUpdate


def create_wallet(
    db: Session,
    owner_id: UUID,
    payload: WalletCreate,
) -> Wallet:
    wallet = Wallet(
        owner_id=owner_id,
        name=payload.name,
        base_currency=payload.base_currency,
    )
    db.add(wallet)
    db.flush()

    owner_membership = WalletMember(
        wallet_id=wallet.id,
        user_id=owner_id,
        role="owner",
    )
    db.add(owner_membership)

    db.commit()
    db.refresh(wallet)
    return wallet


def list_wallets_for_user(
    db: Session,
    user_id: UUID,
) -> List[Wallet]:
    """
    All wallets where the user is a member (including owned ones).
    """
    return (
        db.query(Wallet)
        .join(WalletMember, WalletMember.wallet_id == Wallet.id)
        .filter(WalletMember.user_id == user_id)
        .order_by(Wallet.created_at.desc())
        .all()
    )


def get_wallet_for_user(
    db: Session,
    user_id: UUID,
    wallet_id: UUID,
) -> Optional[Wallet]:
    """
    Fetch wallet if the user is a member.
    """
    return (
        db.query(Wallet)
        .join(WalletMember, WalletMember.wallet_id == Wallet.id)
        .filter(
            Wallet.id == wallet_id,
            WalletMember.user_id == user_id,
        )
        .first()
    )


def get_user_role_in_wallet(
    db: Session,
    user_id: UUID,
    wallet_id: UUID,
) -> Optional[str]:
    membership = (
        db.query(WalletMember)
        .filter(
            WalletMember.wallet_id == wallet_id,
            WalletMember.user_id == user_id,
        )
        .first()
    )
    return membership.role if membership else None


def update_wallet(
    db: Session,
    user_id: UUID,
    wallet_id: UUID,
    payload: WalletUpdate,
) -> Optional[Wallet]:
    """
    Only the owner can update the wallet.
    """
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet or wallet.owner_id != user_id:
        return None

    if payload.name is not None:
        wallet.name = payload.name
    if payload.base_currency is not None:
        wallet.base_currency = payload.base_currency

    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def delete_wallet(
    db: Session,
    user_id: UUID,
    wallet_id: UUID,
) -> bool:
    """
    Only the owner can delete the wallet.
    NOTE: This will fail if there are related records and
    cascading rules are not configured in the DB.
    """
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet or wallet.owner_id != user_id:
        return False

    db.delete(wallet)
    db.commit()
    return True


def add_member(
    db: Session,
    owner_id: UUID,
    wallet_id: UUID,
    user_id: UUID,
    role: str = "member",
) -> Optional[WalletMember]:
    """
    Only the owner can add members.
    """
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet or wallet.owner_id != owner_id:
        return None

    existing = (
        db.query(WalletMember)
        .filter(
            WalletMember.wallet_id == wallet_id,
            WalletMember.user_id == user_id,
        )
        .first()
    )
    if existing:
        existing.role = role
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    member = WalletMember(
        wallet_id=wallet_id,
        user_id=user_id,
        role=role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_member(
    db: Session,
    owner_id: UUID,
    wallet_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Only the owner can remove members.
    """
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet or wallet.owner_id != owner_id:
        return False

    membership = (
        db.query(WalletMember)
        .filter(
            WalletMember.wallet_id == wallet_id,
            WalletMember.user_id == user_id,
        )
        .first()
    )
    if not membership:
        return False

    db.delete(membership)
    db.commit()
    return True

