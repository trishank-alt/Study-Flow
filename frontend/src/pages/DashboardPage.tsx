import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import ProgressBar from '../components/ProgressBar/ProgressBar';
import { progressService } from '../services/schedule';
import type { DashboardStats } from '../types';
import './DashboardPage.css';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    progressService
      .getDashboard()
      .then(setStats)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <Navbar title="Dashboard" />
        <main className="main-content">
          <div className="loading-page"><div className="spinner" /></div>
        </main>
      </div>
    );
  }

  const data = stats || {
    total_hours: 0,
    weekly_hours: 0,
    study_streak: 0,
    total_subjects: 0,
    total_topics: 0,
    overall_completion: 0,
    upcoming_exams: 0,
    recent_sessions: [],
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <Navbar title="Dashboard" />
      <main className="main-content">
        <div className="page-header">
          <div>
            <h1 className="page-title">Dashboard</h1>
            <p className="page-subtitle">Your study overview at a glance</p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid-stats stagger-children">
          <div className="stat-card purple">
            <div className="stat-icon purple">📖</div>
            <div className="stat-value">{data.total_hours}</div>
            <div className="stat-label">Total Hours Studied</div>
          </div>
          <div className="stat-card blue">
            <div className="stat-icon blue">📈</div>
            <div className="stat-value">{data.weekly_hours}</div>
            <div className="stat-label">Hours This Week</div>
          </div>
          <div className="stat-card orange">
            <div className="stat-icon orange">🔥</div>
            <div className="stat-value">{data.study_streak}</div>
            <div className="stat-label">Day Study Streak</div>
          </div>
          <div className="stat-card green">
            <div className="stat-icon green">🎯</div>
            <div className="stat-value">{data.upcoming_exams}</div>
            <div className="stat-label">Upcoming Exams</div>
          </div>
        </div>

        {/* Progress Section */}
        <div className="dashboard-section animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <h2 className="section-title">Overall Progress</h2>
          <div className="glass-card">
            <div className="dashboard-progress-row">
              <div>
                <span className="dashboard-progress-label">Subjects</span>
                <span className="dashboard-progress-count">{data.total_subjects}</span>
              </div>
              <div>
                <span className="dashboard-progress-label">Topics</span>
                <span className="dashboard-progress-count">{data.total_topics}</span>
              </div>
              <div style={{ flex: 1 }}>
                <span className="dashboard-progress-label">Completion</span>
                <ProgressBar value={data.overall_completion} variant="success" />
              </div>
            </div>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="dashboard-section animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <h2 className="section-title">Recent Study Sessions</h2>
          {data.recent_sessions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📚</div>
              <h3>No sessions yet</h3>
              <p>Start studying to see your activity here</p>
            </div>
          ) : (
            <div className="recent-sessions-list">
              {data.recent_sessions.map((session) => (
                <div key={session.id} className="glass-card session-card">
                  <div className="session-info">
                    <span className="session-topic">{session.topic_title || 'Topic'}</span>
                    <span className="session-subject">{session.subject_name || ''}</span>
                  </div>
                  <div className="session-meta">
                    <span className="session-duration">{session.duration_minutes} min</span>
                    <span className="session-date">
                      {session.completed_at
                        ? new Date(session.completed_at).toLocaleDateString()
                        : ''}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
