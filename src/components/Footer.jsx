import { Link } from 'react-router-dom';
import { FiBookOpen, FiMail, FiHeart } from 'react-icons/fi';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <img src="/logo.png" alt="Lydistories" />
            <span>Lydistories</span>
          </div>
          <p className="footer-tagline">Your digital library for books, study guides, articles, and more. Knowledge at your fingertips.</p>
        </div>

        <div className="footer-links">
          <div className="footer-col">
            <h4>Explore</h4>
            <Link to="/browse">Browse All</Link>
            <Link to="/browse?category=book">Books</Link>
            <Link to="/browse?category=guide">Study Guides</Link>
            <Link to="/browse?category=article">Articles</Link>
          </div>
          <div className="footer-col">
            <h4>Account</h4>
            <Link to="/login">Login</Link>
            <Link to="/register">Sign Up</Link>
            <Link to="/dashboard">My Library</Link>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="container">
          <p>© {new Date().getFullYear()} Lydistories. All rights reserved.</p>
          <p className="footer-made">Made with <FiHeart className="heart" /> for readers everywhere</p>
        </div>
      </div>
    </footer>
  );
}
