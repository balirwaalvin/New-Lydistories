import { Link } from 'react-router-dom';
import { FiBookOpen, FiFileText, FiBook, FiFile } from 'react-icons/fi';
import { API_URL } from '../context/AuthContext';
import './ContentCard.css';

const categoryIcons = { book: FiBook, guide: FiBookOpen, article: FiFileText, document: FiFile };
const categoryColors = { book: '#E8383F', guide: '#60A5FA', article: '#34D399', document: '#FBBF24' };

export default function ContentCard({ item }) {
  const Icon = categoryIcons[item.category] || FiFile;
  const color = categoryColors[item.category] || '#888';

  return (
    <Link to={`/content/${item.id}`} className="content-card card">
      <div className="card-cover" style={{ borderColor: color }}>
        {item.cover_image ? (
          <img src={`${API_URL}/uploads/${item.cover_image}`} alt={item.title} />
        ) : (
          <div className="card-cover-placeholder" style={{ background: `linear-gradient(135deg, ${color}22, ${color}44)` }}>
            <Icon style={{ color, fontSize: '2.5rem' }} />
          </div>
        )}
        <span className={`badge badge-${item.category}`} style={{ position: 'absolute', top: 12, left: 12 }}>
          {item.category}
        </span>
        {item.is_featured ? (
          <span className="badge badge-primary" style={{ position: 'absolute', top: 12, right: 12 }}>★ Featured</span>
        ) : null}
      </div>
      <div className="card-body">
        <h3 className="card-title">{item.title}</h3>
        <p className="card-author">by {item.author}</p>
        <p className="card-desc">{item.description}</p>
        <div className="card-footer">
          <span className="card-price">UGX {Number(item.price).toLocaleString()}</span>
          <span className="card-pages">{item.page_count} pages</span>
        </div>
      </div>
    </Link>
  );
}
