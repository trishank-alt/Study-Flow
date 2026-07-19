import api from './api';
import type { User, AuthToken } from '../types';

export const authService = {
  async register(email: string, password: string): Promise<User> {
    const { data } = await api.post<User>('/auth/register', { email, password });
    return data;
  },

  async login(email: string, password: string): Promise<AuthToken> {
    const { data } = await api.post<AuthToken>('/auth/login', { email, password });
    return data;
  },

  async getMe(): Promise<User> {
    const { data } = await api.get<User>('/auth/me');
    return data;
  },
};
