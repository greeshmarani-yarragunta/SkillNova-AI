import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/authService';
import {
  FiUser, FiMail, FiPhone, FiGithub, FiLinkedin,
  FiAward, FiSave, FiCheckCircle, FiAlertCircle
} from 'react-icons/fi';

const ProfilePage = () => {
  const { user, refreshUser } = useAuth();

  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone: user?.phone || '',
    bio: user?.bio || '',
    avatar: user?.avatar || '',
    student_profile: {
      current_education: user?.student_profile?.current_education || '',
      target_role: user?.student_profile?.target_role || 'Python Full Stack Developer',
      experience_level: user?.student_profile?.experience_level || 'Fresher',
      github_url: user?.student_profile?.github_url || '',
      linkedin_url: user?.student_profile?.linkedin_url || '',
    },
    instructor_profile: {
      title: user?.instructor_profile?.title || '',
      organization: user?.instructor_profile?.organization || '',
      expertise: user?.instructor_profile?.expertise || '',
    },
  });

  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleStudentProfileChange = (e) => {
    setFormData({
      ...formData,
      student_profile: {
        ...formData.student_profile,
        [e.target.name]: e.target.value,
      },
    });
  };

  const handleInstructorProfileChange = (e) => {
    setFormData({
      ...formData,
      instructor_profile: {
        ...formData.instructor_profile,
        [e.target.name]: e.target.value,
      },
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');
    setError('');

    try {
      await authService.updateProfile(formData);
      await refreshUser();
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container fade-in" style={{ maxWidth: '780px', padding: '2rem 1rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
          Account & Profile Settings
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Manage your personal information, career target role, and portfolio links.
        </p>
      </div>

      {success && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            background: 'var(--success-light)',
            color: 'var(--success)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            marginBottom: '1.5rem',
          }}
        >
          <FiCheckCircle />
          <span>{success}</span>
        </div>
      )}

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

      <form onSubmit={handleSubmit} className="card" style={{ padding: '2.5rem 2rem' }}>
        {/* Avatar & Role Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '2rem' }}>
          <img
            src={formData.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=SkillNova'}
            alt="Profile Avatar"
            style={{ width: '64px', height: '64px', borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--primary)' }}
          />
          <div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700 }}>{user?.username}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{user?.email}</div>
            <span className="badge badge-primary" style={{ marginTop: '0.35rem' }}>
              {user?.role}
            </span>
          </div>
        </div>

        {/* Basic Info */}
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
          Personal Information
        </h3>

        <div className="grid grid-cols-2 gap-4">
          <div className="form-group">
            <label className="form-label">First Name</label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Last Name</label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              className="form-input"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="form-group">
            <label className="form-label">Phone Number</label>
            <input
              type="text"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+1 (555) 000-0000"
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Avatar Image URL</label>
            <input
              type="text"
              name="avatar"
              value={formData.avatar}
              onChange={handleChange}
              placeholder="https://..."
              className="form-input"
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Bio / Professional Summary</label>
          <textarea
            rows="3"
            name="bio"
            value={formData.bio}
            onChange={handleChange}
            placeholder="A brief summary about your background and interests..."
            className="form-textarea"
          />
        </div>

        {/* Student Specific Fields */}
        {user?.role === 'STUDENT' && (
          <>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '1.5rem 0 1rem 0', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              Career Preparation Profile
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Target Industry Role</label>
                <input
                  type="text"
                  name="target_role"
                  value={formData.student_profile.target_role}
                  onChange={handleStudentProfileChange}
                  placeholder="e.g. Python Full Stack Developer"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Experience Bracket</label>
                <select
                  name="experience_level"
                  value={formData.student_profile.experience_level}
                  onChange={handleStudentProfileChange}
                  className="form-select"
                >
                  <option value="Fresher">Fresher / Entry Level</option>
                  <option value="1-2 Years">Junior (1-2 Years)</option>
                  <option value="3-5 Years">Mid-Level (3-5 Years)</option>
                  <option value="5+ Years">Senior (5+ Years)</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Current Degree / Education</label>
              <input
                type="text"
                name="current_education"
                value={formData.student_profile.current_education}
                onChange={handleStudentProfileChange}
                placeholder="e.g. B.Tech Computer Science"
                className="form-input"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">GitHub Profile URL</label>
                <input
                  type="url"
                  name="github_url"
                  value={formData.student_profile.github_url}
                  onChange={handleStudentProfileChange}
                  placeholder="https://github.com/..."
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label className="form-label">LinkedIn Profile URL</label>
                <input
                  type="url"
                  name="linkedin_url"
                  value={formData.student_profile.linkedin_url}
                  onChange={handleStudentProfileChange}
                  placeholder="https://linkedin.com/in/..."
                  className="form-input"
                />
              </div>
            </div>
          </>
        )}

        {/* Instructor Specific Fields */}
        {user?.role === 'INSTRUCTOR' && (
          <>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '1.5rem 0 1rem 0', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              Instructor Profile
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Professional Title</label>
                <input
                  type="text"
                  name="title"
                  value={formData.instructor_profile.title}
                  onChange={handleInstructorProfileChange}
                  placeholder="e.g. Principal Software Engineer"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Organization / Company</label>
                <input
                  type="text"
                  name="organization"
                  value={formData.instructor_profile.organization}
                  onChange={handleInstructorProfileChange}
                  placeholder="e.g. SkillNova Academy"
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Core Technical Expertise</label>
              <textarea
                rows="2"
                name="expertise"
                value={formData.instructor_profile.expertise}
                onChange={handleInstructorProfileChange}
                placeholder="e.g. Python, Distributed Systems, Django, Machine Learning"
                className="form-textarea"
              />
            </div>
          </>
        )}

        <button
          type="submit"
          disabled={saving}
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '1.5rem', padding: '0.75rem' }}
        >
          <FiSave /> {saving ? 'Saving Changes...' : 'Save Profile Changes'}
        </button>
      </form>
    </div>
  );
};

export default ProfilePage;
