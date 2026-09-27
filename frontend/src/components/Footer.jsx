import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FiCpu, FiArrowRight } from 'react-icons/fi';
import './Footer.css';

const PUBLIC_ROUTES = ['/', '/about', '/contact', '/login', '/signup'];

const Footer = () => {
  const location = useLocation();

  // The footer should appear ONLY on public pages
  if (!PUBLIC_ROUTES.includes(location.pathname)) {
    return null;
  }

  const handleLinkClick = (e, to) => {
    // If middle-click or modifier key, allow default browser link handling (e.g. open in new tab)
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || (e.button && e.button !== 0)) {
      return;
    }

    // Check if it's an anchor link on the current page
    if (to.startsWith('#')) {
      e.preventDefault();
      const id = to.replace('#', '');
      const element = document.getElementById(id) || document.querySelector(to);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      return;
    }

    // If navigating to the same page, smoothly scroll to top
    if (location.pathname === to) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      // Route change: allow Link to navigate and ensure smooth scroll to top after route change
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 50);
    }
  };

  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-inner">
          {/* Brand & Description */}
          <div className="footer-brand">
            <Link
              to="/"
              onClick={(e) => handleLinkClick(e, '/')}
              className="footer-brand-header"
            >
              <div className="footer-brand-icon">
                <FiCpu style={{ fontSize: '1rem' }} />
              </div>
              <span className="footer-brand-title">
                Skill<span>Nova</span> AI
              </span>
            </Link>
            <p className="footer-description">
              AI-powered technical skill assessment platform.
            </p>
          </div>

          {/* Quick Links */}
          <div className="footer-links-col">
            <h4 className="footer-links-heading">Quick Links</h4>
            <ul className="footer-nav-grid">
              <li>
                <Link
                  to="/"
                  onClick={(e) => handleLinkClick(e, '/')}
                  className="footer-nav-link"
                >
                  Home
                </Link>
              </li>
              <li>
                <Link
                  to="/assessments"
                  onClick={(e) => handleLinkClick(e, '/assessments')}
                  className="footer-nav-link"
                >
                  Assessments
                </Link>
              </li>
              <li>
                <Link
                  to="/skills"
                  onClick={(e) => handleLinkClick(e, '/skills')}
                  className="footer-nav-link"
                >
                  Skills
                </Link>
              </li>
              <li>
                <Link
                  to="/ai-assistant"
                  onClick={(e) => handleLinkClick(e, '/ai-assistant')}
                  className="footer-nav-link"
                >
                  AI Assistant
                </Link>
              </li>
              <li>
                <Link
                  to="/interview-prep"
                  onClick={(e) => handleLinkClick(e, '/interview-prep')}
                  className="footer-nav-link"
                >
                  Interview Prep
                </Link>
              </li>
              <li>
                <Link
                  to="/resume-analyzer"
                  onClick={(e) => handleLinkClick(e, '/resume-analyzer')}
                  className="footer-nav-link"
                >
                  Resume Analyzer
                </Link>
              </li>
            </ul>

            {/* AI Support Prompt */}
            <div className="footer-support-prompt">
              <span className="footer-support-text">Need help?</span>
              <Link
                to="/ai-assistant"
                onClick={(e) => handleLinkClick(e, '/ai-assistant')}
                className="footer-support-action"
              >
                Chat with AI Assistant <FiArrowRight style={{ fontSize: '0.8rem' }} />
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom-bar">
          <p className="footer-copyright">
            © 2026 SkillNova AI
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
