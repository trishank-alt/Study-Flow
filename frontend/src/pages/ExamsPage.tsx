import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import Modal from '../components/Modal/Modal';
import { examsService } from '../services/exams';
import { subjectsService } from '../services/subjects';
import type { Exam, Subject } from '../types';
import './ExamsPage.css';

export default function ExamsPage() {
  const [exams, setExams] = useState<Exam[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form state
  const [examName, setExamName] = useState('');
  const [examSubjectId, setExamSubjectId] = useState<number>(0);
  const [examDate, setExamDate] = useState('');

  const loadData = async () => {
    try {
      const [examsData, subjectsData] = await Promise.all([
        examsService.list(),
        subjectsService.list(),
      ]);
      setExams(examsData);
      setSubjects(subjectsData);
      if (subjectsData.length > 0 && examSubjectId === 0) {
        setExamSubjectId(subjectsData[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await examsService.create({
      subject_id: examSubjectId,
      name: examName,
      exam_date: examDate,
    });
    setExamName('');
    setExamDate('');
    setShowModal(false);
    loadData();
  };

  const handleDelete = async (id: number) => {
    if (confirm('Delete this exam?')) {
      await examsService.remove(id);
      loadData();
    }
  };

  const getCountdownColor = (days: number | undefined) => {
    if (days === undefined) return 'var(--text-muted)';
    if (days <= 3) return 'var(--accent-red)';
    if (days <= 7) return 'var(--accent-orange)';
    if (days <= 14) return 'var(--accent-primary)';
    return 'var(--accent-green)';
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <Navbar title="Exams" />
      <main className="main-content">
        <div className="page-header">
          <div>
            <h1 className="page-title">Exams</h1>
            <p className="page-subtitle">Track upcoming examinations</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)} id="add-exam-btn">
            + Add Exam
          </button>
        </div>

        {isLoading ? (
          <div className="loading-page"><div className="spinner" /></div>
        ) : exams.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <h3>No exams scheduled</h3>
            <p>Add your upcoming exams to generate study plans</p>
          </div>
        ) : (
          <div className="exams-list stagger-children">
            {exams.map((exam) => (
              <div key={exam.id} className="glass-card exam-card">
                <div className="exam-card-left">
                  <div className="exam-countdown" style={{ color: getCountdownColor(exam.days_remaining) }}>
                    {exam.days_remaining !== undefined && exam.days_remaining >= 0
                      ? exam.days_remaining
                      : '—'}
                  </div>
                  <span className="exam-countdown-label">
                    {exam.days_remaining !== undefined && exam.days_remaining >= 0
                      ? 'days left'
                      : 'passed'}
                  </span>
                </div>
                <div className="exam-card-info">
                  <h3 className="exam-name">{exam.name}</h3>
                  <span className="exam-subject">{exam.subject_name}</span>
                  <span className="exam-date">
                    {new Date(exam.exam_date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </span>
                </div>
                <button
                  className="btn btn-ghost btn-icon"
                  onClick={() => handleDelete(exam.id)}
                  title="Delete exam"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        )}

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add Exam">
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label className="form-label" htmlFor="exam-name">Exam Name</label>
              <input
                id="exam-name"
                className="form-input"
                placeholder="e.g. Midterm Exam"
                value={examName}
                onChange={(e) => setExamName(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="exam-subject">Subject</label>
              <select
                id="exam-subject"
                className="form-select"
                value={examSubjectId}
                onChange={(e) => setExamSubjectId(Number(e.target.value))}
              >
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="exam-date">Exam Date</label>
              <input
                id="exam-date"
                type="date"
                className="form-input"
                value={examDate}
                onChange={(e) => setExamDate(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
              Add Exam
            </button>
          </form>
        </Modal>
      </main>
    </div>
  );
}
