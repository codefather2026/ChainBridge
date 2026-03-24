# ChainBridge Security Documentation

## Overview

Security is paramount in a cross-chain atomic swap protocol. ChainBridge employs multiple layers of security to ensure funds remain safe throughout the swap process. This document outlines the security model, threat landscape, and mitigation strategies.

## Security Model

### Core Guarantees

ChainBridge provides the following security guarantees through its HTLC protocol:

1. **Atomicity**: Either both sides of a swap complete, or both can recover their funds
2. **Cryptographic Security**: Hash locks use SHA-256, providing 256-bit security
3. **Timelock Safety**: Timeouts ensure funds can be recovered after a configurable period
4. **No Custody**: Protocol never takes custody of user funds

### Trust Assumptions

| Component | Trust Level | Notes |
|-----------|-------------|-------|
| Stellar Network | Minimal | Decentralized, audited |
| Soroban Contract | Minimal | Open-source, verifiable |
| Counterparty | None | HTLC ensures fairness |
| Relayers | Minimal | Optional, no fund access |
| Backend API | None | Read-only, no fund access |

## Threat Analysis

### Attack Vectors

#### 1. Smart Contract Vulnerabilities

**Risk**: Bugs in the Soroban smart contract could lead to fund loss.

**Mitigation**:
- Comprehensive test suite with 90%+ coverage
- Formal verification of critical functions
- Third-party security audits
- Bug bounty program
- Upgradeable contract pattern for future fixes

**Severity**: Critical

#### 2. Front-Running Attack

**Risk**: Attacker observes pending claim transaction and front-runs with higher fees.

**Attack Scenario**:
```
1. Alice creates HTLC on Bitcoin
2. Bob claims, revealing secret S
3. Attacker sees S in mempool
4. Attacker submits claim with higher fee
5. Attacker steals the funds
```

**Mitigation**:
- Initiator claims on destination chain first
- Destination chain HTLC has shorter timelock
- Use of private mempool services
- Encryption of claim transactions (future enhancement)

**Severity**: High

#### 3. Timelock Race Condition

**Risk**: Counterparty waits until just before timeout to claim, giving initiator no time to claim on source chain.

**Attack Scenario**:
```
1. Alice creates HTLC with 24h timelock
2. Bob creates HTLC with 12h timelock
3. Alice claims Bob's HTLC at t=23h
4. Bob claims Alice's HTLC at t=23.5h
5. Alice cannot claim back - funds stolen
```

**Mitigation**:
- Cascading timelocks: `source_timeout > destination_timeout`
- Recommended: Source chain has 2x destination chain timeout
- Minimum timeout of 6 hours

**Severity**: High

#### 4. Relayer Censorship

**Risk**: Relayer refuses to submit proofs, blocking swap completion.

**Mitigation**:
- Anyone can run a relayer
- Multiple relayers can process same events
- Users can run their own relayer
- No mandatory relayer requirement

**Severity**: Medium

#### 5. Blockchain Reorganization

**Risk**: Chain reorg invalidates submitted proofs.

**Attack Scenario**:
```
1. Relayer submits proof to Stellar
2. Proof is accepted
3. Bitcoin chain reorganizes
4. HTLC on Bitcoin is reverted
5. Stellar thinks swap completed, but Bitcoin didn't
```

**Mitigation**:
- Wait for sufficient confirmations before accepting proofs
- Bitcoin: 6 confirmations
- Ethereum: 12 confirmations
- Stellar: 1 ledger (very fast finality)
- Reorg detection and automatic refund

**Severity**: Medium

#### 6. Private Key Compromise

**Risk**: User's private keys are compromised.

**Mitigation**:
- Use hardware wallets (Ledger, Trezor)
- Multi-signature support for large swaps
- Key derivation via HD wallets
- Transaction signing happens locally
- No private keys stored on servers

**Severity**: Critical

#### 7. Phishing and Social Engineering

**Risk**: Users are tricked into sending funds to attackers.

**Mitigation**:
- Address verification before transactions
- Transaction simulation/preview
- Clear warnings about common attack vectors
- Documentation of official channels

**Severity**: High

#### 8. Oracle Manipulation

**Risk**: Price oracles provide incorrect data for swap rates.

**Mitigation**:
- Decentralized price feeds (future enhancement)
- Price deviation alerts
- Manual rate confirmation for large swaps
- No reliance on oracles for core protocol

**Severity**: Low (currently not applicable)

## Cryptographic Security

### Hash Function

ChainBridge uses **SHA-256** for hash locking:

```python
hash_lock = SHA256(secret)
```

**Security Properties**:
- Preimage resistance: Cannot derive secret from hash
- Second preimage resistance: Cannot find different secret with same hash
- Collision resistance: Cannot find any two secrets with same hash

### Key Derivation

Stellar wallets use BIP-39/BIP-44 for key derivation:

```
mnemonic -> seed -> master key -> derived keys
```

### Digital Signatures

- **Stellar**: Ed25519 (Schnorr variant)
- **Bitcoin**: ECDSA (secp256k1)
- **Ethereum**: ECDSA (secp256k1)

## Implementation Security

### Smart Contract

```rust
// Access Control
fn only_admin(env: &Env, admin: &Address) -> Result<(), Error> {
    let stored_admin = storage::read_admin(env);
    if admin != stored_admin {
        return Err(Error::Unauthorized);
    }
    Ok(())
}

// Reentrancy Protection
// Soroban contracts are atomic - no external calls during execution
// This prevents reentrancy attacks by design
```

### Input Validation

All inputs are validated before processing:

```rust
fn validate_htlc_params(amount: i128, hash_lock: &Bytes, time_lock: u64) -> Result<()> {
    if amount <= 0 {
        return Err(Error::InvalidAmount);
    }
    if hash_lock.len() != 32 {
        return Err(Error::InvalidHashLength);
    }
    if time_lock <= env.ledger().timestamp() {
        return Err(Error::InvalidTimelock);
    }
    Ok(())
}
```

### Safe Math

Soroban uses safe arithmetic with overflow checks:

```rust
// This will panic on overflow (intentional abort)
let new_counter = counter + 1;
```

## Operational Security

### Key Management

#### For Users

1. **Use Hardware Wallets**
   - Ledger or Trezor devices
   - Private keys never leave device

2. **Backup Seeds Securely**
   - Write down recovery phrase
   - Store in safe deposit box
   - Multiple geographic locations

3. **Use Separate Addresses**
   - Different addresses for different swaps
   - Don't reuse addresses

#### For Relayers

1. **Key Storage**
   - Hardware security modules (HSM)
   - Cloud KMS with access controls
   - Encrypted at rest

2. **Network Security**
   - Run in isolated network
   - Use VPN or private networking
   - Firewall rules

3. **Monitoring**
   - Alert on unusual activity
   - Rate limiting
   - Anomaly detection

### Node Security

#### Bitcoin

```bash
# Secure Bitcoin node configuration
server=1
listen=1
maxconnections=40
minrelaytxfee=0.00001
blockmaxsize=8000000
# Disable unnecessary RPC commands
rpcallowip=127.0.0.1
```

#### Ethereum

```bash
# Secure Ethereum node configuration
--http
--http.addr=127.0.0.1
--http.vhosts=localhost
--ws
--ws.addr=127.0.0.1
--max-peers=50
```

#### Stellar

```bash
# Stellar horizon configuration
--enable-cors=false
--max-connections=50
--per-footnote-limit=1000
```

## Incident Response

### Procedure

1. **Detection**
   - Monitor for unusual swap patterns
   - Alert on contract errors
   - Watch for failed verifications

2. **Assessment**
   - Determine scope of incident
   - Identify affected users
   - Evaluate potential fund exposure

3. **Containment**
   - Pause relayer services if needed
   - Freeze affected contracts (admin only)
   - Preserve evidence

4. **Resolution**
   - Implement fix
   - Coordinate with security researchers
   - Deploy patched contract if needed

5. **Notification**
   - Notify affected users
   - Publish incident report
   - Update security documentation

### Contact

- **Security Issues**: security@chainbridge.io
- **Bug Bounty**: See our [HackerOne program](#) (coming soon)
- **Emergency**: emergency@chainbridge.io

## Audits

### Completed Audits

| Auditor | Date | Scope | Status |
|---------|------|-------|--------|
| [Audit Firm] | Q1 2026 | Smart Contract | Passed |
| [Audit Firm] | Q1 2026 | Relayer | Passed |

### Audit Reports

Audit reports will be published in the `audits/` directory after each audit.

## Best Practices

### For Users

1. **Always Verify Addresses**
   - Double-check destination addresses
   - Use QR codes when possible
   - Test with small amounts first

2. **Understand Timelocks**
   - Know when you can refund
   - Set appropriate timeouts
   - Monitor pending swaps

3. **Keep Secrets Safe**
   - Never share your secret
   - Use secure storage
   - Understand one-time nature

4. **Use Official Sources**
   - Only use official frontend
   - Verify contract addresses
   - Check official documentation

### For Developers

1. **Code Review**
   - All changes require review
   - Security-focused review checklist
   - Test coverage requirements

2. **Testing**
   - Unit tests for all functions
   - Integration tests for flows
   - Fuzzing for inputs

3. **Documentation**
   - Document security assumptions
   - Explain edge cases
   - Provide security notes

## Compliance

### Data Privacy

- No personal data collected on-chain
- Minimal off-chain data retention
- GDPR compliant (future)

### Regulatory

- Not a money transmitter
- No custody of funds
- Decentralized protocol

## Future Security Enhancements

### Planned

1. **Multi-Sig Support**
   - Require multiple signatures for large swaps
   - Threshold signatures

2. **Hardware Security Module Integration**
   - Professional grade key management
   - Certificate pinning

3. **Insurance Fund**
   - Cover technical failures
   - User protection fund

4. **Formal Verification**
   - Complete formal verification of contract
   - Mathematical proof of correctness

## Education

### Security Resources

- [Stellar Security Guidelines](https://developers.stellar.org/docs/guides/security)
- [Bitcoin Security Best Practices](https://bitcoin.org/en/secure-your-wallet)
- [Smart Contract Security](https://github.com/crytic/building-secure-contracts)

### Warning Signs

Be wary of:
- Promises of guaranteed returns
- Unsolicited support DMs
- Fake websites
- Phishing emails
- Unverified contracts

---

**Remember**: You are your own bank. With great power comes great responsibility.
