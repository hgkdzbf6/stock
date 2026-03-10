/** 认证服务 */
import apiClient from './api';
import type { User, TokenResponse } from '../types/api';

export const authService = {
  /** 用户登录 */
  async login(username: string, password: string) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post<TokenResponse>(
      '/auth/login',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    // 保存token
    if (response?.access_token) {
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      apiClient.setToken(response.access_token);
    }

    return response;
  },

  /** 用户注册 */
  async register(data: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
    phone?: string;
  }) {
    return apiClient.post('/auth/register', data);
  },

  /** 获取当前用户信息 */
  async getCurrentUser() {
    return apiClient.get<User>('/auth/me');
  },

  /** 用户登出 */
  async logout() {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      apiClient.clearToken();
    }
  },

  /** 检查是否已登录 */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  /** 获取当前用户信息（从localStorage） */
  getCurrentUserFromStorage(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /** 获取token */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  /** 更新用户信息 */
  async updateProfile(data: {
    full_name?: string;
    phone?: string;
    email?: string;
  }) {
    return apiClient.put('/auth/profile', data);
  },

  /** 修改密码 */
  async changePassword(data: {
    old_password: string;
    new_password: string;
  }) {
    return apiClient.post('/auth/change-password', data);
  },

  /** 获取认证头 */
  getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  },
};
