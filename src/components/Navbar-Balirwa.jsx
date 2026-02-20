import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, API_URL } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { FiSearch, FiMenu, FiX, FiLogOut, FiGrid, FiBookOpen, FiUser, FiSun, FiMoon } from 'react-icons/fi';
import './Navbar.css';

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/browse?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchOpen(false);
      setSearchQuery('');
    }
  };

  const avatarUrl = user?.avatar_url ? `${API_URL}${user.avatar_url}` : null;

  return (
    <nav className="navbar">
      <div className="navbar-inner container">
        <Link to="/" className="navbar-brand">
          <img src="/logo.png" alt="Lydistories" className="navbar-logo" />
          <span className="navbar-title">Lydistories</span>
        </Link>

        <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
          <Link to="/" onClick={() => setMenuOpen(false)}>Home</Link>
          <Link to="/browse" onClick={() => setMenuOpen(false)}>Browse</Link>
          {user && <Link to="/dashboard" onClick={() => setMenuOpen(false)}>My Library</Link>}
          {isAdmin && <Link to="/admin" onClick={() => setMenuOpen(false)} className="admin-link">Admin</Link>}

          {!user && (
            <div className="mobile-auth-buttons">
              <Link to="/login" className="btn btn-ghost" onClick={() => setMenuOpen(false)}>Log in</Link>
              <Link to="/register" className="btn btn-primary" onClick={() => setMenuOpen(false)}>Sign up</Link>
            </div>
          )}
        </div>

        <div className="navbar-actions">
          <button className="btn-icon nav-icon" onClick={() => setSearchOpen(!searchOpen)} aria-label="Search">
            <FiSearch />
          </button>

          {/* Theme toggle */}
          <button
            className="btn-icon nav-icon"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            id="navbar-theme-toggle"
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <FiSun /> : <FiMoon />}
          </button>

          {user ? (
            <div className="profile-menu">
              <button className="profile-trigger" onClick={() => setProfileOpen(!profileOpen)} aria-label="Profile menu">
                <div className="avatar">
                  {avatarUrl
                    ? <img src={avatarUrl} alt={user.name} className="avatar-photo" />
                    : user.name.charAt(0).toUpperCase()
                  }
                </div>
              </button>
              {profileOpen && (
                <div className="profile-dropdown" onClick={() => setProfileOpen(false)}>
                  <div className="profile-header">
                    <div className="avatar avatar-lg">
                      {avatarUrl
                        ? <img src={avatarUrl} alt={user.name} className="avatar-photo" />
                        : user.name.charAt(0).toUpperCase()
                      }
                    </div>
                    <div>
                      <p className="profile-name">{user.name}</p>
                      <p className="profile-email">{user.email}</p>
                    </div>
                  </div>
                  <div className="profile-divider" />
                  <Link to="/dashboard" className="profile-item"><FiBookOpen /> My Library</Link>
                  <Link to="/profile" className="profile-item"><FiUser /> Edit Profile</Link>
                  {isAdmin && <Link to="/admin" className="profile-item"><FiGrid /> Admin Portal</Link>}
                  <div className="profile-divider" />
                  <button className="profile-item logout" onClick={logout}><FiLogOut /> Logout</button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <Link to="/login" className="btn btn-ghost btn-sm">Log in</Link>
              <Link to="/register" className="btn btn-primary btn-sm">Sign up</Link>
            </div>
          )}

          <button className="btn-icon nav-icon mobile-menu" onClick={() => setMenuOpen(!menuOpen)} aria-label="Menu">
            {menuOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>
      </div>

      {searchOpen && (
        <div className="search-bar">
          <form onSubmit={handleSearch} className="container">
            <FiSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search books, guides, articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
            />
            <button type="button" className="search-close" onClick={() => setSearchOpen(false)}>
              <FiX />
            </button>
          </form>
        </div>
      )}
    </nav>
  );
}
