import React from 'react';
import { Link } from 'react-router-dom';
import { FiMessageSquare, FiArrowRight, FiHome, FiCheckCircle } from 'react-icons/fi';

const ContactPage = () => {
  return (
    <div className="container fade-in" style={{ padding: '4rem 1.5rem', maxWidth: '780px' }}>
      <div
        className="card"
        style={{
          textAlign: 'center',
          padding: '3.5rem 2rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1.5rem',
          boxShadow: 'var(--shadow-md)',
        }}
      >
        <span className="badge badge-primary" style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem', fontWeight: 700 }}>
          GET HELP
        </span>

        <h1
          style={{
            fontSize: '2.5rem',
            fontWeight: 800,
            letterSpacing: '-0.025em',
            color: 'var(--text)',
            lineHeight: 1.2,
            margin: 0,
          }}
        >
          Need Help With SkillNova AI?
        </h1>

        <p
          style={{
            fontSize: '1.05rem',
            color: 'var(--muted)',
            lineHeight: 1.6,
            maxWidth: '580px',
            margin: 0,
          }}
        >
          Have questions about assessments, technical skills, interview preparation, resume analysis, or how SkillNova AI works? Our AI Assistant can help you instantly.
        </p>

        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '1rem',
            justifyContent: 'center',
            marginTop: '0.5rem',
          }}
        >
          <Link to="/ai-assistant" className="btn btn-primary" style={{ padding: '0.75rem 1.6rem', fontSize: '1rem' }}>
            <FiMessageSquare /> Chat With AI Assistant <FiArrowRight />
          </Link>
          <Link to="/" className="btn btn-secondary" style={{ padding: '0.75rem 1.4rem', fontSize: '1rem' }}>
            <FiHome /> Back to Home
          </Link>
        </div>

        {/* Feature summary points */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '1.5rem',
            marginTop: '1.5rem',
            paddingTop: '1.75rem',
            borderTop: '1px solid var(--border)',
            width: '100%',
            fontSize: '0.85rem',
            color: 'var(--muted)',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FiCheckCircle style={{ color: 'var(--primary)' }} /> Technical Assessments
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FiCheckCircle style={{ color: 'var(--primary)' }} /> Skill Analysis
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FiCheckCircle style={{ color: 'var(--primary)' }} /> Interview Preparation
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FiCheckCircle style={{ color: 'var(--primary)' }} /> Resume Analysis
          </span>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;
