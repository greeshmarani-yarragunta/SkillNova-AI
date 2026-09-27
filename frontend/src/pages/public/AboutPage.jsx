import React from 'react';
import { FiCheckCircle, FiCpu, FiLayers, FiShield, FiTrendingUp } from 'react-icons/fi';

const AboutPage = () => {
  return (
    <div className="container fade-in" style={{ padding: '3.5rem 1.5rem', maxWidth: '960px' }}>
      <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
        <div className="badge badge-primary" style={{ marginBottom: '1rem' }}>About SkillNova AI</div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '1rem' }}>
          Bridging the Gap Between Technical Skills & Industry Readiness
        </h1>
        <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '750px', margin: '0 auto' }}>
          SkillNova AI is an intelligent engineering platform that transforms skill evaluation into actionable, data-driven career readiness.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '2.5rem', padding: '2.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1rem' }}>Our Mission</h2>
        <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '1.5rem' }}>
          Traditional tutorials leave learners with a false sense of security. Job seekers memorize syntax but struggle when faced with real-world problems, edge case debugging, and technical interview pressure.
        </p>
        <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          SkillNova AI combines real-time 30-question diagnostic skill assessments, AI topic analysis, interactive mock interviews with constructive feedback, and automated resume gap analysis.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6" style={{ marginBottom: '3rem' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div style={{ background: 'var(--primary-light)', color: 'var(--primary)', padding: '0.65rem', borderRadius: 'var(--radius-md)' }}>
              <FiCpu style={{ fontSize: '1.3rem' }} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>AI Intelligence Layer</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
            Powered by Google Gemini with deterministic fallback heuristics. Generates dynamic assessment questions, evaluates candidate responses, and provides constructive feedback.
          </p>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div style={{ background: 'var(--success-light)', color: 'var(--success)', padding: '0.65rem', borderRadius: 'var(--radius-md)' }}>
              <FiShield style={{ fontSize: '1.3rem' }} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Robust Relational Architecture</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
            Built on Django REST Framework and MySQL. Enforces role-based permissions, JWT authentication, and transactional integrity across assessment attempts, resume analysis, and interview simulations.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
