import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

/** Standardized query keys by domain */
export const queryKeys = {
  swaps: {
    all: ["swaps"] as const,
    list: (filters?: Record<string, unknown>) => ["swaps", "list", filters] as const,
    detail: (id: string) => ["swaps", "detail", id] as const,
  },
  transactions: {
    all: ["transactions"] as const,
    list: (filters?: Record<string, unknown>) => ["transactions", "list", filters] as const,
    detail: (id: string) => ["transactions", "detail", id] as const,
  },
  orders: {
    all: ["orders"] as const,
    list: (pair?: string) => ["orders", "list", pair] as const,
    detail: (id: string) => ["orders", "detail", id] as const,
    book: (pair: string) => ["orders", "book", pair] as const,
  },
  dashboard: {
    health: ["dashboard", "health"] as const,
    stats: ["dashboard", "stats"] as const,
  },
  wallet: {
    balance: (chain: string, address: string) => ["wallet", "balance", chain, address] as const,
  },
} as const;
