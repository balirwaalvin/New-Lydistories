import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiUsers, FiBookOpen, FiDollarSign, FiTrendingUp, FiPlus, FiEdit, FiTrash2, FiList } from 'react-icons/fi';
import { useApi } from '../../hooks/useApi';
import './Admin.css';

export default function AdminDashboard() {
  const { apiFetch } = useApi();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchStats(); }, []);

  const fetchStats = async () => {
    try {
      const data = await apiFetch('/api/users/stats');
      setStats(data.stats);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  if (loading) return <div className="loading-page"><div className="spinner" /></div>;

  return (
    <div className="admin-page page-enter">
      <div className="container">
        <div className="admin-header">
          <div>
            <h1>Admin Dashboard</h1>
            <p>Manage your Lydistories platform</p>
          </div>
          <Link to="/admin/content/new" className="btn btn-primary"><FiPlus /> Add Content</Link>
        </div>

        <div className="admin-stats">
          <div className="admin-stat">
            <div className="as-icon" style={{ background: 'rgba(196,30,36,0.12)' }}><FiUsers style={{ color: '#E8383F' }} /></div>
            <div><p className="as-num">{stats?.total_users || 0}</p><p className="as-label">Total Users</p></div>
          </div>
          <div className="admin-stat">
            <div className="as-icon" style={{ background: 'rgba(59,130,246,0.12)' }}><FiBookOpen style={{ color: '#60A5FA' }} /></div>
            <div><p className="as-num">{stats?.total_content || 0}</p><p className="as-label">Content Items</p></div>
          </div>
          <div className="admin-stat">
            <div className="as-icon" style={{ background: 'rgba(16,185,129,0.12)' }}><FiDollarSign style={{ color: '#34D399' }} /></div>
            <div><p className="as-num">UGX {Number(stats?.total_revenue || 0).toLocaleString()}</p><p className="as-label">Revenue</p></div>
          </div>
          <div className="admin-stat">
            <div className="as-icon" style={{ background: 'rgba(245,158,11,0.12)' }}><FiTrendingUp style={{ color: '#FBBF24' }} /></div>
            <div><p className="as-num">{stats?.total_payments || 0}</p><p className="as-label">Transactions</p></div>
          </div>
        </div>

        <div className="admin-quick-links">
          <Link to="/admin/content" className="admin-link-card card">
            <FiList />
            <h3>Manage Content</h3>
            <p>View, edit, or delete content</p>
          </Link>
          <Link to="/admin/content/new" className="admin-link-card card">
            <FiPlus />
            <h3>Add New Content</h3>
            <p>Upload PDFs or add text content</p>
          </Link>
          <Link to="/admin/users" className="admin-link-card card">
            <FiUsers />
            <h3>Manage Users</h3>
            <p>View and manage user accounts</p>
          </Link>
        </div>

        {/* Recent transactions */}
        {stats?.recent_payments?.length > 0 && (
          <section className="admin-section">
            <h2>Recent Transactions</h2>
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr><th>User</th><th>Content</th><th>Amount</th><th>Date</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {stats.recent_payments.map(p => (
                    <tr key={p.id}>
                      <td>{p.user_name}</td>
                      <td>{p.content_title}</td>
                      <td>UGX {Number(p.amount).toLocaleString()}</td>
                      <td>{new Date(p.created_at).toLocaleDateString()}</td>
                      <td><span className="badge badge-primary">{p.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
