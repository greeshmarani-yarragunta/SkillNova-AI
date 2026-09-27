import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { aiService } from '../../services/aiService';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiAward, FiHelpCircle, FiActivity,
  FiPlusCircle, FiList, FiTrendingUp, FiArrowRight, FiCheckCircle
} from 'react-icons/fi';

const InstructorDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsData, questionsData] = await Promise.all([
          aiService.getInstructorStats(),
          aiService.getInstructorQuestions(),
        ]);
        setStats(statsData);
        setQuestions(questionsData || []);
      } catch (err) {
        console.error('Failed to load instructor assessment analytics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading instructor assessment analytics..." />;
  }

  const displayName = user?.first_name
    ? `${user.first_name}${user.last_name ? ' ' + user.last_name : ''}`
    : (user?.name || user?.username || 'Dr. Marcus');

  const totalQuestionsCount = stats?.total_questions || questions.length || 0;

  // Compute Questions by Skill
  const questionsBySkill = questions.reduce((acc, q) => {
    const skillName = q.skill_name || 'General';
    acc[skillName] = (acc[skillName] || 0) + 1;
    return acc;
  }, {});

  // Compute Questions by Difficulty
  const questionsByDifficulty = questions.reduce(
    (acc, q) => {
      const diff = q.difficulty || 'Intermediate';
      if (acc[diff] !== undefined) {
        acc[diff] += 1;
      } else {
        acc[diff] = 1;
      }
      return acc;
    },
    { Beginner: 0, Intermediate: 0, Advanced: 0 }
  );

  const skillsList = Object.entries(questionsBySkill);

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* 1. Instructor Welcome Section */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, var(--surface), var(--primary-light))',
          padding: '2rem 2.25rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1.5rem',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.35rem', letterSpacing: '-0.02em' }}>
            Welcome back, {displayName}!
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: '0.95rem', margin: 0 }}>
            Manage technical assessments, questions, and student performance.
          </p>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
          <Link to="/instructor/questions?new=true" className="btn btn-primary">
            <FiPlusCircle /> Create Question
          </Link>
          <Link to="/instructor/ai-questions" className="btn btn-secondary">
            <FiHelpCircle /> AI Generate Questions
          </Link>
        </div>
      </div>

      {/* 2. Instructor Statistics: 4 Key Metrics */}
      <div className="grid grid-cols-4 gap-4">
        {/* Metric 1: Total Questions */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Total Questions</span>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiList style={{ fontSize: '1.15rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {totalQuestionsCount}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem', margin: 0 }}>
            In instructor question pool
          </p>
        </div>

        {/* Metric 2: Assessments Created */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Assessments Created</span>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--secondary-light)', color: 'var(--secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiAward style={{ fontSize: '1.15rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {stats?.total_assessments || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem', margin: 0 }}>
            Platform evaluations generated
          </p>
        </div>

        {/* Metric 3: Student Attempts */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Student Attempts</span>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--warning-bg)', color: 'var(--warning)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiActivity style={{ fontSize: '1.15rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {stats?.student_attempts || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem', margin: 0 }}>
            Completed student submissions
          </p>
        </div>

        {/* Metric 4: Average Student Score */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Average Student Score</span>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--success-bg)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiTrendingUp style={{ fontSize: '1.15rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {stats?.avg_score || 0}%
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem', margin: 0 }}>
            Cohort assessment average
          </p>
        </div>
      </div>

      {/* 3. Quick Actions (Only 4 Instructor Actions) */}
      <div className="card">
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text)', marginBottom: '1.25rem' }}>
          Quick Actions
        </h2>
        <div className="grid grid-cols-4 gap-4">
          <Link
            to="/instructor/questions?new=true"
            className="instructor-quick-action"
          >
            <div className="quick-action-icon" style={{ background: 'var(--primary-light)', color: 'var(--primary)' }}>
              <FiPlusCircle size={22} />
            </div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text)', margin: '0.65rem 0 0.25rem 0' }}>
              Create Question
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--muted)', margin: 0 }}>
              Author a new technical question manually
            </p>
          </Link>

          <Link
            to="/instructor/ai-questions"
            className="instructor-quick-action"
          >
            <div className="quick-action-icon" style={{ background: 'var(--secondary-light)', color: 'var(--secondary)' }}>
              <FiHelpCircle size={22} />
            </div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text)', margin: '0.65rem 0 0.25rem 0' }}>
              AI Generate Questions
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--muted)', margin: 0 }}>
              Draft AI multiple-choice questions
            </p>
          </Link>

          <Link
            to="/instructor/questions"
            className="instructor-quick-action"
          >
            <div className="quick-action-icon" style={{ background: 'var(--success-bg)', color: 'var(--success)' }}>
              <FiList size={22} />
            </div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text)', margin: '0.65rem 0 0.25rem 0' }}>
              Question Bank
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--muted)', margin: 0 }}>
              Review, filter, and edit question pool
            </p>
          </Link>

          <Link
            to="/instructor/performance"
            className="instructor-quick-action"
          >
            <div className="quick-action-icon" style={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}>
              <FiActivity size={22} />
            </div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text)', margin: '0.65rem 0 0.25rem 0' }}>
              Student Performance
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--muted)', margin: 0 }}>
              Inspect student scores and topic breakdowns
            </p>
          </Link>
        </div>
      </div>

      {/* 4. Question Bank Overview */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text)' }}>
              Question Bank Overview
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--muted)', margin: 0 }}>
              Inventory distribution across technical disciplines and difficulty tiers.
            </p>
          </div>
          <Link to="/instructor/questions" className="btn btn-outline btn-sm">
            View Question Bank <FiArrowRight style={{ marginLeft: '0.35rem' }} />
          </Link>
        </div>

        <div className="grid grid-cols-2 gap-6" style={{ gridTemplateColumns: '1.2fr 0.8fr' }}>
          {/* Questions by Skill */}
          <div style={{ background: 'var(--bg-subtle)', borderRadius: 'var(--radius-md)', padding: '1.25rem', border: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Questions by Skill
            </h3>
            {skillsList.length === 0 ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--muted)', textAlign: 'center', padding: '1rem 0' }}>
                No questions authored yet.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {skillsList.map(([skillName, count]) => {
                  const pct = totalQuestionsCount > 0 ? Math.round((count / totalQuestionsCount) * 100) : 0;
                  return (
                    <div key={skillName}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                        <span style={{ fontWeight: 600, color: 'var(--text)' }}>{skillName}</span>
                        <span style={{ color: 'var(--muted)', fontWeight: 600 }}>{count} questions ({pct}%)</span>
                      </div>
                      <div style={{ width: '100%', height: '6px', background: 'var(--border)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div
                          style={{
                            width: `${pct}%`,
                            height: '100%',
                            background: 'linear-gradient(90deg, var(--primary), var(--secondary))',
                            borderRadius: '4px',
                            transition: 'width 0.4s ease',
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Questions by Difficulty Tier */}
          <div style={{ background: 'var(--bg-subtle)', borderRadius: 'var(--radius-md)', padding: '1.25rem', border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Questions by Difficulty
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem 0.85rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="badge badge-success" style={{ fontSize: '0.75rem' }}>Beginner</span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Fundamental syntax & concepts</span>
                  </div>
                  <span style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text)' }}>
                    {questionsByDifficulty.Beginner}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem 0.85rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="badge badge-primary" style={{ fontSize: '0.75rem' }}>Intermediate</span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Applied logic & patterns</span>
                  </div>
                  <span style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text)' }}>
                    {questionsByDifficulty.Intermediate}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem 0.85rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="badge badge-warning" style={{ fontSize: '0.75rem' }}>Advanced</span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>System edge-cases & internals</span>
                  </div>
                  <span style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text)' }}>
                    {questionsByDifficulty.Advanced}
                  </span>
                </div>
              </div>
            </div>

            <div style={{ marginTop: '1rem', paddingTop: '0.85rem', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
              <span style={{ color: 'var(--muted)' }}>Total Pool Size:</span>
              <strong style={{ color: 'var(--text)' }}>{totalQuestionsCount} Questions</strong>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Student Performance Overview */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text)' }}>
              Recent Student Assessment Attempts
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--muted)', margin: 0 }}>
              Latest test completions and diagnostic benchmark results.
            </p>
          </div>
          <Link
            to="/instructor/performance"
            style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            All Performance <FiArrowRight />
          </Link>
        </div>

        {!stats?.recent_attempts || stats.recent_attempts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--muted)' }}>
            No student assessment submissions recorded yet.
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student Email</th>
                  <th>Skill</th>
                  <th>Difficulty</th>
                  <th>Score</th>
                  <th>Estimated Level</th>
                  <th>Completed Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_attempts.map((a) => (
                  <tr key={a.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text)' }}>{a.student_email}</td>
                    <td>{a.skill_name}</td>
                    <td>
                      <span className="badge badge-neutral">{a.difficulty}</span>
                    </td>
                    <td>
                      <span style={{ fontWeight: 800, color: a.percentage >= 70 ? 'var(--success)' : a.percentage >= 50 ? 'var(--warning)' : 'var(--danger)' }}>
                        {a.percentage}%
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${a.skill_level === 'Advanced' ? 'badge-success' : a.skill_level === 'Intermediate' ? 'badge-primary' : 'badge-warning'}`}>
                        {a.skill_level}
                      </span>
                    </td>
                    <td style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
                      {a.completed_at ? new Date(a.completed_at).toLocaleDateString() : 'Recent'}
                    </td>
                    <td>
                      <Link to={`/assessments/${a.id}`} className="btn btn-outline btn-sm">
                        View Result
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <style>{`
        .instructor-quick-action {
          display: flex;
          flex-direction: column;
          padding: 1.25rem 1rem;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          text-decoration: none;
          color: inherit;
          transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .instructor-quick-action:hover {
          transform: translateY(-2px);
          border-color: var(--primary);
          box-shadow: var(--shadow-md);
        }
        .quick-action-icon {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </div>
  );
};

export default InstructorDashboard;
