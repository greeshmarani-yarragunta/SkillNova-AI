import React, { useState, useEffect } from 'react';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import { FiLayers, FiPlus, FiTrash2, FiSave, FiAlertCircle } from 'react-icons/fi';

const SkillsManagementPage = () => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: 'Programming',
    difficulty: 'Beginner',
    description: '',
    topics_string: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const loadSkills = async () => {
    try {
      const data = await authService.getSkills();
      setSkills(data);
    } catch (err) {
      console.error('Failed to load skills', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSkills();
  }, []);

  const handleAddSkill = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    const topicsArray = formData.topics_string
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    try {
      await authService.createSkill({
        name: formData.name,
        category: formData.category,
        difficulty: formData.difficulty,
        description: formData.description,
        topics: topicsArray,
      });

      setFormData({
        name: '',
        category: 'Programming',
        difficulty: 'Beginner',
        description: '',
        topics_string: '',
      });
      setShowAddForm(false);
      await loadSkills();
    } catch (err) {
      setError('Failed to create skill. Ensure name is unique.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this skill and its taxonomy record?')) return;
    try {
      await authService.deleteSkill(id);
      setSkills(skills.filter((s) => s.id !== id));
    } catch (err) {
      alert('Failed to delete skill.');
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading skill catalog..." />;
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
            Skill Taxonomy Management
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Configure technical disciplines, topics, and difficulty benchmarks across SkillNova AI.
          </p>
        </div>

        <button onClick={() => setShowAddForm(!showAddForm)} className="btn btn-primary">
          <FiPlus /> {showAddForm ? 'Cancel' : 'Add New Skill'}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddSkill} className="card fade-in" style={{ padding: '2rem', border: '2px solid var(--primary)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem' }}>
            Create New Skill
          </h2>

          {error && (
            <div style={{ background: 'var(--danger-light)', color: 'var(--danger)', padding: '0.75rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
              {error}
            </div>
          )}

          <div className="grid grid-cols-3 gap-4">
            <div className="form-group">
              <label className="form-label">Skill Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Kubernetes"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="form-select"
              >
                <option value="Programming">Programming</option>
                <option value="Framework">Framework</option>
                <option value="Database">Database</option>
                <option value="Core CS">Core CS</option>
                <option value="AI/ML">AI/ML</option>
                <option value="DevOps">DevOps</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Difficulty</label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                className="form-select"
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              rows="2"
              required
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Short explanation of what this technical skill encompasses..."
              className="form-textarea"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Curriculum Topics (Comma-separated)</label>
            <input
              type="text"
              value={formData.topics_string}
              onChange={(e) => setFormData({ ...formData, topics_string: e.target.value })}
              placeholder="Pods, Deployments, Services, Ingress, Helm"
              className="form-input"
            />
          </div>

          <button type="submit" disabled={submitting} className="btn btn-primary">
            <FiSave /> {submitting ? 'Saving Skill...' : 'Save Skill to System'}
          </button>
        </form>
      )}

      {/* Skills Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-container" style={{ border: 'none' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Category</th>
                <th>Difficulty</th>
                <th>Topics Count</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {skills.map((skill) => (
                <tr key={skill.id}>
                  <td style={{ fontWeight: 700 }}>{skill.name}</td>
                  <td>
                    <span className="badge badge-primary">{skill.category}</span>
                  </td>
                  <td>
                    <span className="badge badge-neutral">{skill.difficulty}</span>
                  </td>
                  <td>{skill.topics?.length || 0} topics configured</td>
                  <td>
                    <button
                      onClick={() => handleDelete(skill.id)}
                      className="btn btn-outline btn-sm"
                      title="Delete Skill"
                    >
                      <FiTrash2 style={{ color: 'var(--danger)' }} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SkillsManagementPage;
