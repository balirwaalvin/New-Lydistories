import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiUser, FiMail, FiLock, FiArrowRight } from 'react-icons/fi';
import './AuthPages.css';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(name, email, password);
      navigate('/dashboard');
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
            <h2>Join Lydistories</h2>
            <p>Create your account and start reading</p>
          </div>
        </div>
        <div className="auth-form-section">
          <form className="auth-form" onSubmit={handleSubmit}>
            <h1>Sign Up</h1>
            <p className="auth-subtitle">Create your free account</p>

            {error && <div className="auth-error">{error}</div>}

            <div className="input-group">
              <label>Full Name</label>
              <input type="text" className="input" placeholder="John Doe" value={name} onChange={e => setName(e.target.value)} required />
            </div>
            <div className="input-group">
              <label>Email</label>
              <input type="email" className="input" placeholder="you@example.com" value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
            <div className="input-group">
              <label>Password</label>
              <input type="password" className="input" placeholder="Min 6 characters" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />
            </div>

            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 8 }} disabled={loading}>
              {loading ? 'Creating account...' : <>Create Account <FiArrowRight /></>}
            </button>

            <p className="auth-switch">Already have an account? <Link to="/login">Log in</Link></p>
          </form>
        </div>
      </div>
    </div>
  );
}
