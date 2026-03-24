import { useState, useCallback } from "react";

interface UseAsyncState<T> {
  loading: boolean;
  error: Error | null;
  value: T | null;
}

export function useAsync<T>() {
  const [state, setState] = useState<UseAsyncState<T>>({
    loading: false,
    error: null,
    value: null,
  });

  const execute = useCallback(async (asyncFunction: () => Promise<T>) => {
    setState({ loading: true, error: null, value: null });

    try {
      const result = await asyncFunction();
      setState({ loading: false, error: null, value: result });
      return result;
    } catch (error) {
      setState({ loading: false, error: error as Error, value: null });
      throw error;
    }
  }, []);

  return { ...state, execute };
}
