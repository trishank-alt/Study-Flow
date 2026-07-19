import api from './api';
import type { Subject } from '../types';

export const subjectsService = {
  async list(): Promise<Subject[]> {
    const { data } = await api.get<Subject[]>('/subjects');
    return data;
  },

  async create(name: string): Promise<Subject> {
    const { data } = await api.post<Subject>('/subjects', { name });
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/subjects/${id}`);
  },
};
