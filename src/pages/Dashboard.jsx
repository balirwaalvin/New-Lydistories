import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiBookOpen, FiDollarSign, FiBookmark, FiClock } from 'react-icons/fi';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const { apiFetch } = useApi();
  const [data, setData] = useState(null);
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const [dashData, bmData] = await Promise.all([
        apiFetch('/api/users/dashboard'),
        apiFetch('/api/bookmarks')
      ]);
      setData(dashData);
      setBookmarks(bmData.bookmarks);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  if (loading) return <div className="loading-page"><div className="spinner" /><p>Loading dashboard...</p></div>;

  return (
    <div className="dashboard-page page-enter">
      <div className="container">
        <div className="dash-header">
          <div>
            <h1>Welcome back, {user?.name}! 👋</h1>
            <p>Your personal reading dashboard</p>
          </div>
        </div>

        <div className="dash-stats">
          <div className="dash-stat-card">
            <FiBookOpen className="ds-icon" />
            <div>
              <p className="ds-num">{data?.total_purchased || 0}</p>
              <p className="ds-label">Purchased</p>
            </div>
          </div>
          <div className="dash-stat-card">
            <FiBookmark className="ds-icon" style={{ color: '#60A5FA' }} />
            <div>
              <p className="ds-num">{data?.bookmarks_count || 0}</p>
              <p className="ds-label">Bookmarks</p>
            </div>
          </div>
          <div className="dash-stat-card">
            <FiDollarSign className="ds-icon" style={{ color: '#34D399' }} />
            <div>
              <p className="ds-num">UGX {Number(data?.total_spent || 0).toLocaleString()}</p>
              <p className="ds-label">Total Spent</p>
            </div>
          </div>
        </div>

        {/* Purchased content */}
        <section className="dash-section">
          <h2>📖 My Library</h2>
          {data?.purchased_content?.length > 0 ? (
            <div className="dash-content-list">
              {data.purchased_content.map(item => (
                <Link to={`/content/${item.id}`} key={item.id} className="dash-content-item card">
                  <div className="dci-info">
                    <h3>{item.title}</h3>
                    <p>by {item.author} • {item.category}</p>
                  </div>
                  <div className="dci-progress">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${item.progress_percent || 0}%` }} />
                    </div>
                    <span>{Math.round(item.progress_percent || 0)}%</span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="dash-empty">
              <p>You haven't purchased any content yet.</p>
              <Link to="/browse" className="btn btn-primary">Browse Library</Link>
            </div>
          )}
        </section>

        {/* Bookmarks */}
        {bookmarks.length > 0 && (
          <section className="dash-section">
            <h2>🔖 Bookmarks</h2>
            <div className="dash-content-list">
              {bookmarks.map(bm => (
                <Link to={`/content/${bm.content_id}`} key={bm.id} className="dash-content-item card">
                  <div className="dci-info">
                    <h3>{bm.title}</h3>
                    <p>by {bm.author} • UGX {Number(bm.price).toLocaleString()}</p>
                  </div>
                  <span className={`badge badge-${bm.category}`}>{bm.category}</span>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
