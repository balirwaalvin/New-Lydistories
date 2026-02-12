import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FiSearch, FiFilter } from 'react-icons/fi';
import ContentCard from '../components/ContentCard';
import { API_URL } from '../context/AuthContext';
import './BrowsePage.css';

const categories = [
  { value: '', label: 'All' },
  { value: 'book', label: '📚 Books' },
  { value: 'guide', label: '📖 Study Guides' },
  { value: 'article', label: '📰 Articles' },
  { value: 'document', label: '📄 Documents' },
];

export default function BrowsePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [category, setCategory] = useState(searchParams.get('category') || '');

  useEffect(() => {
    fetchContent();
  }, [category, searchParams]);

  const fetchContent = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (category) params.set('category', category);
      const s = searchParams.get('search') || search;
      if (s) params.set('search', s);
      
      const res = await fetch(`${API_URL}/api/content?${params}`);
      const data = await res.json();
      setContent(data.content);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams(prev => {
      if (search) prev.set('search', search);
      else prev.delete('search');
      return prev;
    });
    fetchContent();
  };

  return (
    <div className="browse-page page-enter">
      <div className="container">
        <div className="browse-header">
          <h1>Browse Library</h1>
          <p>Explore our collection of books, study guides, articles, and documents</p>
        </div>

        <div className="browse-controls">
          <form className="browse-search" onSubmit={handleSearch}>
            <FiSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search by title, author, or topic..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input"
            />
          </form>

          <div className="category-filters">
            {categories.map(cat => (
              <button
                key={cat.value}
                className={`filter-chip ${category === cat.value ? 'active' : ''}`}
                onClick={() => setCategory(cat.value)}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="content-grid">
            {[1,2,3,4,5,6].map(i => (
              <div key={i} className="skeleton" style={{ height: 320, borderRadius: 16 }} />
            ))}
          </div>
        ) : content.length === 0 ? (
          <div className="empty-state">
            <FiSearch style={{ fontSize: '3rem', color: 'var(--color-light-faint)' }} />
            <h3>No content found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <>
            <p className="results-count">{content.length} item{content.length !== 1 ? 's' : ''} found</p>
            <div className="content-grid">
              {content.map(item => <ContentCard key={item.id} item={item} />)}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
