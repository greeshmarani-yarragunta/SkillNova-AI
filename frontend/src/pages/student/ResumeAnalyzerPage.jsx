import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { resumeService } from '../../services/resumeService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiFileText, FiUploadCloud, FiCheckCircle, FiAlertTriangle,
  FiAward, FiArrowRight, FiCheck, FiX, FiLayers, FiBriefcase, FiBook
} from 'react-icons/fi';

const ResumeAnalyzerPage = () => {
  const [targetRole, setTargetRole] = useState('Python Developer');
  const [file, setFile] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [useTextInput, setUseTextInput] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF document.');
      setFile(null);
      return;
    }

    if (selected.size > 5 * 1024 * 1024) {
      setError('File size exceeds 5MB limit.');
      setFile(null);
      return;
    }

    setError('');
    setFile(selected);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!file && !resumeText.trim()) {
      setError('Please provide a PDF resume or paste resume text.');
      return;
    }

    setError('');
    setAnalyzing(true);

    try {
      const formData = new FormData();
      formData.append('target_role', targetRole);
      if (file && !useTextInput) {
        formData.append('resume', file);
      } else {
        formData.append('resume_text', resumeText);
      }

      const data = await resumeService.analyzeResume(formData);
      setAnalysisResult(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to analyze resume. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="container fade-in" style={{ maxWidth: '880px', padding: '2rem 1rem' }}>
      {/* Header */}
      <div
        className="card"
        style={{
          padding: '2rem',
          marginBottom: '2rem',
          background: 'linear-gradient(135deg, var(--bg-surface), var(--primary-light))',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--primary)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem',
            }}
          >
            <FiFileText />
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>AI Resume Skill-Gap Analyzer</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Upload your PDF resume to extract skills, benchmark against target role requirements, and receive a customized bridge curriculum.
        </p>
      </div>

      {error && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            background: 'var(--danger-light)',
            color: 'var(--danger)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            marginBottom: '1.5rem',
          }}
        >
          <FiAlertTriangle />
          <span>{error}</span>
        </div>
      )}

      {/* 1. Upload Form */}
      {!analysisResult && (
        <div className="card" style={{ padding: '2.5rem 2rem' }}>
          <form onSubmit={handleAnalyze}>
            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
              <label className="form-label">Target Industry Role</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="form-select"
              >
                <option value="Python Developer">Python Developer</option>
                <option value="Full Stack Developer">Full Stack Developer</option>
                <option value="Frontend Developer">Frontend Developer</option>
                <option value="Backend Developer">Backend Developer</option>
                <option value="Data Scientist">Data Scientist</option>
              </select>
            </div>

            {/* Input Mode Toggle */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.75rem' }}>
              <button
                type="button"
                onClick={() => setUseTextInput(!useTextInput)}
                style={{ fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 600 }}
              >
                {useTextInput ? 'Switch to PDF File Upload' : 'Or Paste Resume Text Directly'}
              </button>
            </div>

            {useTextInput ? (
              <div className="form-group">
                <label className="form-label">Paste Resume Content</label>
                <textarea
                  rows="8"
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste your resume sections, skills, and projects here..."
                  className="form-textarea"
                  style={{ fontFamily: 'var(--font-mono)', fontSize: '0.885rem' }}
                />
              </div>
            ) : (
              <div className="form-group">
                <label className="form-label">Upload PDF Resume (Max 5MB)</label>
                <div
                  style={{
                    border: '2px dashed var(--border-color)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '2.5rem 1.5rem',
                    textAlign: 'center',
                    background: 'var(--bg-subtle)',
                    cursor: 'pointer',
                    position: 'relative',
                  }}
                >
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      opacity: 0,
                      cursor: 'pointer',
                    }}
                  />
                  <FiUploadCloud style={{ fontSize: '2.5rem', color: 'var(--primary)', marginBottom: '0.75rem' }} />
                  <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                    {file ? file.name : 'Click or Drag & Drop your PDF resume here'}
                  </div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Supports standard PDF documents'}
                  </span>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={analyzing}
              className="btn btn-primary btn-lg"
              style={{ width: '100%', marginTop: '1.5rem' }}
            >
              {analyzing ? 'Extracting & Benchmarking Skills...' : 'Analyze Resume with AI'}
            </button>
          </form>
        </div>
      )}

      {/* 2. Analysis Results View */}
      {analysisResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Match Score Card */}
          <div
            className="card"
            style={{
              padding: '2.5rem 2rem',
              textAlign: 'center',
              background: 'linear-gradient(135deg, var(--bg-surface), var(--primary-light))',
            }}
          >
            <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
              Target Role: {analysisResult.target_role}
            </div>
            <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--primary)', marginBottom: '0.25rem' }}>
              {analysisResult.match_percentage}%
            </div>
            <div style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
              Overall Role Skill Alignment
            </div>

            <button onClick={() => setAnalysisResult(null)} className="btn btn-secondary btn-sm">
              Upload Another Resume
            </button>
          </div>

          {/* Two Columns: Skills You Have vs Skills To Improve */}
          <div className="grid grid-cols-2 gap-6">
            {/* Skills You Have */}
            <div className="card">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)' }}>
                <FiCheckCircle /> Skills You Have ({analysisResult.detected_skills?.length || 0})
              </h3>
              {analysisResult.detected_skills?.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {analysisResult.detected_skills.map((skill, i) => (
                    <span key={i} className="badge badge-success" style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}>
                      ✓ {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No core target skills detected in document.</p>
              )}
            </div>

            {/* Skills To Improve */}
            <div className="card">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--warning)' }}>
                <FiAlertTriangle /> Skills To Acquire ({analysisResult.missing_skills?.length || 0})
              </h3>
              {analysisResult.missing_skills?.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {analysisResult.missing_skills.map((skill, i) => (
                    <span key={i} className="badge badge-warning" style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}>
                      + {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--success)', fontSize: '0.9rem' }}>You possess all benchmark skills for this role!</p>
              )}
            </div>
          </div>

          {/* Suggested Assessments based on Gaps */}
          {analysisResult.missing_skills && analysisResult.missing_skills.length > 0 && (
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <FiAward style={{ color: 'var(--secondary)' }} /> Suggested Assessments
                </h3>
                <span className="badge badge-primary">Direct Skill Benchmark</span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                Benchmark your proficiency in detected skill gap areas by taking an AI-generated assessment:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '0.75rem' }}>
                {analysisResult.missing_skills.map((skill, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.85rem 1rem',
                      background: 'var(--background-secondary)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border)',
                    }}
                  >
                    <span style={{ fontWeight: 600, color: 'var(--text)' }}>{skill}</span>
                    <Link
                      to="/assessments/new"
                      className="btn btn-primary btn-sm"
                      style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
                    >
                      Start Test <FiArrowRight style={{ marginLeft: '0.25rem' }} />
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Learning Path */}
          <div className="card">
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FiAward style={{ color: 'var(--primary)' }} /> Recommended Learning Path
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {analysisResult.recommended_learning_path?.map((step, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1rem 1.25rem',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: 'var(--primary)',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '0.8rem',
                      }}
                    >
                      {i + 1}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{step.skill}</div>
                      <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>{step.action}</div>
                    </div>
                  </div>
                  <span className={`badge ${step.priority === 'High' ? 'badge-danger' : 'badge-neutral'}`}>
                    {step.priority} Priority
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Detected Resume Sections */}
          <div className="grid grid-cols-2 gap-6">
            <div className="card">
              <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FiBook /> Education Detected
              </h4>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.885rem', color: 'var(--text-secondary)' }}>
                {analysisResult.education_detected?.map((ed, i) => (
                  <li key={i}>• {ed}</li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FiBriefcase /> Projects Detected
              </h4>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.885rem', color: 'var(--text-secondary)' }}>
                {analysisResult.projects_detected?.map((proj, i) => (
                  <li key={i}>• {proj}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeAnalyzerPage;
