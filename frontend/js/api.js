// Determine API URL based on where the frontend is hosted
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = IS_LOCAL 
    ? 'http://localhost:8000/api' 
    : 'https://ramz-backend-g9ad.onrender.com/api'; // Actual render URL

async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const method = options.method || 'GET';
    const cacheKey = `ramz_cache_${endpoint}`;
    
    // Clear cache on write operations to ensure fresh data
    if (method !== 'GET') {
        Object.keys(sessionStorage).forEach(key => {
            if (key.startsWith('ramz_cache_')) sessionStorage.removeItem(key);
        });
    }

    // Check cache for GET requests
    if (method === 'GET') {
        const cachedStr = sessionStorage.getItem(cacheKey);
        if (cachedStr) {
            try {
                const cached = JSON.parse(cachedStr);
                const isExpired = Date.now() - cached.timestamp > 5 * 60 * 1000; // 5 minutes
                if (!isExpired) {
                    return cached.data;
                }
            } catch (e) {
                sessionStorage.removeItem(cacheKey);
            }
        }
    }
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Remove Content-Type for FormData
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    }

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        if (response.status === 401) {
            // Unauthorized, redirect to login
            localStorage.removeItem('token');
            window.location.href = 'index.html';
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }

        // Cache the successful GET response
        if (method === 'GET') {
            sessionStorage.setItem(cacheKey, JSON.stringify({
                timestamp: Date.now(),
                data: data
            }));
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
