import uuid
from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, TimestampMixin


class HTLC(Base, TimestampMixin):
    __tablename__ = "htlcs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    onchain_id = Column(String, unique=True, index=True)
    swap_id = Column(
        UUID(as_uuid=True), ForeignKey("cross_chain_swaps.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sender = Column(String, nullable=False, index=True)
    sender_user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    receiver = Column(String, nullable=False, index=True)
    receiver_user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount = Column(BigInteger, nullable=False)
    hash_lock = Column(String, nullable=False, index=True)
    time_lock = Column(BigInteger, nullable=False, index=True)
    status = Column(String, nullable=False, default="active", index=True)
    secret = Column(String, nullable=True)
    hash_algorithm = Column(String, nullable=False, default="sha256")
