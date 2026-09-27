import React from 'react';
import { Link } from 'react-router-dom';
import {
  FiAward, FiArrowRight, FiCheckCircle,
  FiTrendingUp, FiZap, FiTarget
} from 'react-icons/fi';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-page fade-in">
      {/* 1. Hero Section */}
      <section className="hero-section">
        <div className="landing-container">
          <div className="hero-centered-content">
            <span className="hero-badge">
              <FiZap size={13} /> SkillNova AI
            </span>

            <h1 className="hero-heading">
              Test Your Skills.<br />
              Discover Your Gaps.<br />
              Improve With <span className="hero-highlight">AI.</span>
            </h1>

            <p className="hero-description">
              An AI-powered platform that assesses your technical skills, identifies weak areas, and helps you prepare for your next opportunity.
            </p>

            <div className="hero-actions">
              <Link to="/assessments/new" className="hero-btn-primary">
                Take a Skill Test <FiArrowRight size={16} />
              </Link>
              <a href="#features" className="hero-btn-secondary">
                Explore Features
              </a>
            </div>

            {/* Small Trust/Feature Points */}
            <div className="hero-trust-list">
              <span className="hero-trust-item">
                <FiCheckCircle className="hero-trust-icon" /> Adaptive AI Evaluation
              </span>
              <span className="hero-trust-item">
                <FiCheckCircle className="hero-trust-icon" /> Topic-Level Diagnostics
              </span>
              <span className="hero-trust-item">
                <FiCheckCircle className="hero-trust-icon" /> 30-Question Assessments
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Core Capabilities Section */}
      <section id="features" className="capabilities-section">
        <div className="landing-container">
          <div className="capabilities-header">
            <span className="capabilities-badge">Core Capabilities</span>
            <h2 className="capabilities-title">Built for Serious Technical Growth</h2>
            <p className="capabilities-subtitle">
              Targeted tools designed to evaluate your technical skills and accelerate career progression.
            </p>
          </div>

          <div className="capabilities-grid">
            {/* Feature 1: AI Skill Assessments */}
            <div className="capability-card">
              <div className="capability-icon-box">
                <FiAward />
              </div>
              <h3 className="capability-card-title">AI Skill Assessments</h3>
              <p className="capability-card-desc">
                Generate technical assessments based on skill and difficulty.
              </p>
              <Link to="/assessments/new" className="capability-card-link">
                Start an assessment <FiArrowRight size={14} />
              </Link>
            </div>

            {/* Feature 2: Skill Gap Analysis */}
            <div className="capability-card">
              <div className="capability-icon-box">
                <FiTarget />
              </div>
              <h3 className="capability-card-title">Skill Gap Analysis</h3>
              <p className="capability-card-desc">
                Identify strengths and areas that need improvement.
              </p>
              <Link to="/skills" className="capability-card-link">
                Explore skills <FiArrowRight size={14} />
              </Link>
            </div>

            {/* Feature 3: AI Career Preparation */}
            <div className="capability-card">
              <div className="capability-icon-box">
                <FiTrendingUp />
              </div>
              <h3 className="capability-card-title">AI Career Preparation</h3>
              <p className="capability-card-desc">
                Practice interviews and analyze your resume.
              </p>
              <Link to="/interview-prep" className="capability-card-link">
                Prepare now <FiArrowRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Call to Action Section */}
      <section className="landing-cta-section">
        <div className="landing-container">
          <div className="cta-box">
            <h2 className="cta-title">Ready to Validate Your Engineering Skills?</h2>
            <p className="cta-desc">
              Join software engineers testing their technical proficiency across Python, React, SQL, Django, and modern cloud technologies.
            </p>
            <div className="cta-buttons">
              <Link to="/assessments/new" className="hero-btn-primary">
                Take Free Assessment Now <FiArrowRight size={16} />
              </Link>
              <Link to="/skills" className="hero-btn-secondary">
                View Supported Skills
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
