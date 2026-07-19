import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import Modal from '../components/Modal/Modal';
import { resourcesService } from '../services/resources';
import { subjectsService } from '../services/subjects';
import type { Resource, Subject } from '../types';
import './ResourcesPage.css';

export default function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  // Modal view state
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);

  // Form upload state
  const [title, setTitle] = useState('');
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | ''>('');
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      const [resData, subData] = await Promise.all([
        resourcesService.list(),
        subjectsService.list(),
      ]);
      setResources(resData);
      setSubjects(subData);
    } catch (err) {
      console.error('Failed to load resources page data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

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
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      if (!title) {
        // Auto-fill title with filename without extension
        setTitle(droppedFile.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title) return;

    setIsUploading(true);
    setMessage('');
    setError('');

    try {
      await resourcesService.upload(
        file,
        title,
        selectedSubjectId === '' ? undefined : selectedSubjectId,
        undefined // topic id optional
      );
      setMessage('Document uploaded successfully! AI processing has started in the background.');
      setTitle('');
      setFile(null);
      setSelectedSubjectId('');
      loadData();
    } catch (err) {
      console.error(err);
      setError('Failed to upload document.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await resourcesService.remove(id);
        loadData();
      } catch (err) {
        console.error(err);
        alert('Failed to delete resource.');
      }
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <Navbar title="Study Materials" />
      <main className="main-content">
        <div className="page-header">
          <div>
            <h1 className="page-title">Study Materials</h1>
            <p className="page-subtitle">Upload lecture notes or past papers to generate AI summaries</p>
          </div>
        </div>

        <div className="resources-layout">
          {/* Left Column: Upload Form */}
          <div className="resources-upload-col animate-fade-in">
            <div className="glass-card upload-card">
              <h3 className="section-title">📤 Upload Material</h3>
              <form onSubmit={handleUploadSubmit} className="upload-form">
                {message && <div className="form-alert success">{message}</div>}
                {error && <div className="form-alert error">{error}</div>}

                <div className="form-group">
                  <label className="form-label" htmlFor="doc-title">Document Title</label>
                  <input
                    id="doc-title"
                    className="form-input"
                    placeholder="e.g. Lecture 1 Notes"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="doc-subject">Subject (Optional)</label>
                  <select
                    id="doc-subject"
                    className="form-select"
                    value={selectedSubjectId}
                    onChange={(e) => setSelectedSubjectId(e.target.value === '' ? '' : Number(e.target.value))}
                  >
                    <option value="">Unassigned</option>
                    {subjects.map((sub) => (
                      <option key={sub.id} value={sub.id}>{sub.name}</option>
                    ))}
                  </select>
                </div>

                <div
                  className={`drag-drop-area ${dragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    id="file-upload"
                    className="file-input-hidden"
                    accept=".pdf,.txt"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="file-upload" className="drag-drop-label">
                    <span className="upload-icon">📄</span>
                    {file ? (
                      <span className="file-info">
                        <strong>Selected file:</strong> {file.name} ({Math.round(file.size / 1024)} KB)
                      </span>
                    ) : (
                      <span>Drag & drop notes/PDF here or <strong>browse</strong></span>
                    )}
                  </label>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary btn-block"
                  disabled={isUploading || !file}
                  style={{ marginTop: '1rem', width: '100%' }}
                >
                  {isUploading ? '⏳ Uploading...' : '🚀 Process & Upload Document'}
                </button>
              </form>
            </div>
          </div>

          {/* Right Column: List of Materials */}
          <div className="resources-list-col animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <h3 className="section-title">📚 Materials Repository</h3>

            {isLoading ? (
              <div className="loading-page"><div className="spinner" /></div>
            ) : resources.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📚</div>
                <h3>No materials uploaded</h3>
                <p>Upload PDFs or text files to generate structured AI notes summaries.</p>
              </div>
            ) : (
              <div className="resources-grid stagger-children">
                {resources.map((res) => {
                  const subject = subjects.find((s) => s.id === res.subject_id);
                  return (
                    <div
                      key={res.id}
                      className="glass-card resource-card"
                      onClick={() => setSelectedResource(res)}
                    >
                      <div className="resource-card-header">
                        <div className="resource-icon-wrapper">
                          <span className="resource-file-icon">
                            {res.content_type === 'application/pdf' ? '🟥' : '📄'}
                          </span>
                        </div>
                        <div className="resource-meta-info">
                          <h4 className="resource-title">{res.title}</h4>
                          <span className="resource-date">
                            {res.created_at ? new Date(res.created_at).toLocaleDateString() : ''}
                          </span>
                        </div>
                        <button
                          className="btn btn-ghost btn-icon btn-sm delete-resource-btn"
                          onClick={(e) => handleDelete(res.id, e)}
                          title="Delete material"
                        >
                          🗑️
                        </button>
                      </div>

                      <div className="resource-card-body">
                        {subject && (
                          <span className="badge badge-medium subject-tag">{subject.name}</span>
                        )}
                        <span className={`status-tag status-${res.embedding_status}`}>
                          {res.embedding_status === 'pending'
                            ? '⏳ Processing AI...'
                            : res.embedding_status === 'processed'
                              ? '✨ AI Ready'
                              : '⚠️ AI Failed'}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* View Document Summary Modal */}
        <Modal
          isOpen={selectedResource !== null}
          onClose={() => setSelectedResource(null)}
          title={selectedResource?.title || 'Document summary'}
        >
          {selectedResource && (
            <div className="resource-summary-view">
              <div className="summary-meta">
                <span className="summary-filename">📁 File: {selectedResource.filename}</span>
                <span className={`status-tag status-${selectedResource.embedding_status}`}>
                  {selectedResource.embedding_status}
                </span>
              </div>
              <hr className="divider" />
              {selectedResource.embedding_status === 'pending' ? (
                <div className="processing-state">
                  <div className="spinner" />
                  <p>AI is generating note summary in the background...</p>
                </div>
              ) : selectedResource.embedding_status === 'failed' ? (
                <div className="error-state">
                  <p>Processing failed. Here is the log info:</p>
                  <pre className="error-box">{selectedResource.summary}</pre>
                </div>
              ) : (
                <div className="summary-content markdown-body">
                  {/* Summary matches structured JSON output displayed beautifully */}
                  <div dangerouslySetInnerHTML={{
                    __html: selectedResource.summary
                      ? selectedResource.summary
                          .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                          .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
                          .replace(/^- (.*$)/gim, '<li>$1</li>')
                          .replace(/\n\n/g, '<br />')
                      : 'No summary available.'
                  }} />
                </div>
              )}
            </div>
          )}
        </Modal>
      </main>
    </div>
  );
}
