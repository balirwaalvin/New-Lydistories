import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiTrash2, FiShield } from 'react-icons/fi';
import { useApi } from '../../hooks/useApi';
import './Admin.css';

export default function AdminUsers() {
  const { apiFetch } = useApi();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    try {
      const data = await apiFetch('/api/users');
      setUsers(data.users);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const deleteUser = async (id, name) => {
    if (!confirm(`Delete user "${name}"? This cannot be undone.`)) return;
    try {
      await apiFetch(`/api/users/${id}`, { method: 'DELETE' });
      setUsers(prev => prev.filter(u => u.id !== id));
    } catch (err) { alert(err.message); }
  };

  const toggleRole = async (id, currentRole) => {
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    try {
      await apiFetch(`/api/users/${id}`, { method: 'PUT', body: JSON.stringify({ role: newRole }) });
      setUsers(prev => prev.map(u => u.id === id ? {...u, role: newRole} : u));
    } catch (err) { alert(err.message); }
  };

  if (loading) return <div className="loading-page"><div className="spinner" /></div>;

  return (
    <div className="admin-page page-enter">
      <div className="container">
        <div className="admin-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/admin')}><FiArrowLeft /></button>
            <div>
              <h1>User Management</h1>
              <p>{users.length} registered users</p>
            </div>
          </div>
        </div>

        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td><strong>{user.name}</strong></td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`badge ${user.role === 'admin' ? 'badge-primary' : 'badge-article'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="btn btn-dark btn-sm" onClick={() => toggleRole(user.id, user.role)}
                        title={user.role === 'admin' ? 'Remove admin' : 'Make admin'}>
                        <FiShield />
                      </button>
                      {user.role !== 'admin' && (
                        <button className="btn btn-dark btn-sm" onClick={() => deleteUser(user.id, user.name)}
                          style={{ color: '#E8383F' }}><FiTrash2 /></button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
