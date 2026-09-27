import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { assessmentService } from '../../services/assessmentService';
import LoadingSpinner from '../../components/LoadingSpinner';
import confetti from 'canvas-confetti';
import {
  FiAward, FiCheckCircle, FiAlertTriangle, FiArrowRight,
  FiRotateCcw, FiList, FiClock, FiCheck, FiX, FiHelpCircle, FiUsers
} from 'react-icons/fi';

const AssessmentResultPage = () => {
  const { id } = useParams();
  const { isInstructor, isAdmin } = useAuth();
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeQuestionTab, setActiveQuestionTab] = useState(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        setLoading(true);
        setError('');
        const data = await assessmentService.getAssessmentDetail(id);
        setAssessment(data);

        // Subtle confetti celebration for strong scores
        if (data.percentage >= 70) {
          confetti({
            particleCount: 80,
            spread: 60,
            origin: { y: 0.6 },
          });
        }
      } catch (err) {
        const statusCode = err.response?.status;
        if (statusCode === 401) {
          setError('Your session has expired. Please log in again.');
        } else if (statusCode === 403) {
          setError('You do not have permission to view this assessment.');
        } else if (statusCode === 404) {
          setError('Assessment result not found.');
        } else if (statusCode >= 500) {
          setError('Unable to load assessment results right now.');
        } else {
          setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to load assessment results.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [id]);

  if (loading) {
    return <LoadingSpinner message="Calculating assessment diagnostic & AI evaluation..." />;
  }

  if (error || !assessment) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <div
          style={{
            maxWidth: '480px',
            margin: '0 auto',
            background: 'var(--surface)',
            padding: '2.5rem 2rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-md)',
          }}
        >
          <FiAlertTriangle style={{ fontSize: '2.5rem', color: 'var(--warning)', marginBottom: '1rem' }} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text)' }}>
            {error || 'Assessment result not found.'}
          </h2>
          <p style={{ color: 'var(--muted)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.5 }}>
            {error === 'You do not have permission to view this assessment.'
              ? 'You are not authorized to view assessment results belonging to another student.'
              : error === 'Assessment result not found.'
              ? 'The requested assessment could not be found in our records.'
              : error === 'Your session has expired. Please log in again.'
              ? 'Please log in with your credentials to view this assessment.'
              : 'Unable to retrieve this assessment result at this time.'}
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
            {isInstructor ? (
              <Link to="/instructor/performance" className="btn btn-primary">
                Return to Student Performance
              </Link>
            ) : (
              <Link to="/dashboard" className="btn btn-primary">
                Return to Dashboard
              </Link>
            )}
          </div>
        </div>
      </div>
    );
  }

  const totalQuestions = assessment.question_count || assessment.questions?.length || 30;
  const correctCount = assessment.score !== undefined && assessment.score !== null ? Math.round(assessment.score) : Math.round((assessment.percentage / 100) * totalQuestions);
  const incorrectCount = Math.max(0, totalQuestions - correctCount);

  // SVG Circular Score Ring geometry
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (assessment.percentage / 100) * circumference;

  const getScoreColor = (percent) => {
    if (percent >= 75) return 'var(--success)';
    if (percent >= 55) return 'var(--primary)';
    return 'var(--warning)';
  };

  return (
    <div className="fade-in" style={{ maxWidth: '860px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Section: Circular Score Indicator & Diagnostic Estimate */}
      <div
        className="card"
        style={{
          padding: '2.5rem 2rem',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          position: 'relative',
        }}
      >
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.65rem', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)', margin: 0 }}>
              {assessment.skill_name} Assessment
            </h1>
            {isInstructor && (
              <span className="badge badge-primary" style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>
                Instructor Review
              </span>
            )}
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '0.9rem', margin: 0 }}>
            Difficulty: <strong>{assessment.difficulty}</strong> • Completed {assessment.completed_at ? new Date(assessment.completed_at).toLocaleDateString() : 'Today'}
            {assessment.student_email && (
              <span> • Student: <strong style={{ color: 'var(--text)' }}>{assessment.student_name || assessment.student_email}</strong></span>
            )}
          </p>
        </div>

        {/* Large Circular Score Indicator */}
        <div style={{ position: 'relative', width: '160px', height: '160px', margin: '0.5rem 0 1.25rem 0' }}>
          <svg width="160" height="160" viewBox="0 0 160 160">
            {/* Background Track */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              fill="transparent"
              stroke="var(--background-secondary)"
              strokeWidth="12"
            />
            {/* Animated Score Progress */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              fill="transparent"
              stroke={getScoreColor(assessment.percentage)}
              strokeWidth="12"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform="rotate(-90 80 80)"
              style={{ transition: 'stroke-dashoffset 1s ease' }}
            />
          </svg>
          <div
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text)', lineHeight: 1 }}>
              {assessment.percentage}%
            </span>
            <span
              style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: getScoreColor(assessment.percentage),
                marginTop: '0.25rem',
              }}
            >
              {assessment.skill_level}
            </span>
          </div>
        </div>

        {/* Disclaimer / Accuracy Note */}
        <p
          style={{
            fontSize: '0.825rem',
            color: 'var(--muted)',
            maxWidth: '520px',
            lineHeight: 1.5,
            background: 'var(--background-secondary)',
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-full)',
            border: '1px solid var(--border)',
          }}
        >
          ℹ️ Assessment Estimate: This evaluation reflects estimated proficiency based on test questions answered and topic coverage.
        </p>
      </div>

      {/* Grid: Strong Areas, Needs Improvement, AI Recommendations */}
      <div className="grid grid-cols-3 gap-6">
        {/* Strong Areas Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--success-bg)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiCheckCircle />
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)' }}>
              Strong Areas
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
            {assessment.strong_areas && assessment.strong_areas.length > 0 ? (
              assessment.strong_areas.map((topic, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.5rem',
                    fontSize: '0.875rem',
                    color: 'var(--text)',
                    padding: '0.45rem 0.65rem',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--success-bg)',
                    border: '1px solid var(--success-border)',
                  }}
                >
                  <span style={{ color: 'var(--success)', fontWeight: 700 }}>✓</span>
                  <span>{topic}</span>
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>No dominant areas identified yet.</p>
            )}
          </div>
        </div>

        {/* Needs Improvement Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--warning-bg)', color: 'var(--warning)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiAlertTriangle />
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)' }}>
              Needs Improvement
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
            {assessment.weak_areas && assessment.weak_areas.length > 0 ? (
              assessment.weak_areas.map((topic, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.5rem',
                    fontSize: '0.875rem',
                    color: 'var(--text)',
                    padding: '0.45rem 0.65rem',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--warning-bg)',
                    border: '1px solid var(--warning-border)',
                  }}
                >
                  <span style={{ color: 'var(--warning)', fontWeight: 700 }}>⚠</span>
                  <span>{topic}</span>
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--success)', fontSize: '0.85rem' }}>No critical weak areas identified.</p>
            )}
          </div>
        </div>

        {/* AI Recommendations Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiAward />
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)' }}>
              AI Recommendations
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', flex: 1 }}>
            {assessment.recommendations && assessment.recommendations.length > 0 ? (
              assessment.recommendations.map((rec, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.5rem',
                    fontSize: '0.85rem',
                    color: 'var(--text)',
                    lineHeight: 1.4,
                  }}
                >
                  <span
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: 'var(--primary-light)',
                      color: 'var(--primary)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      flexShrink: 0,
                      marginTop: '1px',
                    }}
                  >
                    {i + 1}
                  </span>
                  <span>{rec}</span>
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>Keep practicing technical assessments.</p>
            )}
          </div>
        </div>
      </div>

      {/* Assessment Summary Section */}
      <div className="card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)', marginBottom: '1.25rem' }}>
          Assessment Summary
        </h3>

        <div className="grid grid-cols-4 gap-4" style={{ marginBottom: '1.75rem' }}>
          <div style={{ background: 'var(--background-secondary)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>Total Questions</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text)', marginTop: '0.25rem' }}>
              {totalQuestions}
            </div>
          </div>

          <div style={{ background: 'var(--background-secondary)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>Correct</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--success)', marginTop: '0.25rem' }}>
              {correctCount}
            </div>
          </div>

          <div style={{ background: 'var(--background-secondary)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>Incorrect</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--danger)', marginTop: '0.25rem' }}>
              {incorrectCount}
            </div>
          </div>

          <div style={{ background: 'var(--background-secondary)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>Score</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary)', marginTop: '0.25rem' }}>
              {assessment.percentage}%
            </div>
          </div>
        </div>

        {/* Buttons: Retake Test, Try Another Skill, View History, or Instructor Navigation */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', justifyContent: 'center' }}>
          {isInstructor ? (
            <>
              <Link
                to="/instructor/performance"
                className="btn btn-primary"
                style={{ minWidth: '180px' }}
              >
                <FiUsers /> Back to Performance
              </Link>
              <Link
                to="/instructor/dashboard"
                className="btn btn-secondary"
                style={{ minWidth: '160px' }}
              >
                Instructor Dashboard
              </Link>
            </>
          ) : (
            <>
              <Link
                to={`/assessments/new?skill=${assessment.skill}`}
                className="btn btn-primary"
                style={{ minWidth: '160px' }}
              >
                <FiRotateCcw /> Retake Test
              </Link>
              <Link
                to="/skills"
                className="btn btn-secondary"
                style={{ minWidth: '160px' }}
              >
                Try Another Skill
              </Link>
              <Link
                to="/assessment-history"
                className="btn btn-outline"
                style={{ minWidth: '160px' }}
              >
                <FiList /> View History
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Detailed Question Review Section */}
      {assessment.questions && assessment.questions.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)', marginBottom: '0.5rem' }}>
            Detailed Question Breakdown
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginBottom: '1.5rem' }}>
            Review your answers, correct solutions, and explanations.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {assessment.questions.map((q, idx) => {
              const isCorrect = q.is_correct;
              const isOpen = activeQuestionTab === q.id || activeQuestionTab === null;

              return (
                <div
                  key={q.id}
                  style={{
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-md)',
                    overflow: 'hidden',
                    background: 'var(--background-secondary)',
                  }}
                >
                  <div
                    onClick={() => setActiveQuestionTab(activeQuestionTab === q.id ? -1 : q.id)}
                    style={{
                      padding: '1rem 1.25rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      background: 'var(--surface)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span
                        style={{
                          width: '24px',
                          height: '24px',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          background: isCorrect ? 'var(--success-bg)' : 'var(--danger-bg)',
                          color: isCorrect ? 'var(--success)' : 'var(--danger)',
                          border: isCorrect ? '1px solid var(--success-border)' : '1px solid var(--danger-border)',
                        }}
                      >
                        {isCorrect ? '✓' : '✕'}
                      </span>
                      <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text)' }}>
                        Q{idx + 1}: {q.question_text.slice(0, 75)}...
                      </span>
                    </div>

                    <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                      {q.topic || 'Core'}
                    </span>
                  </div>

                  <div style={{ padding: '1.25rem', borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <p style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text)' }}>
                      {q.question_text}
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem', fontSize: '0.85rem' }}>
                      {['A', 'B', 'C', 'D'].map((optKey) => {
                        const optText = q[`option_${optKey.toLowerCase()}`];
                        const isStudentChoice = q.user_answer === optKey;
                        const isCorrectOption = q.correct_option === optKey;

                        let bg = 'var(--surface)';
                        let border = '1px solid var(--border)';
                        let color = 'var(--text-secondary)';

                        if (isCorrectOption) {
                          bg = 'var(--success-bg)';
                          border = '1px solid var(--success-border)';
                          color = 'var(--success)';
                        } else if (isStudentChoice && !isCorrectOption) {
                          bg = 'var(--danger-bg)';
                          border = '1px solid var(--danger-border)';
                          color = 'var(--danger)';
                        }

                        return (
                          <div
                            key={optKey}
                            style={{
                              padding: '0.65rem 0.85rem',
                              borderRadius: 'var(--radius-sm)',
                              background: bg,
                              border: border,
                              color: color,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                            }}
                          >
                            <strong>{optKey}:</strong> {optText}
                            {isStudentChoice && (
                              <span style={{ fontSize: '0.7rem', fontWeight: 700 }}>
                                {isInstructor ? '(Student Answer)' : '(Your Answer)'}
                              </span>
                            )}
                            {isCorrectOption && <span style={{ fontSize: '0.7rem', fontWeight: 700 }}>✓ Correct</span>}
                          </div>
                        );
                      })}
                    </div>

                    {q.explanation && (
                      <div
                        style={{
                          marginTop: '0.5rem',
                          padding: '0.75rem',
                          borderRadius: 'var(--radius-sm)',
                          background: 'var(--surface)',
                          fontSize: '0.825rem',
                          color: 'var(--muted)',
                          lineHeight: 1.5,
                          borderLeft: '3px solid var(--primary)',
                        }}
                      >
                        <strong>Explanation:</strong> {q.explanation}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default AssessmentResultPage;
