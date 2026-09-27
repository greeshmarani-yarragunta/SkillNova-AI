import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiUsers, FiAward, FiLayers, FiActivity,
  FiShield, FiArrowRight, FiCheckCircle, FiList, FiTrendingUp
} from 'react-icons/fi';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await authService.getAdminStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to load admin platform stats', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Aggregating platform metrics..." />;
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header Banner */}
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--danger)',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
              }}
            >
              <FiShield />
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)' }}>
              Platform Administration
            </h1>
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
            System-wide oversight of user accounts, skills taxonomy, assessment tests, and question moderation.
          </p>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
          <Link to="/admin/users" className="btn btn-primary">
            <FiUsers /> User Directory
          </Link>
          <Link to="/instructor/questions" className="btn btn-secondary">
            <FiList /> Question Moderation
          </Link>
        </div>
      </div>

      {/* 6 KPI Cards: Total Users, Students, Instructors, Assessments, Questions, Test Attempts */}
      <div className="grid grid-cols-3 gap-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
        {/* Total Users */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Total Users</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiUsers />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {stats?.total_users || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Registered platform accounts
          </p>
        </div>

        {/* Students */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Students</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--secondary-light)', color: 'var(--secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiUsers />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--secondary)' }}>
            {stats?.total_students || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Active candidate profiles
          </p>
        </div>

        {/* Instructors */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Instructors</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--warning-bg)', color: 'var(--warning)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiAward />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--warning)' }}>
            {stats?.total_instructors || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Educators & question authors
          </p>
        </div>

        {/* Assessments */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Assessments</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiActivity />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--primary)' }}>
            {stats?.total_assessments || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Total assessment records
          </p>
        </div>

        {/* Questions */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Questions</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--success-bg)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiList />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--success)' }}>
            {stats?.total_questions || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            In active pool & bank
          </p>
        </div>

        {/* Test Attempts */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted)' }}>Test Attempts</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'var(--success-bg)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FiCheckCircle />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text)' }}>
            {stats?.test_attempts || 0}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.25rem' }}>
            Avg Score: {stats?.avg_assessment_score || 0}%
          </p>
        </div>
      </div>

      {/* Moderation Controls & Quick Navigation Cards */}
      <div className="grid grid-cols-3 gap-6">
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <FiUsers style={{ color: 'var(--primary)', fontSize: '1.25rem' }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>
                User Management
              </h3>
            </div>
            <p style={{ color: 'var(--muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              View student and instructor profiles, toggle active status, manage role-based access permissions.
            </p>
          </div>
          <Link to="/admin/users" className="btn btn-primary btn-sm" style={{ width: '100%' }}>
            Open User Table <FiArrowRight />
          </Link>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <FiLayers style={{ color: 'var(--secondary)', fontSize: '1.25rem' }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>
                Skill Taxonomy
              </h3>
            </div>
            <p style={{ color: 'var(--muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Maintain technical skills catalog ({stats?.total_skills || 0} active skills), curriculum topics, and difficulty levels.
            </p>
          </div>
          <Link to="/admin/skills" className="btn btn-secondary btn-sm" style={{ width: '100%' }}>
            Manage Skills <FiArrowRight />
          </Link>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <FiAward style={{ color: 'var(--success)', fontSize: '1.25rem' }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>
                Assessment Moderation
              </h3>
            </div>
            <p style={{ color: 'var(--muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Review student assessment logs, question pools, verify grading accuracy, and moderate questions.
            </p>
          </div>
          <Link to="/admin/assessments" className="btn btn-outline btn-sm" style={{ width: '100%' }}>
            View Assessments <FiArrowRight />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
