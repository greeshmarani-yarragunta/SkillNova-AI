import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { FiSun, FiMoon } from 'react-icons/fi';

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`btn btn-secondary ${className}`}
      style={{
        padding: '0.5rem',
        borderRadius: 'var(--radius-full)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
      aria-label="Toggle Theme"
    >
      {theme === 'dark' ? (
        <FiSun style={{ color: '#fbbf24', fontSize: '1.2rem' }} />
      ) : (
        <FiMoon style={{ color: 'var(--primary)', fontSize: '1.2rem' }} />
      )}
    </button>
  );
};

export default ThemeToggle;
