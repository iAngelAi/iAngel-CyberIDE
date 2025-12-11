import { useState, useEffect, useRef, useCallback } from 'react';

// Use environment variable or fallback to localhost
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
const RECONNECT_INTERVAL = 3000; // 3 seconds

interface WebSocketOptions<T = unknown> {
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (data: T, event: MessageEvent) => void;
  onError?: (event: Event) => void;
  autoConnect?: boolean;
}

export function useWebSocket<T = unknown>(options: WebSocketOptions<T> = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<T | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  
  // Keep options in a ref to avoid effect dependencies changing
  const optionsRef = useRef(options);
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  const connect = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('[Neural Uplink] Connected to Core');
        optionsRef.current.onOpen?.();
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('[Neural Uplink] Disconnected from Core');
        optionsRef.current.onClose?.();
        
        // Auto reconnect
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('[Neural Uplink] Attempting reconnection...');
          connect();
        }, RECONNECT_INTERVAL);
      };

      ws.onerror = (event: Event) => {
        console.error('[Neural Uplink] Connection Error:', event);
        optionsRef.current.onError?.(event);
      };

      ws.onmessage = (event) => {
        // Fail-safe: If we receive a message, we must be connected
        setIsConnected(true);
        
        try {
          const data = JSON.parse(event.data) as T;
          setLastMessage(data);
          optionsRef.current.onMessage?.(data, event);
        } catch (e) {
          console.warn('[Neural Uplink] Failed to parse message:', event.data);
        }
      };

    } catch (error) {
      console.error('[Neural Uplink] Connection setup failed:', error);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('[Neural Uplink] Cannot send message: Not connected');
    }
  }, []);

  // Initial connection
  useEffect(() => {
    if (options.autoConnect !== false) {
      connect();
    }
    return () => disconnect();
  }, [connect, disconnect, options.autoConnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect
  };
}