import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
});

// Request interceptor to add the JWT token to each request
api.interceptors.request.use(
    async (config) => {
        const authStore = useAuthStore();
        const token = authStore.getToken();

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh on receiving a 401 error
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        // Check if error.response exists
        if (error.response) {
            const originalRequest = error.config;
            if (error.response.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;
                const authStore = useAuthStore();

                try {
                    await authStore.refreshToken();
                    const newToken = authStore.getToken();
                    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    // Handle failed refresh (e.g., log out the user, redirect to login)
                    // authStore.setLogout();
                    // Redirect to login or show an error message
                    console.error('Error refreshing token:', refreshError);
                    // router.push({ name: 'Login', params: { redirect: 'asd' } });
                }
            }
        }

        // Handle errors without a response (e.g., network errors)
        return Promise.reject(error);
    }
);


export default api;
