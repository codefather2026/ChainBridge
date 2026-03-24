# ChainBridge Relayer Documentation

## Overview

The ChainBridge relayer is a critical infrastructure component that monitors multiple blockchains, generates cross-chain proofs, and facilitates the completion of atomic swaps. Relayers play a vital role in enabling trustless cross-chain communication without requiring users to run full nodes for each supported blockchain.

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RELAYER ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Relayer Core Service                              │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │    │
│  │  │  Event          │  │  Proof           │  │  Submission     │  │    │
│  │  │  Processor      │  │  Generator       │  │  Service        │  │    │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │    │
│  │           │                    │                    │            │    │
│  │           └────────────────────┼────────────────────┘            │    │
│  │                                │                                     │    │
│  │                    ┌───────────┴───────────┐                       │    │
│  │                    │   State Manager       │                       │    │
│  │                    │   & Task Queue        │                       │    │
│  │                    └───────────┬───────────┘                       │    │
│  └─────────────────────────────────┼─────────────────────────────────────┘    │
│                                    │                                          │
│         ┌──────────────────────────┼──────────────────────────┐              │
│         │                          │                          │              │
│         ▼                          ▼                          ▼              │
│  ┌──────────────┐          ┌──────────────┐          ┌──────────────┐       │
│  │  Bitcoin    │          │  Ethereum    │          │   Stellar   │       │
│  │  Monitor    │          │  Monitor     │          │   Monitor   │       │
│  │              │          │              │          │              │       │
│  │ • RPC       │          │ • RPC        │          │ • RPC       │       │
│  │ • WebSocket │          │ • WebSocket  │          │ • WebSocket │       │
│  │ • mempool   │          │ • Events     │          │ • Events    │       │
│  └──────────────┘          └──────────────┘          └──────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. Event Monitor

Monitors each blockchain for relevant events:

- **Bitcoin**: HTLC creation transactions, claim transactions, refund transactions
- **Ethereum**: HTLC contract events (Created, Claimed, Refunded)
- **Stellar**: Soroban contract events from ChainBridge

#### 2. Proof Generator

Generates verifiable proofs for cross-chain verification:

- **SPV Proofs**: Simplified Payment Verification for Bitcoin
- **Merkle Proofs**: Receipt and log proofs for Ethereum
- **Transaction Proofs**: Inclusion proofs for Stellar

#### 3. Submission Service

Submits proofs and transactions to target chains:

- Invokes Soroban contract methods
- Broadcasts Bitcoin transactions
- Calls Ethereum contract functions

#### 4. State Manager

Maintains relayer state:

- Processed event tracking
- Pending swap state machine
- Retry queue for failed submissions

## Supported Blockchains

| Chain | Status | Features |
|-------|--------|----------|
| Bitcoin | Implemented | SPV proofs, tx monitoring |
| Ethereum | Implemented | Event logs, Merkle proofs |
| Stellar | Implemented | Soroban contract events |
| Solana | Planned | Transaction proofs |
| Polygon | Planned | Event logs |

## Installation

### Prerequisites

- Rust 1.70+
- Cargo
- Access to blockchain RPC endpoints
- PostgreSQL for state persistence
- Redis for task queue

### Build from Source

```bash
# Clone the repository
git clone https://github.com/floxxih/ChainBridge.git
cd ChainBridge/relayer

# Build release binary
cargo build --release

# The binary will be at target/release/chainbridge-relayer
```

### Docker Deployment

```bash
# Build Docker image
docker build -t chainbridge-relayer:latest ./relayer

# Run container
docker run -d \
  --name chainbridge-relayer \
  -e BITCOIN_RPC_URL=http://bitcoin:8332 \
  -e ETHEREUM_RPC_URL=http://ethereum:8545 \
  -e STELLAR_RPC_URL=https://soroban-testnet.stellar.org \
  -e DATABASE_URL=postgresql://user:pass@localhost/relayer \
  chainbridge-relayer:latest
```

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| BITCOIN_RPC_URL | Yes | Bitcoin RPC URL | - |
| BITCOIN_RPC_USER | No | Bitcoin RPC username | - |
| BITCOIN_RPC_PASS | No | Bitcoin RPC password | - |
| ETHEREUM_RPC_URL | Yes | Ethereum RPC URL | - |
| ETHEREUM_RPC_WS_URL | No | Ethereum WebSocket URL | - |
| STELLAR_RPC_URL | Yes | Stellar Soroban RPC URL | - |
| STELLAR_NETWORK | Yes | Network (testnet/mainnet) | testnet |
| CHAINBRIDGE_CONTRACT_ID | Yes | ChainBridge contract address | - |
| DATABASE_URL | Yes | PostgreSQL connection string | - |
| REDIS_URL | No | Redis connection string | - |
| RELAYER_FEE | No | Fee per swap (in basis points) | 0 |
| LOG_LEVEL | No | Logging level | info |

### Configuration File

Alternatively, create a config file:

```yaml
# relayer.yaml
relayer:
  fee_bps: 5
  max_concurrent_swaps: 10
  retry_attempts: 3
  retry_delay_seconds: 30

bitcoin:
  rpc_url: "http://localhost:8332"
  rpc_user: "user"
  rpc_pass: "pass"
  confirmations: 6

ethereum:
  rpc_url: "https://mainnet.infura.io/v3/YOUR_KEY"
  contract_address: "0x..."
  confirmations: 12

stellar:
  rpc_url: "https://soroban-mainnet.stellar.org"
  network: "mainnet"
  contract_id: "C..."
```

## Operation

### Starting the Relayer

```bash
# Basic usage
./target/release/chainbridge-relayer --config relayer.yaml

# With environment variables
BITCOIN_RPC_URL=http://localhost:8332 \
ETHEREUM_RPC_URL=http://localhost:8545 \
STELLAR_RPC_URL=https://soroban-testnet.stellar.org \
DATABASE_URL=postgresql://localhost/relayer \
./target/release/chainbridge-relayer
```

### Running Modes

#### Full Mode

Monitors all supported chains and processes all events:

```bash
chainbridge-relayer --mode full
```

#### Light Mode

Only monitors Stellar and processes incoming proofs:

```bash
chainbridge-relayer --mode light
```

#### Bitcoin-Only Mode

Only monitors Bitcoin:

```bash
chainbridge-relayer --mode bitcoin
```

### Monitoring

#### Health Check

```bash
curl http://localhost:8080/health
```

Response:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "chains": {
    "bitcoin": "connected",
    "ethereum": "connected",
    "stellar": "connected"
  }
}
```

#### Metrics

Prometheus metrics available at `/metrics`:

```bash
curl http://localhost:8080/metrics
```

Key metrics:
- `relayer_swaps_processed_total`: Total swaps processed
- `relayer_proofs_generated_total`: Total proofs generated
- `relayer_submissions_failed_total`: Failed submission count
- `relayer_chain_block_height`: Current block height per chain

## Proof Generation

### Bitcoin SPV Proof

```rust
use bitcoin::{Block, MerkleBlock, Transaction};

fn generate_spv_proof(
    tx_hash: &Txid,
    block_hash: &BlockHash,
    merkle_block: &MerkleBlock,
) -> BitcoinProof {
    BitcoinProof {
        tx_hash: tx_hash.to_vec(),
        block_header: block_header_to_bytes(block),
        merkle_proof: merkle_block.serialize(),
        tx_index: merkle_block.merkle_tx_index(),
    }
}
```

### Ethereum Merkle Proof

```rust
fn generate_eth_proof(
    log: &Log,
    receipt: &Receipt,
    block: &Header,
) -> EthereumProof {
    EthereumProof {
        receipt_proof: generate_receipt_proof(receipt),
        log_proof: generate_log_proof(log, receipt),
        block_header: block_to_bytes(block),
    }
}
```

### Proof Verification

All proofs are verified against the ChainBridge smart contract:

```rust
fn submit_proof(relayer: &Relayer, proof: &ChainProof) -> Result<()> {
    let tx = contract.invoke("verify_proof", &[proof]);
    relayer.submit_transaction(tx)?;
    Ok(())
}
```

## Swap Processing Flow

### 1. HTLC Created Event

```
┌────────────┐     ┌──────────────┐     ┌─────────────┐
│ Blockchain │────>│ Event Filter │────>│ State Queue │
│   Event    │     │              │     │             │
└────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
                                       ┌────────────────┐
                                       │ Wait for       │
                                       │ Counterparty   │
                                       │ HTLC           │
                                       └────────┬───────┘
                                                │
                                                ▼
                                       ┌────────────────┐
                                       │ Monitor Claim  │
                                       │ & Generate     │
                                       │ Proof          │
                                       └────────────────┘
```

### 2. HTLC Claimed Event

```
┌────────────┐     ┌──────────────┐     ┌─────────────┐
│ Blockchain │────>│ Event Filter │────>│ Extract     │
│   Event    │     │              │     │ Secret      │
└────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
                                       ┌────────────────┐
                                       │ Generate Proof │
                                       │ of Claim       │
                                       └────────┬───────┘
                                                │
                                                ▼
                                       ┌────────────────┐
                                       │ Submit to      │
                                       │ Stellar        │
                                       │ Contract       │
                                       └────────┬───────┘
                                                │
                                                ▼
                                       ┌────────────────┐
                                       │ Update Swap    │
                                       │ Status         │
                                       └────────────────┘
```

## Relayer Fees

### Fee Structure

Relayers can earn fees for their services:

| Fee Type | Description |
|----------|-------------|
| Fixed Fee | Flat fee per swap |
| Percentage | Percentage of swap value |
| Gas Reimbursement | Reimbursement for on-chain costs |

### Fee Configuration

```yaml
relayer:
  fee_type: "percentage"  # fixed, percentage, or gas
  fee_bps: 10             # basis points (0.1%)
  min_fee: 1000          # minimum fee in stroops
  max_fee: 1000000       # maximum fee in stroops
```

### Fee Collection

Fees are automatically deducted from completed swaps:

```
Swap Amount: 100 XLM
Fee (0.1%):   0.1 XLM
Net to User:  99.9 XLM
```

## Security

### Key Management

Relayers must securely manage:

- Private keys for signing transactions
- RPC credentials
- Database credentials

### Best Practices

1. **Key Storage**: Use hardware security modules (HSM) or secure enclaves
2. **Network Isolation**: Run relayer in isolated network segment
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Monitoring**: Alert on unusual activity
5. **Backup**: Regular backups of state data

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Key compromise | HSM storage, multi-sig |
| Front-running | Private mempool, encryption |
| Denial of Service | Rate limiting, DDoS protection |
| Data corruption | Regular backups, checksums |

## Troubleshooting

### Common Issues

#### Connection Failures

```
Error: Failed to connect to Bitcoin RPC
```

**Solution**: Check RPC URL, credentials, and network connectivity

#### Proof Generation Fails

```
Error: Insufficient confirmations for proof
```

**Solution**: Wait for more block confirmations, adjust confirmation requirements

#### Transaction Stuck

```
Error: Transaction not confirmed after 10 minutes
```

**Solution**: Check gas/fee settings, rebump fees if supported

### Debug Logging

Enable debug logging:

```bash
RUST_LOG=debug ./chainbridge-relayer
```

### Health Checks

```bash
# Check chain connectivity
curl http://localhost:8080/health/chains

# Check pending swaps
curl http://localhost:8080/debug/swaps/pending
```

## API Endpoints

### Relayer Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/health/chains` | GET | Chain connectivity |
| `/metrics` | GET | Prometheus metrics |
| `/swaps/pending` | GET | Pending swaps |
| `/swaps/{id}` | GET | Swap details |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/pause` | POST | Pause relayer |
| `/admin/resume` | POST | Resume relayer |
| `/admin/force-sync` | POST | Force state sync |

## Development

### Running Tests

```bash
cd relayer
cargo test
```

### Running with Local Stack

```bash
# Start local testnet
docker-compose -f docker-compose.local.yml up -d

# Run relayer against local stack
cargo run -- --config config/local.yaml
```

### Adding Support for New Chains

1. Implement `ChainMonitor` trait for the new chain
2. Add proof generation for the chain
3. Update configuration schema
4. Add tests and documentation

## Contributing

Contributions to the relayer are welcome! Please see our [Contributing Guide](../CONTRIBUTING.md).

### Running Benchmarks

```bash
cargo bench
```

## License

MIT License - see [LICENSE](../LICENSE) for details.
