import React from 'react';
import { CgSpinner } from 'react-icons/cg';

const LoadingSpinner = ({ size = 28, text = 'Loading...' }) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.75rem',
        padding: '3rem 1rem',
        color: 'var(--text-secondary)',
      }}
    >
      <CgSpinner
        className="animate-spin"
        style={{ fontSize: `${size}px`, color: 'var(--primary)' }}
      />
      {text && <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{text}</span>}
    </div>
  );
};

export default LoadingSpinner;
