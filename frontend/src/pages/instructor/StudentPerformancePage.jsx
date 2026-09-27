import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { aiService } from '../../services/aiService';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiUsers, FiActivity, FiAward, FiSearch,
  FiFilter, FiCheckCircle, FiAlertTriangle, FiArrowRight
} from 'react-icons/fi';

const StudentPerformancePage = () => {
  const [performances, setPerformances] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedSkill, setSelectedSkill] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [perfData, skillsData] = await Promise.all([
          aiService.getInstructorPerformance(),
          authService.getSkills(),
        ]);
        setPerformances(perfData || []);
        setSkills(skillsData || []);
      } catch (err) {
        console.error('Failed to load performance metrics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredPerformances = performances.filter((p) => {
    const matchesSkill = !selectedSkill || String(p.skill_name?.toLowerCase()) === String(selectedSkill.toLowerCase());
    const matchesSearch =
      !search ||
      p.student_email?.toLowerCase().includes(search.toLowerCase()) ||
      p.student_role?.toLowerCase().includes(search.toLowerCase()) ||
      p.skill_name?.toLowerCase().includes(search.toLowerCase());
    return matchesSkill && matchesSearch;
  });

  const totalAttempts = performances.length;
  const avgScore = totalAttempts > 0
    ? Math.round(performances.reduce((acc, curr) => acc + (curr.percentage || 0), 0) / totalAttempts)
    : 0;
  const highPerformers = performances.filter((p) => p.percentage >= 80).length;
  const needsPractice = performances.filter((p) => p.percentage < 60).length;

  if (loading) return <LoadingSpinner message="Analyzing student assessment performance..." />;

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.25rem' }}>
          Student Assessment Performance
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
          Evaluate student test results, identify common knowledge bottlenecks, and monitor proficiency trends.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card">
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Test Attempts</span>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)', marginTop: '0.25rem' }}>
            {totalAttempts}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Total completed assessments
          </p>
        </div>

        <div className="card">
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Average Score</span>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--primary)', marginTop: '0.25rem' }}>
            {avgScore}%
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Across all skills tested
          </p>
        </div>

        <div className="card">
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>High Performers (≥80%)</span>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--success)', marginTop: '0.25rem' }}>
            {highPerformers}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Demonstrating advanced mastery
          </p>
        </div>

        <div className="card">
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Needs Practice (&lt;60%)</span>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--warning)', marginTop: '0.25rem' }}>
            {needsPractice}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Requiring targeted study
          </p>
        </div>
      </div>

      {/* Performance Filter Bar */}
      <div
        className="card"
        style={{
          padding: '1.25rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flex: 1, minWidth: '240px' }}>
          <FiSearch style={{ color: 'var(--muted)' }} />
          <input
            type="text"
            className="form-input"
            style={{ padding: '0.5rem 0.75rem', border: 'none', background: 'transparent' }}
            placeholder="Search by student email, target role, or skill..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <FiFilter style={{ color: 'var(--muted)', fontSize: '0.9rem' }} />
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedSkill}
            onChange={(e) => setSelectedSkill(e.target.value)}
          >
            <option value="">All Technical Skills</option>
            {skills.map((s) => (
              <option key={s.id} value={s.name}>{s.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Performance Table */}
      {filteredPerformances.length === 0 ? (
        <div className="card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--muted)' }}>
          <FiActivity style={{ fontSize: '2rem', marginBottom: '0.5rem' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>No Test Records Found</h3>
          <p style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
            No assessment attempts match the selected criteria.
          </p>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Student Email</th>
                <th>Target Role</th>
                <th>Skill</th>
                <th>Difficulty</th>
                <th>Score</th>
                <th>Estimated Level</th>
                <th>Detected Weak Topics</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredPerformances.map((p) => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 600, color: 'var(--text)' }}>
                    {p.student_email}
                  </td>
                  <td>
                    <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
                      {p.student_role || 'Developer'}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>
                      {p.skill_name}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                      {p.difficulty}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 800, color: p.percentage >= 75 ? 'var(--success)' : p.percentage >= 50 ? 'var(--warning)' : 'var(--danger)' }}>
                      {p.percentage}%
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${p.skill_level === 'Advanced' ? 'badge-success' : p.skill_level === 'Intermediate' ? 'badge-primary' : 'badge-warning'}`}>
                      {p.skill_level}
                    </span>
                  </td>
                  <td style={{ maxWidth: '220px' }}>
                    {p.weak_areas && p.weak_areas.length > 0 ? (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                        {p.weak_areas.slice(0, 2).map((w, i) => (
                          <span
                            key={i}
                            style={{
                              fontSize: '0.7rem',
                              padding: '0.15rem 0.4rem',
                              borderRadius: 'var(--radius-sm)',
                              background: 'var(--warning-bg)',
                              color: 'var(--warning)',
                            }}
                          >
                            ⚠ {w}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--success)' }}>✓ Strong</span>
                    )}
                  </td>
                  <td style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
                    {p.completed_at ? new Date(p.completed_at).toLocaleDateString() : 'Recent'}
                  </td>
                  <td>
                    <Link to={`/assessments/${p.id}`} className="btn btn-outline btn-sm">
                      Inspect
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default StudentPerformancePage;
