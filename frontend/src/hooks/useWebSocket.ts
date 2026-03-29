import { useCallback, useEffect, useMemo, useRef, useState } from "react";

interface WebSocketMessage {
  type: string;
  channel?: string;
  data?: any;
}

interface SubscribeOptions {
  /** Optionally filter to only specific event_types, e.g. ['swap.status_changed'] */
  eventTypes?: string[];
}

interface UseWebSocketOptions {
  enabled?: boolean;
}

const RECONNECT_BASE_MS = 1_000;
const RECONNECT_MAX_MS = 30_000;
const RECONNECT_MULTIPLIER = 2;
const RECONNECT_JITTER_FACTOR = 0.3;

export function useWebSocket(
  url: string | null,
  token: string | null,
  options: UseWebSocketOptions = {}
) {
  const enabled = options.enabled ?? true;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout>>();
  const reconnectAttempts = useRef(0);
  const shouldReconnect = useRef(true);

  const listeners = useRef<Map<string, Set<(data: any) => void>>>(new Map());
  const subscriptions = useRef<Map<string, SubscribeOptions>>(new Map());

  const canConnect = useMemo(() => Boolean(enabled && url && token), [enabled, token, url]);

  const clearReconnectTimer = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = undefined;
    }
  }, []);

  const sendRaw = useCallback((payload: object) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(payload));
    }
  }, []);

  const resubscribeAll = useCallback(() => {
    subscriptions.current.forEach((opts, channel) => {
      sendRaw({
        type: "subscribe",
        channel,
        event_types: opts.eventTypes ?? [],
      });
    });
  }, [sendRaw]);

  const scheduleReconnect = useCallback(
    (connectFn: () => void) => {
      if (!canConnect || !shouldReconnect.current) return;

      clearReconnectTimer();

      const attempt = reconnectAttempts.current;
      const exponentialDelay = Math.min(
        RECONNECT_BASE_MS * RECONNECT_MULTIPLIER ** attempt,
        RECONNECT_MAX_MS
      );
      const jitter = Math.floor(exponentialDelay * Math.random() * RECONNECT_JITTER_FACTOR);
      const delay = Math.min(exponentialDelay + jitter, RECONNECT_MAX_MS);

      reconnectTimeout.current = setTimeout(() => {
        reconnectAttempts.current += 1;
        connectFn();
      }, delay);
    },
    [canConnect, clearReconnectTimer]
  );

  const disconnect = useCallback(() => {
    clearReconnectTimer();
    setIsConnected(false);

    if (ws.current) {
      ws.current.onclose = null;
      ws.current.onerror = null;
      ws.current.onopen = null;
      ws.current.onmessage = null;
      ws.current.close();
      ws.current = null;
    }
  }, [clearReconnectTimer]);

  const connect = useCallback(() => {
    if (!canConnect) return;
    if (ws.current?.readyState === WebSocket.CONNECTING) return;

    clearReconnectTimer();

    if (ws.current) {
      ws.current.onclose = null;
      ws.current.close();
      ws.current = null;
    }

    let wsUrl: URL;
    try {
      wsUrl = new URL(url!);
      wsUrl.searchParams.set("token", token!);
    } catch {
      setError(new Error("Invalid WebSocket URL"));
      return;
    }

    const socket = new WebSocket(wsUrl.toString());

    socket.onopen = () => {
      setIsConnected(true);
      setError(null);
      reconnectAttempts.current = 0;
      resubscribeAll();
    };

    socket.onclose = () => {
      setIsConnected(false);
      ws.current = null;
      scheduleReconnect(connect);
    };

    socket.onerror = () => {
      setError(new Error("WebSocket connection error"));
    };

    socket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        if (message.type === "ping") {
          sendRaw({ type: "pong" });
          return;
        }

        const key = message.channel ?? message.type;
        const channelListeners = listeners.current.get(key);
        if (channelListeners) {
          channelListeners.forEach((cb) => cb(message.data));
        }
      } catch {
        // Ignore malformed frames.
      }
    };

    ws.current = socket;
  }, [canConnect, clearReconnectTimer, resubscribeAll, scheduleReconnect, sendRaw, token, url]);

  useEffect(() => {
    shouldReconnect.current = true;

    if (!canConnect) {
      disconnect();
      return;
    }

    connect();

    const handleOnline = () => {
      if (!ws.current || ws.current.readyState === WebSocket.CLOSED) {
        connect();
      }
    };

    window.addEventListener("online", handleOnline);

    return () => {
      shouldReconnect.current = false;
      window.removeEventListener("online", handleOnline);
      disconnect();
    };
  }, [canConnect, connect, disconnect]);

  const subscribe = useCallback(
    (channel: string, callback: (data: any) => void, opts: SubscribeOptions = {}) => {
      if (!listeners.current.has(channel)) {
        listeners.current.set(channel, new Set());
      }
      listeners.current.get(channel)!.add(callback);

      subscriptions.current.set(channel, opts);
      sendRaw({ type: "subscribe", channel, event_types: opts.eventTypes ?? [] });

      return () => {
        const set = listeners.current.get(channel);
        if (!set) return;

        set.delete(callback);
        if (set.size === 0) {
          listeners.current.delete(channel);
          subscriptions.current.delete(channel);
          sendRaw({ type: "unsubscribe", channel });
        }
      };
    },
    [sendRaw]
  );

  const updatePreferences = useCallback(
    (channel: string, eventTypes: string[]) => {
      subscriptions.current.set(channel, { eventTypes });
      sendRaw({ type: "update_preferences", channel, event_types: eventTypes });
    },
    [sendRaw]
  );

  const send = useCallback((type: string, data: object) => sendRaw({ type, ...data }), [sendRaw]);

  return { isConnected, error, subscribe, updatePreferences, send };
}
