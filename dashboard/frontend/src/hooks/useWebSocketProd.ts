import { useEffect, useRef, useCallback, useState } from 'react';

export interface WebSocketMessage<T = any> {
  type: string;
  data?: T;
  id?: string;
  timestamp?: number;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  reconnectAttempts: number;
  lastMessageTime: number;
  latency: number;
  error: string | null;
}

class WebSocketManagerProd {
  private socket: WebSocket | null = null;
  private url: string;
  private config: Required<WebSocketConfig>;
  private messageHandlers: Map<string, (msg: WebSocketMessage) => void> = new Map();
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  private heartbeatTimeoutId: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private lastHeartbeatTime = 0;
  private messageQueue: WebSocketMessage[] = [];

  constructor(url: string, config: WebSocketConfig) {
    this.url = url;
    this.config = {
      reconnectInterval: config.reconnectInterval ?? 1000,
      maxReconnectAttempts: config.maxReconnectAttempts ?? 10,
      heartbeatInterval: config.heartbeatInterval ?? 30000,
      debug: config.debug ?? false,
      ...config,
    };
    this.log('✅ WebSocket Manager initialized', { url });
  }

  async connect(): Promise<void> {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.log('Already connected');
      return;
    }

    try {
      this.log('🔗 Connecting to WebSocket', { url: this.url });
      this.socket = new WebSocket(this.url);

      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onerror = this.handleError.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
    } catch (error) {
      this.log('❌ Connection error', { error });
      this.handleError(error as Event);
    }
  }

  disconnect(): void {
    this.log('🔌 Disconnecting');
    this.clearReconnectTimeout();
    this.clearHeartbeat();
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  private handleOpen(): void {
    this.log('✨ Connected');
    this.reconnectAttempts = 0;
    this.lastHeartbeatTime = Date.now();
    this.flushMessageQueue();
    this.startHeartbeat();
    this.emit('__connected__', {});
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data) as WebSocketMessage;
      if (message.type === 'pong') {
        this.lastHeartbeatTime = Date.now();
        return;
      }
      const handler = this.messageHandlers.get(message.type);
      if (handler) handler(message);
      this.emit('__message__', message);
    } catch (error) {
      this.log('⚠️ Message parse error', { error });
    }
  }

  private handleError(event: Event): void {
    this.log('❌ WebSocket error', { error: event });
    this.emit('__error__', { error: 'WebSocket error' });
  }

  private handleClose(): void {
    this.log('🔌 Disconnected');
    this.clearHeartbeat();

    if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
      const delay = this.calculateBackoffDelay();
      this.log('🔄 Reconnecting...', { attempt: this.reconnectAttempts + 1, delay });
      this.reconnectTimeoutId = setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, delay);
      this.emit('__reconnecting__', { attempt: this.reconnectAttempts + 1, delay });
    } else {
      this.log('❌ Max reconnect attempts reached');
      this.emit('__max_reconnects_reached__', {});
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimeoutId = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  }

  private clearHeartbeat(): void {
    if (this.heartbeatTimeoutId) {
      clearInterval(this.heartbeatTimeoutId);
      this.heartbeatTimeoutId = null;
    }
  }

  send(message: WebSocketMessage): boolean {
    if (this.socket?.readyState === WebSocket.OPEN) {
      try {
        this.socket.send(JSON.stringify(message));
        return true;
      } catch (error) {
        this.messageQueue.push(message);
        return false;
      }
    } else {
      this.messageQueue.push(message);
      return false;
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.socket?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift();
      if (message) this.send(message);
    }
  }

  on(type: string, handler: (msg: WebSocketMessage) => void): () => void {
    this.messageHandlers.set(type, handler);
    return () => this.messageHandlers.delete(type);
  }

  private emit(type: string, data: any): void {
    const handler = this.messageHandlers.get(type);
    if (handler) handler({ type, data });
  }

  getState(): WebSocketState {
    return {
      isConnected: this.socket?.readyState === WebSocket.OPEN,
      isConnecting: this.socket?.readyState === WebSocket.CONNECTING,
      reconnectAttempts: this.reconnectAttempts,
      lastMessageTime: this.lastHeartbeatTime,
      latency: Date.now() - this.lastHeartbeatTime,
      error: null,
    };
  }

  private calculateBackoffDelay(): number {
    const baseDelay = this.config.reconnectInterval;
    const exponentialDelay = baseDelay * Math.pow(2, this.reconnectAttempts);
    const maxDelay = 30000;
    const randomJitter = Math.random() * 1000;
    return Math.min(exponentialDelay, maxDelay) + randomJitter;
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
  }

  private log(message: string, data?: any): void {
    if (this.config.debug) {
      console.log(`[WebSocket] ${message}`, data);
    }
  }
}

let globalWebSocketManager: WebSocketManagerProd | null = null;

export const useWebSocketProd = (config: WebSocketConfig) => {
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    reconnectAttempts: 0,
    lastMessageTime: 0,
    latency: 0,
    error: null,
  });

  const managerRef = useRef<WebSocketManagerProd>(null!);

  useEffect(() => {
    if (!managerRef.current) {
      managerRef.current = new WebSocketManagerProd(config.url, config);
      globalWebSocketManager = managerRef.current;
    }
  }, [config.url]);

  useEffect(() => {
    const manager = managerRef.current;
    if (!manager) return;

    manager.connect();

    const unsubConnected = manager.on('__connected__', () => {
      setState(s => ({ ...s, isConnected: true, isConnecting: false, reconnectAttempts: 0 }));
    });

    const unsubReconnecting = manager.on('__reconnecting__', (msg: any) => {
      setState(s => ({ ...s, isConnecting: true, reconnectAttempts: msg.data.attempt }));
    });

    const unsubError = manager.on('__error__', (msg: any) => {
      setState(s => ({ ...s, error: msg.data.error }));
    });

    const stateIntervalId = setInterval(() => {
      const managerState = manager.getState();
      setState(managerState);
    }, 1000);

    return () => {
      clearInterval(stateIntervalId);
      unsubConnected();
      unsubReconnecting();
      unsubError();
    };
  }, []);

  const subscribe = useCallback(
    (type: string, handler: (msg: WebSocketMessage) => void): (() => void) => {
      return managerRef.current.on(type, handler);
    },
    []
  );

  const send = useCallback((message: WebSocketMessage) => {
    return managerRef.current.send(message);
  }, []);

  return {
    ...state,
    subscribe,
    send,
  };
};

export const getWebSocketManagerProd = () => globalWebSocketManager;
