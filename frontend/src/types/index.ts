export interface Swap {
  id: string;
  initiator: string;
  responder: string;
  inputAsset: string;
  outputAsset: string;
  inputAmount: string;
  outputAmount: string;
  hashlock: string;
  timelock: number;
  status: SwapStatus;
  createdAt: string;
  updatedAt: string;
}

export enum SwapStatus {
  PENDING = "pending",
  LOCKED_INITIATOR = "locked_initiator",
  LOCKED_RESPONDER = "locked_responder",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

export interface CreateSwapRequest {
  inputAsset: string;
  outputAsset: string;
  inputAmount: string;
  outputAmount: string;
  responder?: string;
}

export interface WalletInfo {
  address: string;
  chain: string;
  balance: string;
}
