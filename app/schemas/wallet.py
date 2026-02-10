from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WalletBase(BaseModel):
    name: str = Field(..., max_length=255)
    base_currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
        description="ISO currency code, e.g. INR, USD, EUR",
    )


class WalletCreate(WalletBase):
    """
    Payload to create a wallet. The caller becomes the owner.
    """


class WalletUpdate(BaseModel):
    name: str | None = None
    base_currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="ISO currency code, e.g. INR, USD, EUR",
    )


class WalletMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class WalletResponse(WalletBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    members: list[WalletMemberResponse] = []

    class Config:
        from_attributes = True


class WalletWithRole(WalletResponse):
    """
    Wallet plus the current user's role within it.
    """

    current_user_role: str

