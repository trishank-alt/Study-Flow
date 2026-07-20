export interface User {
  id: number;
  email: string;
  created_at?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface Subject {
  id: number;
  user_id: number;
  name: string;
  created_at?: string;
  topic_count?: number;
  completion?: number;
}

export interface Topic {
  id: number;
  subject_id: number;
  title: string;
  difficulty: 'easy' | 'medium' | 'hard';
  estimated_hours: number;
  completion_percentage: number;
  created_at?: string;
}

export interface Exam {
  id: number;
  subject_id: number;
  name: string;
  exam_date: string;
  subject_name?: string;
  created_at?: string;
  days_remaining?: number;
}

export interface ScheduleItem {
  id: number;
  topic_id: number;
  scheduled_date: string;
  planned_minutes: number;
  completed: boolean;
  topic_title?: string;
  subject_name?: string;
  created_at?: string;
}

export interface StudySession {
  id: number;
  topic_id: number;
  duration_minutes: number;
  completed_at?: string;
  topic_title?: string;
  subject_name?: string;
}

export interface DashboardStats {
  total_hours: number;
  weekly_hours: number;
  study_streak: number;
  total_subjects: number;
  total_topics: number;
  overall_completion: number;
  upcoming_exams: number;
  recent_sessions: StudySession[];
}

export interface UserSettings {
  user_id: number;
  llm_provider: string;
  model_name: string;
  ollama_url: string;
  created_at?: string;
  updated_at?: string;
}

export interface Resource {
  id: number;
  user_id: number;
  subject_id?: number;
  topic_id?: number;
  title: string;
  filename: string;
  content_type: string;
  summary?: string;
  embedding_status?: string;
  processed_at?: string;
  created_at?: string;
}

export interface ExplainResponse {
  title: string;
  overview: string;
  key_points: string[];
  examples: string[];
  common_mistakes: string[];
}

export interface QuizQuestion {
  question: string;
  options: string[];
  answer_index: number;
  explanation: string;
}

export interface QuizResponse {
  questions: QuizQuestion[];
}

export interface ChatHistoryItem {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatResponse {
  reply: string;
}

export interface ScheduleReviewResponse {
  overall_status: string;
  insights: string[];
  warnings: string[];
  suggestions: string[];
}

export interface ExamTopicAnalysis {
  title: string;
  frequency: string;
  recommended_hours: number;
  insight: string;
}

export interface ExamPaperAnalysisResult {
  summary: string;
  difficulty: string;
  topics: ExamTopicAnalysis[];
  important_concepts: string[];
  commonly_repeated: string[];
  missing_topics: string[];
  study_strategy: string;
  confidence: number;
}

export interface ExamPaperAnalysisResponse {
  status: string;
  result: ExamPaperAnalysisResult | null;
  error: string | null;
}
