import React, { useState, useEffect } from 'react';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import { FiUsers, FiSearch, FiCheckCircle, FiXCircle, FiUserPlus, FiX, FiAlertCircle } from 'react-icons/fi';

const UsersManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [updatingId, setUpdatingId] = useState(null);

  // Modal State for Instructor Creation
  const [showAddModal, setShowAddModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');
  const [instructorForm, setInstructorForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    title: 'Lead Technical Instructor',
    organization: 'SkillNova Academy',
    expertise: 'Full Stack Web Development, Python, Cloud Systems',
  });

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await authService.getAdminUsers(roleFilter, searchTerm);
      setUsers(data);
    } catch (err) {
      console.error('Failed to load users', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [roleFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadUsers();
  };

  const handleToggleStatus = async (user) => {
    const nextStatus = !user.is_active;
    setUpdatingId(user.id);
    try {
      const updatedUser = await authService.updateAdminUser(user.id, { is_active: nextStatus });
      setUsers((prevUsers) =>
        prevUsers.map((u) => (u.id === user.id ? { ...u, is_active: updatedUser.is_active } : u))
      );
      setActionSuccess(`Account for ${user.email} ${nextStatus ? 'activated' : 'deactivated'} successfully.`);
      setTimeout(() => setActionSuccess(''), 4000);
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to update user status.';
      alert(msg);
      loadUsers();
    } finally {
      setUpdatingId(null);
    }
  };

  const handleChangeRole = async (user, newRole) => {
    setUpdatingId(user.id);
    try {
      const updatedUser = await authService.updateAdminUser(user.id, { role: newRole });
      setUsers((prevUsers) =>
        prevUsers.map((u) => (u.id === user.id ? { ...u, role: updatedUser.role, is_active: updatedUser.is_active } : u))
      );
      setActionSuccess(`Role for ${user.email} updated to ${newRole}.`);
      setTimeout(() => setActionSuccess(''), 4000);
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to update role.';
      alert(msg);
      loadUsers();
    } finally {
      setUpdatingId(null);
    }
  };

  const handleInstructorFormChange = (e) => {
    setInstructorForm({ ...instructorForm, [e.target.name]: e.target.value });
    setFormError('');
  };

  const handleCreateInstructorSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!instructorForm.email || !instructorForm.password) {
      setFormError('Email and Password are required.');
      return;
    }

    if (instructorForm.password.length < 6) {
      setFormError('Password must be at least 6 characters long.');
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.createAdminInstructor(instructorForm);
      setShowAddModal(false);
      setActionSuccess(`Instructor account created successfully for ${instructorForm.email}!`);
      setTimeout(() => setActionSuccess(''), 5000);
      setInstructorForm({
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        title: 'Lead Technical Instructor',
        organization: 'SkillNova Academy',
        expertise: 'Full Stack Web Development, Python, Cloud Systems',
      });
      loadUsers();
    } catch (err) {
      const resp = err.response?.data;
      if (resp?.email) {
        setFormError(Array.isArray(resp.email) ? resp.email[0] : resp.email);
      } else if (resp?.username) {
        setFormError(Array.isArray(resp.username) ? resp.username[0] : resp.username);
      } else if (resp?.error) {
        setFormError(resp.error);
      } else {
        setFormError('Failed to create instructor account. Please verify input data.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
            User Directory & Governance
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Activate or deactivate accounts, provision verified instructor access, and manage role authorizations.
          </p>
        </div>

        <button
          onClick={() => {
            setFormError('');
            setShowAddModal(true);
          }}
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.65rem 1.25rem' }}
        >
          <FiUserPlus style={{ fontSize: '1.1rem' }} />
          <span>Add Instructor</span>
        </button>
      </div>

      {/* Global Success Notification */}
      {actionSuccess && (
        <div
          className="fade-in"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            background: 'var(--success-light)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: 'var(--success)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.875rem',
          }}
        >
          <FiCheckCircle style={{ flexShrink: 0 }} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
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
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {['', 'STUDENT', 'INSTRUCTOR', 'ADMIN'].map((r) => (
            <button
              key={r}
              onClick={() => setRoleFilter(r)}
              className={`btn btn-sm ${roleFilter === r ? 'btn-primary' : 'btn-secondary'}`}
            >
              {r ? `${r}S` : 'ALL USERS'}
            </button>
          ))}
        </div>

        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
          <div style={{ position: 'relative', width: '250px' }}>
            <FiSearch style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search by name, email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input"
              style={{ paddingLeft: '2.2rem', height: '38px', fontSize: '0.85rem' }}
            />
          </div>
          <button type="submit" className="btn btn-primary btn-sm">
            Search
          </button>
        </form>
      </div>

      {/* Users Table */}
      {loading ? (
        <LoadingSpinner text="Loading user directory..." />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Registered</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <img
                          src={u.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=SkillNova'}
                          alt={u.username}
                          style={{ width: '34px', height: '34px', borderRadius: '50%', objectFit: 'cover' }}
                        />
                        <div>
                          <div style={{ fontWeight: 700 }}>
                            {u.first_name ? `${u.first_name} ${u.last_name || ''}` : u.username}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>@{u.username}</div>
                        </div>
                      </div>
                    </td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        value={u.role}
                        onChange={(e) => handleChangeRole(u, e.target.value)}
                        disabled={updatingId === u.id}
                        className="form-select"
                        style={{ padding: '0.3rem 0.5rem', fontSize: '0.8rem', width: '130px' }}
                      >
                        <option value="STUDENT">Student</option>
                        <option value="INSTRUCTOR">Instructor</option>
                        <option value="ADMIN">Admin</option>
                      </select>
                    </td>
                    <td>
                      <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {u.is_active ? 'Active' : 'Deactivated'}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <button
                        onClick={() => handleToggleStatus(u)}
                        disabled={updatingId === u.id}
                        className={`btn btn-sm ${u.is_active ? 'btn-outline' : 'btn-secondary'}`}
                        style={{ fontSize: '0.78rem' }}
                      >
                        {updatingId === u.id ? 'Updating...' : u.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Instructor Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div
            className="modal-content fade-in"
            onClick={(e) => e.stopPropagation()}
            style={{ padding: '2rem', maxWidth: '580px' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
                  Create Instructor Account
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                  Provision a verified instructor account with direct access to create questions and analyze student performance.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="btn btn-secondary btn-sm"
                style={{ padding: '0.35rem', borderRadius: '50%' }}
              >
                <FiX />
              </button>
            </div>

            {formError && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.65rem',
                  background: 'var(--danger-light)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: 'var(--danger)',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.875rem',
                  marginBottom: '1.25rem',
                }}
              >
                <FiAlertCircle style={{ flexShrink: 0 }} />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleCreateInstructorSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">First Name</label>
                  <input
                    type="text"
                    required
                    name="first_name"
                    value={instructorForm.first_name}
                    onChange={handleInstructorFormChange}
                    className="form-input"
                    placeholder="e.g. Elena"
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Last Name</label>
                  <input
                    type="text"
                    required
                    name="last_name"
                    value={instructorForm.last_name}
                    onChange={handleInstructorFormChange}
                    className="form-input"
                    placeholder="e.g. Vance"
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    required
                    name="email"
                    value={instructorForm.email}
                    onChange={handleInstructorFormChange}
                    className="form-input"
                    placeholder="instructor@skillnova.ai"
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Initial Password</label>
                  <input
                    type="password"
                    required
                    name="password"
                    value={instructorForm.password}
                    onChange={handleInstructorFormChange}
                    className="form-input"
                    placeholder="Minimum 6 characters"
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Professional Title</label>
                  <input
                    type="text"
                    name="title"
                    value={instructorForm.title}
                    onChange={handleInstructorFormChange}
                    className="form-input"
                    placeholder="Lead Technical Instructor"
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Organization</label>
                  <input
                    type="text"
                    name="organization"
                    value={instructorForm.organization}
                    onChange={handleInstructorFormChange}
                    className="form-input"
                    placeholder="SkillNova Academy"
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label">Primary Expertise</label>
                <input
                  type="text"
                  name="expertise"
                  value={instructorForm.expertise}
                  onChange={handleInstructorFormChange}
                  className="form-input"
                  placeholder="e.g. Python, Full Stack Web Development, Cloud Systems"
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn btn-secondary"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  <FiUserPlus />
                  <span>{isSubmitting ? 'Creating Instructor...' : 'Create Instructor'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersManagementPage;
