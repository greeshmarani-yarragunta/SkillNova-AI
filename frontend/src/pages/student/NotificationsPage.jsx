import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { notificationService } from '../../services/notificationService';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiBell, FiCheckCircle, FiCheck, FiArrowRight,
  FiAward, FiFileText, FiZap, FiActivity
} from 'react-icons/fi';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const { fetchUnreadCount } = useAuth();

  const loadNotifications = async () => {
    try {
      const data = await notificationService.getNotifications();
      setNotifications(data);
      await fetchUnreadCount();
    } catch (err) {
      console.error('Failed to load notifications', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkRead = async (id) => {
    try {
      await notificationService.markRead(id);
      setNotifications(
        notifications.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      await fetchUnreadCount();
    } catch (err) {
      console.error('Error marking notification read', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllRead();
      setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
      await fetchUnreadCount();
    } catch (err) {
      console.error('Error marking all notifications read', err);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'assessment':
        return <FiAward style={{ color: 'var(--primary)' }} />;
      case 'interview':
        return <FiActivity style={{ color: 'var(--secondary)' }} />;
      case 'resume':
        return <FiFileText style={{ color: 'var(--success)' }} />;
      default:
        return <FiBell style={{ color: 'var(--primary)' }} />;
    }
  };

  if (loading) {
    return <LoadingSpinner text="Fetching your notifications..." />;
  }

  return (
    <div className="container fade-in" style={{ maxWidth: '820px', padding: '2rem 1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
            Notifications & Alerts
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Track assessments, resume evaluations, and AI interview prep updates.
          </p>
        </div>

        <button onClick={handleMarkAllRead} className="btn btn-secondary btn-sm">
          <FiCheck /> Mark All Read
        </button>
      </div>

      {notifications.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <FiBell style={{ fontSize: '2.5rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>All Caught Up</h3>
          <p style={{ color: 'var(--text-secondary)' }}>You have no notifications right now.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className="card"
              style={{
                padding: '1.25rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem',
                background: notif.is_read ? 'var(--bg-surface)' : 'var(--bg-surface-elevated)',
                borderLeft: notif.is_read ? '1px solid var(--border-color)' : '4px solid var(--primary)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.25rem',
                    flexShrink: 0,
                  }}
                >
                  {getIcon(notif.notification_type)}
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                    <h4 style={{ fontSize: '0.985rem', fontWeight: notif.is_read ? 600 : 800 }}>
                      {notif.title}
                    </h4>
                    {!notif.is_read && (
                      <span className="badge badge-primary" style={{ padding: '0.1rem 0.4rem', fontSize: '0.65rem' }}>
                        NEW
                      </span>
                    )}
                  </div>
                  <p style={{ fontSize: '0.885rem', color: 'var(--text-secondary)', lineHeight: 1.4, marginBottom: '0.35rem' }}>
                    {notif.message}
                  </p>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {new Date(notif.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
                {notif.link && (
                  <Link to={notif.link} className="btn btn-outline btn-sm">
                    Open <FiArrowRight />
                  </Link>
                )}
                {!notif.is_read && (
                  <button
                    onClick={() => handleMarkRead(notif.id)}
                    className="btn btn-secondary btn-sm"
                    title="Mark as Read"
                  >
                    <FiCheck />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;
