import api from './api';
import type { Exam } from '../types';

export const examsService = {
  async list(): Promise<Exam[]> {
    const { data } = await api.get<Exam[]>('/exams');
    return data;
  },

  async create(exam: { subject_id: number; name: string; exam_date: string }): Promise<Exam> {
    const { data } = await api.post<Exam>('/exams', exam);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/exams/${id}`);
  },
};
