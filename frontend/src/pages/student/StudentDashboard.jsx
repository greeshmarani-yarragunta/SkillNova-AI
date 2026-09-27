import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/authService';
import { assessmentService } from '../../services/assessmentService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiAward, FiTrendingUp, FiCheckCircle, FiClock,
  FiArrowRight, FiZap, FiPlusCircle, FiMessageSquare,
  FiBriefcase, FiFileText, FiAlertCircle
} from 'react-icons/fi';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [assessments, setAssessments] = useState([]);
  const [studentSkills, setStudentSkills] = useState([]);
  const [allSkills, setAllSkills] = useState([]);

  useEffect(() => {
    if (user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') {
      return;
    }

    const fetchDashboardData = async () => {
      try {
        const [assessData, studentSkillsData, allSkillsData] = await Promise.all([
          assessmentService.getAssessmentResults(),
          authService.getStudentSkills(),
          authService.getSkills(),
        ]);

        const assessList = Array.isArray(assessData) ? assessData : assessData.results || [];
        setAssessments(assessList);
        setStudentSkills(studentSkillsData || []);
        setAllSkills(allSkillsData || []);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  if (user?.role === 'INSTRUCTOR') {
    return <Navigate to="/instructor/dashboard" replace />;
  }
  if (user?.role === 'ADMIN') {
    return <Navigate to="/admin/dashboard" replace />;
  }

  if (loading) {
    return <LoadingSpinner message="Loading your assessment dashboard..." />;
  }

  const profile = user?.student_profile || {};

  // Top Metrics Calculation
  const testsTaken = assessments.length;
  const avgScore = testsTaken > 0
    ? Math.round(assessments.reduce((acc, curr) => acc + (curr.percentage || 0), 0) / testsTaken)
    : 0;

  const distinctSkills = new Set(assessments.map((a) => a.skill_name || a.skill)).size;

  const now = new Date();
  const testsThisMonth = assessments.filter((a) => {
    if (!a.completed_at && !a.created_at) return false;
    const testDate = new Date(a.completed_at || a.created_at);
    return testDate.getMonth() === now.getMonth() && testDate.getFullYear() === now.getFullYear();
  }).length;

  // Skill Progress mapping
  // Build a map of latest assessment scores per skill
  const skillScoreMap = {};
  assessments.forEach((a) => {
    const name = a.skill_name || 'Skill';
    if (!skillScoreMap[name]) {
      skillScoreMap[name] = {
        name,
        percentage: a.percentage,
        skill_level: a.skill_level,
        difficulty: a.difficulty,
        date: a.completed_at || a.created_at,
      };
    }
  });

  const progressSkillsList = Object.values(skillScoreMap);

  // Recommended Skills: platform skills not yet assessed or with score < 75
  const assessedSkillNames = new Set(Object.keys(skillScoreMap));
  const recommendedSkills = allSkills
    .filter((s) => !assessedSkillNames.has(s.name) || (skillScoreMap[s.name]?.percentage < 75))
    .slice(0, 4);

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Welcome Header */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, var(--surface), var(--primary-light))',
          padding: '2rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1.5rem',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.35rem' }}>
            Welcome back, {user?.first_name || user?.username}!
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
            Target Role: <strong style={{ color: 'var(--primary)' }}>{profile.target_role || 'Full Stack Developer'}</strong> • Focus on identifying skill gaps and test readiness.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link to="/assessments/new" className="btn btn-primary">
            <FiAward /> Take Assessment
          </Link>
          <Link to="/interview-prep" className="btn btn-secondary">
            <FiBriefcase /> Mock Interview
          </Link>
        </div>
      </div>

      {/* Top Cards: Tests Taken, Average Score, Skills Assessed, Tests This Month */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Tests Taken</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiCheckCircle style={{ fontSize: '1.1rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {testsTaken}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Total completed AI assessments
          </p>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Average Score</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--secondary-light)', color: 'var(--secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiTrendingUp style={{ fontSize: '1.1rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {avgScore}%
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Across all technical areas
          </p>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Skills Assessed</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--success-bg)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiZap style={{ fontSize: '1.1rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {distinctSkills}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Distinct technical stacks tested
          </p>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Tests This Month</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--warning-bg)', color: 'var(--warning)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiClock style={{ fontSize: '1.1rem' }} />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {testsThisMonth}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Activity this billing cycle
          </p>
        </div>
      </div>

      {/* Main Grid: Skill Progress & Recent Assessments */}
      <div className="grid grid-cols-2 gap-6" style={{ gridTemplateColumns: '1.1fr 1fr' }}>
        {/* Skill Progress */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>
              Skill Progress
            </h3>
            <Link to="/skills" className="btn btn-outline btn-sm">
              Explore All Skills
            </Link>
          </div>

          {progressSkillsList.length === 0 ? (
            <div style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--muted)' }}>
              <p style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>No assessed skills yet. Take an assessment to populate your skill proficiency bar.</p>
              <Link to="/assessments/new" className="btn btn-primary btn-sm">
                Take First Assessment
              </Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
              {progressSkillsList.map((skill) => (
                <div key={skill.name}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text)' }}>
                        {skill.name}
                      </span>
                      <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                        {skill.skill_level}
                      </span>
                    </div>
                    <span style={{ fontWeight: 800, fontSize: '0.95rem', color: skill.percentage >= 75 ? 'var(--success)' : skill.percentage >= 50 ? 'var(--warning)' : 'var(--danger)' }}>
                      {skill.percentage}%
                    </span>
                  </div>
                  <div className="progress-container">
                    <div
                      className="progress-bar"
                      style={{
                        width: `${skill.percentage}%`,
                        background: skill.percentage >= 75 ? 'var(--success)' : skill.percentage >= 50 ? 'var(--primary)' : 'var(--warning)',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)', marginBottom: '0.5rem' }}>
              Quick Actions
            </h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
              Accelerate your technical career readiness with AI-guided tools.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <Link
                to="/assessments/new"
                className="card card-clickable"
                style={{
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  background: 'var(--background-secondary)',
                }}
              >
                <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FiAward />
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>Take Assessment</div>
                <p style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Generate adaptive technical test</p>
              </Link>

              <Link
                to="/ai-assistant"
                className="card card-clickable"
                style={{
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  background: 'var(--background-secondary)',
                }}
              >
                <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--secondary-light)', color: 'var(--secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FiMessageSquare />
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>Ask AI</div>
                <p style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Instant technical answers & quiz</p>
              </Link>

              <Link
                to="/interview-prep"
                className="card card-clickable"
                style={{
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  background: 'var(--background-secondary)',
                }}
              >
                <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--success-bg)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FiBriefcase />
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>Practice Interview</div>
                <p style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Simulate mock interviews with feedback</p>
              </Link>

              <Link
                to="/resume-analyzer"
                className="card card-clickable"
                style={{
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  background: 'var(--background-secondary)',
                }}
              >
                <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--warning-bg)', color: 'var(--warning)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FiFileText />
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>Analyze Resume</div>
                <p style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Detect gaps against target role</p>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Assessments Section */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>
              Recent Assessments
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
              View your most recent performance evaluations and identify weak areas.
            </p>
          </div>
          <Link to="/assessment-history" className="btn btn-outline btn-sm">
            View All History <FiArrowRight />
          </Link>
        </div>

        {assessments.length === 0 ? (
          <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--muted)' }}>
            <p style={{ marginBottom: '1rem' }}>No assessments completed yet.</p>
            <Link to="/assessments/new" className="btn btn-primary btn-sm">
              Start Assessment Now
            </Link>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Skill</th>
                  <th>Difficulty</th>
                  <th>Score</th>
                  <th>Skill Level</th>
                  <th>Weak Areas</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {assessments.slice(0, 5).map((a) => (
                  <tr key={a.id}>
                    <td>
                      <span style={{ fontWeight: 700, color: 'var(--text)' }}>{a.skill_name}</span>
                    </td>
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
                    <td style={{ maxWidth: '240px' }}>
                      {a.weak_areas && a.weak_areas.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                          {a.weak_areas.slice(0, 2).map((w, idx) => (
                            <span
                              key={idx}
                              style={{
                                fontSize: '0.7rem',
                                padding: '0.15rem 0.4rem',
                                borderRadius: 'var(--radius-sm)',
                                background: 'var(--warning-bg)',
                                color: 'var(--warning)',
                                border: '1px solid var(--warning-border)',
                              }}
                            >
                              ⚠ {w}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span style={{ fontSize: '0.8rem', color: 'var(--success)' }}>✓ Strong across all</span>
                      )}
                    </td>
                    <td style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
                      {a.completed_at ? new Date(a.completed_at).toLocaleDateString('en-US', { day: 'numeric', month: 'short' }) : 'Recent'}
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

      {/* Recommended Skills */}
      {recommendedSkills.length > 0 && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>
                Recommended Skills
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
                AI-recommended technical competencies for your target career role.
              </p>
            </div>
            <Link to="/skills" className="btn btn-outline btn-sm">
              All Skills <FiArrowRight />
            </Link>
          </div>

          <div className="grid grid-cols-4 gap-4">
            {recommendedSkills.map((s) => (
              <div
                key={s.id}
                className="card"
                style={{
                  background: 'var(--background-secondary)',
                  padding: '1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.85rem',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text)' }}>
                      {s.name}
                    </span>
                    <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>
                      {s.category || 'Tech'}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--muted)', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {s.description || 'Core technical capability evaluation.'}
                  </p>
                </div>

                <Link
                  to={`/assessments/new?skill=${s.id}`}
                  className="btn btn-primary btn-sm"
                  style={{ width: '100%' }}
                >
                  <FiAward /> Take Test
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
