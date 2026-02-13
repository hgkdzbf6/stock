/** 认证服务 */
import apiClient from './api';
import type { User, TokenResponse } from '@types/api';

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
    if (response.data?.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      apiClient.setToken(response.data.access_token);
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
};
