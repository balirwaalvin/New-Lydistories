import { useAuth, API_URL } from '../context/AuthContext';

export function useApi() {
  const { token } = useAuth();

  const apiFetch = async (endpoint, options = {}) => {
    const headers = { ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  };

  return { apiFetch, API_URL };
}
