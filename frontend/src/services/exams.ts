import api from './api';
import type { Exam, ExamPaperAnalysisResponse } from '../types';

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

  async uploadPaper(examId: number, file: File): Promise<{ message: string; resource_id: number; status: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post<{ message: string; resource_id: number; status: string }>(
      `/exams/${examId}/paper`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return data;
  },

  async getAnalysis(examId: number): Promise<ExamPaperAnalysisResponse> {
    const { data } = await api.get<ExamPaperAnalysisResponse>(`/exams/${examId}/analysis`);
    return data;
  },

  async deleteAnalysis(examId: number): Promise<void> {
    await api.delete(`/exams/${examId}/analysis`);
  },
};
