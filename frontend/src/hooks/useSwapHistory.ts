import { create } from "zustand";
import { persist } from "zustand/middleware";
import { useCallback } from "react";
import { SwapStatus } from "@/types";

export interface SwapHistoryItem {
  id: string;
  from: string;
  to: string;
  amount: string;
  toAmount: string;
  status: SwapStatus;
  date: string;
  otherChainTx?: string;
}

interface SwapHistoryStore {
  swaps: SwapHistoryItem[];
  upsertSwap: (swap: SwapHistoryItem) => void;
  removeSwap: (id: string) => void;
  setSwaps: (swaps: SwapHistoryItem[]) => void;
}

export const useSwapHistoryStore = create<SwapHistoryStore>()(
  persist(
    (set) => ({
      swaps: [],
      upsertSwap: (swap) =>
        set((state) => {
          const existingIndex = state.swaps.findIndex((item) => item.id === swap.id);
          if (existingIndex === -1) {
            return { swaps: [swap, ...state.swaps].slice(0, 300) };
          }
          const next = [...state.swaps];
          next[existingIndex] = { ...next[existingIndex], ...swap };
          return { swaps: next };
        }),
      removeSwap: (id) =>
        set((state) => ({
          swaps: state.swaps.filter((item) => item.id !== id),
        })),
      setSwaps: (swaps) => set({ swaps }),
    }),
    {
      name: "chainbridge-swaps",
    }
  )
);

const MOCK_SWAPS: SwapHistoryItem[] = [
  {
    id: "swap_001",
    from: "XLM",
    to: "BTC",
    amount: "5,000",
    toAmount: "0.009",
    status: SwapStatus.COMPLETED,
    date: "2024-03-20T10:00:00Z",
  },
  {
    id: "swap_002",
    from: "ETH",
    to: "XLM",
    amount: "1.2",
    toAmount: "12,500",
    status: SwapStatus.PENDING,
    date: "2024-03-21T14:30:00Z",
  },
  {
    id: "swap_003",
    from: "BTC",
    to: "ETH",
    amount: "0.05",
    toAmount: "1.8",
    status: SwapStatus.EXPIRED,
    date: "2024-03-19T08:15:00Z",
  },
];

export function useMockSwaps() {
  const swaps = useSwapHistoryStore((state) => state.swaps);
  const setSwaps = useSwapHistoryStore((state) => state.setSwaps);

  const seedMockSwaps = useCallback(() => {
    if (swaps.length === 0) {
      setSwaps(MOCK_SWAPS);
    }
  }, [setSwaps, swaps.length]);

  return { seedMockSwaps };
}
