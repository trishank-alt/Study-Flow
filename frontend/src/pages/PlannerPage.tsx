import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import { scheduleService } from '../services/schedule';
import { aiService } from '../services/ai';
import type { ScheduleItem, ScheduleReviewResponse } from '../types';
import './PlannerPage.css';

export default function PlannerPage() {
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [dailyMinutes, setDailyMinutes] = useState(120);

  // AI Advisor state
  const [reviewData, setReviewData] = useState<ScheduleReviewResponse | null>(null);
  const [isReviewing, setIsReviewing] = useState(false);
  const [reviewError, setReviewError] = useState('');

  const loadSchedule = async () => {
    try {
      const data = await scheduleService.list();
      setSchedule(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSchedule();
  }, []);

  const handleGenerate = async (useAi?: boolean) => {
    setIsGenerating(true);
    setReviewData(null); // Clear previous advice
    try {
      const data = await scheduleService.generate(dailyMinutes, undefined, useAi);
      setSchedule(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleToggleComplete = async (item: ScheduleItem) => {
    await scheduleService.markComplete(item.id, !item.completed);
    loadSchedule();
  };

  const handleReview = async () => {
    setIsReviewing(true);
    setReviewError('');
    try {
      const data = await aiService.reviewSchedule();
      setReviewData(data);
    } catch (err) {
      console.error(err);
      setReviewError('Failed to generate AI study advisor review.');
    } finally {
      setIsReviewing(false);
    }
  };

  // Group schedule items by date
  const groupedByDate = schedule.reduce<Record<string, ScheduleItem[]>>((acc, item) => {
    const dateKey = item.scheduled_date;
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(item);
    return acc;
  }, {});

  const sortedDates = Object.keys(groupedByDate).sort();

  return (
    <div className="app-layout">
      <Sidebar />
      <Navbar title="Study Planner" />
      <main className="main-content">
        <div className="page-header">
          <div>
            <h1 className="page-title">Study Planner</h1>
            <p className="page-subtitle">Your generated study schedule</p>
          </div>
          <div className="planner-controls" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <div className="planner-minutes-input">
              <label className="form-label" htmlFor="daily-minutes">Daily minutes</label>
              <input
                id="daily-minutes"
                type="number"
                className="form-input"
                min="30"
                step="15"
                value={dailyMinutes}
                onChange={(e) => setDailyMinutes(Number(e.target.value))}
                style={{ width: '90px' }}
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={() => handleGenerate(true)}
              disabled={isGenerating}
              id="generate-ai-schedule-btn"
              title="Generate schedule using AI"
            >
              {isGenerating ? '⏳ Generating...' : '🤖 Generate with AI'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleGenerate(false)}
              disabled={isGenerating}
              id="generate-rule-schedule-btn"
              title="Generate schedule using rules"
            >
              {isGenerating ? '⏳ Generating...' : '⚙️ Rule-Based'}
            </button>
          </div>
        </div>

        {/* AI Schedule Advisor Panel */}
        {schedule.length > 0 && (
          <div className="glass-card advisor-card animate-fade-in" style={{ marginBottom: '2rem' }}>
            <div className="advisor-header">
              <div className="advisor-title-wrapper">
                <span className="advisor-icon">🧠</span>
                <div>
                  <h3 className="advisor-title">AI Study Schedule Advisor</h3>
                  <p className="advisor-subtitle">Get feedback on your current schedule balance, burnout risk, and exam preparedness</p>
                </div>
              </div>
              <button
                className="btn btn-secondary btn-sm btn-advisor-action"
                onClick={handleReview}
                disabled={isReviewing}
              >
                {isReviewing ? '⏳ Reviewing...' : '🧠 Review My Schedule'}
              </button>
            </div>

            {reviewError && <div className="form-alert error" style={{ marginTop: '1rem' }}>{reviewError}</div>}

            {reviewData && (
              <div className="advisor-results animate-fade-in" style={{ marginTop: '1.2rem' }}>
                <div className="advisor-status-box glass-inner-card">
                  <span className="status-label">Schedule Balance: </span>
                  <span className="status-value">{reviewData.overall_status}</span>
                </div>

                <div className="advisor-grid" style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                  {/* Left Column: Insights */}
                  <div className="advisor-col">
                    <h4 className="col-title">📊 Insights</h4>
                    <ul className="advisor-list">
                      {reviewData.insights.map((ins, i) => (
                        <li key={i}>{ins}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Right Column: Warnings & Suggestions */}
                  <div className="advisor-col">
                    {reviewData.warnings.length > 0 && (
                      <div className="advisor-subcol warning-col" style={{ marginBottom: '1rem' }}>
                        <h4 className="col-title" style={{ color: 'var(--accent-red)' }}>⚠️ Warnings</h4>
                        <ul className="advisor-list warnings-list">
                          {reviewData.warnings.map((warn, i) => (
                            <li key={i}>{warn}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="advisor-subcol suggestion-col">
                      <h4 className="col-title" style={{ color: 'var(--accent-orange)' }}>💡 Suggestions</h4>
                      <ul className="advisor-list suggestions-list">
                        {reviewData.suggestions.map((sug, i) => (
                          <li key={i}>{sug}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {isLoading ? (
          <div className="loading-page"><div className="spinner" /></div>
        ) : schedule.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📅</div>
            <h3>No schedule yet</h3>
            <p>Add subjects, topics, and exams — then generate a study plan using AI or rules</p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', marginTop: '1rem' }}>
              <button
                className="btn btn-primary"
                onClick={() => handleGenerate(true)}
                disabled={isGenerating}
              >
                🤖 Generate with AI
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => handleGenerate(false)}
                disabled={isGenerating}
              >
                ⚙️ Rule-Based Schedule
              </button>
            </div>
          </div>
        ) : (
          <div className="planner-timeline stagger-children">
            {sortedDates.map((dateStr) => {
              const items = groupedByDate[dateStr];
              const dateObj = new Date(dateStr + 'T00:00:00');
              const isToday = dateStr === new Date().toISOString().split('T')[0];
              const isPast = new Date(dateStr) < new Date(new Date().toISOString().split('T')[0]);

              return (
                <div key={dateStr} className={`planner-day ${isToday ? 'planner-day-today' : ''} ${isPast ? 'planner-day-past' : ''}`}>
                  <div className="planner-day-header">
                    <span className="planner-day-name">
                      {dateObj.toLocaleDateString('en-US', { weekday: 'short' })}
                    </span>
                    <span className="planner-day-date">
                      {dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                    {isToday && <span className="planner-today-badge">Today</span>}
                  </div>
                  <div className="planner-day-items">
                    {items.map((item) => (
                      <div
                        key={item.id}
                        className={`planner-item ${item.completed ? 'planner-item-done' : ''}`}
                        onClick={() => handleToggleComplete(item)}
                        role="button"
                        tabIndex={0}
                      >
                        <div className={`planner-item-check ${item.completed ? 'checked' : ''}`}>
                          {item.completed ? '✓' : ''}
                        </div>
                        <div className="planner-item-info">
                          <span className="planner-item-topic">{item.topic_title}</span>
                          <span className="planner-item-subject">{item.subject_name}</span>
                        </div>
                        <span className="planner-item-duration">{item.planned_minutes} min</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
