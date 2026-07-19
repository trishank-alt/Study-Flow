import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import Modal from '../components/Modal/Modal';
import ProgressBar from '../components/ProgressBar/ProgressBar';
import { subjectsService } from '../services/subjects';
import type { Subject } from '../types';
import './SubjectsPage.css';

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const loadSubjects = async () => {
    try {
      const data = await subjectsService.list();
      setSubjects(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSubjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await subjectsService.create(newName);
      setNewName('');
      setShowModal(false);
      loadSubjects();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to create subject');
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this subject and all its topics?')) {
      await subjectsService.remove(id);
      loadSubjects();
    }
  };

  const subjectColors = ['purple', 'blue', 'green', 'orange', 'pink', 'cyan'];

  return (
    <div className="app-layout">
      <Sidebar />
      <Navbar title="Subjects" />
      <main className="main-content">
        <div className="page-header">
          <div>
            <h1 className="page-title">Subjects</h1>
            <p className="page-subtitle">Manage your academic subjects</p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => setShowModal(true)}
            id="add-subject-btn"
          >
            + Add Subject
          </button>
        </div>

        {isLoading ? (
          <div className="loading-page"><div className="spinner" /></div>
        ) : subjects.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <h3>No subjects yet</h3>
            <p>Add your first subject to get started</p>
            <button
              className="btn btn-primary"
              onClick={() => setShowModal(true)}
              style={{ marginTop: '1rem' }}
            >
              + Add Subject
            </button>
          </div>
        ) : (
          <div className="grid-cards stagger-children">
            {subjects.map((subject, index) => {
              const color = subjectColors[index % subjectColors.length];
              return (
                <div
                  key={subject.id}
                  className={`glass-card subject-card subject-card-${color}`}
                  onClick={() => navigate(`/subjects/${subject.id}`)}
                  role="button"
                  tabIndex={0}
                  id={`subject-card-${subject.id}`}
                >
                  <div className="subject-card-header">
                    <h3 className="subject-card-name">{subject.name}</h3>
                    <button
                      className="btn btn-ghost btn-icon btn-sm"
                      onClick={(e) => handleDelete(subject.id, e)}
                      title="Delete subject"
                    >
                      🗑️
                    </button>
                  </div>
                  <div className="subject-card-meta">
                    <span>{subject.topic_count || 0} topics</span>
                  </div>
                  <ProgressBar
                    value={subject.completion || 0}
                    variant={color === 'green' ? 'success' : color === 'orange' ? 'warm' : 'primary'}
                    size="sm"
                  />
                </div>
              );
            })}
          </div>
        )}

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add Subject">
          <form onSubmit={handleCreate}>
            {error && <div className="login-error">{error}</div>}
            <div className="form-group">
              <label className="form-label" htmlFor="subject-name">Subject Name</label>
              <input
                id="subject-name"
                className="form-input"
                placeholder="e.g. Mathematics"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                required
                autoFocus
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
              Create Subject
            </button>
          </form>
        </Modal>
      </main>
    </div>
  );
}
