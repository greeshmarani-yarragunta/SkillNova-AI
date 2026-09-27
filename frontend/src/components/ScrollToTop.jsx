import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * ScrollToTop handles automatic smooth scrolling on route changes
 * and handles anchor link scrolling with sticky header offset.
 */
const ScrollToTop = () => {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
  }, []);

  useEffect(() => {
    if (hash) {
      const id = hash.replace('#', '');
      const element = document.getElementById(id) || document.querySelector(hash);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
    }

    // Smoothly scroll to the top of the new page
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });

    const timer = setTimeout(() => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    }, 50);

    return () => clearTimeout(timer);
  }, [pathname, hash]);

  return null;
};

export default ScrollToTop;
