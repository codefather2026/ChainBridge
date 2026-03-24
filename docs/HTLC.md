# HTLC Protocol Specification

## Overview

Hash Time-Locked Contracts (HTLCs) are the foundation of ChainBridge's atomic swap mechanism. This document details the protocol for cross-chain atomic swaps, including the cryptographic primitives, verification mechanisms, and sequence flows.

## HTLC Fundamentals

### What is an HTLC?

An HTLC is a smart contract that:
1. **Locks funds** with a cryptographic hash condition
2. **Enforces a timelock** after which funds can be refunded
3. **Enables atomic execution** through secret revelation

### Key Properties

| Property | Description |
|----------|-------------|
| **Atomicity** | Either both sides complete or both refund |
| **Trustless** | No trusted third party required |
| **Timelocked** | Funds recoverable after timeout |
| **Hash-locked** | Secret required to claim |

## Cryptographic Primitives

### Hash Function

ChainBridge uses **SHA-256** for hash locking:

```
H = SHA256(S)
```

Where:
- `S` = Secret preimage (32 random bytes)
- `H` = Hash lock (32 bytes)

### Why SHA-256?

- Battle-tested cryptographic hash function
- 256-bit security level
- Native support in all supported blockchains
- Efficient computation on embedded devices

### Secret Generation

```python
import os
import hashlib

def generate_secret() -> bytes:
    """Generate cryptographically secure 32-byte secret"""
    secret = os.urandom(32)
    return secret

def compute_hash(secret: bytes) -> bytes:
    """Compute SHA256 hash of secret"""
    return hashlib.sha256(secret).digest()
```

## Cross-Chain Swap Protocol

### Protocol Participants

| Role | Description |
|------|-------------|
| **Initiator** | Creates the swap, locks funds on source chain |
| **Responder** | Locks funds on destination chain |
| **Relayer** (optional) | Monitors chains, submits proofs, earns fees |

### Protocol Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CROSS-CHAIN ATOMIC SWAP PROTOCOL                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Alice (Initiator)              Bob (Responder)                            │
│  ─────────────────              ─────────────────                           │
│       │                              │                                       │
│       │  1. Generate Secret S        │                                       │
│       │     Compute H = SHA256(S)   │                                       │
│       │                              │                                       │
│       ├─────────────────────────────>│                                       │
│       │      2. Propose Swap         │                                       │
│       │      (H, amount, timeout)    │                                       │
│       │                              │                                       │
│       │  3. Verify Proposal          │                                       │
│       │     Check conditions         │                                       │
│       │                              │                                       │
│       │  4. Create HTLC on           │                                       │
│       │     Destination Chain        │                                       │
│       │     (H, timeout_dest)        │                                       │
│       │<─────────────────────────────┤                                       │
│       │                              │                                       │
│       │  5. Verify Destination       │                                       │
│       │     HTLC Locked              │                                       │
│       │                              │                                       │
│       │  6. Create HTLC on           │                                       │
│       │     Source Chain             │                                       │
│       │     (H, timeout_src)         │                                       │
│       ├─────────────────────────────>│                                       │
│       │                              │                                       │
│       │  7. Verify Source            │                                       │
│       │     HTLC Locked              │                                       │
│       │                              │                                       │
│       │  8. Claim Destination        │                                       │
│       │     HTLC with Secret S       │                                       │
│       │<─────────────────────────────┤                                       │
│       │                              │                                       │
│       │  9. Secret Revealed!         │                                       │
│       │     (via blockchain event)   │                                       │
│       │                              │                                       │
│       │  10. Claim Source            │                                       │
│       │      HTLC with Secret S      │                                       │
│       ├─────────────────────────────>│                                       │
│       │                              │                                       │
│       │  11. Swap Complete!          │                                       │
│       │      Both parties have       │                                       │
│       │      received their funds   │                                       │
│       │                              │                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Steps

#### Phase 1: Negotiation

1. **Initiator** generates random secret `S` (32 bytes)
2. **Initiator** computes hash `H = SHA256(S)`
3. **Initiator** sends proposal to **Responder** containing:
   - Hash `H`
   - Amount and asset details
   - Source and destination chains
   - Proposed timeouts

#### Phase 2: Lock Funds

4. **Responder** creates HTLC on destination chain with:
   - Hash lock: `H`
   - Timelock: `T_dest` (e.g., 12 hours)
   - Recipient: Initiator's address on destination chain

5. **Initiator** verifies HTLC was created on destination chain

6. **Initiator** creates HTLC on source chain with:
   - Hash lock: `H`
   - Timelock: `T_src` (e.g., 24 hours, must be > T_dest)
   - Recipient: Responder's address on source chain

7. **Responder** verifies HTLC was created on source chain

#### Phase 3: Claim

8. **Initiator** (or helper) claims destination HTLC by revealing `S`

9. **Responder** detects secret revelation via blockchain event

10. **Responder** claims source HTLC using revealed secret `S`

#### Phase 4: Completion

11. Both HTLCs are now claimed - swap complete!

#### Phase 5: Refund (if needed)

If swap is not completed before timeout:

- After `T_dest`: Responder can refund destination HTLC
- After `T_src`: Initiator can refund source HTLC

## Timelock Requirements

### Why Cascading Timeouts?

```
Source Chain Timeout (T_src) > Destination Chain Timeout (T_dest)
```

This ensures:
- Initiator has time to claim after Responder claims
- No race condition where one party waits until last moment
- Fair gameplay for both participants

### Recommended Timeouts

| Scenario | Source Chain | Destination Chain |
|----------|--------------|-------------------|
| Stellar → Bitcoin | 24 hours | 12 hours |
| Stellar → Ethereum | 24 hours | 12 hours |
| Stellar → Solana | 24 hours | 12 hours |

### Minimum Timeout

- Minimum recommended: 6 hours
- Allows time for:
  - Block confirmations
  - Relayer processing
  - Manual intervention if needed

## Cross-Chain Verification

### Verification Types

#### 1. HTLC Existence Verification

Prove that an HTLC was created on another chain with specific parameters.

```
Proof Components:
- Transaction hash (TxID)
- Block height
- Merkle proof of transaction inclusion
- Decoded HTLC parameters
```

#### 2. HTLC Claim Verification

Prove that an HTLC was claimed with a specific secret.

```
Proof Components:
- Transaction hash of claim
- Block height
- Merkle proof
- Revealed secret (optional, can be derived)
```

#### 3. Block Finality

Different chains have different finality guarantees:

| Chain | Finality | Confirmations |
|-------|----------|---------------|
| Bitcoin | ~60 minutes | 6 blocks |
| Ethereum | ~12 minutes | 12-15 blocks |
| Solana | ~0.4 seconds | 1 block (local) |
| Stellar | ~5 seconds | 1 ledger |

### Proof Formats

#### Bitcoin SPV Proof

```
struct BitcoinSPVProof {
    tx_hash: [u8; 32],
    block_header: BlockHeader,
    merkle_proof: Vec<MerkleNode>,
    tx_index: u32,
}
```

#### Ethereum Merkle Proof

```
struct EthereumProof {
    tx_receipt: Receipt,
    block_header: Header,
    merkle_proof: Vec<bytes>,
    log_index: u32,
}
```

#### Solana Transaction Proof

```
struct SolanaProof {
    tx_signature: [u8; 64],
    block_hash: Hash,
    merkle_proof: Vec<bytes>,
    confirmations: u64,
}
```

### Verification Process

```rust
fn verify_chain_proof(env: &Env, proof: &ChainProof) -> Result<bool, Error> {
    match proof.chain {
        Chain::Bitcoin => verify_bitcoin_proof(proof),
        Chain::Ethereum => verify_ethereum_proof(proof),
        Chain::Solana => verify_solana_proof(proof),
        _ => Err(Error::InvalidChain),
    }
}
```

## Sequence Diagrams

### Happy Path (Successful Swap)

```
┌─────────┐      ┌─────────┐      ┌──────────┐      ┌─────────┐      ┌──────────┐
│ Alice   │      │  Relayer│      │ Stellar  │      │ Relayer │      │  Bitcoin │
│(Init)   │      │         │      │ Contract │      │ (BTC)   │      │ Network  │
└────┬────┘      └────┬────┘      └────┬─────┘      └────┬────┘      └────┬─────┘
     │                │                │                 │                │
     │ Generate S     │                │                 │                │
     │ H = SHA256(S)  │                │                 │                │
     │                │                │                 │                │
     │───────────────>│                │                 │                │
     │ Propose Swap   │                │                 │                │
     │                │                │                 │                │
     │                │───────────────>│                 │                │
     │                │ Create Order   │                 │                │
     │                │                │                 │                │
     │<───────────────│                │                 │                │
     │ Order ID       │                │                 │                │
     │                │                │                 │                │
     │                │                │<──────┐         │                │
     │                │                │       │         │                │
     │                │                │ Create HTLC    │                │
     │                │                │ (Alice→Bob)    │                │
     │                │                │       │         │                │
     │                │                │───────┘         │                │
     │                │                │ HTLC Created    │                │
     │                │                │                 │                │
     │                │                │ Event: HTLC    │                │
     │                │                │───────>─────────>│                │
     │                │                │                 │ Monitor BTC    │
     │                │                │                 │                │
     │                │                │                 │<───────────────┤
     │                │                │                 │ Create BTC    │
     │                │                │                 │ HTLC          │
     │                │                │                 │───────────────>│
     │                │                │                 │                │
     │                │                │                 │<───────────────┤
     │                │                │                 │ BTC HTLC Lock │
     │                │                │                 │                │
     │                │<────────────────│<─────── Event ──│                │
     │ Verify BTC HTLC│                │                 │                │
     │ Locked         │                │                 │                │
     │                │                │                 │                │
     │                │                │<────── Invoke ──│                │
     │                │                │ create_htlc()    │                │
     │                │                │───────>─────────>│                │
     │                │                │                 │                │
     │                │                │                 │───────────────>│
     │                │                │                 │ Claim BTC HTLC│
     │                │                │                 │ with Secret S │
     │                │                │                 │<───────────────│
     │                │                │                 │                │
     │                │<────────────────│<─────── Event ──│                │
     │                │ HTLC Claimed,   │                 │                │
     │                │ Secret Revealed │                 │                │
     │                │                 │                 │                │
     │<───────────────│<─────── Event ──│                 │                │
     │ Secret S       │                 │                 │                │
     │ Revealed!      │                 │                 │                │
     │                │                 │                 │                │
     │                │                │<────── Invoke ──│                │
     │                │                │ claim_htlc()    │                │
     │                │                │ with Secret S   │                │
     │                │                │                 │                │
     │                │                │───────>─────────>│                │
     │                │                │ Success!        │                │
     │                │                │                 │                │
     │ Swap Complete! │                 │                 │                │
     └────────────────┴─────────────────┴─────────────────┴────────────────┘
```

### Refund Path

```
┌─────────┐      ┌──────────┐      ┌─────────┐
│ Alice   │      │ Stellar  │      │ Bitcoin │
│         │      │ Contract │      │ Network │
└────┬────┘      └────┬─────┘      └───┬─────┘
     │                │                │
     │ Create HTLC    │                │
     │ (24h timeout)  │                │
     │───────────────>│                │
     │                │                │
     │<───────────────│                │
     │ HTLC Created   │                │
     │                │                │
     │ ... (no claim) │                │
     │                │                │
     │ 24h passes...  │                │
     │                │                │
     │                │<────── Invoke ──│
     │                │ refund_htlc()   │
     │                │                 │
     │                │───────>─────────│
     │                │ Refunded!       │
     │                │                 │
     │<───────────────│                 │
     │ Refund Success │                 │
     │                │                 │
     └────────────────┴─────────────────┘
```

## Security Analysis

### Atomicity Guarantees

The protocol guarantees atomicity through:

1. **Cryptographic Binding**: Hash lock ties both HTLCs together
2. **Sequential Reveal**: Secret revealed in one direction enables the other
3. **Timelock Safety**: Refund capability prevents permanent lockup

### Attack Scenarios

#### 1. Front-Running Attack

**Risk**: Attacker sees initiator's claim transaction and front-runs with higher fee.

**Mitigation**: Initiator reveals secret on destination chain first. Since initiator controls the secret, they have priority on destination chain claim.

#### 2. Timelock Race

**Risk**: Responder waits until just before timeout to claim, giving initiator no time to claim on source chain.

**Mitigation**: `T_src > T_dest` ensures initiator has at least as much time as responder, usually more.

#### 3. Relayer Censorship

**Risk**: Relayer refuses to submit proof, blocking swap completion.

**Mitigation**: Anyone can submit proofs - relayers are optional. Users can run their own relayer.

#### 4. Blockchain Reorganization

**Risk**: Chain reorg invalidates proof submitted to Stellar.

**Mitigation**: Wait for sufficient confirmations before considering proof final. Recommended: 6 Bitcoin confirmations, 12 Ethereum blocks.

### Privacy Considerations

- **Secret Visibility**: Revealed on destination chain claim, visible to anyone watching
- **Address Linkability**: Both parties learn each other's addresses on respective chains
- **Amount Visibility**: All amounts are public on-chain

For enhanced privacy, consider:
- Using different addresses for each swap
- Mixing services (if available on destination chain)
- CoinJoin for Bitcoin

## Implementation Details

### Soroban Contract

```rust
// HTLC creation
pub fn create_htlc(
    env: Env,
    sender: Address,
    receiver: Address,
    amount: i128,
    hash_lock: Bytes,
    time_lock: u64,
) -> Result<u64, Error> {
    // Validate inputs
    if amount <= 0 {
        return Err(Error::InvalidAmount);
    }
    if hash_lock.len() != 32 {
        return Err(Error::InvalidHashLength);
    }
    if time_lock <= env.ledger().timestamp() {
        return Err(Error::InvalidTimelock);
    }
    
    // Create HTLC
    let htlc_id = storage::increment_htlc_counter(&env);
    let htlc = HTLC {
        sender,
        receiver,
        amount,
        hash_lock,
        time_lock,
        status: HTLCStatus::Active,
        secret: None,
        created_at: env.ledger().timestamp(),
    };
    storage::write_htlc(&env, htlc_id, &htlc);
    Ok(htlc_id)
}

// HTLC claim
pub fn claim_htlc(
    env: &Env,
    htlc_id: u64,
    secret: Bytes,
) -> Result<(), Error> {
    let mut htlc = storage::read_htlc(env, htlc_id)?;
    
    // Check status
    if htlc.status != HTLCStatus::Active {
        return Err(Error::AlreadyClaimed);
    }
    
    // Check timelock
    if env.ledger().timestamp() >= htlc.time_lock {
        return Err(Error::HTLCExpired);
    }
    
    // Verify secret
    let computed_hash = env.crypto().sha256(&secret);
    if computed_hash != htlc.hash_lock {
        return Err(Error::InvalidSecret);
    }
    
    // Update status
    htlc.status = HTLCStatus::Claimed;
    htlc.secret = Some(secret);
    storage::write_htlc(env, htlc_id, &htlc);
    
    // Transfer funds (implementation depends on asset type)
    // ...
    
    Ok(())
}
```

### Bitcoin HTLC Script

```javascript
// P2SH HTLC script for Bitcoin
const HTLC_script = `
OP_IF
    // Revealed secret case
    OP_SHA256 <hash> OP_EQUALVERIFY <receiver_pubkey> OP_CHECKSIG
OP_ELSE
    // Refund case
    <expiry> OP_CHECKSEQUENCEVERIFY OP_DROP <sender_pubkey> OP_CHECKSIG
OP_ENDIF
`;
```

### Ethereum HTLC Contract (Solidity)

```solidity
// Simplified Ethereum HTLC
contract HTLC {
    bytes32 public hashLock;
    address public sender;
    address public receiver;
    uint256 public timelock;
    bool public claimed;
    bool public refunded;
    
    constructor(
        bytes32 _hashLock,
        address _sender,
        address _receiver,
        uint256 _timelock
    ) {
        hashLock = _hashLock;
        sender = _sender;
        receiver = _receiver;
        timelock = _timelock;
    }
    
    function claim(bytes32 _secret) public {
        require(!claimed && !refunded, "Already resolved");
        require(msg.sender == receiver, "Not receiver");
        require(
            sha256(abi.encodePacked(_secret)) == hashLock,
            "Invalid secret"
        );
        require(block.timestamp < timelock, "Timelock expired");
        
        claimed = true;
        // Transfer funds
        payable(receiver).transfer(address(this).balance);
    }
    
    function refund() public {
        require(!claimed && !refunded, "Already resolved");
        require(msg.sender == sender, "Not sender");
        require(block.timestamp >= timelock, "Timelock not expired");
        
        refunded = true;
        // Transfer funds back
        payable(sender).transfer(address(this).balance);
    }
}
```

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| InvalidSecret | Wrong secret provided | Verify correct secret |
| HTLCExpired | Timelock passed | Initiate refund |
| HTLCNotFound | HTLC doesn't exist | Check HTLC ID |
| AlreadyClaimed | HTLC already claimed | Check status |

### Recovery Procedures

1. **Expired Unclaimed HTLC**: Call `refund_htlc()` after timeout
2. **Failed Claim**: Verify secret is correct, retry with correct secret
3. **Proof Rejected**: Regenerate proof with more confirmations

## Best Practices

### For Users

1. **Verify Timeouts**: Ensure sufficient time for completion
2. **Monitor Progress**: Watch both chains for events
3. **Keep Secrets Safe**: Lose secret = lose funds (if unclaimed)
4. **Test First**: Use testnet before mainnet

### For Relayers

1. **Monitor Reliability**: Ensure 24/7 monitoring
2. **Quick Response**: Submit proofs promptly
3. **Fee Management**: Set appropriate fees
4. **Proof Storage**: Keep proof data for disputes

### For Integrators

1. **Finality Confirmation**: Wait for sufficient confirmations
2. **Event Monitoring**: Watch for all HTLC events
3. **Error Handling**: Implement retry logic
4. **Testing**: Thoroughly test with testnet

## References

- [Architecture Overview](./ARCHITECTURE.md)
- [Smart Contract Documentation](./SMARTCONTRACT.md)
- [Relayer Documentation](./RELAYER.md)
- [Bitcoin HTLC Wiki](https://en.bitcoin.it/wiki/Hash_Time_Locked_Contracts)
- [Atomic Swap Protocol](https://en.wikipedia.org/wiki/Atomic_swap)
