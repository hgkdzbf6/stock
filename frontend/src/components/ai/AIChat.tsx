/**AI聊天组件*/
import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { chatStream, QUICK_QUESTIONS } from '@/services/ai';
import type { ChatRequest } from '@/services/ai';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AIChatProps {
  context?: Record<string, any>;
  onAnalyze?: (type: string) => void;
}

export const AIChat: React.FC<AIChatProps> = ({ context, onAnalyze }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '您好！我是您的AI量化投资顾问。我可以帮您分析市场行情、评估持仓风险、优化交易策略。请问有什么可以帮助您的？',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setIsStreaming(true);

    // 创建AI消息占位符
    const aiMessageId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      {
        id: aiMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      },
    ]);

    try {
      let fullContent = '';
      
      await chatStream(
        {
          question: userMessage.content,
          context,
          stream: true,
        },
        (chunk) => {
          fullContent += chunk;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId
                ? { ...msg, content: fullContent }
                : msg
            )
          );
        },
        () => {
          setIsLoading(false);
          setIsStreaming(false);
        },
        (error) => {
          console.error('Chat error:', error);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId
                ? {
                    ...msg,
                    content: `抱歉，发生了错误：${error.message}`,
                  }
                : msg
            )
          );
          setIsLoading(false);
          setIsStreaming(false);
        }
      );
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessageId
            ? {
                ...msg,
                content: '抱歉，发生了错误，请稍后再试。',
              }
            : msg
        )
      );
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  // 按Enter发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 点击快速问题
  const handleQuickQuestion = (question: string) => {
    setInput(question);
    inputRef.current?.focus();
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          AI 量化顾问
        </CardTitle>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col overflow-hidden p-0">
        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                <div
                  className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-400'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                  <User className="h-4 w-4 text-gray-600" />
                </div>
              )}
            </div>
          ))}

          {isStreaming && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                <Loader2 className="h-4 w-4 text-white animate-spin" />
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.1s' }}
                  />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 快速问题 */}
        {messages.length <= 1 && (
          <div className="px-4 py-2 border-t">
            <div className="text-xs text-gray-500 mb-2">快速提问：</div>
            <div className="flex flex-wrap gap-2">
              {QUICK_QUESTIONS.slice(0, 4).map((q) => (
                <Button
                  key={q.id}
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuickQuestion(q.question)}
                  className="text-xs"
                >
                  {q.question}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* 输入框 */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的问题..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              size="icon"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <div className="text-xs text-gray-400 mt-2">
            按 Enter 发送，Shift + Enter 换行
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AIChat;