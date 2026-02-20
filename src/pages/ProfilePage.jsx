import { useState, useRef } from 'react';
import { useAuth, API_URL } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { FiCamera, FiEdit2, FiSave, FiX, FiUser, FiMail, FiCalendar, FiSun, FiMoon } from 'react-icons/fi';
import './ProfilePage.css';

export default function ProfilePage() {
    const { user, token, login } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const [editing, setEditing] = useState(false);
    const [saving, setSaving] = useState(false);
    const [uploadingAvatar, setUploadingAvatar] = useState(false);
    const [message, setMessage] = useState(null);
    const [form, setForm] = useState({
        name: user?.name || '',
        email: user?.email || '',
        current_password: '',
        new_password: '',
        confirm_password: '',
    });
    const fileInputRef = useRef();

    const showMsg = (text, type = 'success') => {
        setMessage({ text, type });
        setTimeout(() => setMessage(null), 3500);
    };

    const handleSave = async (e) => {
        e.preventDefault();
        if (form.new_password && form.new_password !== form.confirm_password) {
            showMsg('New passwords do not match.', 'error');
            return;
        }
        setSaving(true);
        try {
            const res = await fetch(`${API_URL}/api/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    name: form.name,
                    current_password: form.current_password || undefined,
                    new_password: form.new_password || undefined,
                }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error);

            // Update user in context by re-fetching /me
            const meRes = await fetch(`${API_URL}/api/auth/me`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            const meData = await meRes.json();
            if (meRes.ok) {
                // Patch stored user via AuthContext's setUser (we expose it)
                window.__lydistories_setUser?.(meData.user);
            }

            setEditing(false);
            setForm(f => ({ ...f, current_password: '', new_password: '', confirm_password: '' }));
            showMsg('Profile updated successfully!');
        } catch (err) {
            showMsg(err.message || 'Failed to update profile.', 'error');
        } finally {
            setSaving(false);
        }
    };

    const handleAvatarClick = () => fileInputRef.current?.click();

    const handleAvatarChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            showMsg('Please select an image file.', 'error');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            showMsg('Image must be smaller than 5MB.', 'error');
            return;
        }

        setUploadingAvatar(true);
        try {
            const formData = new FormData();
            formData.append('avatar', file);
            const res = await fetch(`${API_URL}/api/profile/avatar`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
                body: formData,
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error);

            // Refresh user data
            const meRes = await fetch(`${API_URL}/api/auth/me`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            const meData = await meRes.json();
            if (meRes.ok) window.__lydistories_setUser?.(meData.user);

            showMsg('Profile picture updated!');
        } catch (err) {
            showMsg(err.message || 'Failed to upload avatar.', 'error');
        } finally {
            setUploadingAvatar(false);
            e.target.value = '';
        }
    };

    const avatarUrl = user?.avatar_url ? `${API_URL}${user.avatar_url}` : null;

    return (
        <div className="profile-page page-enter">
            <div className="container">
                {message && (
                    <div className={`profile-toast profile-toast--${message.type}`}>
                        {message.text}
                    </div>
                )}

                <div className="profile-hero">
                    {/* Avatar */}
                    <div className="profile-avatar-wrap">
                        <div className="profile-avatar" onClick={handleAvatarClick} title="Change profile picture">
                            {avatarUrl ? (
                                <img src={avatarUrl} alt={user?.name} className="avatar-img" />
                            ) : (
                                <span className="avatar-initials">{user?.name?.charAt(0).toUpperCase()}</span>
                            )}
                            <div className={`avatar-overlay ${uploadingAvatar ? 'uploading' : ''}`}>
                                {uploadingAvatar ? (
                                    <div className="avatar-spinner" />
                                ) : (
                                    <FiCamera className="avatar-cam-icon" />
                                )}
                            </div>
                        </div>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleAvatarChange}
                            style={{ display: 'none' }}
                            id="avatar-upload"
                        />
                        <p className="avatar-hint">Click photo to change</p>
                    </div>

                    {/* Basic info */}
                    <div className="profile-identity">
                        <h1 className="profile-name-display">{user?.name}</h1>
                        <span className={`badge ${user?.role === 'admin' ? 'badge-primary' : 'badge-guide'}`}>
                            {user?.role === 'admin' ? '⚡ Admin' : '📖 Reader'}
                        </span>
                        <p className="profile-email-display">{user?.email}</p>
                    </div>
                </div>

                <div className="profile-panels">
                    {/* Edit Profile Panel */}
                    <div className="profile-panel card">
                        <div className="panel-header">
                            <h2><FiUser /> Account Details</h2>
                            {!editing && (
                                <button className="btn btn-outline btn-sm" onClick={() => setEditing(true)}>
                                    <FiEdit2 /> Edit
                                </button>
                            )}
                        </div>

                        {editing ? (
                            <form onSubmit={handleSave} className="profile-form">
                                <div className="input-group">
                                    <label htmlFor="prof-name">Full Name</label>
                                    <input
                                        id="prof-name"
                                        className="input"
                                        value={form.name}
                                        onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                                        required
                                    />
                                </div>
                                <div className="input-group">
                                    <label>Email</label>
                                    <input className="input" value={form.email} disabled style={{ opacity: 0.5, cursor: 'not-allowed' }} />
                                    <small className="form-hint">Email cannot be changed</small>
                                </div>

                                <div className="form-divider" />
                                <p className="change-pw-label">Change Password <span>(leave blank to keep current)</span></p>

                                <div className="input-group">
                                    <label htmlFor="prof-cur-pw">Current Password</label>
                                    <input
                                        id="prof-cur-pw"
                                        type="password"
                                        className="input"
                                        placeholder="••••••••"
                                        value={form.current_password}
                                        onChange={e => setForm(f => ({ ...f, current_password: e.target.value }))}
                                    />
                                </div>
                                <div className="input-group">
                                    <label htmlFor="prof-new-pw">New Password</label>
                                    <input
                                        id="prof-new-pw"
                                        type="password"
                                        className="input"
                                        placeholder="Min. 6 characters"
                                        value={form.new_password}
                                        onChange={e => setForm(f => ({ ...f, new_password: e.target.value }))}
                                    />
                                </div>
                                <div className="input-group">
                                    <label htmlFor="prof-conf-pw">Confirm New Password</label>
                                    <input
                                        id="prof-conf-pw"
                                        type="password"
                                        className="input"
                                        placeholder="Repeat new password"
                                        value={form.confirm_password}
                                        onChange={e => setForm(f => ({ ...f, confirm_password: e.target.value }))}
                                    />
                                </div>

                                <div className="form-actions">
                                    <button type="submit" className="btn btn-primary" disabled={saving}>
                                        <FiSave /> {saving ? 'Saving...' : 'Save Changes'}
                                    </button>
                                    <button type="button" className="btn btn-dark" onClick={() => setEditing(false)}>
                                        <FiX /> Cancel
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <div className="profile-info-list">
                                <div className="info-row">
                                    <FiUser className="info-icon" />
                                    <div>
                                        <p className="info-label">Full Name</p>
                                        <p className="info-value">{user?.name}</p>
                                    </div>
                                </div>
                                <div className="info-row">
                                    <FiMail className="info-icon" />
                                    <div>
                                        <p className="info-label">Email Address</p>
                                        <p className="info-value">{user?.email}</p>
                                    </div>
                                </div>
                                <div className="info-row">
                                    <FiCalendar className="info-icon" />
                                    <div>
                                        <p className="info-label">Member Since</p>
                                        <p className="info-value">
                                            {user?.created_at
                                                ? new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
                                                : '—'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Preferences Panel */}
                    <div className="profile-panel card">
                        <div className="panel-header">
                            <h2>{theme === 'dark' ? <FiMoon /> : <FiSun />} Appearance</h2>
                        </div>
                        <div className="theme-toggle-row">
                            <div>
                                <p className="theme-label">Theme</p>
                                <p className="theme-desc">{theme === 'dark' ? 'Dark mode is active' : 'Light mode is active'}</p>
                            </div>
                            <button
                                className={`theme-pill ${theme === 'light' ? 'light' : ''}`}
                                onClick={toggleTheme}
                                aria-label="Toggle theme"
                                id="theme-toggle-btn"
                            >
                                <span className="theme-pill-thumb">
                                    {theme === 'dark' ? <FiMoon /> : <FiSun />}
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
