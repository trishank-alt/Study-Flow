import api from './api';
import type { Topic } from '../types';

export const topicsService = {
  async listBySubject(subjectId: number): Promise<Topic[]> {
    const { data } = await api.get<Topic[]>(`/subjects/${subjectId}/topics`);
    return data;
  },

  async create(subjectId: number, topic: { title: string; difficulty: string; estimated_hours: number }): Promise<Topic> {
    const { data } = await api.post<Topic>(`/subjects/${subjectId}/topics`, topic);
    return data;
  },

  async update(topicId: number, updates: Partial<Topic>): Promise<Topic> {
    const { data } = await api.patch<Topic>(`/topics/${topicId}`, updates);
    return data;
  },

  async remove(topicId: number): Promise<void> {
    await api.delete(`/topics/${topicId}`);
  },
};
