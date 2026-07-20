import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import Modal from '../components/Modal/Modal';
import { examsService } from '../services/exams';
import { subjectsService } from '../services/subjects';
import type { Exam, Subject, ExamPaperAnalysisResponse } from '../types';
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

  // Past Paper Analysis States
  const [analyses, setAnalyses] = useState<Record<number, ExamPaperAnalysisResponse>>({});
  const [selectedExamId, setSelectedExamId] = useState<number | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [dragActive, setDragActive] = useState(false);

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

      // Fetch analysis status for each exam
      const analysisMap: Record<number, ExamPaperAnalysisResponse> = {};
      await Promise.all(
        examsData.map(async (exam) => {
          try {
            const statusRes = await examsService.getAnalysis(exam.id);
            analysisMap[exam.id] = statusRes;
          } catch (err) {
            console.error(`Failed to fetch analysis for exam ${exam.id}:`, err);
          }
        })
      );
      setAnalyses(analysisMap);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Polling hook to periodically check processing status
  useEffect(() => {
    const processingIds = Object.keys(analyses)
      .map(Number)
      .filter((id) => analyses[id]?.status === 'processing');

    if (processingIds.length === 0) return;

    const interval = setInterval(async () => {
      let updated = false;
      const newAnalyses = { ...analyses };

      await Promise.all(
        processingIds.map(async (id) => {
          try {
            const res = await examsService.getAnalysis(id);
            if (res.status !== 'processing') {
              newAnalyses[id] = res;
              updated = true;
            }
          } catch (err) {
            console.error(`Polling analysis failed for exam ${id}:`, err);
          }
        })
      );

      if (updated) {
        setAnalyses(newAnalyses);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [analyses]);

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

  // Past Paper handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0]);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || selectedExamId === null) return;

    setIsUploading(true);
    setUploadError('');

    try {
      await examsService.uploadPaper(selectedExamId, uploadFile);
      // Immediately transition local state status to processing
      setAnalyses((prev) => ({
        ...prev,
        [selectedExamId]: {
          status: 'processing',
          result: null,
          error: null,
        },
      }));
      setShowUploadModal(false);
      setUploadFile(null);
    } catch (err) {
      console.error(err);
      setUploadError('Failed to upload past exam paper.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteAnalysis = async (examId: number) => {
    try {
      await examsService.deleteAnalysis(examId);
      setAnalyses((prev) => ({
        ...prev,
        [examId]: {
          status: 'not_uploaded',
          result: null,
          error: null,
        },
      }));
    } catch (err) {
      console.error(err);
      alert('Failed to delete past paper analysis.');
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
            <p className="page-subtitle">Track upcoming examinations & analyze past papers</p>
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
            {exams.map((exam) => {
              const analysis = analyses[exam.id];
              return (
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

                    {/* Past Paper Section */}
                    <div className="exam-paper-section animate-fade-in" style={{ marginTop: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {(!analysis || analysis.status === 'not_uploaded') && (
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => {
                            setSelectedExamId(exam.id);
                            setShowUploadModal(true);
                          }}
                        >
                          🧠 Analyze Past Paper
                        </button>
                      )}
                      {analysis?.status === 'processing' && (
                        <span className="status-tag status-pending">
                          ⏳ Analyzing Paper...
                        </span>
                      )}
                      {analysis?.status === 'failed' && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span className="status-tag status-failed">
                            ⚠️ Analysis Failed
                          </span>
                          <button
                            className="btn btn-ghost btn-sm btn-icon"
                            onClick={() => {
                              setSelectedExamId(exam.id);
                              setShowUploadModal(true);
                            }}
                            title="Retry upload"
                          >
                            🔄
                          </button>
                          <button
                            className="btn btn-ghost btn-sm btn-icon"
                            onClick={() => handleDeleteAnalysis(exam.id)}
                            title="Delete failed analysis"
                            style={{ color: 'var(--accent-red)' }}
                          >
                            🗑️
                          </button>
                        </div>
                      )}
                      {analysis?.status === 'completed' && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span
                            className="status-tag status-processed"
                            style={{ cursor: 'pointer' }}
                            onClick={() => {
                              setSelectedExamId(exam.id);
                              setShowAnalysisModal(true);
                            }}
                            title="Click to view AI Analysis"
                          >
                            ✨ Analysis Ready
                          </span>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => {
                              setSelectedExamId(exam.id);
                              setShowAnalysisModal(true);
                            }}
                          >
                            📊 View Analysis
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                  <button
                    className="btn btn-ghost btn-icon"
                    onClick={() => handleDelete(exam.id)}
                    title="Delete exam"
                  >
                    🗑️
                  </button>
                </div>
              );
            })}
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

        {/* Upload past paper modal */}
        <Modal
          isOpen={showUploadModal}
          onClose={() => {
            setShowUploadModal(false);
            setUploadFile(null);
            setUploadError('');
          }}
          title="Upload Exam Paper"
        >
          <form onSubmit={handleUploadSubmit}>
            {uploadError && <div className="form-alert error">{uploadError}</div>}
            
            <div
              className={`drag-drop-area ${dragActive ? 'active' : ''} ${uploadFile ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              style={{
                border: '2px dashed var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-xl)',
                textAlign: 'center',
                cursor: 'pointer',
                marginBottom: 'var(--space-md)'
              }}
            >
              <input
                type="file"
                id="paper-file-upload"
                className="file-input-hidden"
                accept=".pdf,.txt"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <label htmlFor="paper-file-upload" style={{ cursor: 'pointer', display: 'block' }}>
                <span style={{ fontSize: 'var(--font-size-3xl)', display: 'block', marginBottom: 'var(--space-sm)' }}>📄</span>
                {uploadFile ? (
                  <span>
                    <strong>Selected file:</strong> {uploadFile.name} ({Math.round(uploadFile.size / 1024)} KB)
                  </span>
                ) : (
                  <span>Drag & drop exam paper PDF/text here or <strong>browse</strong></span>
                )}
              </label>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={isUploading || !uploadFile}
              style={{ width: '100%' }}
            >
              {isUploading ? '⏳ Uploading...' : '🚀 Start AI Analysis'}
            </button>
          </form>
        </Modal>

        {/* View AI past paper analysis modal */}
        <Modal
          isOpen={showAnalysisModal}
          onClose={() => setShowAnalysisModal(false)}
          title={`AI Analysis: ${exams.find(e => e.id === selectedExamId)?.name || 'Exam'}`}
        >
          {selectedExamId !== null && analyses[selectedExamId]?.result && (
            <div className="exam-analysis-view" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
              
              {/* Top Banner Card */}
              <div className="glass-card" style={{ padding: 'var(--space-md)', background: 'rgba(255, 255, 255, 0.03)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span className="analysis-meta-label" style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>Difficulty:</span>
                  <span className={`badge badge-${analyses[selectedExamId].result?.difficulty}`} style={{ marginLeft: '0.5rem' }}>
                    {analyses[selectedExamId].result?.difficulty}
                  </span>
                </div>
                <div>
                  <span className="analysis-meta-label" style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>AI Confidence:</span>
                  <span style={{ fontWeight: 'bold', marginLeft: '0.5rem', color: 'var(--accent-primary)' }}>
                    {Math.round((analyses[selectedExamId].result?.confidence || 0) * 100)}%
                  </span>
                </div>
              </div>

              {/* Summary & Strategy Section */}
              <div>
                <h4 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: '0.3rem' }}>📝 Summary Overview</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)', lineHeight: 1.5 }}>
                  {analyses[selectedExamId].result?.summary}
                </p>
              </div>

              <div>
                <h4 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: '0.3rem' }}>💡 Recommended Study Strategy</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)', lineHeight: 1.5 }}>
                  {analyses[selectedExamId].result?.study_strategy}
                </p>
              </div>

              {/* Topics Breakdown Table */}
              <div>
                <h4 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: '0.5rem' }}>📊 Tested Topics & Suggested Prep</h4>
                <div style={{ overflowX: 'auto' }}>
                  <table className="analysis-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--font-size-sm)' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                        <th style={{ padding: '8px 4px' }}>Topic</th>
                        <th style={{ padding: '8px 4px' }}>Frequency</th>
                        <th style={{ padding: '8px 4px' }}>Suggested Hours</th>
                        <th style={{ padding: '8px 4px' }}>Actionable Prep Insight</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analyses[selectedExamId].result?.topics.map((t, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                          <td style={{ padding: '8px 4px', fontWeight: 600 }}>{t.title}</td>
                          <td style={{ padding: '8px 4px' }}>
                            <span className={`badge badge-${t.frequency === 'high' ? 'hard' : t.frequency === 'medium' ? 'medium' : 'easy'}`} style={{ fontSize: '10px', padding: '1px 6px' }}>
                              {t.frequency}
                            </span>
                          </td>
                          <td style={{ padding: '8px 4px' }}>{t.recommended_hours}h</td>
                          <td style={{ padding: '8px 4px', color: 'var(--text-muted)' }}>{t.insight}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Grid: Repeated vs Missing */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
                <div>
                  <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, marginBottom: '0.3rem', color: 'var(--accent-orange)' }}>🔄 Repeated Patterns / Questions</h4>
                  <ul style={{ paddingLeft: '20px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {analyses[selectedExamId].result?.commonly_repeated.map((item, idx) => (
                      <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, marginBottom: '0.3rem', color: 'var(--accent-red)' }}>❓ Missing Core Topics</h4>
                  <ul style={{ paddingLeft: '20px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {analyses[selectedExamId].result?.missing_topics.map((item, idx) => (
                      <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, marginBottom: '0.3rem', color: 'var(--accent-green)' }}>🧠 Important Concepts & Definitions</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {analyses[selectedExamId].result?.important_concepts.map((concept, idx) => (
                    <span key={idx} className="badge badge-easy" style={{ textTransform: 'none', fontSize: '10px' }}>
                      {concept}
                    </span>
                  ))}
                </div>
              </div>

              {/* Actions Footer */}
              <hr style={{ borderColor: 'rgba(255,255,255,0.05)', margin: 'var(--space-sm) 0' }} />
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => {
                    if (confirm('Are you sure you want to delete this past paper and AI analysis?')) {
                      handleDeleteAnalysis(selectedExamId);
                      setShowAnalysisModal(false);
                    }
                  }}
                  style={{ color: 'var(--accent-red)' }}
                >
                  🗑️ Delete Analysis
                </button>
              </div>

            </div>
          )}
        </Modal>
      </main>
    </div>
  );
}
