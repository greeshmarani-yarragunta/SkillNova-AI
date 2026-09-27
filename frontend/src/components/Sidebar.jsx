import React from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  FiGrid, FiCheckSquare, FiAward, FiClock, FiMessageSquare,
  FiBriefcase, FiFileText, FiBell, FiUser, FiLogOut,
  FiHelpCircle, FiActivity, FiUsers, FiLayers, FiList, FiCpu
} from 'react-icons/fi';

const Sidebar = ({ mobileOpen, onCloseMobile }) => {
  const { user, logout, isInstructor, isAdmin, unreadCount } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const studentLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: FiGrid },
    { to: '/assessments/new', label: 'Assessments', icon: FiAward },
    { to: '/skills', label: 'Skills', icon: FiCheckSquare },
    { to: '/assessment-history', label: 'Assessment History', icon: FiClock },
    { to: '/ai-assistant', label: 'AI Assistant', icon: FiMessageSquare },
    { to: '/interview-prep', label: 'Interview Prep', icon: FiBriefcase },
    { to: '/resume-analyzer', label: 'Resume Analyzer', icon: FiFileText },
    { to: '/notifications', label: 'Notifications', icon: FiBell, badge: unreadCount },
    { to: '/profile', label: 'Profile', icon: FiUser },
  ];

  const instructorLinks = [
    { to: '/instructor/dashboard', label: 'Dashboard', icon: FiGrid },
    { to: '/instructor/questions', label: 'Questions Bank', icon: FiList },
    { to: '/instructor/ai-questions', label: 'AI Question Generator', icon: FiHelpCircle },
    { to: '/instructor/performance', label: 'Student Performance', icon: FiActivity },
    { to: '/notifications', label: 'Notifications', icon: FiBell, badge: unreadCount },
    { to: '/profile', label: 'Profile', icon: FiUser },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Dashboard', icon: FiGrid },
    { to: '/admin/users', label: 'User Directory', icon: FiUsers },
    { to: '/admin/skills', label: 'Skill Taxonomy', icon: FiLayers },
    { to: '/admin/assessments', label: 'Assessments Log', icon: FiAward },
    { to: '/admin/questions', label: 'Question Moderation', icon: FiList },
    { to: '/notifications', label: 'Notifications', icon: FiBell, badge: unreadCount },
    { to: '/profile', label: 'Profile', icon: FiUser },
  ];

  let navLinks = studentLinks;
  if (isAdmin) {
    navLinks = adminLinks;
  } else if (isInstructor) {
    navLinks = instructorLinks;
  }

  const sidebarContent = (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100%',
        padding: '1.25rem 0.85rem',
      }}
    >
      <div>
        {/* Brand Header */}
        <Link
          to="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            padding: '0.25rem 0.5rem 1.25rem 0.5rem',
            borderBottom: '1px solid var(--border)',
            marginBottom: '1rem',
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              boxShadow: '0 2px 8px rgba(20, 184, 166, 0.3)',
              flexShrink: 0,
            }}
          >
            <FiCpu style={{ fontSize: '1.2rem' }} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ fontSize: '1.15rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text)' }}>
              Skill<span style={{ color: 'var(--secondary)' }}>Nova</span>
            </span>
            <span className="badge badge-primary" style={{ padding: '0.1rem 0.35rem', fontSize: '0.6rem' }}>
              AI
            </span>
          </div>
        </Link>

        {/* Portal Identifier */}
        <div style={{ padding: '0 0.5rem 1.25rem 0.5rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0.45rem 0.75rem',
              borderRadius: 'var(--radius-md)',
              background: 'var(--background-secondary)',
              border: '1px solid var(--border)',
            }}
          >
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--muted)', letterSpacing: '0.05em' }}>
              PORTAL
            </span>
            <span
              className={`badge ${
                isAdmin ? 'badge-danger' : isInstructor ? 'badge-warning' : 'badge-primary'
              }`}
              style={{ fontSize: '0.7rem', padding: '0.1rem 0.45rem' }}
            >
              {user?.role}
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {navLinks.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onCloseMobile}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.65rem 0.85rem',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.885rem',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? '#FFFFFF' : 'var(--muted)',
                  background: isActive ? 'var(--primary)' : 'transparent',
                  transition: 'all 0.15s ease-in-out',
                })}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Icon style={{ fontSize: '1.15rem' }} />
                  <span>{item.label}</span>
                </div>
                {item.badge > 0 && (
                  <span
                    className="badge badge-danger"
                    style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}
                  >
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Footer Summary */}
      <div
        style={{
          borderTop: '1px solid var(--border)',
          paddingTop: '1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', overflow: 'hidden' }}>
          <img
            src={user?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=SkillNova'}
            alt={user?.first_name || user?.username}
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              objectFit: 'cover',
              border: '2px solid var(--border)',
              flexShrink: 0,
            }}
          />
          <div style={{ overflow: 'hidden' }}>
            <div
              style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: 'var(--text)',
                whiteSpace: 'nowrap',
                textOverflow: 'ellipsis',
                overflow: 'hidden',
              }}
            >
              {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username}
            </div>
            <div
              style={{
                fontSize: '0.725rem',
                color: 'var(--muted)',
                whiteSpace: 'nowrap',
                textOverflow: 'ellipsis',
                overflow: 'hidden',
              }}
            >
              {user?.email}
            </div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="btn btn-outline"
          style={{ padding: '0.45rem', borderRadius: 'var(--radius-md)' }}
          title="Sign Out"
        >
          <FiLogOut style={{ fontSize: '1rem' }} />
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Sidebar */}
      <aside
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: 'var(--sidebar-width)',
          height: '100vh',
          background: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border)',
          overflowY: 'auto',
          zIndex: 90,
          boxSizing: 'border-box',
        }}
        className="dashboard-sidebar-desktop"
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Slide-out */}
      {mobileOpen && (
        <div
          className="modal-overlay"
          onClick={onCloseMobile}
          style={{ zIndex: 300, justifyContent: 'flex-start', padding: 0 }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="fade-in"
            style={{
              width: '280px',
              height: '100%',
              background: 'var(--bg-sidebar)',
              borderRight: '1px solid var(--border)',
              boxShadow: 'var(--shadow-xl)',
            }}
          >
            {sidebarContent}
          </div>
        </div>
      )}

      <style>{`
        @media (max-width: 899px) {
          .dashboard-sidebar-desktop {
            display: none !important;
          }
        }
      `}</style>
    </>
  );
};

export default Sidebar;
