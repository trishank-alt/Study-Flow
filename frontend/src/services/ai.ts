import api from './api';
import type {
  ExplainResponse,
  QuizResponse,
  ChatHistoryItem,
  ChatResponse,
  ScheduleReviewResponse,
} from '../types';

export const aiService = {
  async explain(topicId: number): Promise<ExplainResponse> {
    const { data } = await api.post<ExplainResponse>('/ai/explain', { topic_id: topicId });
    return data;
  },

  async generateQuiz(topicId: number): Promise<QuizResponse> {
    const { data } = await api.post<QuizResponse>('/ai/quiz', { topic_id: topicId });
    return data;
  },

  async chat(messages: ChatHistoryItem[]): Promise<ChatResponse> {
    const { data } = await api.post<ChatResponse>('/ai/chat', { messages });
    return data;
  },

  async reviewSchedule(): Promise<ScheduleReviewResponse> {
    const { data } = await api.post<ScheduleReviewResponse>('/ai/review-schedule');
    return data;
  },
};
