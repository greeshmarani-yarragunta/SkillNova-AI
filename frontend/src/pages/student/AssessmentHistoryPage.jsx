import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { assessmentService } from '../../services/assessmentService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiClock, FiAward, FiSearch, FiFilter, FiArrowRight,
  FiAlertTriangle, FiCheckCircle, FiPlusCircle
} from 'react-icons/fi';

const AssessmentHistoryPage = () => {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('ALL');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await assessmentService.getAssessmentResults();
      const list = Array.isArray(data) ? data : data.results || [];
      setAssessments(list);
    } catch (err) {
      console.error('Failed to load assessment history:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredAssessments = assessments.filter((item) => {
    const matchesSearch =
      item.skill_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.difficulty?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.skill_level?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDiff =
      selectedDifficulty === 'ALL' ||
      item.difficulty?.toLowerCase() === selectedDifficulty.toLowerCase();
    return matchesSearch && matchesDiff;
  });

  const getLevelBadgeClass = (level) => {
    if (level === 'Advanced' || level === 'Strong' || level === 'Proficient') return 'badge-success';
    if (level === 'Intermediate') return 'badge-primary';
    return 'badge-warning';
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'Recent';
    const d = new Date(isoString);
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  if (loading) return <LoadingSpinner message="Loading assessment history..." />;

  return (
    <div className="fade-in">
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.25rem' }}>
            Assessment History
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
            Review your past AI skill tests, track progress, and inspect weak topics.
          </p>
        </div>

        <Link to="/assessments/new" className="btn btn-primary">
          <FiPlusCircle /> Take New Assessment
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div
        className="card"
        style={{
          marginBottom: '1.5rem',
          padding: '1rem 1.25rem',
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
            placeholder="Search by skill name or level..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FiFilter style={{ color: 'var(--muted)', fontSize: '0.9rem' }} />
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
          >
            <option value="ALL">All Difficulties</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
      </div>

      {/* History Table */}
      {filteredAssessments.length === 0 ? (
        <div
          className="card"
          style={{
            padding: '3rem 1.5rem',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1rem',
          }}
        >
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'var(--primary-light)',
              color: 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.75rem',
            }}
          >
            <FiAward />
          </div>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text)', marginBottom: '0.35rem' }}>
              No Assessments Found
            </h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.9rem', maxWidth: '420px' }}>
              {assessments.length === 0
                ? "You haven't taken any skill assessments yet. Test your technical proficiency now!"
                : "No assessments match your current search or filter criteria."}
            </p>
          </div>
          <Link to="/assessments/new" className="btn btn-primary">
            Start Your First Assessment
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
                <th>Estimated Level</th>
                <th>Weak Topics</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAssessments.map((item) => (
                <tr key={item.id}>
                  {/* Skill */}
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: 'var(--text)' }}>
                      <span>{item.skill_name}</span>
                    </div>
                  </td>

                  {/* Difficulty */}
                  <td>
                    <span className="badge badge-neutral" style={{ fontSize: '0.75rem' }}>
                      {item.difficulty}
                    </span>
                  </td>

                  {/* Score */}
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontWeight: 800, fontSize: '1rem', color: item.percentage >= 70 ? 'var(--success)' : item.percentage >= 50 ? 'var(--warning)' : 'var(--danger)' }}>
                        {item.percentage}%
                      </span>
                    </div>
                  </td>

                  {/* Level */}
                  <td>
                    <span className={`badge ${getLevelBadgeClass(item.skill_level)}`}>
                      {item.skill_level}
                    </span>
                  </td>

                  {/* Weak topics */}
                  <td style={{ maxWidth: '240px' }}>
                    {item.weak_areas && item.weak_areas.length > 0 ? (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                        {item.weak_areas.slice(0, 2).map((weak, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: '0.725rem',
                              padding: '0.15rem 0.45rem',
                              borderRadius: 'var(--radius-sm)',
                              background: 'var(--warning-bg)',
                              color: 'var(--warning)',
                              border: '1px solid var(--warning-border)',
                            }}
                          >
                            ⚠ {weak}
                          </span>
                        ))}
                        {item.weak_areas.length > 2 && (
                          <span style={{ fontSize: '0.725rem', color: 'var(--muted)', alignSelf: 'center' }}>
                            +{item.weak_areas.length - 2} more
                          </span>
                        )}
                      </div>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--success)' }}>
                        ✓ None detected
                      </span>
                    )}
                  </td>

                  {/* Date */}
                  <td style={{ color: 'var(--muted)', fontSize: '0.85rem', whiteSpace: 'nowrap' }}>
                    {formatDate(item.completed_at || item.created_at)}
                  </td>

                  {/* View result button */}
                  <td>
                    <Link
                      to={`/assessments/${item.id}`}
                      className="btn btn-outline btn-sm"
                      style={{ gap: '0.35rem' }}
                    >
                      View Result <FiArrowRight />
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

export default AssessmentHistoryPage;
