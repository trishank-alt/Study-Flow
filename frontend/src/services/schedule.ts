import api from './api';
import type { ScheduleItem, DashboardStats, StudySession } from '../types';

export const scheduleService = {
  async list(): Promise<ScheduleItem[]> {
    const { data } = await api.get<ScheduleItem[]>('/schedule');
    return data;
  },

  async generate(dailyMinutes: number = 120, startDate?: string): Promise<ScheduleItem[]> {
    const payload: Record<string, unknown> = { daily_study_minutes: dailyMinutes };
    if (startDate) payload.start_date = startDate;
    const { data } = await api.post<ScheduleItem[]>('/schedule/generate', payload);
    return data;
  },

  async markComplete(id: number, completed: boolean): Promise<ScheduleItem> {
    const { data } = await api.patch<ScheduleItem>(`/schedule/${id}`, { completed });
    return data;
  },
};

export const progressService = {
  async logSession(topicId: number, durationMinutes: number): Promise<StudySession> {
    const { data } = await api.post<StudySession>('/progress/sessions', {
      topic_id: topicId,
      duration_minutes: durationMinutes,
    });
    return data;
  },

  async getDashboard(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>('/progress/dashboard');
    return data;
  },
};
