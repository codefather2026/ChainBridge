import uuid

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin


class ChainTransaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("chain", "tx_hash", name="uq_transactions_chain_tx_hash"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    swap_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cross_chain_swaps.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("swap_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    htlc_id = Column(UUID(as_uuid=True), ForeignKey("htlcs.id", ondelete="SET NULL"), nullable=True, index=True)

    chain = Column(String, nullable=False, index=True)
    tx_hash = Column(String, nullable=False, index=True)
    tx_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending", index=True)

    amount = Column(BigInteger, nullable=True)
    asset = Column(String, nullable=True)
    block_number = Column(BigInteger, nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
