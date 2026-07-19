import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import Modal from '../components/Modal/Modal';
import ProgressBar from '../components/ProgressBar/ProgressBar';
import { topicsService } from '../services/topics';
import { subjectsService } from '../services/subjects';
import { progressService } from '../services/schedule';
import { aiService } from '../services/ai';
import type { Topic, Subject, ExplainResponse, QuizResponse } from '../types';
import './SubjectDetailsPage.css';

export default function SubjectDetailsPage() {
  const { subjectId } = useParams<{ subjectId: string }>();
  const navigate = useNavigate();
  const [subject, setSubject] = useState<Subject | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showLogModal, setShowLogModal] = useState(false);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
  const [logMinutes, setLogMinutes] = useState(30);

  // Add topic form state
  const [newTitle, setNewTitle] = useState('');
  const [newDifficulty, setNewDifficulty] = useState('medium');
  const [newHours, setNewHours] = useState(1);

  // AI Explain State
  const [explainData, setExplainData] = useState<ExplainResponse | null>(null);
  const [showExplainModal, setShowExplainModal] = useState(false);
  const [isExplaining, setIsExplaining] = useState<number | null>(null);

  // AI Quiz State
  const [quizData, setQuizData] = useState<QuizResponse | null>(null);
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState<number | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswerIndex, setSelectedAnswerIndex] = useState<number | null>(null);
  const [quizScore, setQuizScore] = useState(0);

  const id = Number(subjectId);

  const loadData = async () => {
    try {
      const [subjectsData, topicsData] = await Promise.all([
        subjectsService.list(),
        topicsService.listBySubject(id),
      ]);
      const found = subjectsData.find((s) => s.id === id);
      setSubject(found || null);
      setTopics(topicsData);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [subjectId]);

  const handleAddTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    await topicsService.create(id, {
      title: newTitle,
      difficulty: newDifficulty,
      estimated_hours: newHours,
    });
    setNewTitle('');
    setNewDifficulty('medium');
    setNewHours(1);
    setShowAddModal(false);
    loadData();
  };

  const handleUpdateCompletion = async (topicId: number, value: number) => {
    await topicsService.update(topicId, { completion_percentage: value });
    loadData();
  };

  const handleDeleteTopic = async (topicId: number) => {
    if (confirm('Delete this topic?')) {
      await topicsService.remove(topicId);
      loadData();
    }
  };

  const handleLogSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedTopicId) {
      await progressService.logSession(selectedTopicId, logMinutes);
      setShowLogModal(false);
      setSelectedTopicId(null);
      setLogMinutes(30);
      loadData();
    }
  };

  const handleExplain = async (topicId: number) => {
    setIsExplaining(topicId);
    try {
      const data = await aiService.explain(topicId);
      setExplainData(data);
      setShowExplainModal(true);
    } catch (err) {
      console.error(err);
      alert('Failed to fetch AI topic explanation.');
    } finally {
      setIsExplaining(null);
    }
  };

  const handleGenerateQuiz = async (topicId: number) => {
    setIsGeneratingQuiz(topicId);
    try {
      const data = await aiService.generateQuiz(topicId);
      setQuizData(data);
      setCurrentQuestionIndex(0);
      setSelectedAnswerIndex(null);
      setQuizScore(0);
      setShowQuizModal(true);
    } catch (err) {
      console.error(err);
      alert('Failed to generate AI quiz.');
    } finally {
      setIsGeneratingQuiz(null);
    }
  };

  const handleAnswerSelect = (index: number) => {
    if (selectedAnswerIndex !== null || !quizData) return;
    setSelectedAnswerIndex(index);
    const correctIdx = quizData.questions[currentQuestionIndex].answer_index;
    if (index === correctIdx) {
      setQuizScore((prev) => prev + 1);
    }
  };

  const handleNextQuestion = () => {
    setSelectedAnswerIndex(null);
    setCurrentQuestionIndex((prev) => prev + 1);
  };

  if (isLoading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <Navbar title="Subject Details" />
        <main className="main-content">
          <div className="loading-page"><div className="spinner" /></div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <Navbar title={subject?.name || 'Subject'} />
      <main className="main-content">
        <div className="page-header">
          <div>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/subjects')} style={{ marginBottom: '0.5rem' }}>
              ← Back to Subjects
            </button>
            <h1 className="page-title">{subject?.name || 'Subject'}</h1>
            <p className="page-subtitle">{topics.length} topics</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)} id="add-topic-btn">
            + Add Topic
          </button>
        </div>

        {topics.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <h3>No topics yet</h3>
            <p>Add topics to track your study progress</p>
          </div>
        ) : (
          <div className="topics-list stagger-children">
            {topics.map((topic) => (
              <div key={topic.id} className="glass-card topic-card">
                <div className="topic-card-top">
                  <div className="topic-info">
                    <h3 className="topic-title">{topic.title}</h3>
                    <div className="topic-meta">
                      <span className={`badge badge-${topic.difficulty}`}>{topic.difficulty}</span>
                      <span className="topic-hours">{topic.estimated_hours}h estimated</span>
                    </div>
                  </div>
                  <div className="topic-actions">
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => {
                        setSelectedTopicId(topic.id);
                        setShowLogModal(true);
                      }}
                    >
                      📝 Log
                    </button>
                    <button
                      className="btn btn-ghost btn-sm btn-ai-action"
                      onClick={() => handleExplain(topic.id)}
                      disabled={isExplaining !== null}
                    >
                      {isExplaining === topic.id ? '⏳' : '💡 Explain'}
                    </button>
                    <button
                      className="btn btn-ghost btn-sm btn-ai-action"
                      onClick={() => handleGenerateQuiz(topic.id)}
                      disabled={isGeneratingQuiz !== null}
                    >
                      {isGeneratingQuiz === topic.id ? '⏳' : '⚔️ Quiz'}
                    </button>
                    <button
                      className="btn btn-ghost btn-icon btn-sm"
                      onClick={() => handleDeleteTopic(topic.id)}
                      title="Delete topic"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                <div className="topic-progress">
                  <ProgressBar
                    value={topic.completion_percentage}
                    variant={
                      topic.completion_percentage >= 80
                        ? 'success'
                        : topic.completion_percentage >= 40
                          ? 'warm'
                          : 'primary'
                    }
                  />
                  <div className="topic-completion-controls">
                    {[0, 25, 50, 75, 100].map((v) => (
                      <button
                        key={v}
                        className={`btn btn-ghost btn-sm ${topic.completion_percentage === v ? 'active-completion' : ''}`}
                        onClick={() => handleUpdateCompletion(topic.id, v)}
                      >
                        {v}%
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Add Topic Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add Topic">
          <form onSubmit={handleAddTopic}>
            <div className="form-group">
              <label className="form-label" htmlFor="topic-title">Title</label>
              <input
                id="topic-title"
                className="form-input"
                placeholder="e.g. Integration"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="topic-difficulty">Difficulty</label>
              <select
                id="topic-difficulty"
                className="form-select"
                value={newDifficulty}
                onChange={(e) => setNewDifficulty(e.target.value)}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="topic-hours">Estimated Hours</label>
              <input
                id="topic-hours"
                type="number"
                className="form-input"
                min="0.5"
                step="0.5"
                value={newHours}
                onChange={(e) => setNewHours(Number(e.target.value))}
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
              Add Topic
            </button>
          </form>
        </Modal>

        {/* Log Session Modal */}
        <Modal isOpen={showLogModal} onClose={() => setShowLogModal(false)} title="Log Study Session">
          <form onSubmit={handleLogSession}>
            <div className="form-group">
              <label className="form-label" htmlFor="log-minutes">Duration (minutes)</label>
              <input
                id="log-minutes"
                type="number"
                className="form-input"
                min="5"
                step="5"
                value={logMinutes}
                onChange={(e) => setLogMinutes(Number(e.target.value))}
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
              Log Session
            </button>
          </form>
        </Modal>

        {/* AI Explain Modal */}
        <Modal
          isOpen={showExplainModal}
          onClose={() => setShowExplainModal(false)}
          title={explainData?.title || 'Explanation'}
        >
          {explainData && (
            <div className="explain-modal-view">
              <div className="explain-overview glass-inner-card">
                <h4>Overview</h4>
                <p>{explainData.overview}</p>
              </div>

              <div className="explain-section">
                <h4>🔑 Key Concepts</h4>
                <ul className="explain-list">
                  {explainData.key_points.map((pt, i) => (
                    <li key={i}>{pt}</li>
                  ))}
                </ul>
              </div>

              <div className="explain-section">
                <h4>💡 Practical Examples</h4>
                <div className="explain-examples-grid">
                  {explainData.examples.map((ex, i) => (
                    <div key={i} className="explain-example-item glass-inner-card">
                      {ex}
                    </div>
                  ))}
                </div>
              </div>

              <div className="explain-section alert-section">
                <h4>⚠️ Common Misconceptions</h4>
                <ul className="explain-mistakes-list">
                  {explainData.common_mistakes.map((mk, i) => (
                    <li key={i}>{mk}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </Modal>

        {/* AI Quiz Modal */}
        <Modal
          isOpen={showQuizModal}
          onClose={() => setShowQuizModal(false)}
          title="Interactive practice quiz"
        >
          {quizData && (
            <div className="quiz-modal-view">
              {currentQuestionIndex < quizData.questions.length ? (
                <>
                  <div className="quiz-progress-header">
                    <span>Question {currentQuestionIndex + 1} of {quizData.questions.length}</span>
                    <span>Current Score: {quizScore}/{quizData.questions.length}</span>
                  </div>
                  <hr className="divider" />
                  <div className="quiz-question-card">
                    <h3 className="quiz-question-text">
                      {quizData.questions[currentQuestionIndex].question}
                    </h3>
                    <div className="quiz-options-list">
                      {quizData.questions[currentQuestionIndex].options.map((opt, optIdx) => {
                        const isSelected = selectedAnswerIndex === optIdx;
                        const isCorrect = quizData.questions[currentQuestionIndex].answer_index === optIdx;
                        const hasAnswered = selectedAnswerIndex !== null;

                        let optClass = '';
                        if (hasAnswered) {
                          if (isCorrect) optClass = 'correct';
                          else if (isSelected) optClass = 'incorrect';
                          else optClass = 'disabled';
                        }

                        return (
                          <button
                            key={optIdx}
                            className={`quiz-option-btn ${optClass}`}
                            onClick={() => handleAnswerSelect(optIdx)}
                            disabled={hasAnswered}
                          >
                            <span className="option-label">{String.fromCharCode(65 + optIdx)}</span>
                            <span className="option-text">{opt}</span>
                          </button>
                        );
                      })}
                    </div>

                    {selectedAnswerIndex !== null && (
                      <div className="quiz-explanation-box animate-fade-in">
                        <h4>
                          {selectedAnswerIndex === quizData.questions[currentQuestionIndex].answer_index
                            ? '✅ Correct!'
                            : '❌ Incorrect'}
                        </h4>
                        <p>{quizData.questions[currentQuestionIndex].explanation}</p>
                        <button
                          className="btn btn-primary"
                          onClick={handleNextQuestion}
                          style={{ marginTop: '1.2rem', float: 'right' }}
                        >
                          {currentQuestionIndex === quizData.questions.length - 1
                            ? 'Finish Quiz'
                            : 'Next Question ➔'}
                        </button>
                        <div style={{ clear: 'both' }} />
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="quiz-results-card text-center">
                  <span className="quiz-result-icon">🏆</span>
                  <h2>Quiz Completed!</h2>
                  <div className="result-score-display">
                    <span className="result-score">{quizScore}</span>
                    <span className="result-total">/ {quizData.questions.length}</span>
                  </div>
                  <p className="result-feedback">
                    {quizScore === quizData.questions.length
                      ? 'Perfect score! Excellent understanding!'
                      : quizScore >= quizData.questions.length / 2
                        ? 'Good effort! Review the explanations to get a perfect score.'
                        : 'Keep practicing! Review this topic with your AI tutor.'}
                  </p>
                  <button
                    className="btn btn-primary"
                    onClick={() => {
                      setCurrentQuestionIndex(0);
                      setSelectedAnswerIndex(null);
                      setQuizScore(0);
                    }}
                    style={{ marginTop: '1.5rem', marginRight: '1rem' }}
                  >
                    🔄 Try Again
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowQuizModal(false)}
                    style={{ marginTop: '1.5rem' }}
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
          )}
        </Modal>
      </main>
    </div>
  );
}
