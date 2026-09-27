import React, { useState } from 'react';
import { aiService } from '../../services/aiService';
import LoadingSpinner from '../../components/LoadingSpinner';
import confetti from 'canvas-confetti';
import {
  FiActivity, FiAward, FiCheckCircle, FiAlertCircle,
  FiArrowRight, FiZap, FiHelpCircle, FiSend, FiRefreshCw
} from 'react-icons/fi';

const InterviewPrepPage = () => {
  const [targetRole, setTargetRole] = useState('Python Developer');
  const [experienceLevel, setExperienceLevel] = useState('Fresher');
  const [selectedSkills, setSelectedSkills] = useState(['Python', 'Django', 'SQL', 'REST APIs']);

  const [generating, setGenerating] = useState(false);
  const [session, setSession] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const availableSkillOptions = ['Python', 'Django', 'React', 'JavaScript', 'SQL', 'REST APIs', 'Git', 'Docker', 'Machine Learning'];

  const toggleSkill = (skill) => {
    if (selectedSkills.includes(skill)) {
      if (selectedSkills.length > 1) {
        setSelectedSkills(selectedSkills.filter((s) => s !== skill));
      }
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError('');
    setGenerating(true);

    try {
      const data = await aiService.generateInterview(targetRole, experienceLevel, selectedSkills);
      setSession(data);
      setAnswers({});
    } catch (err) {
      setError('Failed to generate interview set. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSubmitAnswers = async () => {
    if (!session) return;
    setSubmitting(true);
    setError('');

    try {
      const evaluated = await aiService.submitInterviewAnswers(session.id, answers);
      setSession(evaluated);

      if (evaluated.overall_score >= 70) {
        confetti({
          particleCount: 90,
          spread: 60,
          origin: { y: 0.6 },
        });
      }
    } catch (err) {
      setError('Failed to evaluate interview answers. Please try again.');
    } finally {
      setSubmitting(false);
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
            <FiActivity />
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>AI Mock Interview Preparation</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Practice role-specific technical, conceptual, scenario, project, and HR questions with constructive AI grading and concepts analysis.
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
          <FiAlertCircle />
          <span>{error}</span>
        </div>
      )}

      {/* 1. Setup Form */}
      {!session && (
        <div className="card" style={{ padding: '2.5rem 2rem' }}>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '1.5rem' }}>Configure Interview Target</h2>

          <form onSubmit={handleGenerate}>
            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Target Role</label>
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

              <div className="form-group">
                <label className="form-label">Experience Bracket</label>
                <select
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                  className="form-select"
                >
                  <option value="Fresher">Fresher / Entry Level</option>
                  <option value="1-2 Years">Junior (1-2 Years)</option>
                  <option value="3-5 Years">Mid-Level (3-5 Years)</option>
                  <option value="5+ Years">Senior (5+ Years)</option>
                </select>
              </div>
            </div>

            {/* Skills selection */}
            <div className="form-group">
              <label className="form-label">Select Interview Focus Skills</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.25rem' }}>
                {availableSkillOptions.map((skill) => {
                  const isSelected = selectedSkills.includes(skill);
                  return (
                    <button
                      key={skill}
                      type="button"
                      onClick={() => toggleSkill(skill)}
                      className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ borderRadius: 'var(--radius-full)' }}
                    >
                      {isSelected ? '✓ ' : '+ '} {skill}
                    </button>
                  );
                })}
              </div>
            </div>

            <button
              type="submit"
              disabled={generating}
              className="btn btn-primary btn-lg"
              style={{ width: '100%', marginTop: '1.5rem' }}
            >
              {generating ? 'Generating Interview Session with AI...' : 'Generate 5-Question Interview'}
            </button>
          </form>
        </div>
      )}

      {/* 2. Evaluation Results View */}
      {session && session.is_completed && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Summary Card */}
          <div
            className="card"
            style={{
              padding: '2.5rem 2rem',
              textAlign: 'center',
              background: 'linear-gradient(135deg, var(--bg-surface), var(--primary-light))',
            }}
          >
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: session.overall_score >= 70 ? 'var(--success)' : 'var(--warning)',
                color: '#ffffff',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.8rem',
                marginBottom: '1rem',
              }}
            >
              <FiAward />
            </div>

            <h2 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
              Interview Performance: {session.overall_score}%
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '650px', margin: '0 auto 1.5rem auto', lineHeight: 1.6 }}>
              {session.overall_feedback}
            </p>

            <button onClick={() => setSession(null)} className="btn btn-secondary">
              <FiRefreshCw /> Start New Interview
            </button>
          </div>

          {/* Strengths & Improvements */}
          <div className="grid grid-cols-2 gap-6">
            <div className="card">
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FiCheckCircle /> Candidate Strengths
              </h3>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {session.strengths?.map((s, i) => (
                  <li key={i} style={{ display: 'flex', gap: '0.4rem' }}>
                    <span>•</span> <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FiAlertCircle /> Areas to Deepen
              </h3>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {session.improvements?.map((s, i) => (
                  <li key={i} style={{ display: 'flex', gap: '0.4rem' }}>
                    <span>•</span> <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Detailed Question Evaluations */}
          <div>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 800, marginBottom: '1.25rem' }}>
              Detailed Question Feedback
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {session.questions?.map((q, idx) => {
                const evalData = session.evaluation?.find((e) => e.question_id === q.id) || {};
                const userAns = session.answers?.[q.id] || session.answers?.[String(q.id)] || '';

                return (
                  <div key={q.id} className="card" style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                      <span className="badge badge-primary">{q.category} Round</span>
                      <span className="badge badge-neutral">Score: {evalData.score || 0}/100</span>
                    </div>

                    <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', lineHeight: 1.4 }}>
                      {q.question}
                    </h4>

                    {/* Student Answer */}
                    <div style={{ background: 'var(--bg-subtle)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem', fontSize: '0.9rem' }}>
                      <strong style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                        YOUR ANSWER:
                      </strong>
                      <p style={{ color: 'var(--text-primary)', whiteSpace: 'pre-line' }}>{userAns || '(No response recorded)'}</p>
                    </div>

                    {/* AI Constructive Feedback */}
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.75rem' }}>
                      <strong>AI Evaluation:</strong> {evalData.feedback}
                    </div>

                    {/* Missing concepts */}
                    {evalData.missing_concepts?.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>Missing Concepts:</span>
                        {evalData.missing_concepts.map((c, i) => (
                          <span key={i} className="badge badge-warning" style={{ fontSize: '0.72rem' }}>
                            {c}
                          </span>
                        ))}
                      </div>
                    )}

                    {evalData.tips && (
                      <div style={{ fontSize: '0.825rem', color: 'var(--primary)', marginTop: '0.5rem', fontStyle: 'italic' }}>
                        💡 Senior Tip: {evalData.tips}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* 3. Answering Questions Interface */}
      {session && !session.is_completed && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>
              Round for: {session.target_role} ({session.experience_level})
            </span>
            <button
              onClick={handleSubmitAnswers}
              disabled={submitting}
              className="btn btn-primary"
            >
              {submitting ? 'Analyzing Responses...' : 'Submit Answers for AI Review'}
            </button>
          </div>

          {session.questions?.map((q, idx) => (
            <div key={q.id} className="card" style={{ padding: '1.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <span className="badge badge-primary">
                  Question {idx + 1} of {session.questions.length} • {q.category}
                </span>
              </div>

              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.25rem', lineHeight: 1.5 }}>
                {q.question}
              </h3>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label" style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                  Type your detailed answer or approach below:
                </label>
                <textarea
                  rows="4"
                  value={answers[q.id] || ''}
                  onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                  placeholder="Outline definitions, architecture considerations, and real-world examples..."
                  className="form-textarea"
                />
              </div>
            </div>
          ))}

          <div style={{ textAlign: 'center', margin: '1rem 0 2rem 0' }}>
            <button
              onClick={handleSubmitAnswers}
              disabled={submitting}
              className="btn btn-primary btn-lg"
              style={{ minWidth: '260px' }}
            >
              {submitting ? 'Analyzing Responses...' : 'Finish & Evaluate Interview'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewPrepPage;
