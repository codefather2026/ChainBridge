# ChainBridge Smart Contract Documentation

## Overview

The ChainBridge smart contract is deployed on Stellar's Soroban platform and serves as the core protocol for trustless cross-chain atomic swaps. It implements the Hash Time-Locked Contract (HTLC) pattern to ensure atomicity - either both sides of a swap complete, or both parties can recover their funds.

## Contract Address

```
Contract ID: [To be deployed on mainnet]
Networks: Stellar Mainnet, Stellar Testnet
```

## Contract Interface

### Initialization

```rust
/// Initialize the cross-chain bridge protocol
/// # Arguments
/// * `admin` - Address of the admin who can manage chain configuration
fn init(env: Env, admin: Address) -> Result<(), Error>
```

### HTLC Operations

#### Create HTLC

```rust
/// Create a Hash Time-Locked Contract
/// # Arguments
/// * `sender` - Address creating the HTLC (funds sender)
/// * `receiver` - Address that can claim the HTLC
/// * `amount` - Amount of tokens/asset to lock
/// * `hash_lock` - 32-byte SHA256 hash of the secret
/// * `time_lock` - Unix timestamp when HTLC expires
/// # Returns
/// * `htlc_id` - Unique identifier for the created HTLC
fn create_htlc(
    env: Env,
    sender: Address,
    receiver: Address,
    amount: i128,
    hash_lock: Bytes,
    time_lock: u64,
) -> Result<u64, Error>
```

#### Claim HTLC

```rust
/// Claim HTLC by revealing the secret
/// # Arguments
/// * `receiver` - Address claiming the HTLC (must be the receiver)
/// * `htlc_id` - ID of the HTLC to claim
/// * `secret` - The preimage that hashes to the hash_lock
fn claim_htlc(
    env: Env,
    receiver: Address,
    htlc_id: u64,
    secret: Bytes,
) -> Result<(), Error>
```

#### Refund HTLC

```rust
/// Refund HTLC after timelock expires
/// # Arguments
/// * `sender` - Original creator of the HTLC
/// * `htlc_id` - ID of the HTLC to refund
fn refund_htlc(
    env: Env,
    sender: Address,
    htlc_id: u64,
) -> Result<(), Error>
```

#### Get HTLC Details

```rust
/// Get complete HTLC information
fn get_htlc(env: Env, htlc_id: u64) -> Result<HTLC, Error>

/// Get current HTLC status
fn get_htlc_status(env: Env, htlc_id: u64) -> Result<HTLCStatus, Error>

/// Get revealed secret (only available after claim)
fn get_secret(env: Env, htlc_id: u64) -> Result<Option<Bytes>, Error>
```

### Order Management

#### Create Order

```rust
/// Create a swap order in the order book
/// # Arguments
/// * `creator` - Address creating the order
/// * `from_chain` - Source chain for the swap
/// * `to_chain` - Destination chain for the swap
/// * `from_asset` - Asset to send (e.g., "XLM", "BTC")
/// * `to_asset` - Asset to receive
/// * `from_amount` - Amount to send
/// * `to_amount` - Amount desired in return
/// * `expiry` - Unix timestamp when order expires
fn create_order(
    env: Env,
    creator: Address,
    from_chain: Chain,
    to_chain: Chain,
    from_asset: String,
    to_asset: String,
    from_amount: i128,
    to_amount: i128,
    expiry: u64,
) -> Result<u64, Error>
```

#### Match Order

```rust
/// Match and execute a swap order
/// # Arguments
/// * `counterparty` - Address matching the order
/// * `order_id` - ID of the order to match
/// # Returns
/// * `swap_id` - ID of the created cross-chain swap
fn match_order(
    env: Env,
    counterparty: Address,
    order_id: u64,
) -> Result<u64, Error>
```

#### Cancel Order

```rust
/// Cancel an unmatched order
fn cancel_order(
    env: Env,
    creator: Address,
    order_id: u64,
) -> Result<(), Error>
```

#### Get Order

```rust
/// Get order details
fn get_order(env: Env, order_id: u64) -> Result<SwapOrder, Error>
```

### Cross-Chain Swap Operations

#### Verify Proof

```rust
/// Verify a cross-chain proof
/// # Arguments
/// * `proof` - ChainProof containing chain ID, tx hash, block height, and proof data
/// # Returns
/// * `bool` - True if proof is valid
fn verify_proof(
    env: Env,
    proof: ChainProof,
) -> Result<bool, Error>
```

#### Complete Swap

```rust
/// Complete a cross-chain swap using verified proof
/// # Arguments
/// * `swap_id` - ID of the swap to complete
/// * `proof` - Verified proof from the other chain
fn complete_swap(
    env: Env,
    swap_id: u64,
    proof: ChainProof,
) -> Result<(), Error>
```

#### Get Swap Details

```rust
fn get_swap(env: Env, swap_id: u64) -> Result<CrossChainSwap, Error>
```

### Admin Functions

#### Add Supported Chain

```rust
/// Add a new supported blockchain
/// # Arguments
/// * `admin` - Admin address for authorization
/// * `chain_id` - Numeric chain identifier
fn add_chain(
    env: Env,
    admin: Address,
    chain_id: u8,
) -> Result<(), Error>
```

## Data Types

### HTLCStatus

```rust
pub enum HTLCStatus {
    Active,    // HTLC is locked and awaiting claim
    Claimed,   // HTLC has been claimed with secret
    Refunded,  // HTLC has been refunded after expiry
    Expired,   // HTLC expired without action
}
```

### Chain

```rust
pub enum Chain {
    Bitcoin,    // Chain ID: 0
    Ethereum,  // Chain ID: 1
    Solana,    // Chain ID: 2
    Polygon,   // Chain ID: 3
    BSC,       // Chain ID: 4
}
```

### HTLC

```rust
pub struct HTLC {
    pub sender: Address,           // HTLC creator
    pub receiver: Address,         // Intended recipient
    pub amount: i128,             // Amount locked
    pub hash_lock: Bytes,         // SHA256(secret)
    pub time_lock: u64,          // Expiry timestamp
    pub status: HTLCStatus,      // Current status
    pub secret: Option<Bytes>,   // Revealed secret (if claimed)
    pub created_at: u64,         // Creation timestamp
}
```

### SwapOrder

```rust
pub struct SwapOrder {
    pub id: u64,
    pub creator: Address,
    pub from_chain: Chain,
    pub to_chain: Chain,
    pub from_asset: String,
    pub to_asset: String,
    pub from_amount: i128,
    pub to_amount: i128,
    pub expiry: u64,
    pub matched: bool,
    pub counterparty: Option<Address>,
}
```

### CrossChainSwap

```rust
pub struct CrossChainSwap {
    pub id: u64,
    pub stellar_htlc_id: u64,
    pub other_chain: Chain,
    pub other_chain_tx: String,  // Tx hash on other chain
    pub stellar_party: Address,
    pub other_party: String,    // Address on other chain
    pub completed: bool,
}
```

### ChainProof

```rust
pub struct ChainProof {
    pub chain: Chain,
    pub tx_hash: String,
    pub block_height: u64,
    pub proof_data: Bytes,      // Merkle/SPV proof
}
```

## Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 1 | AlreadyInitialized | Contract already initialized |
| 2 | NotInitialized | Contract not initialized |
| 3 | Unauthorized | Caller not authorized |
| 4 | InvalidAmount | Amount must be positive |
| 5 | HTLCNotFound | HTLC does not exist |
| 6 | HTLCExpired | HTLC timelock has passed |
| 7 | HTLCNotExpired | HTLC timelock not yet passed |
| 8 | InvalidSecret | Secret does not match hash |
| 9 | AlreadyClaimed | HTLC already claimed |
| 10 | AlreadyRefunded | HTLC already refunded |
| 11 | InvalidHashLength | Hash must be 32 bytes |
| 12 | InvalidTimelock | Timelock invalid |
| 13 | OrderNotFound | Order does not exist |
| 14 | OrderAlreadyMatched | Order already matched |
| 15 | OrderExpired | Order has expired |
| 16 | InvalidChain | Chain not supported |
| 17 | ProofVerificationFailed | Proof verification failed |

## HTLC Protocol Flow

### Step 1: HTLC Creation

1. Initiator generates a random secret `S` (32 bytes)
2. Computes hash `H = SHA256(S)`
3. Calls `create_htlc()` with:
   - Receiver's address
   - Amount to lock
   - Hash `H`
   - Timeout timestamp (e.g., 24 hours from now)
4. Contract stores HTLC and returns HTLC ID

### Step 2: HTLC Claiming

1. Receiver observes HTLC creation on Stellar
2. Receiver creates corresponding HTLC on destination chain
3. Initiator (or relayer) reveals secret `S` by claiming destination HTLC
4. Receiver detects secret revelation
5. Receiver calls `claim_htlc()` with secret `S`
6. Contract verifies `SHA256(S) == H`
7. If valid, funds are transferred to receiver

### Step 3: HTLC Refund (if expiry)

1. If HTLC is not claimed before timeout
2. Initiator calls `refund_htlc()`
3. Contract verifies timelock has passed
4. Funds are returned to initiator

## Storage Structure

### Persistent Storage Keys

```rust
enum DataKey {
    Admin,                    // Contract admin address
    HTLCCounter,             // HTLC ID counter
    HTLC(u64),              // Individual HTLC data
    OrderCounter,           // Order ID counter
    Order(u64),             // Individual order data
    SwapCounter,            // Swap ID counter
    Swap(u64),             // Individual swap data
    SupportedChain(u8),    // Supported chain flag
}
```

### Storage Usage

- **Instance Storage**: Admin, counters (frequent access)
- **Persistent Storage**: HTLCs, Orders, Swaps (larger data)

## Security Considerations

### Hash Lock Security

- Uses SHA256 for hash locking (battle-tested)
- 32-byte secrets provide 256-bit security
- Preimage resistance ensures secret cannot be derived from hash

### Timelock Security

- Minimum timelock: Recommended 24 hours for Stellar side
- Cascading timeouts: Destination chain timeout < source chain timeout
- Prevents race conditions where counterparty waits until last moment

### Authorization

- All state-changing operations require authentication
- `require_auth()` ensures only designated parties can act
- Admin functions protected by admin address verification

## Gas/Resource Considerations

### Soroban Resource Model

- **Storage Write**: Permanent storage with initial rent
- **Compute**: Instruction count limits
- **Ledger Entry**: Persistent data storage

### Optimization

- Use appropriate storage types (instance vs persistent)
- Minimize contract code size
- Batch operations when possible

## Testing

### Unit Tests

Run tests with:
```bash
cd smartcontract
cargo test
```

### Test Coverage

- HTLC creation with valid/invalid parameters
- Claim with correct/incorrect secret
- Refund before/after expiry
- Order creation and matching
- Error handling and edge cases

## Deployment

### Testnet Deployment

```bash
# Build contract
cargo build --release --target wasm32-unknown-unknown

# Deploy to testnet
soroban contract deploy \
  --wasm target/wasm32-unknown-unknown/release/chainbridge.wasm \
  --network testnet
```

### Mainnet Deployment

```bash
# Deploy to mainnet
soroban contract deploy \
  --wasm target/wasm32-unknown-unknown/release/chainbridge.wasm \
  --network mainnet
```

## Upgradeability

The current contract is not upgradeable. Future versions may implement:
- Proxy pattern for upgradeability
- Migration functions for data transfer
- Governance for parameter updates

## Events

### Emitted Events

The contract emits events for off-chain monitoring:

- `HTLCCreated`: When new HTLC is created
- `HTLCClaimed`: When HTLC is successfully claimed
- `HTLCRefunded`: When HTLC is refunded
- `OrderCreated`: When new order is placed
- `OrderMatched`: When order is matched
- `SwapCompleted`: When cross-chain swap completes

## Integration with Relayer

1. Relayer monitors events from contract
2. When HTLC is created, relayer watches destination chain
3. When claim happens, relayer generates proof
4. Relayer submits proof to complete Stellar side
5. Backend tracks swap status via events

## Examples

### Creating an HTLC (JavaScript/Freighter)

```javascript
import { Contract, Keypair, Networks } from 'stellar-sdk';

const secret = Keypair.random().random(); // 32 bytes
const hashLock = sha256(secret);

const tx = await contract.invoke({
  method: 'create_htlc',
  args: [
    receiverAddress,
    '1000000000', // 10 XLM in stroops
    hashLock,
    Math.floor(Date.now() / 1000) + 86400 // 24 hours
  ]
});
```

### Claiming an HTLC

```javascript
const tx = await contract.invoke({
  method: 'claim_htlc',
  args: [
    htlcId,
    secret // The preimage
  ]
});
```

## References

- [Architecture Overview](./ARCHITECTURE.md)
- [HTLC Protocol](./HTLC.md)
- [Relayer Documentation](./RELAYER.md)
- [API Documentation](./API.md)
- [Soroban SDK Documentation](https://soroban.stellar.org/docs)
