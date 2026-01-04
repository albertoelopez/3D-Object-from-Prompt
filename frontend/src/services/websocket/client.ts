import { WSMessage } from '@/types/api';

export type WebSocketMessageHandler = (message: WSMessage) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private handlers: Set<WebSocketMessageHandler> = new Set();
  private jobId: string | null = null;
  private pingInterval: ReturnType<typeof setInterval> | null = null;

  connect(jobId: string): void {
    this.jobId = jobId;
    this.reconnectAttempts = 0;
    this.createConnection();
  }

  private createConnection(): void {
    if (!this.jobId) return;

    const wsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.host}`;
    const url = `${wsUrl}/ws/jobs/${this.jobId}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        this.handlers.forEach((handler) => handler(message));
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.stopPingInterval();

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting (attempt ${this.reconnectAttempts})...`);
        setTimeout(() => this.createConnection(), this.reconnectInterval);
      }
    };
  }

  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping', timestamp: new Date().toISOString() });
    }, 30000);
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  send(message: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  addHandler(handler: WebSocketMessageHandler): void {
    this.handlers.add(handler);
  }

  removeHandler(handler: WebSocketMessageHandler): void {
    this.handlers.delete(handler);
  }

  disconnect(): void {
    this.stopPingInterval();
    this.handlers.clear();
    this.jobId = null;

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export const wsClient = new WebSocketClient();
