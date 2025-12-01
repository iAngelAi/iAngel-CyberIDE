import { useEffect, useLayoutEffect, useRef, useState, useCallback } from 'react';
import type { BackendWebSocketMessage } from '../types/backend';
import { BackendWebSocketMessageSchema } from '../schemas/websocketValidation';

/**
 * WebSocket connection status
 */
export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

/**
 * WebSocket event handlers
 */
export interface WebSocketHandlers {
  onMessage?: (message: BackendWebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

/**
 * Custom hook for managing WebSocket connection to Neural Core backend
 *
 * Features:
 * - Auto-reconnection with exponential backoff
 * - Type-safe message handling
 * - Connection status tracking
 * - Manual send capabilities
 *
 * @param url - WebSocket URL (e.g., 'ws://localhost:8000/ws')
 * @param handlers - Event handlers for WebSocket events
 * @param options - Configuration options
 */
export function useWebSocket(
  url: string,
  handlers: WebSocketHandlers = {},
  options: {
    autoConnect?: boolean;
    reconnect?: boolean;
    reconnectInterval?: number;
    maxReconnectAttempts?: number;
  } = {}
) {
  const {
    autoConnect = true,
    reconnect = true,
    reconnectInterval = 1000,
    maxReconnectAttempts = 10,
  } = options;

  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<BackendWebSocketMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const intentionalCloseRef = useRef(false);

  // Store handlers and options in refs to avoid stale closures
  const handlersRef = useRef(handlers);
  const reconnectRef = useRef(reconnect);
  const maxReconnectAttemptsRef = useRef(maxReconnectAttempts);
  const reconnectIntervalRef = useRef(reconnectInterval);

  // Update refs when values change
  // Use useLayoutEffect to ensure refs are updated synchronously before paint
  useLayoutEffect(() => {
    handlersRef.current = handlers;
    reconnectRef.current = reconnect;
    maxReconnectAttemptsRef.current = maxReconnectAttempts;
    reconnectIntervalRef.current = reconnectInterval;
  }, [handlers, reconnect, maxReconnectAttempts, reconnectInterval]);

  // Create stable refs for connect/disconnect functions
  const connectRef = useRef<(() => void) | undefined>(undefined);
  const disconnectRef = useRef<(() => void) | undefined>(undefined);

  /**
   * Calculate reconnection delay with exponential backoff
   * Stored in ref for stable access from reconnection logic
   */
  const getReconnectDelay = () => {
    const attempt = reconnectAttemptsRef.current;
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, max 30s
    return Math.min(reconnectIntervalRef.current * Math.pow(2, attempt), 30000);
  };

  /**
   * Disconnect from WebSocket server
   */
  disconnectRef.current = () => {
    console.log('[WebSocket] Disconnecting...');
    intentionalCloseRef.current = true;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('disconnected');
  };

  /**
   * Connect to WebSocket server
   */
  connectRef.current = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.warn('[WebSocket] Already connected');
      return;
    }

    console.log(`[WebSocket] Connecting to ${url}...`);
    setStatus('connecting');

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        setStatus('connected');
        reconnectAttemptsRef.current = 0;
        handlersRef.current.onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          // 1. Parse raw JSON
          const rawData = JSON.parse(event.data);

          // 2. Validate with Zod (Runtime type checking - defense against malformed backend data)
          const result = BackendWebSocketMessageSchema.safeParse(rawData);

          if (!result.success) {
            console.error('[WebSocket] Blocked invalid message:', result.error.format());
            // Message doesn't match expected schema - discard it
            return;
          }

          // 3. Use the validated data (TypeScript knows this is 100% correct)
          const message = result.data;
          setLastMessage(message);
          handlersRef.current.onMessage?.(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        setStatus('error');
        handlersRef.current.onError?.(error);
      };

      ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected', event.code, event.reason);
        setStatus('disconnected');
        wsRef.current = null;
        handlersRef.current.onDisconnect?.();

        // Auto-reconnect if not intentional close
        // Use ref values to ensure we have latest options
        if (!intentionalCloseRef.current && reconnectRef.current && reconnectAttemptsRef.current < maxReconnectAttemptsRef.current) {
          const delay = getReconnectDelay();
          console.log(`[WebSocket] Reconnecting in ${delay}ms... (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttemptsRef.current})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connectRef.current?.();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttemptsRef.current) {
          console.error('[WebSocket] Max reconnection attempts reached');
        }
      };
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
      setStatus('error');
    }
  };

  /**
   * Public API: Connect function
   */
  const connect = useCallback(() => {
    connectRef.current?.();
  }, []);

  /**
   * Public API: Disconnect function
   */
  const disconnect = useCallback(() => {
    disconnectRef.current?.();
  }, []);

  /**
   * Send a message to the server
   */
  const send = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('[WebSocket] Cannot send - not connected');
    }
  }, []);

  /**
   * Request test run from backend
   */
  const requestTestRun = useCallback(() => {
    send({ command: 'run_tests' });
  }, [send]);

  /**
   * Request status refresh from backend
   */
  const requestStatusRefresh = useCallback(() => {
    send({ command: 'refresh_status' });
  }, [send]);

  // Auto-connect on mount if enabled
  // CRITICAL FIX: Only depend on autoConnect and url for connection lifecycle
  // The connect/disconnect logic is in refs, so we don't need them as dependencies
  useEffect(() => {
    // Reset intentional close flag when effect runs
    intentionalCloseRef.current = false;

    if (autoConnect) {
      connectRef.current?.();
    }

    // Cleanup on unmount
    return () => {
      disconnectRef.current?.();
    };
    // Only re-run if autoConnect or url changes
    // Changes to reconnect/maxReconnectAttempts/reconnectInterval don't require reconnection
  }, [autoConnect, url]);

  return {
    status,
    lastMessage,
    connect,
    disconnect,
    send,
    requestTestRun,
    requestStatusRefresh,
    isConnected: status === 'connected',
  };
}
