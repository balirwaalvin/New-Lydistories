import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiBookmark, FiLock, FiCheck, FiClock, FiFileText } from 'react-icons/fi';
import { useAuth, API_URL } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';
import PaymentModal from '../components/PaymentModal';
import './ContentPage.css';

export default function ContentPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const { apiFetch } = useApi();
  const navigate = useNavigate();
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPayment, setShowPayment] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [fontSize, setFontSize] = useState(16);
  const token = localStorage.getItem('lydistories_token');

  useEffect(() => {
    fetchContent();
    if (user) checkBookmark();
  }, [id, user]);

  const fetchContent = async () => {
    try {
      const headers = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const res = await fetch(`${API_URL}/api/content/${id}`, { headers });
      const data = await res.json();
      setContent(data.content);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const checkBookmark = async () => {
    try {
      const data = await apiFetch('/api/bookmarks');
      setBookmarked(data.bookmarks.some(b => b.content_id === parseInt(id)));
    } catch {}
  };

  const toggleBookmark = async () => {
    if (!user) return navigate('/login');
    try {
      if (bookmarked) {
        await apiFetch(`/api/bookmarks/${id}`, { method: 'DELETE' });
      } else {
        await apiFetch('/api/bookmarks', { method: 'POST', body: JSON.stringify({ content_id: parseInt(id) }) });
      }
      setBookmarked(!bookmarked);
    } catch (err) { console.error(err); }
  };

  const handlePaymentSuccess = () => {
    setShowPayment(false);
    fetchContent();
  };

  if (loading) return <div className="loading-page"><div className="spinner" /><p>Loading...</p></div>;
  if (!content) return <div className="loading-page"><p>Content not found</p></div>;

  const hasAccess = content.has_access;

  return (
    <div className="content-page page-enter">
      <div className="container">
        <button className="btn btn-ghost" onClick={() => navigate(-1)} style={{ marginBottom: 20 }}>
          <FiArrowLeft /> Back
        </button>

        <div className="content-layout">
          {/* Sidebar Info */}
          <aside className="content-sidebar">
            <div className="content-cover-large">
              {content.cover_image ? (
                <img src={`${API_URL}/uploads/${content.cover_image}`} alt={content.title} />
              ) : (
                <div className="cover-placeholder-lg">
                  <FiFileText />
                </div>
              )}
            </div>
            <div className="content-meta">
              <span className={`badge badge-${content.category}`}>{content.category}</span>
              <h1>{content.title}</h1>
              <p className="meta-author">by {content.author}</p>
              <p className="meta-desc">{content.description}</p>
              
              <div className="meta-details">
                <div className="meta-row"><FiFileText /> {content.page_count} pages</div>
                <div className="meta-row"><FiClock /> Added {new Date(content.created_at).toLocaleDateString()}</div>
              </div>

              <div className="price-tag">
                <span className="price-amount">UGX {Number(content.price).toLocaleString()}</span>
              </div>

              {hasAccess ? (
                <div className="access-badge"><FiCheck /> You have access</div>
              ) : (
                <button className="btn btn-primary btn-lg" style={{ width: '100%' }}
                  onClick={() => user ? setShowPayment(true) : navigate('/login')}>
                  <FiLock /> {user ? 'Purchase to Read' : 'Login to Purchase'}
                </button>
              )}

              {user && (
                <button className={`btn ${bookmarked ? 'btn-primary' : 'btn-outline'}`} style={{ width: '100%', marginTop: 8 }}
                  onClick={toggleBookmark}>
                  <FiBookmark /> {bookmarked ? 'Bookmarked' : 'Add Bookmark'}
                </button>
              )}
            </div>
          </aside>

          {/* Content Area */}
          <main className="content-reader-area">
            {hasAccess && content.full_text ? (
              <>
                <div className="reader-controls">
                  <span>Font size:</span>
                  <button className="btn btn-dark btn-sm" onClick={() => setFontSize(f => Math.max(12, f - 2))}>A-</button>
                  <button className="btn btn-dark btn-sm" onClick={() => setFontSize(f => Math.min(24, f + 2))}>A+</button>
                </div>
                <div className="reader-content" style={{ fontSize }}>
                  {content.full_text.split('\n').map((para, i) => 
                    para.trim() ? <p key={i}>{para}</p> : <br key={i} />
                  )}
                </div>
              </>
            ) : (
              <div className="preview-section">
                <h2>Preview</h2>
                <div className="preview-text">
                  {(content.preview_text || '').split('\n').map((para, i) =>
                    para.trim() ? <p key={i}>{para}</p> : <br key={i} />
                  )}
                </div>
                <div className="paywall-barrier">
                  <div className="paywall-card glass">
                    <FiLock className="paywall-icon" />
                    <h3>Continue Reading</h3>
                    <p>Purchase this content to unlock the full text</p>
                    <button className="btn btn-primary btn-lg"
                      onClick={() => user ? setShowPayment(true) : navigate('/login')}>
                      {user ? `Unlock for UGX ${Number(content.price).toLocaleString()}` : 'Login to Purchase'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>

      {showPayment && (
        <PaymentModal
          content={content}
          onClose={() => setShowPayment(false)}
          onSuccess={handlePaymentSuccess}
        />
      )}
    </div>
  );
}
