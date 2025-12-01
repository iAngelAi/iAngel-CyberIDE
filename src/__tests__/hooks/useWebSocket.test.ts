/**
 * Test Suite: useWebSocket Hook
 *
 * PURPOSE: Test WebSocket connection lifecycle and message handling
 * RULE 1 COMPLIANCE: All mock messages pass Zod validation
 * RULE 3 COMPLIANCE: Disconnect/reconnect simulation with limbo states
 *
 * Tests cover:
 * - Connection lifecycle (connecting → connected → disconnected)
 * - Zod validation blocks invalid messages
 * - Exponential backoff reconnection
 * - WebSocket close event (code 1006) triggers reconnection
 * - No errors when sending during disconnected state
 * - Max reconnection attempts respected
 * - Manual disconnect prevents auto-reconnect
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useWebSocket, type WebSocketStatus } from '../../hooks/useWebSocket';
import {
  createMockWebSocketMessage_NeuralStatus,
  createMockWebSocketMessage_FileChange,
  invalidMocks,
} from '../helpers/mockData';

/**
 * Helper to wait for React effects to be applied
 * This ensures WebSocket event handlers are attached before we simulate events
 */
async function flushEffects() {
  await act(async () => {
    await new Promise(resolve => setTimeout(resolve, 0));
  });
}

// Mock WebSocket that we can control
class ControlledMockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState: number = ControlledMockWebSocket.CONNECTING;
  url: string;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Store instance for test control
    (global as any).__lastWebSocket = this;
  }

  send(data: string): void {
    if (this.readyState !== ControlledMockWebSocket.OPEN) {
      console.warn('[MockWebSocket] Cannot send - not connected');
    }
  }

  close(code?: number, reason?: string): void {
    this.readyState = ControlledMockWebSocket.CLOSED;
    if (this.onclose) {
      const closeEvent = new CloseEvent('close', {
        code: code || 1000,
        reason: reason || '',
      });
      this.onclose(closeEvent);
    }
  }

  // Test helper: simulate connection opening
  simulateOpen(): void {
    this.readyState = ControlledMockWebSocket.OPEN;
    if (this.onopen) {
      this.onopen(new Event('open'));
    }
  }

  // Test helper: simulate receiving message
  simulateMessage(data: any): void {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }));
    }
  }

  // Test helper: simulate error
  simulateError(): void {
    if (this.onerror) {
      this.onerror(new Event('error'));
    }
  }
}

describe('useWebSocket: Connection Lifecycle', () => {
  beforeEach(() => {
    global.WebSocket = ControlledMockWebSocket as any;
    (global as any).__lastWebSocket = null;
  });

  afterEach(() => {
    // Clean up any WebSocket instances
    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    if (ws && ws.readyState !== ControlledMockWebSocket.CLOSED) {
      ws.close();
    }
  });

  it('should start in disconnected state with autoConnect=false', () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', {}, { autoConnect: false })
    );

    expect(result.current.status).toBe('disconnected');
    expect(result.current.isConnected).toBe(false);
  });

  it('should transition from connecting to connected', async () => {
    const onConnect = vi.fn();

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { onConnect }, { autoConnect: true })
    );

    // Wait for all effects to settle and get the final WebSocket instance
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Get the mock WebSocket instance (after StrictMode has settled)
    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    expect(ws).toBeTruthy();
    expect(result.current.status).toBe('connecting');

    // Simulate connection opening - wrap in act to handle state updates
    await act(async () => {
      ws.simulateOpen();
    });

    // Status should now be connected
    expect(result.current.status).toBe('connected');
    expect(result.current.isConnected).toBe(true);
    expect(onConnect).toHaveBeenCalledTimes(1);
  });

  it('should handle error state', async () => {
    const onError = vi.fn();

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { onError }, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();

    act(() => {
      ws.simulateError();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('error');
    });

    expect(onError).toHaveBeenCalled();
  });

  it('should handle disconnection', async () => {
    const onDisconnect = vi.fn();

    const { result } = renderHook(() =>
      useWebSocket(
        'ws://localhost:8000/ws',
        { onDisconnect },
        { autoConnect: true, reconnect: false }
      )
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();

    // Connect first
    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Disconnect
    act(() => {
      ws.close(1000, 'Normal closure');
    });

    await waitFor(() => {
      expect(result.current.status).toBe('disconnected');
    });

    expect(onDisconnect).toHaveBeenCalledTimes(1);
  });
});

describe('useWebSocket: Message Handling (RULE 1)', () => {
  beforeEach(() => {
    global.WebSocket = ControlledMockWebSocket as any;
    (global as any).__lastWebSocket = null;
  });

  afterEach(() => {
    // Clean up any WebSocket instances
    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    if (ws && ws.readyState !== ControlledMockWebSocket.CLOSED) {
      ws.close();
    }
  });

  it('should receive and validate valid messages', async () => {
    const onMessage = vi.fn();
    const validMessage = createMockWebSocketMessage_NeuralStatus();

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { onMessage }, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Send valid message
    act(() => {
      ws.simulateMessage(validMessage);
    });

    await waitFor(() => {
      expect(onMessage).toHaveBeenCalledTimes(1);
    });

    expect(onMessage).toHaveBeenCalledWith(validMessage);
    expect(result.current.lastMessage).toEqual(validMessage);
  });

  it('should block invalid messages (RULE 1)', async () => {
    const onMessage = vi.fn();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { onMessage }, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Send invalid message
    act(() => {
      ws.simulateMessage(invalidMocks.invalidIllumination);
    });

    // Wait a bit to ensure no message is processed
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100));
    });

    // Message should be blocked
    expect(onMessage).not.toHaveBeenCalled();
    expect(result.current.lastMessage).toBeNull();
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[WebSocket] Blocked invalid message'),
      expect.anything()
    );

    consoleSpy.mockRestore();
  });

  it('should block message with missing fields (RULE 1)', async () => {
    const onMessage = vi.fn();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { onMessage }, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Send message with missing fields
    act(() => {
      ws.simulateMessage({ type: 'neural_status' }); // Missing 'data' and 'timestamp'
    });

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100));
    });

    expect(onMessage).not.toHaveBeenCalled();
    expect(consoleSpy).toHaveBeenCalled();

    consoleSpy.mockRestore();
  });

  it('should handle multiple valid messages in sequence', async () => {
    const onMessage = vi.fn();
    const message1 = createMockWebSocketMessage_NeuralStatus();
    const message2 = createMockWebSocketMessage_FileChange();

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', { onMessage }, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Send first message
    act(() => {
      ws.simulateMessage(message1);
    });

    await waitFor(() => {
      expect(onMessage).toHaveBeenCalledTimes(1);
    });

    // Send second message
    act(() => {
      ws.simulateMessage(message2);
    });

    await waitFor(() => {
      expect(onMessage).toHaveBeenCalledTimes(2);
    });

    expect(result.current.lastMessage).toEqual(message2);
  });
});

describe('useWebSocket: Reconnection Logic (RULE 3)', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    global.WebSocket = ControlledMockWebSocket as any;
    (global as any).__lastWebSocket = null;
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
    // Clean up any WebSocket instances
    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    if (ws && ws.readyState !== ControlledMockWebSocket.CLOSED) {
      ws.close();
    }
  });

  it('should trigger reconnection after disconnect (RULE 3)', async () => {
    const { result } = renderHook(() =>
      useWebSocket(
        'ws://localhost:8000/ws',
        {},
        { autoConnect: true, reconnect: true, reconnectInterval: 1000 }
      )
    );

    const ws1 = (global as any).__lastWebSocket as ControlledMockWebSocket;

    // Connect
    act(() => {
      ws1.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Disconnect (simulate abnormal closure - code 1006)
    act(() => {
      ws1.close(1006, 'Abnormal closure');
    });

    await waitFor(() => {
      expect(result.current.status).toBe('disconnected');
    });

    // Fast-forward to trigger reconnection
    act(() => {
      vi.advanceTimersByTime(1000);
    });

    // Should attempt reconnection
    await waitFor(() => {
      expect(result.current.status).toBe('connecting');
    });

    const ws2 = (global as any).__lastWebSocket as ControlledMockWebSocket;
    expect(ws2).not.toBe(ws1); // New WebSocket instance
  });

  it('should use exponential backoff for reconnection attempts', async () => {
    const { result } = renderHook(() =>
      useWebSocket(
        'ws://localhost:8000/ws',
        {},
        { autoConnect: true, reconnect: true, reconnectInterval: 1000, maxReconnectAttempts: 5 }
      )
    );

    const ws1 = (global as any).__lastWebSocket as ControlledMockWebSocket;

    // Connect and disconnect
    act(() => {
      ws1.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    act(() => {
      ws1.close(1006);
    });

    // First reconnect: 1s
    act(() => {
      vi.advanceTimersByTime(1000);
    });

    const ws2 = (global as any).__lastWebSocket as ControlledMockWebSocket;
    expect(ws2).not.toBe(ws1);

    // Fail again
    act(() => {
      ws2.close(1006);
    });

    // Second reconnect: 2s (exponential backoff)
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    const ws3 = (global as any).__lastWebSocket as ControlledMockWebSocket;
    expect(ws3).not.toBe(ws2);

    // Fail again
    act(() => {
      ws3.close(1006);
    });

    // Third reconnect: 4s
    act(() => {
      vi.advanceTimersByTime(4000);
    });

    const ws4 = (global as any).__lastWebSocket as ControlledMockWebSocket;
    expect(ws4).not.toBe(ws3);
  });

  it('should respect max reconnection attempts', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { result } = renderHook(() =>
      useWebSocket(
        'ws://localhost:8000/ws',
        {},
        { autoConnect: true, reconnect: true, reconnectInterval: 100, maxReconnectAttempts: 2 }
      )
    );

    const ws1 = (global as any).__lastWebSocket as ControlledMockWebSocket;

    act(() => {
      ws1.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Disconnect and fail twice
    for (let i = 0; i < 2; i++) {
      act(() => {
        const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
        ws.close(1006);
      });

      await waitFor(() => {
        expect(result.current.status).toBe('disconnected');
      });

      act(() => {
        vi.advanceTimersByTime(100 * Math.pow(2, i));
      });
    }

    // One more disconnect to exceed max attempts
    act(() => {
      const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
      ws.close(1006);
    });

    await waitFor(() => {
      expect(result.current.status).toBe('disconnected');
    });

    // Advance time - should NOT reconnect
    act(() => {
      vi.advanceTimersByTime(10000);
    });

    expect(result.current.status).toBe('disconnected');
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[WebSocket] Max reconnection attempts reached')
    );

    consoleSpy.mockRestore();
  });

  it('should NOT auto-reconnect after manual disconnect (RULE 3)', async () => {
    const { result } = renderHook(() =>
      useWebSocket(
        'ws://localhost:8000/ws',
        {},
        { autoConnect: true, reconnect: true, reconnectInterval: 1000 }
      )
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Manual disconnect
    act(() => {
      result.current.disconnect();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('disconnected');
    });

    // Advance time - should NOT reconnect
    act(() => {
      vi.advanceTimersByTime(10000);
    });

    expect(result.current.status).toBe('disconnected');
  });

  it('should reset reconnection attempts after successful connection', async () => {
    const { result } = renderHook(() =>
      useWebSocket(
        'ws://localhost:8000/ws',
        {},
        { autoConnect: true, reconnect: true, reconnectInterval: 100, maxReconnectAttempts: 10 }
      )
    );

    const ws1 = (global as any).__lastWebSocket as ControlledMockWebSocket;

    // First connection
    act(() => {
      ws1.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Disconnect
    act(() => {
      ws1.close(1006);
    });

    // Reconnect
    act(() => {
      vi.advanceTimersByTime(100);
    });

    const ws2 = (global as any).__lastWebSocket as ControlledMockWebSocket;

    // Successful reconnection
    act(() => {
      ws2.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Disconnect again
    act(() => {
      ws2.close(1006);
    });

    // Should use initial delay again (100ms, not 200ms)
    act(() => {
      vi.advanceTimersByTime(100);
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connecting');
    });
  });
});

describe('useWebSocket: Send Operations (RULE 3)', () => {
  beforeEach(() => {
    global.WebSocket = ControlledMockWebSocket as any;
    (global as any).__lastWebSocket = null;
  });

  afterEach(() => {
    // Clean up any WebSocket instances
    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    if (ws && ws.readyState !== ControlledMockWebSocket.CLOSED) {
      ws.close();
    }
  });

  it('should send message when connected', async () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', {}, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();
    const sendSpy = vi.spyOn(ws, 'send');

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    // Send message
    act(() => {
      result.current.send({ command: 'test' });
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({ command: 'test' }));
  });

  it('should NOT throw error when sending during disconnected state (RULE 3)', async () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', {}, { autoConnect: false })
    );

    expect(result.current.status).toBe('disconnected');

    // Send while disconnected - should not throw
    expect(() => {
      act(() => {
        result.current.send({ command: 'test' });
      });
    }).not.toThrow();

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[WebSocket] Cannot send - not connected')
    );

    consoleSpy.mockRestore();
  });

  it('should provide requestTestRun helper', async () => {
    const { result} = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', {}, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();
    const sendSpy = vi.spyOn(ws, 'send');

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    act(() => {
      result.current.requestTestRun();
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({ command: 'run_tests' }));
  });

  it('should provide requestStatusRefresh helper', async () => {
    const { result } = renderHook(() =>
      useWebSocket('ws://localhost:8000/ws', {}, { autoConnect: true })
    );

    const ws = (global as any).__lastWebSocket as ControlledMockWebSocket;
    await flushEffects();
    const sendSpy = vi.spyOn(ws, 'send');

    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('connected');
    });

    act(() => {
      result.current.requestStatusRefresh();
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({ command: 'refresh_status' }));
  });
});
