import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import { ProtectedRoute, AdminRoute } from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import BrowsePage from './pages/BrowsePage';
import ContentPage from './pages/ContentPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import ProfilePage from './pages/ProfilePage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminContent from './pages/admin/AdminContent';
import AdminContentEditor from './pages/admin/AdminContentEditor';
import AdminUsers from './pages/admin/AdminUsers';
import './index.css';

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <div className="app">
            <Navbar />
            <main style={{ minHeight: 'calc(100vh - 70px)' }}>
              <Routes>
                {/* Public */}
                <Route path="/" element={<HomePage />} />
                <Route path="/browse" element={<BrowsePage />} />
                <Route path="/content/:id" element={<ContentPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Protected — Logged-in users */}
                <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

                {/* Admin */}
                <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
                <Route path="/admin/content" element={<AdminRoute><AdminContent /></AdminRoute>} />
                <Route path="/admin/content/new" element={<AdminRoute><AdminContentEditor /></AdminRoute>} />
                <Route path="/admin/content/edit/:id" element={<AdminRoute><AdminContentEditor /></AdminRoute>} />
                <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
              </Routes>
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
