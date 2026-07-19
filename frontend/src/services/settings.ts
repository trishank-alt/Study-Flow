import api from './api';
import type { UserSettings } from '../types';

export const settingsService = {
  async get(): Promise<UserSettings> {
    const { data } = await api.get<UserSettings>('/settings');
    return data;
  },

  async update(settings: Partial<UserSettings>): Promise<UserSettings> {
    const { data } = await api.put<UserSettings>('/settings', settings);
    return data;
  },
};
