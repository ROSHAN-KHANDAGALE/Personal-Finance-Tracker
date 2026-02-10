# app/db/models.py
import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    Date,
    Boolean,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="user")
    debts = relationship("Debt", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    base_currency = Column(String(3), nullable=False, default="INR")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User")
    members = relationship(
        "WalletMember",
        back_populates="wallet",
        cascade="all, delete-orphan",
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id"),
        nullable=True,
        comment="Optional wallet that this transaction belongs to",
    )

    date = Column(Date, nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet")


class Debt(Base):
    __tablename__ = "debts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id"),
        nullable=True,
        comment="Optional wallet that this debt belongs to",
    )

    creditor_name = Column(String(255), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    remaining_amount = Column(Numeric(12, 2), nullable=False)

    emi_amount = Column(Numeric(12, 2), nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)

    is_flexible = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    status = Column(String(50), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="debts")
    wallet = relationship("Wallet")
    payments = relationship("Payment", back_populates="debt")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    debt_id = Column(UUID(as_uuid=True), ForeignKey("debts.id"), nullable=False)
    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id"),
        nullable=True,
        comment="Optional wallet this payment belongs to",
    )

    amount_paid = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_mode = Column(String(50), nullable=True)
    note = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payments")
    debt = relationship("Debt", back_populates="payments")
    wallet = relationship("Wallet")


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id"),
        nullable=True,
        comment="Optional wallet for which this recurring transaction applies",
    )

    type = Column(String(50), nullable=False)  # "Income" or "Expense"
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String(50), nullable=True)

    frequency = Column(
        String(20),
        nullable=False,
    )  # e.g. "daily", "weekly", "monthly", "yearly"

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    next_run_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    wallet = relationship("Wallet")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id"),
        nullable=True,
        comment="Optional wallet this budget applies to",
    )

    name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    wallet = relationship("Wallet")
    categories = relationship(
        "BudgetCategory",
        back_populates="budget",
        cascade="all, delete-orphan",
    )


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False)

    category = Column(String(100), nullable=False)
    limit_amount = Column(Numeric(12, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    budget = relationship("Budget", back_populates="categories")


class WalletMember(Base):
    __tablename__ = "wallet_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    role = Column(
        String(20),
        nullable=False,
        default="member",
        comment="Role within the wallet: owner, member, viewer, etc.",
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    wallet = relationship("Wallet", back_populates="members")
