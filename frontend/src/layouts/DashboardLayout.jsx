import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { FiSidebar } from 'react-icons/fi';

const DashboardLayout = () => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <div className="dashboard-container" style={{ minHeight: '100vh', background: 'var(--background)' }}>
      {/* Sidebar: Fixed on desktop, Drawer on mobile */}
      <Sidebar
        mobileOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      {/* Main Column: Header + Main content offset by sidebar width on desktop */}
      <div className="dashboard-main-wrapper">
        <Navbar />

        {/* Mobile Drawer Trigger for Dashboard on smaller screens */}
        <div
          className="mobile-sidebar-bar"
          style={{
            display: 'none',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.65rem 1.25rem',
            background: 'var(--surface)',
            borderBottom: '1px solid var(--border)',
          }}
        >
          <button
            onClick={() => setMobileSidebarOpen(true)}
            className="btn btn-secondary btn-sm"
            style={{ gap: '0.4rem' }}
          >
            <FiSidebar /> Dashboard Menu
          </button>
        </div>

        <main
          className="dashboard-main-content"
          style={{
            flex: 1,
            padding: '2rem 1.5rem',
            maxWidth: '1280px',
            margin: '0 auto',
            width: '100%',
            overflowX: 'hidden',
            boxSizing: 'border-box',
          }}
        >
          <Outlet />
        </main>
      </div>

      <style>{`
        @media (min-width: 900px) {
          .dashboard-main-wrapper {
            margin-left: var(--sidebar-width);
            width: calc(100% - var(--sidebar-width));
            min-height: 100vh;
            display: flex;
            flex-direction: column;
          }
          .mobile-sidebar-bar {
            display: none !important;
          }
        }

        @media (max-width: 899px) {
          .dashboard-main-wrapper {
            margin-left: 0 !important;
            width: 100% !important;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
          }
          .mobile-sidebar-bar {
            display: flex !important;
          }
        }
      `}</style>
    </div>
  );
};

export default DashboardLayout;
