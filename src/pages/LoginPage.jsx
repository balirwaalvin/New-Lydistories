import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiMail, FiLock, FiArrowRight } from 'react-icons/fi';
import './AuthPages.css';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(email, password);
      navigate(user.role === 'admin' ? '/admin' : '/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page page-enter">
      <div className="auth-container">
        <div className="auth-visual">
          <div className="auth-visual-content">
            <img src="/logo.png" alt="Lydistories" className="auth-logo" />
            <h2>Welcome Back</h2>
            <p>Continue your reading journey</p>
          </div>
        </div>
        <div className="auth-form-section">
          <form className="auth-form" onSubmit={handleSubmit}>
            <h1>Log In</h1>
            <p className="auth-subtitle">Enter your credentials to continue</p>
            
            {error && <div className="auth-error">{error}</div>}

            <div className="input-group">
              <label>Email</label>
              <input type="email" className="input" placeholder="you@example.com" value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
            <div className="input-group">
              <label>Password</label>
              <input type="password" className="input" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>

            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 8 }} disabled={loading}>
              {loading ? 'Logging in...' : <>Log In <FiArrowRight /></>}
            </button>

            <p className="auth-switch">Don't have an account? <Link to="/register">Sign up</Link></p>
          </form>
        </div>
      </div>
    </div>
  );
}
