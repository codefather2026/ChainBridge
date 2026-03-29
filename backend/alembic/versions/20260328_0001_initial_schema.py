"""Initial ChainBridge schema

Revision ID: 20260328_0001
Revises:
Create Date: 2026-03-28 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260328_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("wallet_address", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("preferred_chain", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_wallet_address"), "users", ["wallet_address"], unique=True)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)

    op.create_table(
        "swap_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("onchain_id", sa.Integer(), nullable=True),
        sa.Column("creator", sa.String(), nullable=False),
        sa.Column("creator_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("counterparty_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("from_chain", sa.String(), nullable=False),
        sa.Column("to_chain", sa.String(), nullable=False),
        sa.Column("from_asset", sa.String(), nullable=False),
        sa.Column("to_asset", sa.String(), nullable=False),
        sa.Column("from_amount", sa.BigInteger(), nullable=False),
        sa.Column("to_amount", sa.BigInteger(), nullable=False),
        sa.Column("min_fill_amount", sa.BigInteger(), nullable=True),
        sa.Column("filled_amount", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("expiry", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="open"),
        sa.Column("counterparty", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('open', 'matched', 'filled', 'cancelled', 'expired')",
            name="ck_swap_orders_status",
        ),
        sa.ForeignKeyConstraint(["creator_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["counterparty_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_swap_orders_onchain_id"), "swap_orders", ["onchain_id"], unique=True)
    op.create_index(op.f("ix_swap_orders_creator"), "swap_orders", ["creator"], unique=False)
    op.create_index(op.f("ix_swap_orders_creator_user_id"), "swap_orders", ["creator_user_id"], unique=False)
    op.create_index(
        op.f("ix_swap_orders_counterparty_user_id"),
        "swap_orders",
        ["counterparty_user_id"],
        unique=False,
    )
    op.create_index(op.f("ix_swap_orders_status"), "swap_orders", ["status"], unique=False)
    op.create_index(op.f("ix_swap_orders_expiry"), "swap_orders", ["expiry"], unique=False)
    op.create_index(
        "ix_swap_orders_market_pair",
        "swap_orders",
        ["from_chain", "to_chain", "from_asset", "to_asset"],
        unique=False,
    )

    op.create_table(
        "cross_chain_swaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("onchain_id", sa.String(), nullable=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("stellar_htlc_id", sa.String(), nullable=True),
        sa.Column("other_chain", sa.String(), nullable=False),
        sa.Column("other_chain_tx", sa.String(), nullable=True),
        sa.Column("stellar_party", sa.String(), nullable=False),
        sa.Column("other_party", sa.String(), nullable=False),
        sa.Column("initiator_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("responder_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("state", sa.String(), nullable=False, server_default="initiated"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.CheckConstraint(
            "state IN ('initiated', 'locked', 'executed', 'completed', 'failed', 'refunded', 'expired')",
            name="ck_cross_chain_swaps_state",
        ),
        sa.ForeignKeyConstraint(["order_id"], ["swap_orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["initiator_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["responder_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cross_chain_swaps_onchain_id"), "cross_chain_swaps", ["onchain_id"], unique=True)
    op.create_index(op.f("ix_cross_chain_swaps_state"), "cross_chain_swaps", ["state"], unique=False)
    op.create_index(
        op.f("ix_cross_chain_swaps_other_chain"),
        "cross_chain_swaps",
        ["other_chain"],
        unique=False,
    )
    op.create_index(op.f("ix_cross_chain_swaps_order_id"), "cross_chain_swaps", ["order_id"], unique=False)
    op.create_index(
        op.f("ix_cross_chain_swaps_initiator_user_id"),
        "cross_chain_swaps",
        ["initiator_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cross_chain_swaps_responder_user_id"),
        "cross_chain_swaps",
        ["responder_user_id"],
        unique=False,
    )

    op.create_table(
        "htlcs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("onchain_id", sa.String(), nullable=True),
        sa.Column("swap_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("sender_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("receiver", sa.String(), nullable=False),
        sa.Column("receiver_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("hash_lock", sa.String(), nullable=False),
        sa.Column("time_lock", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("secret", sa.String(), nullable=True),
        sa.Column("hash_algorithm", sa.String(), nullable=False, server_default="sha256"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('active', 'claimed', 'refunded', 'expired', 'cancelled')",
            name="ck_htlcs_status",
        ),
        sa.ForeignKeyConstraint(["swap_id"], ["cross_chain_swaps.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sender_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["receiver_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_htlcs_onchain_id"), "htlcs", ["onchain_id"], unique=True)
    op.create_index(op.f("ix_htlcs_sender"), "htlcs", ["sender"], unique=False)
    op.create_index(op.f("ix_htlcs_receiver"), "htlcs", ["receiver"], unique=False)
    op.create_index(op.f("ix_htlcs_status"), "htlcs", ["status"], unique=False)
    op.create_index(op.f("ix_htlcs_hash_lock"), "htlcs", ["hash_lock"], unique=False)
    op.create_index(op.f("ix_htlcs_time_lock"), "htlcs", ["time_lock"], unique=False)
    op.create_index(op.f("ix_htlcs_swap_id"), "htlcs", ["swap_id"], unique=False)
    op.create_index(op.f("ix_htlcs_sender_user_id"), "htlcs", ["sender_user_id"], unique=False)
    op.create_index(op.f("ix_htlcs_receiver_user_id"), "htlcs", ["receiver_user_id"], unique=False)

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("swap_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("htlc_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("chain", sa.String(), nullable=False),
        sa.Column("tx_hash", sa.String(), nullable=False),
        sa.Column("tx_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("amount", sa.BigInteger(), nullable=True),
        sa.Column("asset", sa.String(), nullable=True),
        sa.Column("block_number", sa.BigInteger(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["htlc_id"], ["htlcs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["swap_orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["swap_id"], ["cross_chain_swaps.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chain", "tx_hash", name="uq_transactions_chain_tx_hash"),
    )
    op.create_index(op.f("ix_transactions_user_id"), "transactions", ["user_id"], unique=False)
    op.create_index(op.f("ix_transactions_swap_id"), "transactions", ["swap_id"], unique=False)
    op.create_index(op.f("ix_transactions_order_id"), "transactions", ["order_id"], unique=False)
    op.create_index(op.f("ix_transactions_htlc_id"), "transactions", ["htlc_id"], unique=False)
    op.create_index(op.f("ix_transactions_chain"), "transactions", ["chain"], unique=False)
    op.create_index(op.f("ix_transactions_tx_hash"), "transactions", ["tx_hash"], unique=False)
    op.create_index(op.f("ix_transactions_tx_type"), "transactions", ["tx_type"], unique=False)
    op.create_index(op.f("ix_transactions_status"), "transactions", ["status"], unique=False)
    op.create_index("ix_transactions_chain_status", "transactions", ["chain", "status"], unique=False)

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_keys_key"), "api_keys", ["key"], unique=True)
    op.create_index(op.f("ix_api_keys_owner"), "api_keys", ["owner"], unique=False)
    op.create_index(op.f("ix_api_keys_is_active"), "api_keys", ["is_active"], unique=False)

    op.create_table(
        "swap_disputes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("swap_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submitted_by", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="submitted"),
        sa.Column("priority", sa.String(), nullable=False, server_default="normal"),
        sa.Column("evidence", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("resolution_action", sa.String(), nullable=True),
        sa.Column("refund_override", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("refund_amount", sa.BigInteger(), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("action_log", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["swap_id"], ["cross_chain_swaps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_swap_disputes_swap_id"), "swap_disputes", ["swap_id"], unique=False)
    op.create_index(op.f("ix_swap_disputes_status"), "swap_disputes", ["status"], unique=False)
    op.create_index(op.f("ix_swap_disputes_priority"), "swap_disputes", ["priority"], unique=False)
    op.create_index(
        op.f("ix_swap_disputes_submitted_by"),
        "swap_disputes",
        ["submitted_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_swap_disputes_submitted_by"), table_name="swap_disputes")
    op.drop_index(op.f("ix_swap_disputes_priority"), table_name="swap_disputes")
    op.drop_index(op.f("ix_swap_disputes_status"), table_name="swap_disputes")
    op.drop_index(op.f("ix_swap_disputes_swap_id"), table_name="swap_disputes")
    op.drop_table("swap_disputes")

    op.drop_index(op.f("ix_api_keys_is_active"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_owner"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_key"), table_name="api_keys")
    op.drop_table("api_keys")

    op.drop_index("ix_transactions_chain_status", table_name="transactions")
    op.drop_index(op.f("ix_transactions_status"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_tx_type"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_tx_hash"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_chain"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_htlc_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_order_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_swap_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_user_id"), table_name="transactions")
    op.drop_table("transactions")

    op.drop_index(op.f("ix_htlcs_receiver_user_id"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_sender_user_id"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_swap_id"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_time_lock"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_hash_lock"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_status"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_receiver"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_sender"), table_name="htlcs")
    op.drop_index(op.f("ix_htlcs_onchain_id"), table_name="htlcs")
    op.drop_table("htlcs")

    op.drop_index(op.f("ix_cross_chain_swaps_responder_user_id"), table_name="cross_chain_swaps")
    op.drop_index(op.f("ix_cross_chain_swaps_initiator_user_id"), table_name="cross_chain_swaps")
    op.drop_index(op.f("ix_cross_chain_swaps_order_id"), table_name="cross_chain_swaps")
    op.drop_index(op.f("ix_cross_chain_swaps_other_chain"), table_name="cross_chain_swaps")
    op.drop_index(op.f("ix_cross_chain_swaps_state"), table_name="cross_chain_swaps")
    op.drop_index(op.f("ix_cross_chain_swaps_onchain_id"), table_name="cross_chain_swaps")
    op.drop_table("cross_chain_swaps")

    op.drop_index("ix_swap_orders_market_pair", table_name="swap_orders")
    op.drop_index(op.f("ix_swap_orders_expiry"), table_name="swap_orders")
    op.drop_index(op.f("ix_swap_orders_status"), table_name="swap_orders")
    op.drop_index(op.f("ix_swap_orders_counterparty_user_id"), table_name="swap_orders")
    op.drop_index(op.f("ix_swap_orders_creator_user_id"), table_name="swap_orders")
    op.drop_index(op.f("ix_swap_orders_creator"), table_name="swap_orders")
    op.drop_index(op.f("ix_swap_orders_onchain_id"), table_name="swap_orders")
    op.drop_table("swap_orders")

    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_index(op.f("ix_users_wallet_address"), table_name="users")
    op.drop_table("users")
