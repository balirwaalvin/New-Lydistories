import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiUpload, FiSave, FiLoader } from 'react-icons/fi';
import { useApi } from '../../hooks/useApi';
import { API_URL } from '../../context/AuthContext';
import './Admin.css';

export default function AdminContentEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { apiFetch } = useApi();
  const isEdit = !!id;

  const [form, setForm] = useState({
    title: '', author: '', category: 'article', description: '',
    preview_text: '', full_text: '', price: 5000, is_featured: 0
  });
  const [pdfFile, setPdfFile] = useState(null);
  const [coverFile, setCoverFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const token = localStorage.getItem('lydistories_token');

  useEffect(() => {
    if (isEdit) fetchContent();
  }, [id]);

  const fetchContent = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/api/content/${id}`);
      const c = data.content;
      setForm({
        title: c.title || '', author: c.author || '', category: c.category || 'article',
        description: c.description || '', preview_text: c.preview_text || '',
        full_text: c.full_text || '', price: c.price || 5000, is_featured: c.is_featured || 0
      });
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      if (pdfFile) fd.append('pdf_file', pdfFile);
      if (coverFile) fd.append('cover_image', coverFile);

      const url = isEdit ? `${API_URL}/api/content/${id}` : `${API_URL}/api/content`;
      const method = isEdit ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: { 'Authorization': `Bearer ${token}` },
        body: fd
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      navigate('/admin/content');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading-page"><div className="spinner" /></div>;

  return (
    <div className="admin-page page-enter">
      <div className="container" style={{ maxWidth: 800 }}>
        <div className="admin-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/admin/content')}><FiArrowLeft /></button>
            <h1>{isEdit ? 'Edit Content' : 'Add New Content'}</h1>
          </div>
        </div>

        {error && <div className="auth-error" style={{ marginBottom: 16 }}>{error}</div>}

        <form className="editor-form" onSubmit={handleSubmit}>
          <div className="editor-grid">
            <div className="input-group">
              <label>Title *</label>
              <input className="input" value={form.title} onChange={e => setForm({...form, title: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>Author</label>
              <input className="input" value={form.author} onChange={e => setForm({...form, author: e.target.value})} />
            </div>
            <div className="input-group">
              <label>Category</label>
              <select className="input" value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                <option value="book">📚 Book</option>
                <option value="guide">📖 Study Guide</option>
                <option value="article">📰 Article</option>
                <option value="document">📄 Document</option>
              </select>
            </div>
            <div className="input-group">
              <label>Price (UGX)</label>
              <input type="number" className="input" value={form.price}
                onChange={e => setForm({...form, price: Number(e.target.value)})} min={0} />
            </div>
          </div>

          <div className="input-group">
            <label>Description</label>
            <textarea className="input" value={form.description}
              onChange={e => setForm({...form, description: e.target.value})} rows={3} />
          </div>

          <div className="input-group">
            <label>Preview Text (shown to non-paying users)</label>
            <textarea className="input" value={form.preview_text}
              onChange={e => setForm({...form, preview_text: e.target.value})} rows={4} />
          </div>

          <div className="editor-grid">
            <div className="input-group">
              <label><FiUpload /> Upload PDF</label>
              <input type="file" accept=".pdf" className="input file-input"
                onChange={e => setPdfFile(e.target.files[0])} />
              <p className="input-hint">Text will be extracted automatically from the PDF</p>
            </div>
            <div className="input-group">
              <label>Cover Image</label>
              <input type="file" accept="image/*" className="input file-input"
                onChange={e => setCoverFile(e.target.files[0])} />
            </div>
          </div>

          <div className="input-group">
            <label>Full Text (or leave blank if uploading PDF)</label>
            <textarea className="input" value={form.full_text}
              onChange={e => setForm({...form, full_text: e.target.value})} rows={10} />
          </div>

          <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <input type="checkbox" id="featured" checked={form.is_featured === 1}
              onChange={e => setForm({...form, is_featured: e.target.checked ? 1 : 0})} />
            <label htmlFor="featured" style={{ cursor: 'pointer' }}>⭐ Featured content (shown on homepage)</label>
          </div>

          <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={saving}>
            {saving ? <><FiLoader className="spin" /> Saving...</> : <><FiSave /> {isEdit ? 'Update Content' : 'Publish Content'}</>}
          </button>
        </form>
      </div>
    </div>
  );
}
