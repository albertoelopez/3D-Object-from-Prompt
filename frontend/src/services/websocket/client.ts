import { WSMessage } from '@/types/api';
import { getJob } from '@/services/api/generation';

export type WebSocketMessageHandler = (message: WSMessage) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectInterval = 2000;
  private handlers: Set<WebSocketMessageHandler> = new Set();
  private jobId: string | null = null;
  private pingInterval: ReturnType<typeof setInterval> | null = null;
  private pollingInterval: ReturnType<typeof setInterval> | null = null;
  private usePolling = false;
  private isJobComplete = false;

  connect(jobId: string): void {
    this.jobId = jobId;
    this.reconnectAttempts = 0;
    this.usePolling = false;
    this.isJobComplete = false;
    this.createConnection();
  }

  private createConnection(): void {
    if (!this.jobId || this.isJobComplete) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`;
    const url = `${wsUrl}/ws/jobs/${this.jobId}`;

    console.log('Connecting to WebSocket:', url);
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected successfully');
      this.reconnectAttempts = 0;
      this.stopPolling();
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        if (message.type === 'completion' || message.type === 'error') {
          this.isJobComplete = true;
        }
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

      if (this.isJobComplete) {
        return;
      }

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting (attempt ${this.reconnectAttempts})...`);
        setTimeout(() => this.createConnection(), this.reconnectInterval);
      } else if (!this.usePolling) {
        console.log('WebSocket failed, falling back to polling');
        this.startPolling();
      }
    };
  }

  private startPolling(): void {
    if (this.pollingInterval || !this.jobId || this.isJobComplete) return;

    this.usePolling = true;
    console.log('Starting polling fallback for job:', this.jobId);

    const poll = async () => {
      if (!this.jobId || this.isJobComplete) {
        this.stopPolling();
        return;
      }

      try {
        const job = await getJob(this.jobId);

        const timestamp = new Date().toISOString();

        if (job.status === 'processing' || job.status === 'queued') {
          const progressMessage: WSMessage = {
            type: 'progress_update',
            job_id: this.jobId,
            timestamp,
            progress: job.progress,
            stage: job.stage ?? undefined,
            stage_progress: job.stage_progress,
          };
          this.handlers.forEach((handler) => handler(progressMessage));
        } else if (job.status === 'completed' && job.result) {
          this.isJobComplete = true;
          const completionMessage: WSMessage = {
            type: 'completion',
            job_id: this.jobId,
            timestamp,
            result: job.result,
          };
          this.handlers.forEach((handler) => handler(completionMessage));
          this.stopPolling();
        } else if (job.status === 'failed') {
          this.isJobComplete = true;
          const errorMessage: WSMessage = {
            type: 'error',
            job_id: this.jobId,
            timestamp,
            error: job.error || { code: 'ERROR', message: 'Job failed', recoverable: false },
          };
          this.handlers.forEach((handler) => handler(errorMessage));
          this.stopPolling();
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    poll();
    this.pollingInterval = setInterval(poll, 2000);
  }

  private stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
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
    this.stopPolling();
    this.handlers.clear();
    this.jobId = null;
    this.isJobComplete = true;

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
