import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiPlus, FiEdit, FiTrash2, FiArrowLeft } from 'react-icons/fi';
import { useApi } from '../../hooks/useApi';
import './Admin.css';

export default function AdminContent() {
  const { apiFetch } = useApi();
  const navigate = useNavigate();
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchContent(); }, []);

  const fetchContent = async () => {
    try {
      const data = await apiFetch('/api/content');
      setContent(data.content);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const deleteContent = async (id, title) => {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    try {
      await apiFetch(`/api/content/${id}`, { method: 'DELETE' });
      setContent(prev => prev.filter(c => c.id !== id));
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
              <h1>Content Management</h1>
              <p>{content.length} items in library</p>
            </div>
          </div>
          <Link to="/admin/content/new" className="btn btn-primary"><FiPlus /> Add New</Link>
        </div>

        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>Title</th><th>Author</th><th>Category</th><th>Price (UGX)</th><th>Pages</th><th>Featured</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {content.map(item => (
                <tr key={item.id}>
                  <td><strong>{item.title}</strong></td>
                  <td>{item.author}</td>
                  <td><span className={`badge badge-${item.category}`}>{item.category}</span></td>
                  <td>{Number(item.price).toLocaleString()}</td>
                  <td>{item.page_count}</td>
                  <td>{item.is_featured ? '⭐' : '—'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <Link to={`/admin/content/edit/${item.id}`} className="btn btn-dark btn-sm"><FiEdit /></Link>
                      <button className="btn btn-dark btn-sm" onClick={() => deleteContent(item.id, item.title)}
                        style={{ color: '#E8383F' }}><FiTrash2 /></button>
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
