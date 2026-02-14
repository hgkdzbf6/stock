/** WebSocket服务 */
import { message } from 'antd';

export interface QuoteData {
  code: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

export interface WSMessage {
  type: string;
  code?: string;
  data?: any;
  timestamp?: string;
  success?: boolean;
  message?: string;
  codes?: string[];
  token?: string; // 认证token
}

export type MessageHandler = (message: WSMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectInterval: number = 3000;
  private isConnected: boolean = false;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private heartbeatInterval: NodeJS.Timeout | null = null;

  constructor() {
    // 从环境变量获取WebSocket URL
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    this.url = wsUrl;
  }

  /**
   * 连接WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket连接成功');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          
          // 发送认证消息
          this.send({
            type: 'auth',
            token: localStorage.getItem('access_token') || ''
          });
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data: WSMessage = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('解析WebSocket消息失败:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket连接关闭:', event);
          this.isConnected = false;
          this.stopHeartbeat();
          
          // 尝试重连
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => {
              this.connect().catch(err => {
                console.error('重连失败:', err);
              });
            }, this.reconnectInterval);
          } else {
            message.error('WebSocket连接失败，请刷新页面重试');
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket错误:', error);
          this.isConnected = false;
          reject(error);
        };
      } catch (error) {
        console.error('创建WebSocket连接失败:', error);
        reject(error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.isConnected = false;
    this.messageHandlers.clear();
  }

  /**
   * 发送消息
   */
  send(message: WSMessage): void {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接，无法发送消息');
    }
  }

  /**
   * 订阅股票行情
   */
  subscribe(codes: string[]): void {
    this.send({
      type: 'subscribe',
      codes: codes
    });
  }

  /**
   * 取消订阅
   */
  unsubscribe(codes: string[]): void {
    this.send({
      type: 'unsubscribe',
      codes: codes
    });
  }

  /**
   * 注册消息处理器
   */
  on(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    
    this.messageHandlers.get(type)!.add(handler);
    
    // 返回取消订阅的函数
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        handlers.delete(handler);
      }
    };
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WSMessage): void {
    const type = message.type;
    
    if (type) {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error('消息处理器执行失败:', error);
          }
        });
      }
    }
  }

  /**
   * 开始心跳
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000); // 每30秒发送一次心跳
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * 检查连接状态
   */
  checkConnection(): boolean {
    return this.isConnected && this.ws !== null;
  }
}

// 导出单例
export const wsService = new WebSocketService();