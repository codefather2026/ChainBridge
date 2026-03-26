use soroban_sdk::contracterror;

#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum Error {
    AlreadyInitialized = 1,
    NotInitialized = 2,
    Unauthorized = 3,
    InvalidAmount = 4,
    HTLCNotFound = 5,
    HTLCExpired = 6,
    HTLCNotExpired = 7,
    InvalidSecret = 8,
    AlreadyClaimed = 9,
    AlreadyRefunded = 10,
    InvalidHashLength = 11,
    InvalidTimelock = 12,
    OrderNotFound = 13,
    OrderAlreadyMatched = 14,
    OrderExpired = 15,
    InvalidChain = 16,
    ProofVerificationFailed = 17,
    Paused = 18,
    AmountTooSmall = 19,
    FeeCollectionFailed = 20,
    InvalidFeeRate = 21,
    ThresholdNotMet = 22,
    SignerNotAuthorized = 23,
    RecoveryFailed = 24,
    Timeout = 25,
}
