import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { assessmentService } from '../../services/assessmentService';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import { FiAward, FiSearch, FiFilter, FiCheckCircle } from 'react-icons/fi';

const AssessmentsManagementPage = () => {
  const [assessments, setAssessments] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedSkill, setSelectedSkill] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');

  useEffect(() => {
    const loadAssessments = async () => {
      try {
        setLoading(true);
        const [assessData, skillsData] = await Promise.all([
          assessmentService.getAdminAssessments(),
          authService.getSkills(),
        ]);
        const list = Array.isArray(assessData) ? assessData : assessData.results || [];
        setAssessments(list);
        setSkills(skillsData || []);
      } catch (err) {
        console.error('Failed to load assessment logs', err);
      } finally {
        setLoading(false);
      }
    };
    loadAssessments();
  }, []);

  const filteredAssessments = assessments.filter((a) => {
    const matchesSkill = !selectedSkill || String(a.skill) === String(selectedSkill);
    const matchesDiff = !selectedDifficulty || a.difficulty?.toLowerCase() === selectedDifficulty.toLowerCase();
    const matchesSearch =
      !search ||
      a.student_email?.toLowerCase().includes(search.toLowerCase()) ||
      a.skill_name?.toLowerCase().includes(search.toLowerCase());
    return matchesSkill && matchesDiff && matchesSearch;
  });

  if (loading) {
    return <LoadingSpinner message="Loading platform assessment records..." />;
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.25rem' }}>
          Platform Assessments Log
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
          System-wide record of student test attempts, diagnostic scoring, and level evaluations.
        </p>
      </div>

      {/* Filter Bar */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flex: 1, minWidth: '220px' }}>
          <FiSearch style={{ color: 'var(--muted)' }} />
          <input
            type="text"
            className="form-input"
            style={{ padding: '0.5rem 0.75rem', border: 'none', background: 'transparent' }}
            placeholder="Search by student email or skill..."
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
            <option value="">All Skills</option>
            {skills.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>

          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
          >
            <option value="">All Difficulties</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-container" style={{ border: 'none' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Skill</th>
                <th>Difficulty</th>
                <th>Score</th>
                <th>Assessed Level</th>
                <th>Weak Topics</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAssessments.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--muted)' }}>
                    No assessments match the selected filters.
                  </td>
                </tr>
              ) : (
                filteredAssessments.map((a) => (
                  <tr key={a.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text)' }}>
                      {a.student_email || `User #${a.student}`}
                    </td>
                    <td style={{ fontWeight: 700 }}>{a.skill_name}</td>
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
                    <td style={{ maxWidth: '200px' }}>
                      {a.weak_areas && a.weak_areas.length > 0 ? (
                        <span style={{ fontSize: '0.75rem', color: 'var(--warning)' }}>
                          {a.weak_areas.slice(0, 2).join(', ')}
                        </span>
                      ) : (
                        <span style={{ fontSize: '0.8rem', color: 'var(--success)' }}>✓ Strong</span>
                      )}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>
                      {new Date(a.completed_at || a.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <Link to={`/assessments/${a.id}`} className="btn btn-outline btn-sm">
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AssessmentsManagementPage;
