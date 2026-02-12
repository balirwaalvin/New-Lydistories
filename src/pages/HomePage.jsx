import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiBookOpen, FiUsers, FiTrendingUp, FiStar } from 'react-icons/fi';
import ContentCard from '../components/ContentCard';
import { API_URL } from '../context/AuthContext';
import './HomePage.css';

export default function HomePage() {
  const [featured, setFeatured] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      const res = await fetch(`${API_URL}/api/content`);
      const data = await res.json();
      setFeatured(data.content.filter(c => c.is_featured));
      setRecent(data.content.slice(0, 6));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page page-enter">
      {/* Hero */}
      <section className="hero">
        <div className="hero-bg">
          <div className="hero-glow" />
          <div className="hero-grid" />
        </div>
        <div className="container hero-content">
          <div className="hero-text">
            <span className="hero-badge">📚 Your Digital Library</span>
            <h1>Discover Stories.<br /><span className="text-gradient">Expand Your Mind.</span></h1>
            <p className="hero-desc">
              Access a growing collection of books, study guides, articles, and expert documentation.
              Read anywhere, anytime — knowledge is just a tap away.
            </p>
            <div className="hero-actions">
              <Link to="/browse" className="btn btn-primary btn-lg">
                Start Reading <FiArrowRight />
              </Link>
              <Link to="/register" className="btn btn-outline btn-lg">
                Create Account
              </Link>
            </div>
          </div>
          <div className="hero-visual">
            <div className="hero-card-stack">
              <div className="hero-card hc-1">
                <div className="hc-accent" />
                <div className="hc-lines"><span /><span /><span /></div>
              </div>
              <div className="hero-card hc-2">
                <div className="hc-accent" />
                <div className="hc-lines"><span /><span /><span /></div>
              </div>
              <div className="hero-card hc-3">
                <FiBookOpen className="hc-icon" />
                <div className="hc-lines"><span /><span /><span /><span /></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="stats-section">
        <div className="container stats-grid">
          <div className="stat-item">
            <FiBookOpen className="stat-icon" />
            <div>
              <p className="stat-num">{recent.length}+</p>
              <p className="stat-label">Titles Available</p>
            </div>
          </div>
          <div className="stat-item">
            <FiUsers className="stat-icon" />
            <div>
              <p className="stat-num">100+</p>
              <p className="stat-label">Active Readers</p>
            </div>
          </div>
          <div className="stat-item">
            <FiTrendingUp className="stat-icon" />
            <div>
              <p className="stat-num">4</p>
              <p className="stat-label">Categories</p>
            </div>
          </div>
          <div className="stat-item">
            <FiStar className="stat-icon" />
            <div>
              <p className="stat-num">24/7</p>
              <p className="stat-label">Access</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured */}
      {featured.length > 0 && (
        <section className="section">
          <div className="container">
            <div className="section-header">
              <h2>🔥 Featured Content</h2>
              <Link to="/browse" className="btn btn-ghost">View All <FiArrowRight /></Link>
            </div>
            <div className="content-grid">
              {featured.map(item => <ContentCard key={item.id} item={item} />)}
            </div>
          </div>
        </section>
      )}

      {/* Recent */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2>📖 Latest Additions</h2>
            <Link to="/browse" className="btn btn-ghost">Browse All <FiArrowRight /></Link>
          </div>
          {loading ? (
            <div className="content-grid">
              {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: 320, borderRadius: 16 }} />)}
            </div>
          ) : (
            <div className="content-grid">
              {recent.map(item => <ContentCard key={item.id} item={item} />)}
            </div>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-card glass">
            <h2>Ready to Start Reading?</h2>
            <p>Create a free account and preview our collection. Pay only for what you want to read.</p>
            <div className="cta-actions">
              <Link to="/register" className="btn btn-primary btn-lg">Get Started Free <FiArrowRight /></Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
