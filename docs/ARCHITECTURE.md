# ChainBridge Architecture

## Overview

ChainBridge is a trustless cross-chain atomic swap protocol built on Stellar's Soroban smart contract platform. It enables peer-to-peer swapping of assets between Stellar and other blockchains without requiring wrapped tokens, custodians, or trusted third parties.

The architecture is designed around the Hash Time-Locked Contract (HTLC) pattern, which guarantees atomicity - either both sides of the swap complete successfully, or both parties can refund their funds.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION LAYER                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  Web Frontend   │  │  Mobile Apps    │  │  Third-Party Integrations│ │
│  │  (Next.js)      │  │  (Future)       │  │  (API Access)           │ │
│  └────────┬────────┘  └─────────────────┘  └───────────┬─────────────┘ │
└───────────┼─────────────────────────────────────────────┼───────────────┘
            │                                             │
            │ REST API                                     │ WebSocket
            ▼                                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND SERVICES LAYER                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI Application                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │  │
│  │  │ Order    │ │ Swap     │ │ Proof    │ │ Analytics &       │  │  │
│  │  │ Matching │ │ Manager  │ │ Verifier │ │ Monitoring        │  │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────────┬─────────┘  │  │
│  └───────┼────────────┼────────────┼─────────────────┼─────────────┘  │
│          │            │            │                 │                 │
│  ┌───────▼────────────▼────────────▼─────────────────▼─────────────┐  │
│  │              PostgreSQL + Redis Cache                           │  │
│  │  • Swap orders    • Swap states   • Proof data   • Metrics     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
            │
            │ Soroban RPC
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        STELLAR SOROBAN LAYER                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  ChainBridge Smart Contract                      │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │  │
│  │  │  HTLC Module    │  │  Order Module   │  │  Swap Module     │ │  │
│  │  │  ────────────   │  │  ────────────   │  │  ────────────    │ │  │
│  │  │ • create_htlc   │  │ • create_order  │  │ • verify_proof   │ │  │
│  │  │ • claim_htlc    │  │ • match_order   │  │ • complete_swap  │ │  │
│  │  │ • refund_htlc   │  │ • cancel_order  │  │ • get_swap       │ │  │
│  │  │ • get_htlc      │  │ • get_order     │  │                  │ │  │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────┘ │  │
│  │  ┌──────────────────────────────────────────────────────────┐   │  │
│  │  │              Storage Layer (Persistent)                   │   │  │
│  │  │  • HTLC records  • Order book  • Swap states  • Config   │   │  │
│  │  └──────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
            │
            │ Events & Proofs
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RELAYER NETWORK LAYER                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Relayer Infrastructure                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │  │
│  │  │ Chain Monitor│  │ Proof Gen    │  │ Event Indexer        │  │  │
│  │  │ ──────────── │  │ ──────────── │  │ ─────────────────    │  │  │
│  │  │ • Bitcoin    │  │ • SPV proofs │  │ • HTLC events        │  │  │
│  │  │ • Ethereum   │  │ • Merkle     │  │ • Claim events       │  │  │
│  │  │ • Solana     │  │ • Signatures │  │ • Refund events      │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────────┐   │  │
│  │  │          Light Client Implementations                     │   │  │
│  │  │  • Bitcoin SPV    • Ethereum Light Client   • Solana RPC │   │  │
│  │  └──────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
            │
            │ Network Connections
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL BLOCKCHAINS                              │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │   Bitcoin   │  │    Ethereum     │  │       Solana             │  │
│  │   Network   │  │    Network      │  │       Network            │  │
│  │  ─────────  │  │  ─────────────  │  │  ───────────────────    │  │
│  │ • HTLC txs  │  │ • HTLC contract │  │ • HTLC program          │  │
│  │ • Scripts   │  │ • Events        │  │ • Instructions          │  │
│  └─────────────┘  └─────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Smart Contract Layer (Soroban)

The smart contract is the heart of ChainBridge, deployed on Stellar's Soroban platform. It manages all swap logic, HTLC creation, and state management.

#### Modules

**HTLC Module** (`smartcontract/src/htlc.rs`)
- Creates and manages Hash Time-Locked Contracts
- Validates secrets against hash locks
- Enforces timelock constraints
- Handles claim and refund operations

**Order Module** (`smartcontract/src/order.rs`)
- Manages the decentralized order book
- Creates and matches swap orders
- Tracks order lifecycle
- Enforces order validity periods

**Swap Module** (`smartcontract/src/swap.rs`)
- Coordinates cross-chain swap execution
- Verifies cross-chain proofs
- Manages swap completion workflow
- Emits events for relayer tracking

**Storage Module** (`smartcontract/src/storage.rs`)
- Persistent storage for HTLCs, orders, and swaps
- Instance storage for counters and admin
- Efficient key-value data structures

#### Data Structures

```rust
// HTLC Structure
pub struct HTLC {
    sender: Address,          // Creator of the HTLC
    receiver: Address,        // Intended recipient
    amount: i128,             // Amount locked
    hash_lock: Bytes,         // SHA256 hash of the secret
    time_lock: u64,          // Unix timestamp for expiry
    status: HTLCStatus,      // Active, Claimed, Refunded, Expired
    secret: Option<Bytes>,   // Revealed secret (if claimed)
    created_at: u64,         // Creation timestamp
}

// Swap Order Structure
pub struct SwapOrder {
    id: u64,
    creator: Address,
    from_chain: Chain,
    to_chain: Chain,
    from_asset: String,
    to_asset: String,
    from_amount: i128,
    to_amount: i128,
    expiry: u64,
    matched: bool,
    counterparty: Option<Address>,
}

// Cross-Chain Swap Structure
pub struct CrossChainSwap {
    id: u64,
    stellar_htlc_id: u64,
    other_chain: Chain,
    other_chain_tx: String,   // Transaction hash on other chain
    stellar_party: Address,
    other_party: String,
    completed: bool,
}
```

### 2. Backend Services Layer

The backend provides REST API access, order matching, and integration services.

#### Components

**FastAPI Application** (`backend/app/main.py`)
- RESTful API endpoints for swap operations
- WebSocket support for real-time updates
- CORS middleware for frontend integration
- Health checks and monitoring endpoints

**Planned Services:**
- Order Matching Engine: Matches compatible swap orders
- Proof Verification Service: Validates cross-chain proofs
- Analytics Service: Tracks swap metrics and success rates
- Notification Service: Alerts users of swap events

#### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI | High-performance async API |
| Database | PostgreSQL | Persistent data storage |
| Cache | Redis | Fast state caching, pub/sub |
| ORM | SQLAlchemy | Database models and queries |
| Task Queue | Celery | Async job processing |

### 3. Relayer Network Layer

The relayer network monitors external blockchains and facilitates cross-chain communication.

#### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Relayer Process                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Chain Monitor Service                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │ Bitcoin RPC  │  │ Ethereum RPC │  │ Solana RPC  │ │ │
│  │  │ Connection   │  │ Connection   │  │ Connection  │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │ │
│  └─────────┼─────────────────┼─────────────────┼─────────┘ │
│            │                 │                 │           │
│  ┌─────────▼─────────────────▼─────────────────▼─────────┐ │
│  │              Event Processing Pipeline                 │ │
│  │  • HTLC Created Events                                 │ │
│  │  • HTLC Claimed Events                                 │ │
│  │  • HTLC Refunded Events                                │ │
│  │  • Secret Revealed Events                              │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │              Proof Generation Service                   │ │
│  │  • SPV Proof Generation (Bitcoin)                      │ │
│  │  • Merkle Proof Generation (Ethereum)                  │ │
│  │  • Transaction Receipt Proofs                          │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │           Stellar Submission Service                   │ │
│  │  • Invoke Soroban contract methods                     │ │
│  │  • Submit proofs to ChainBridge contract               │ │
│  │  • Update swap statuses                                │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### Responsibilities

1. **Chain Monitoring**
   - Watch for HTLC creation events on external chains
   - Detect HTLC claims and secret revelations
   - Monitor timelock expirations

2. **Proof Generation**
   - Generate SPV proofs for Bitcoin transactions
   - Create Merkle proofs for Ethereum events
   - Compile transaction inclusion proofs

3. **Cross-Chain Communication**
   - Submit proofs to Stellar smart contract
   - Trigger swap completion flows
   - Emit events for backend tracking

### 4. Frontend Layer

The frontend provides the user interface for creating and executing swaps.

#### Components

```
┌──────────────────────────────────────────────────────────────┐
│                   Next.js Application                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Pages                               │ │
│  │  • Home (Swap Dashboard)                               │ │
│  │  • Create Swap                                         │ │
│  │  • Browse Orders                                       │ │
│  │  • Active Swaps                                        │ │
│  │  • History                                             │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Components                            │ │
│  │  • Wallet Connection (Freighter, MetaMask, etc.)       │ │
│  │  • Swap Form                                           │ │
│  │  • Order Book                                          │ │
│  │  • Swap Tracker                                        │ │
│  │  • Transaction History                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Services                             │ │
│  │  • Stellar SDK Integration                             │ │
│  │  • Ethereum/Web3 Integration                           │ │
│  │  • Bitcoin Integration                                 │ │
│  │  • Backend API Client                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. Swap Creation Flow

```
User                Frontend             Backend            Smart Contract
 │                     │                    │                     │
 │──Create Order───────>│                    │                     │
 │                     │──POST /orders──────>│                     │
 │                     │                    │──create_order()────>│
 │                     │                    │<─────Order ID───────│
 │                     │<────Order ID───────│                     │
 │<──Order Created─────│                    │                     │
 │                     │                    │                     │
```

### 2. Swap Execution Flow

```
Alice               Bob                Stellar HTLC          Bitcoin HTLC
 │                   │                     │                      │
 │──Lock XLM─────────────────────────────>│                      │
 │                   │                     │                      │
 │<──HTLC Created────│─────────────────────│                      │
 │                   │                     │                      │
 │                   │──Lock BTC──────────────────────────────────>│
 │                   │                     │                      │
 │                   │<──HTLC Created──────│──────────────────────│
 │                   │                     │                      │
 │──Claim BTC (reveal secret)──────────────────────────────────────>│
 │                   │                     │                      │
 │                   │<──Secret Revealed───│──────────────────────│
 │                   │                     │                      │
 │                   │──Claim XLM (use secret)──>│                │
 │                   │                     │<─────Claim───────────│
 │                   │                     │                      │
```

### 3. Relayer Proof Submission Flow

```
Bitcoin Network     Relayer          Stellar Contract      Backend
      │               │                    │                 │
      │──HTLC Event──>│                    │                 │
      │               │──Generate Proof─── │                 │
      │               │                    │                 │
      │               │──verify_proof()────>│                 │
      │               │                    │──Event Emitted──>│
      │               │                    │                 │
      │               │                    │<──Update Swap───│
      │               │                    │                 │
```

---

## Sequence Diagrams

### Complete Atomic Swap Sequence

```
┌──────┐          ┌──────┐          ┌──────────┐          ┌───────┐          ┌──────────┐
│Alice │          │ Bob  │          │ Stellar  │          │Relayer│          │ Bitcoin  │
│      │          │      │          │ Contract │          │       │          │ Network  │
└──┬───┘          └──┬───┘          └────┬─────┘          └───┬───┘          └────┬─────┘
   │                 │                   │                   │                  │
   │ 1. Generate    │                   │                   │                  │
   │    Secret S    │                   │                   │                  │
   │    Hash H      │                   │                   │                  │
   │                 │                   │                   │                  │
   │ 2. Create Order│                   │                   │                  │
   │────────────────>│                   │                   │                  │
   │                 │                   │                   │                  │
   │                 │ 3. Match Order    │                   │                  │
   │<────────────────│                   │                   │                  │
   │                 │                   │                   │                  │
   │ 4. Create HTLC │                   │                   │                  │
   │    (H, 24h)     │                   │                   │                  │
   │─────────────────────────────────────>│                   │                  │
   │                 │                   │                   │                  │
   │                 │ 5. Verify Lock    │                   │                  │
   │                 │───────────────────────────────────────>│                  │
   │                 │                   │                   │                  │
   │                 │ 6. Create HTLC   │                   │                  │
   │                 │    (H, 12h)       │                   │                  │
   │                 │──────────────────────────────────────────────────────────>│
   │                 │                   │                   │                  │
   │ 7. Verify Lock │                   │                   │                  │
   │─────────────────────────────────────────────────────────>│                  │
   │                 │                   │                   │                  │
   │ 8. Claim BTC   │                   │                   │                  │
   │    (reveal S)   │                   │                   │                  │
   │──────────────────────────────────────────────────────────────────────────────>│
   │                 │                   │                   │                  │
   │                 │ 9. Detect Secret │                   │                  │
   │                 │<──────────────────────────────────────────────────────────│
   │                 │                   │                   │                  │
   │                 │ 10. Claim XLM    │                   │                  │
   │                 │    (use S)        │                   │                  │
   │                 │─────────────────────────────────────>│                  │
   │                 │                   │                   │                  │
   │                 │                   │ 11. Swap Complete│                  │
   │                 │                   │<──────────────────│                  │
   │                 │                   │                   │                  │
```

---

## Security Model

### 1. Atomicity Guarantees

The HTLC protocol ensures atomic swaps through:

- **Hash Lock**: Funds can only be claimed by revealing the preimage
- **Time Lock**: Funds can be refunded after timeout
- **Cascading Timeouts**: Earlier timeouts on the receiving chain prevent race conditions

### 2. Trust Assumptions

| Component | Trust Level | Rationale |
|-----------|-------------|-----------|
| Stellar Network | Minimal | Decentralized, battle-tested |
| Soroban Contract | Audited | Open-source, verifiable |
| Counterparty | None | HTLC ensures fair exchange |
| Relayers | Minimal | Only submit proofs, no custody |
| Backend | Minimal | No access to funds |

### 3. Attack Vectors & Mitigations

#### Front-Running
- **Risk**: Attacker observes secret revelation and front-runs claim
- **Mitigation**: Secret revealed on destination chain first, giving initiator claim priority

#### Timelock Exploitation
- **Risk**: Counterparty waits until last moment to claim
- **Mitigation**: Cascading timelocks ensure ample time for both parties

#### Relayer Censorship
- **Risk**: Relayers refuse to submit proofs
- **Mitigation**: Anyone can submit proofs (decentralized)

#### Smart Contract Bugs
- **Risk**: Vulnerabilities in contract code
- **Mitigation**: Formal verification, audits, bug bounties

---

## Scalability Considerations

### Current Limitations

1. **Throughput**: Limited by Stellar's transaction capacity
2. **Finality**: Dependent on external chain confirmation times
3. **Storage**: On-chain storage costs for HTLC data

### Future Improvements

1. **Batch Processing**: Group multiple swaps in single transactions
2. **Layer 2**: Integrate with Stellar's future L2 solutions
3. **Optimistic Proofs**: Use optimistic verification for faster swaps
4. **State Channels**: Off-chain swap negotiation

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │  Backend     │  │  PostgreSQL  │  │     Redis      │   │
│  │  Container   │  │  Container   │  │    Container   │   │
│  └──────────────┘  └──────────────┘  └────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │            Local Stellar Testnet (Future)            │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│  ┌────────────────────────────────────────────────────────┐│
│  │                 Ingress Controller                     ││
│  └────────────────────┬───────────────────────────────────┘│
│                       │                                     │
│  ┌────────────────────▼───────────────────────────────────┐│
│  │              API Deployment (3 replicas)               ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │           Relayer Deployment (2 replicas)              ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │         Managed PostgreSQL (Cloud Provider)            ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │          Managed Redis (Cloud Provider)                ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Monitoring & Observability

### Metrics Collected

1. **Swap Metrics**
   - Total swaps created
   - Success rate
   - Average completion time
   - Volume by asset pair

2. **Relayer Metrics**
   - Events processed
   - Proof generation time
   - Transaction submission success rate

3. **System Metrics**
   - API response times
   - Database query performance
   - Cache hit rates

### Logging Strategy

- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARN, ERROR
- **Sensitive Data**: Never log private keys or secrets
- **Retention**: 30 days for operational logs

### Alerting

- Swap failures exceeding threshold
- Relayer downtime
- Smart contract errors
- High latency alerts

---

## Future Architecture Enhancements

### Phase 2: Enhanced Relayer Network

- Incentivized relayer network with stake-based rewards
- Reputation system for relayer reliability
- Distributed key generation for multi-sig operations

### Phase 3: Advanced Features

- AMM integration for instant swaps
- Governance DAO for protocol upgrades
- Cross-chain message passing for DeFi composability

---

## References

- [Stellar Soroban Documentation](https://soroban.stellar.org)
- [HTLC Protocol Specification](./HTLC.md)
- [Smart Contract Documentation](./SMARTCONTRACT.md)
- [Relayer Architecture](./RELAYER.md)
- [API Reference](./API.md)
