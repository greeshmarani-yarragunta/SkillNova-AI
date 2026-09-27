import React, { useState, useEffect } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiCheck, FiPlus, FiAward, FiSearch, FiCode,
  FiDatabase, FiCpu, FiLayers, FiCheckCircle
} from 'react-icons/fi';

const SkillsPage = () => {
  const { user } = useAuth();
  const [skills, setSkills] = useState([]);
  const [studentSkills, setStudentSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [actionLoading, setActionLoading] = useState(null);

  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const [allSkills, userSkills] = await Promise.all([
        authService.getSkills(),
        authService.getStudentSkills(),
      ]);
      setSkills(allSkills);
      setStudentSkills(userSkills || []);
    } catch (err) {
      console.error('Failed to load skills', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'INSTRUCTOR') return;
    fetchData();
  }, [user]);

  if (user?.role === 'INSTRUCTOR') {
    return <Navigate to="/instructor/dashboard" replace />;
  }

  const handleToggleTrack = async (skill) => {
    const existing = studentSkills.find((s) => s.skill === skill.id || s.skill_details?.id === skill.id);
    setActionLoading(skill.id);

    try {
      if (existing) {
        await authService.removeStudentSkill(existing.id);
      } else {
        await authService.addStudentSkill(skill.id, 'Beginner');
      }
      await fetchData();
    } catch (err) {
      console.error('Error toggling skill', err);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading skill library..." />;
  }

  const categories = ['All', 'Programming', 'Framework', 'Database', 'Core CS', 'AI/ML', 'DevOps'];

  const filteredSkills = skills.filter((s) => {
    const matchesCat = category === 'All' || s.category === category;
    const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          s.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.35rem' }}>
            Technical Skill Library
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Select skills to track in your personal portfolio, evaluate proficiency, and practice 30-question assessments.
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div
        className="card"
        style={{
          padding: '1.25rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
        }}
      >
        {/* Category Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`btn btn-sm ${category === cat ? 'btn-primary' : 'btn-secondary'}`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div style={{ position: 'relative', width: '280px' }}>
          <FiSearch
            style={{
              position: 'absolute',
              left: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)',
            }}
          />
          <input
            type="text"
            placeholder="Search skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input"
            style={{ paddingLeft: '2.2rem', paddingRight: '0.75rem', height: '38px', fontSize: '0.875rem' }}
          />
        </div>
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-3 gap-6">
        {filteredSkills.map((skill) => {
          const isTracked = studentSkills.some(
            (s) => s.skill === skill.id || s.skill_details?.id === skill.id
          );
          const studentSkillObj = studentSkills.find(
            (s) => s.skill === skill.id || s.skill_details?.id === skill.id
          );

          return (
            <div key={skill.id} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                    <div
                      style={{
                        width: '42px',
                        height: '42px',
                        borderRadius: 'var(--radius-md)',
                        background: 'var(--primary-light)',
                        color: 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.25rem',
                      }}
                    >
                      <FiCode />
                    </div>
                    <div>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>{skill.name}</h3>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{skill.category}</span>
                    </div>
                  </div>
                  <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                    {skill.difficulty}
                  </span>
                </div>

                <p style={{ fontSize: '0.885rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                  {skill.description}
                </p>

                {/* Topics list pills */}
                {skill.topics && skill.topics.length > 0 && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                      Core Topics:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {skill.topics.slice(0, 4).map((topic, i) => (
                        <span key={i} className="badge badge-neutral" style={{ fontSize: '0.72rem' }}>
                          {topic}
                        </span>
                      ))}
                      {skill.topics.length > 4 && (
                        <span className="badge badge-neutral" style={{ fontSize: '0.72rem' }}>
                          +{skill.topics.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Card Actions */}
              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem' }}>
                <button
                  onClick={() => handleToggleTrack(skill)}
                  disabled={actionLoading === skill.id}
                  className={`btn btn-sm ${isTracked ? 'btn-secondary' : 'btn-outline'}`}
                  style={{ flex: 1 }}
                >
                  {isTracked ? (
                    <>
                      <FiCheck style={{ color: 'var(--success)' }} /> Tracked
                    </>
                  ) : (
                    <>
                      <FiPlus /> Track Skill
                    </>
                  )}
                </button>

                <button
                  onClick={() => navigate(`/assessments/new?skill=${skill.id}`)}
                  className="btn btn-primary btn-sm"
                  style={{ flex: 1 }}
                >
                  <FiAward /> Assess Skill
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SkillsPage;
