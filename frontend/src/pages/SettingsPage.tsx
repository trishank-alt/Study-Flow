import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Sidebar from '../components/Sidebar/Sidebar';
import { useAuth } from '../features/auth/AuthContext';
import { settingsService } from '../services/settings';
import './SettingsPage.css';

export default function SettingsPage() {
  const { user } = useAuth();
  const [provider, setProvider] = useState('mock');
  const [modelName, setModelName] = useState('gpt-4o-mini');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await settingsService.get();
        setProvider(data.llm_provider);
        setModelName(data.model_name);
        setOllamaUrl(data.ollama_url);
      } catch (err) {
        console.error('Failed to load settings:', err);
      }
    }
    loadSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage('');
    setError('');
    try {
      await settingsService.update({
        llm_provider: provider,
        model_name: modelName,
        ollama_url: ollamaUrl,
      });
      setMessage('Settings updated successfully!');
    } catch (err) {
      console.error(err);
      setError('Failed to save settings.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <Navbar title="Settings" />
      <main className="main-content animate-fade-in">
        <div className="page-header">
          <div>
            <h1 className="page-title">Settings</h1>
            <p className="page-subtitle">Manage your account and AI tutor preferences</p>
          </div>
        </div>

        <div className="settings-grid">
          <div className="glass-card settings-section">
            <h2 className="settings-section-title">Profile</h2>
            <div className="settings-profile">
              <div className="settings-avatar">
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="settings-profile-info">
                <span className="settings-email">{user?.email}</span>
                <span className="settings-joined">
                  Member since{' '}
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString('en-US', {
                        month: 'long',
                        year: 'numeric',
                      })
                    : '—'}
                </span>
              </div>
            </div>
          </div>

          <div className="glass-card settings-section">
            <h2 className="settings-section-title">AI Study Tutor & Planner</h2>
            <form onSubmit={handleSave} className="settings-form">
              {message && <div className="settings-alert success">{message}</div>}
              {error && <div className="settings-alert error">{error}</div>}

              <div className="form-group">
                <label className="form-label" htmlFor="llm_provider">LLM Provider</label>
                <select
                  id="llm_provider"
                  className="form-select"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                >
                  <option value="mock">Mock AI Tutor (Offline Mode)</option>
                  <option value="rule-based">Rule-Based Schedule (No AI)</option>
                  <option value="ollama">Ollama (Local LLM)</option>
                  <option value="openai">OpenAI (Cloud API)</option>
                  <option value="anthropic">Anthropic (Cloud API)</option>
                  <option value="gemini">Google Gemini (Cloud API)</option>
                </select>
              </div>

              {provider === 'ollama' && (
                <div className="form-group">
                  <label className="form-label" htmlFor="ollama_url">Ollama Base URL</label>
                  <input
                    id="ollama_url"
                    className="form-input"
                    value={ollamaUrl}
                    onChange={(e) => setOllamaUrl(e.target.value)}
                    placeholder="e.g. http://localhost:11434"
                  />
                </div>
              )}

              {provider !== 'rule-based' && (
                <div className="form-group">
                  <label className="form-label" htmlFor="model_name">Model Name</label>
                  <input
                    id="model_name"
                    className="form-input"
                    value={modelName}
                    onChange={(e) => setModelName(e.target.value)}
                    placeholder={provider === 'ollama' ? 'e.g. qwen' : provider === 'gemini' ? 'e.g. gemini-2.5-flash' : 'e.g. gpt-4o-mini'}
                  />
                </div>
              )}

              {provider === 'openai' && (
                <div className="settings-note">
                  ℹ️ OpenAI calls require the <code>OPENAI_API_KEY</code> environment variable in your backend's <code>.env</code> file.
                </div>
              )}
              {provider === 'anthropic' && (
                <div className="settings-note">
                  ℹ️ Anthropic calls require the <code>ANTHROPIC_API_KEY</code> environment variable in your backend's <code>.env</code> file.
                </div>
              )}
              {provider === 'gemini' && (
                <div className="settings-note">
                  ℹ️ Google Gemini calls require the <code>GEMINI_API_KEY</code> (or <code>GOOGLE_API_KEY</code>) environment variable in your backend's <code>.env</code> file.
                </div>
              )}

              <button type="submit" className="btn btn-primary" disabled={isSaving} style={{ marginTop: '0.5rem' }}>
                {isSaving ? '⏳ Saving...' : '💾 Save AI Configuration'}
              </button>
            </form>
          </div>

          <div className="glass-card settings-section">
            <h2 className="settings-section-title">About</h2>
            <div className="settings-about">
              <div className="settings-about-row">
                <span className="settings-about-label">Application</span>
                <span className="settings-about-value">Study Flow</span>
              </div>
              <div className="settings-about-row">
                <span className="settings-about-label">Version</span>
                <span className="settings-about-value">MVP v1.0</span>
              </div>
              <div className="settings-about-row">
                <span className="settings-about-label">Architecture</span>
                <span className="settings-about-value">Modular Monolith</span>
              </div>
              <div className="settings-about-row">
                <span className="settings-about-label">Frontend</span>
                <span className="settings-about-value">React + TypeScript + Vite</span>
              </div>
              <div className="settings-about-row">
                <span className="settings-about-label">Backend</span>
                <span className="settings-about-value">FastAPI + SQLAlchemy + SQLite</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
