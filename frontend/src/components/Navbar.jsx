import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from './ThemeToggle';
import {
  FiCpu, FiBell, FiUser, FiLogOut, FiMenu, FiX,
  FiCheckSquare, FiLayers, FiMessageSquare, FiBriefcase, FiFileText
} from 'react-icons/fi';

const Navbar = () => {
  const { user, isAuthenticated, logout, unreadCount, isInstructor, isAdmin } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const profileRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfileDropdownOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setProfileDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  // Close dropdown and mobile menu on route changes
  useEffect(() => {
    setProfileDropdownOpen(false);
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getDashboardLink = () => {
    if (isAdmin) return '/admin/dashboard';
    if (isInstructor) return '/instructor/dashboard';
    return '/dashboard';
  };

  const handleDropdownNavigate = (path) => {
    setProfileDropdownOpen(false);
    navigate(path);
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: 'var(--header-height)',
        background: 'var(--surface)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <div className="container flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              boxShadow: '0 2px 8px rgba(20, 184, 166, 0.3)',
            }}
          >
            <FiCpu style={{ fontSize: '1.25rem' }} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text)' }}>
              Skill<span style={{ color: 'var(--secondary)' }}>Nova</span>
            </span>
            <span className="badge badge-primary" style={{ padding: '0.1rem 0.4rem', fontSize: '0.65rem' }}>
              AI
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav
          style={{ display: 'none', alignItems: 'center', gap: '1.5rem' }}
          className="desktop-nav"
        >
          {isAuthenticated ? (
            <>
              {isAdmin ? (
                /* ADMIN Top Nav: Dashboard */
                <Link
                  to={getDashboardLink()}
                  className={`navbar-link ${isActive(getDashboardLink()) ? 'active' : ''}`}
                >
                  Dashboard
                </Link>
              ) : isInstructor ? (
                /* INSTRUCTOR Top Nav: Dashboard */
                <Link
                  to={getDashboardLink()}
                  className={`navbar-link ${isActive(getDashboardLink()) ? 'active' : ''}`}
                >
                  Dashboard
                </Link>
              ) : (
                /* STUDENT Top Nav: Dashboard, Assessments, Skills, AI Assistant, Interview, Resume */
                <>
                  <Link
                    to={getDashboardLink()}
                    className={`navbar-link ${isActive(getDashboardLink()) ? 'active' : ''}`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/assessments/new"
                    className={`navbar-link ${isActive('/assessments/new') ? 'active' : ''}`}
                  >
                    Assessments
                  </Link>
                  <Link
                    to="/skills"
                    className={`navbar-link ${isActive('/skills') ? 'active' : ''}`}
                  >
                    Skills
                  </Link>
                  <Link
                    to="/ai-assistant"
                    className={`navbar-link ${isActive('/ai-assistant') ? 'active' : ''}`}
                  >
                    AI Assistant
                  </Link>
                  <Link
                    to="/interview-prep"
                    className={`navbar-link ${isActive('/interview-prep') ? 'active' : ''}`}
                  >
                    Interview
                  </Link>
                  <Link
                    to="/resume-analyzer"
                    className={`navbar-link ${isActive('/resume-analyzer') ? 'active' : ''}`}
                  >
                    Resume
                  </Link>
                </>
              )}
            </>
          ) : (
            <>
              <Link
                to="/"
                className={`navbar-link ${isActive('/') ? 'active' : ''}`}
              >
                Home
              </Link>
              <Link
                to="/assessments/new"
                className={`navbar-link ${isActive('/assessments/new') ? 'active' : ''}`}
              >
                Assessments
              </Link>
              <Link
                to="/skills"
                className={`navbar-link ${isActive('/skills') ? 'active' : ''}`}
              >
                Skills
              </Link>
              <Link
                to="/about"
                className={`navbar-link ${isActive('/about') ? 'active' : ''}`}
              >
                About
              </Link>
              <Link
                to="/contact"
                className={`navbar-link ${isActive('/contact') ? 'active' : ''}`}
              >
                Contact
              </Link>
            </>
          )}
        </nav>

        {/* Right Action Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ThemeToggle />

          {isAuthenticated ? (
            <>
              {/* Notification Bell */}
              <Link
                to="/notifications"
                className="btn btn-secondary"
                style={{
                  position: 'relative',
                  padding: '0.5rem',
                  borderRadius: 'var(--radius-full)',
                }}
                title="Notifications"
              >
                <FiBell style={{ fontSize: '1.1rem' }} />
                {unreadCount > 0 && (
                  <span
                    style={{
                      position: 'absolute',
                      top: '-2px',
                      right: '-2px',
                      width: '17px',
                      height: '17px',
                      borderRadius: '50%',
                      background: 'var(--danger)',
                      color: 'white',
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Link>

              {/* User Dropdown Preview */}
              <div ref={profileRef} style={{ position: 'relative' }}>
                <button
                  onClick={() => setProfileDropdownOpen((prev) => !prev)}
                  aria-expanded={profileDropdownOpen}
                  aria-haspopup="true"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: 'var(--background-secondary)',
                    border: '1px solid var(--border)',
                    padding: '0.35rem 0.75rem',
                    borderRadius: 'var(--radius-full)',
                  }}
                >
                  <img
                    src={user?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=SkillNova'}
                    alt={user?.first_name || user?.username}
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      objectFit: 'cover',
                    }}
                  />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text)' }}>
                    {user?.first_name || user?.username}
                  </span>
                  <span className={`badge ${isAdmin ? 'badge-danger' : isInstructor ? 'badge-warning' : 'badge-primary'}`} style={{ fontSize: '0.65rem', padding: '0.1rem 0.35rem' }}>
                    {user?.role}
                  </span>
                </button>

                {profileDropdownOpen && (
                  <div
                    className="fade-in"
                    style={{
                      position: 'absolute',
                      right: 0,
                      top: 'calc(100% + 8px)',
                      width: '210px',
                      background: 'var(--surface)',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius-md)',
                      boxShadow: 'var(--shadow-lg)',
                      padding: '0.5rem',
                      zIndex: 200,
                    }}
                  >
                    <div style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid var(--border)', marginBottom: '0.35rem' }}>
                      <p style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Signed in as</p>
                      <p style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {user?.email}
                      </p>
                    </div>

                    <button
                      onClick={() => handleDropdownNavigate('/profile')}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        width: '100%',
                        padding: '0.55rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.875rem',
                        color: 'var(--text)',
                        transition: 'background 0.15s',
                        textAlign: 'left',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--background-secondary)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                    >
                      <FiUser style={{ fontSize: '0.95rem' }} /> Profile
                    </button>

                    <button
                      onClick={() => handleDropdownNavigate(getDashboardLink())}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        width: '100%',
                        padding: '0.55rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.875rem',
                        color: 'var(--text)',
                        transition: 'background 0.15s',
                        textAlign: 'left',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--background-secondary)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                    >
                      <FiLayers style={{ fontSize: '0.95rem' }} /> Dashboard
                    </button>

                    <button
                      onClick={() => {
                        setProfileDropdownOpen(false);
                        handleLogout();
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        width: '100%',
                        padding: '0.55rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.875rem',
                        color: 'var(--danger)',
                        transition: 'background 0.15s',
                        textAlign: 'left',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--danger-bg)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                    >
                      <FiLogOut style={{ fontSize: '0.95rem' }} /> Log Out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Link to="/login" className="btn btn-secondary btn-sm">
                Sign In
              </Link>
              <Link to="/signup" className="btn btn-primary btn-sm">
                Get Started
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="mobile-toggle btn btn-secondary"
            style={{ padding: '0.5rem', display: 'none' }}
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <FiX style={{ fontSize: '1.2rem' }} /> : <FiMenu style={{ fontSize: '1.2rem' }} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div
          className="fade-in"
          style={{
            position: 'absolute',
            top: 'var(--header-height)',
            left: 0,
            width: '100%',
            background: 'var(--surface)',
            borderBottom: '1px solid var(--border)',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.85rem',
            boxShadow: 'var(--shadow-xl)',
          }}
        >
          {isAuthenticated ? (
            <>
              {isAdmin ? (
                /* ADMIN Mobile Nav: Dashboard */
                <Link
                  to={getDashboardLink()}
                  onClick={() => setMobileMenuOpen(false)}
                  style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                >
                  Dashboard
                </Link>
              ) : isInstructor ? (
                /* INSTRUCTOR Mobile Nav: Dashboard */
                <Link
                  to={getDashboardLink()}
                  onClick={() => setMobileMenuOpen(false)}
                  style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                >
                  Dashboard
                </Link>
              ) : (
                /* STUDENT Mobile Nav: Dashboard, Assessments, Skills, AI Assistant, Interview, Resume */
                <>
                  <Link
                    to={getDashboardLink()}
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/assessments/new"
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                  >
                    Assessments
                  </Link>
                  <Link
                    to="/skills"
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                  >
                    Skills
                  </Link>
                  <Link
                    to="/ai-assistant"
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                  >
                    AI Assistant
                  </Link>
                  <Link
                    to="/interview-prep"
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                  >
                    Interview Prep
                  </Link>
                  <Link
                    to="/resume-analyzer"
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
                  >
                    Resume Analyzer
                  </Link>
                </>
              )}
              <Link
                to="/profile"
                onClick={() => setMobileMenuOpen(false)}
                style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
              >
                Profile
              </Link>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="btn btn-danger btn-sm"
                style={{ justifyContent: 'flex-start' }}
              >
                <FiLogOut /> Log Out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
              >
                Home
              </Link>
              <Link
                to="/assessments/new"
                onClick={() => setMobileMenuOpen(false)}
                style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
              >
                Assessments
              </Link>
              <Link
                to="/skills"
                onClick={() => setMobileMenuOpen(false)}
                style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
              >
                Skills
              </Link>
              <Link
                to="/about"
                onClick={() => setMobileMenuOpen(false)}
                style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
              >
                About
              </Link>
              <Link
                to="/contact"
                onClick={() => setMobileMenuOpen(false)}
                style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}
              >
                Contact
              </Link>
            </>
          )}
        </div>
      )}

      {/* Responsive Styles */}
      <style>{`
        @media (min-width: 900px) {
          .desktop-nav {
            display: flex !important;
          }
        }
        @media (max-width: 899px) {
          .mobile-toggle {
            display: flex !important;
          }
        }
      `}</style>
    </header>
  );
};

export default Navbar;
