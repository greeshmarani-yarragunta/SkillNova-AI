import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { assessmentService } from '../../services/assessmentService';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiAward, FiCheckCircle, FiChevronRight, FiChevronLeft,
  FiZap, FiAlertCircle, FiHelpCircle, FiClock, FiSearch
} from 'react-icons/fi';

const SkillAssessmentPage = () => {
  const [searchParams] = useSearchParams();
  const preSelectedSkill = searchParams.get('skill');

  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  // Assessment Setup States
  const [selectedSkillId, setSelectedSkillId] = useState(preSelectedSkill || '');
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [skillSearch, setSkillSearch] = useState('');

  // Active Assessment Taking States
  const [activeAssessment, setActiveAssessment] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  const navigate = useNavigate();

  useEffect(() => {
    const loadSkills = async () => {
      try {
        const data = await authService.getSkills();
        setSkills(data);
        if (!selectedSkillId && data.length > 0) {
          setSelectedSkillId(data[0].id);
        }
      } catch (err) {
        console.error('Failed to load skills for assessment', err);
      } finally {
        setLoading(false);
      }
    };
    loadSkills();
  }, [selectedSkillId]);

  // Assessment Timer
  useEffect(() => {
    let interval = null;
    if (activeAssessment && !submitting) {
      interval = setInterval(() => {
        setSecondsElapsed((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeAssessment, submitting]);

  const handleStartAssessment = async (e) => {
    e.preventDefault();
    if (!selectedSkillId) {
      setError('Please select a skill to begin.');
      return;
    }
    setError('');
    setGenerating(true);

    try {
      // Every assessment automatically contains exactly 30 questions
      const data = await assessmentService.generateAssessment(
        selectedSkillId,
        difficulty,
        30
      );
      setActiveAssessment(data);
      setCurrentIndex(0);
      setAnswers({});
      setSecondsElapsed(0);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate assessment. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectOption = (questionId, optionKey) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionKey,
    }));
  };

  const handleSubmitAssessment = async () => {
    if (!activeAssessment) return;
    const answeredCount = Object.keys(answers).length;
    const totalCount = activeAssessment.questions.length;

    // Student cannot submit an incomplete assessment
    if (answeredCount < totalCount) {
      setError(
        `Incomplete assessment: All ${totalCount} questions must be answered before submitting. You have answered ${answeredCount} of ${totalCount} questions.`
      );
      const firstUnansweredIndex = activeAssessment.questions.findIndex((q) => answers[q.id] === undefined);
      if (firstUnansweredIndex !== -1) {
        setCurrentIndex(firstUnansweredIndex);
      }
      return;
    }

    setError('');
    setSubmitting(true);
    try {
      const result = await assessmentService.submitAssessment(activeAssessment.id, answers);
      navigate(`/assessments/${result.id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit assessment answers. Please try again.');
      setSubmitting(false);
    }
  };

  const formatTimer = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  if (loading) {
    return <LoadingSpinner message="Preparing skill assessment interface..." />;
  }

  const selectedSkillObj = skills.find((s) => s.id === Number(selectedSkillId)) || skills[0];

  // =========================================================================
  // VIEW 1: ACTIVE ASSESSMENT TEST TAKING MODE
  // =========================================================================
  if (activeAssessment) {
    const currentQ = activeAssessment.questions[currentIndex];
    const totalQuestions = activeAssessment.questions.length;
    const progressPercent = Math.round(((currentIndex + 1) / totalQuestions) * 100);
    const selectedAnswer = answers[currentQ?.id];
    const isLastQuestion = currentIndex === totalQuestions - 1;

    const options = [
      { key: 'A', text: currentQ?.option_a },
      { key: 'B', text: currentQ?.option_b },
      { key: 'C', text: currentQ?.option_c },
      { key: 'D', text: currentQ?.option_d },
    ];

    return (
      <div className="fade-in" style={{ maxWidth: '880px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Top Header Card */}
        <div
          className="card"
          style={{
            padding: '1.25rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--primary-light)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.25rem',
              }}
            >
              <FiAward />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text)' }}>
                  {activeAssessment.skill_name} Assessment
                </h2>
                <span className="badge badge-primary">{activeAssessment.difficulty}</span>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>
                Topic: {currentQ?.topic || 'Core Engineering'}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                fontSize: '0.9rem',
                fontWeight: 600,
                color: 'var(--text)',
                background: 'var(--background-secondary)',
                padding: '0.4rem 0.8rem',
                borderRadius: 'var(--radius-full)',
                border: '1px solid var(--border)',
              }}
            >
              <FiClock style={{ color: 'var(--secondary)' }} />
              <span>{formatTimer(secondsElapsed)}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text)' }}>
                Question {currentIndex + 1} of {totalQuestions}
              </span>
              <span
                style={{
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  color: 'var(--primary)',
                  background: 'var(--primary-light)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid var(--primary-border)',
                }}
              >
                Progress: {progressPercent}%
              </span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem', fontSize: '0.8rem', color: 'var(--muted)' }}>
            <span>Question {currentIndex + 1} / {totalQuestions}</span>
            <span>Progress: <strong>{progressPercent}%</strong></span>
          </div>
          <div className="progress-container" style={{ height: '6px' }}>
            <div className="progress-bar" style={{ width: `${progressPercent}%` }} />
          </div>
        </div>

        {/* Question Jumping Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center' }}>
          {activeAssessment.questions.map((q, idx) => {
            const isAnswered = answers[q.id] !== undefined;
            const isCurrent = idx === currentIndex;
            return (
              <button
                key={q.id}
                onClick={() => setCurrentIndex(idx)}
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  border: isCurrent
                    ? '2px solid var(--primary)'
                    : isAnswered
                    ? '1px solid var(--success-border)'
                    : '1px solid var(--border)',
                  background: isCurrent
                    ? 'var(--primary)'
                    : isAnswered
                    ? 'var(--success-bg)'
                    : 'var(--surface)',
                  color: isCurrent
                    ? '#FFFFFF'
                    : isAnswered
                    ? 'var(--success)'
                    : 'var(--muted)',
                  transition: 'all 0.15s ease',
                }}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>

        {/* Question Card */}
        <div className="card" style={{ padding: '2rem' }}>
          <div style={{ marginBottom: '1.75rem' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--secondary)', marginBottom: '0.5rem' }}>
              QUESTION #{currentIndex + 1}
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text)', lineHeight: 1.5 }}>
              {currentQ?.question_text}
            </h3>
          </div>

          {/* Options List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {options.map((opt) => {
              const isSelected = selectedAnswer === opt.key;
              return (
                <div
                  key={opt.key}
                  className={`question-option-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelectOption(currentQ.id, opt.key)}
                >
                  <div className="question-option-letter">
                    {opt.key}
                  </div>
                  <div style={{ fontSize: '0.95rem', color: isSelected ? 'var(--text)' : 'var(--text-secondary)', lineHeight: 1.5, paddingTop: '2px' }}>
                    {opt.text}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom Navigation & Submission */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
          <button
            onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentIndex === 0}
            className="btn btn-secondary"
            style={{ gap: '0.4rem' }}
          >
            <FiChevronLeft /> Previous
          </button>

          <div style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
            {Object.keys(answers).length} of {totalQuestions} answered
          </div>

          {isLastQuestion ? (
            <button
              onClick={handleSubmitAssessment}
              disabled={submitting}
              className="btn btn-primary"
              style={{ gap: '0.5rem' }}
            >
              {submitting ? 'Evaluating with AI...' : 'Submit Assessment'} <FiCheckCircle />
            </button>
          ) : (
            <button
              onClick={() => setCurrentIndex((prev) => Math.min(totalQuestions - 1, prev + 1))}
              className="btn btn-primary"
              style={{ gap: '0.4rem' }}
            >
              Next <FiChevronRight />
            </button>
          )}
        </div>
      </div>
    );
  }

  // =========================================================================
  // VIEW 2: SETUP & SKILL SELECTION VIEW
  // =========================================================================
  const filteredSkills = skills.filter((s) =>
    s.name.toLowerCase().includes(skillSearch.toLowerCase()) ||
    s.category?.toLowerCase().includes(skillSearch.toLowerCase())
  );

  return (
    <div className="fade-in" style={{ maxWidth: '960px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero Setup Header */}
      <div>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.35rem' }}>
          AI Technical Skill Assessment
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
          Select a technical skill, configure your target difficulty, and discover your true proficiency and weak areas with AI evaluation.
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: '1rem',
            background: 'var(--danger-bg)',
            border: '1px solid var(--danger-border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--danger)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.9rem',
          }}
        >
          <FiAlertCircle /> {error}
        </div>
      )}

      {/* Configuration Grid */}
      <form onSubmit={handleStartAssessment} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* Step 1: Select Skill */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text)' }}>
                1. Select Technical Skill
              </h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
                Choose the technical stack or concept you want to test.
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--background-secondary)', padding: '0.35rem 0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }}>
              <FiSearch style={{ color: 'var(--muted)' }} />
              <input
                type="text"
                placeholder="Filter skills..."
                value={skillSearch}
                onChange={(e) => setSkillSearch(e.target.value)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text)', outline: 'none', fontSize: '0.85rem' }}
              />
            </div>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '0.85rem',
              maxHeight: '340px',
              overflowY: 'auto',
              paddingRight: '0.25rem',
            }}
          >
            {filteredSkills.map((s) => {
              const isSelected = String(selectedSkillId) === String(s.id);
              return (
                <div
                  key={s.id}
                  onClick={() => setSelectedSkillId(s.id)}
                  style={{
                    padding: '1rem',
                    borderRadius: 'var(--radius-md)',
                    border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border)',
                    background: isSelected ? 'var(--primary-light)' : 'var(--background-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease-in-out',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '0.5rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.95rem', color: isSelected ? 'var(--primary)' : 'var(--text)' }}>
                      {s.name}
                    </span>
                    {isSelected && <FiCheckCircle style={{ color: 'var(--primary)', fontSize: '1.1rem' }} />}
                  </div>
                  <span className="badge badge-neutral" style={{ fontSize: '0.7rem', width: 'fit-content' }}>
                    {s.category || 'Tech'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Step 2 & 3: Difficulty & Question Count */}
        <div className="grid grid-cols-2 gap-6">
          {/* Difficulty */}
          <div className="card">
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text)', marginBottom: '0.35rem' }}>
              2. Target Difficulty
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: '1.25rem' }}>
              Select the evaluation level for questions.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {[
                { level: 'Beginner', desc: 'Core syntax, variables, basic fundamentals' },
                { level: 'Intermediate', desc: 'Real-world usage, design patterns, debugging' },
                { level: 'Advanced', desc: 'Performance optimization, internals, architecture' },
              ].map((item) => (
                <div
                  key={item.level}
                  onClick={() => setDifficulty(item.level)}
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-md)',
                    border: difficulty === item.level ? '2px solid var(--primary)' : '1px solid var(--border)',
                    background: difficulty === item.level ? 'var(--primary-light)' : 'var(--background-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text)' }}>
                      {item.level}
                    </span>
                    {difficulty === item.level && <FiCheckCircle style={{ color: 'var(--primary)' }} />}
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.2rem' }}>
                    {item.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Assessment Specifications (Standard 30 Questions) */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text)', marginBottom: '0.35rem' }}>
              3. Assessment Structure
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: '1.25rem' }}>
              Standardized SkillNova AI evaluation format.
            </p>

            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
                background: 'var(--background-secondary)',
                padding: '1.25rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border)',
                flex: 1,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Question Count</span>
                <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--primary)' }}>30 Questions</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Format</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text)' }}>Multiple Choice (Single Option)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Estimated Duration</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text)' }}>~45 Minutes</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Evaluation Engine</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text)' }}>Adaptive AI Diagnostics</span>
              </div>
            </div>

            <div
              style={{
                marginTop: '1.25rem',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-md)',
                background: 'var(--primary-light)',
                border: '1px solid var(--primary-border)',
                fontSize: '0.8rem',
                color: 'var(--text)',
                lineHeight: 1.5,
              }}
            >
              ℹ️ All 30 questions must be completed. Instant diagnostic scoring, weak topic detection, and AI recommendations are provided upon submission.
            </div>
          </div>
        </div>

        {/* Start Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            type="submit"
            disabled={generating}
            className="btn btn-primary btn-lg"
            style={{ minWidth: '220px' }}
          >
            {generating ? (
              <>
                <span className="animate-spin">⏳</span> Generating 30 Questions...
              </>
            ) : (
              <>
                <FiZap /> Start Assessment
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SkillAssessmentPage;
