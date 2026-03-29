# Database Schema (PostgreSQL)

This document describes the ChainBridge relational schema introduced in Alembic revision `20260328_0001`.

## Goals

- Track full HTLC, order, and swap lifecycles.
- Support per-user and per-entity transaction history.
- Optimize common read paths for dashboard, orderbook, and monitoring queries.
- Keep schema compatible with existing API routes while adding stronger relationships.

## Tables

### `users`

Stores participant identities and preference metadata.

Key columns:
- `id` (UUID, PK)
- `wallet_address` (unique)
- `display_name`
- `preferred_chain`
- `is_active`

Indexes:
- `ix_users_wallet_address` (unique)
- `ix_users_is_active`

### `swap_orders`

Tracks order creation, partial fills, and terminal status.

Key columns:
- `id` (UUID, PK)
- `onchain_id` (unique, optional)
- `creator`, `counterparty`
- `creator_user_id` -> `users.id` (nullable)
- `counterparty_user_id` -> `users.id` (nullable)
- `from_chain`, `to_chain`, `from_asset`, `to_asset`
- `from_amount`, `to_amount`, `min_fill_amount`, `filled_amount`
- `expiry`, `status`

Constraints:
- `status` check: `open | matched | filled | cancelled | expired`

Indexes:
- `creator`, `creator_user_id`, `counterparty_user_id`
- `status`, `expiry`
- Composite market index on `(from_chain, to_chain, from_asset, to_asset)`

### `cross_chain_swaps`

Tracks cross-chain swap state transitions and links to source orders/users.

Key columns:
- `id` (UUID, PK)
- `onchain_id` (unique, optional)
- `order_id` -> `swap_orders.id` (nullable)
- `stellar_htlc_id`
- `other_chain`, `other_chain_tx`
- `stellar_party`, `other_party`
- `initiator_user_id` -> `users.id` (nullable)
- `responder_user_id` -> `users.id` (nullable)
- `state`

Constraints:
- `state` check: `initiated | locked | executed | completed | failed | refunded | expired`

Indexes:
- `onchain_id` (unique)
- `state`, `other_chain`, `order_id`
- `initiator_user_id`, `responder_user_id`

### `htlcs`

Tracks HTLC lock/claim/refund lifecycle.

Key columns:
- `id` (UUID, PK)
- `onchain_id` (unique, optional)
- `swap_id` -> `cross_chain_swaps.id` (nullable)
- `sender`, `receiver`
- `sender_user_id` -> `users.id` (nullable)
- `receiver_user_id` -> `users.id` (nullable)
- `amount`, `hash_lock`, `time_lock`
- `status`, `secret`, `hash_algorithm`

Constraints:
- `status` check: `active | claimed | refunded | expired | cancelled`

Indexes:
- `onchain_id` (unique)
- `sender`, `receiver`
- `hash_lock`, `time_lock`, `status`
- `swap_id`, `sender_user_id`, `receiver_user_id`

### `transactions`

Canonical transaction ledger across all supported chains.

Key columns:
- `id` (UUID, PK)
- `user_id` -> `users.id` (nullable)
- `swap_id` -> `cross_chain_swaps.id` (nullable)
- `order_id` -> `swap_orders.id` (nullable)
- `htlc_id` -> `htlcs.id` (nullable)
- `chain`, `tx_hash`, `tx_type`, `status`
- `amount`, `asset`, `block_number`, `confirmed_at`
- `metadata` (JSON)

Constraints:
- Unique `(chain, tx_hash)`

Indexes:
- `user_id`, `swap_id`, `order_id`, `htlc_id`
- `chain`, `tx_hash`, `tx_type`, `status`
- Composite `(chain, status)`

### Existing compatibility tables included in migration

- `api_keys`
- `swap_disputes`

These are created in the same initial revision to keep runtime compatibility with auth and dispute routes.

## Relationship Summary

- `users` 1:N `swap_orders` (`creator_user_id`, `counterparty_user_id`)
- `users` 1:N `cross_chain_swaps` (`initiator_user_id`, `responder_user_id`)
- `users` 1:N `htlcs` (`sender_user_id`, `receiver_user_id`)
- `swap_orders` 1:N `cross_chain_swaps`
- `cross_chain_swaps` 1:N `htlcs`
- `users`, `swap_orders`, `cross_chain_swaps`, `htlcs` 1:N `transactions`
- `cross_chain_swaps` 1:N `swap_disputes`

## Alembic Usage

From `backend/`:

```bash
alembic upgrade head
alembic downgrade -1
```

Create additional migration revisions:

```bash
alembic revision --autogenerate -m "describe change"
```
