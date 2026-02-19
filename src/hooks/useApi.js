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

    // Handle non-JSON responses (like 404 HTML pages from Vite or 500 errors)
    const contentType = res.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await res.text();
      console.error("API Error (Non-JSON response):", text);
      throw new Error(`API Error: Received non-JSON response. Status: ${res.status}`);
    }

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  };

  return { apiFetch, API_URL };
}
