import { defineStore, acceptHMRUpdate } from "pinia"
import api from "@/api";
import type { Role, Roles } from "@/types/auth.d"
import _castArray from "lodash/castArray"


interface Token {
	access: string | null;
	refresh: string | null;
}


export const useAuthStore = defineStore("auth", {
	state: () => ({
		logged: !!localStorage.getItem('token'),
		role: "admin" as Role | null,
		user: {},
		token: {
			access: localStorage.getItem('accessToken') || null,
			refresh: localStorage.getItem('refreshToken') || null
		} as Token,
	}),
	actions: {
		setLogged(payload?: any) {
			this.logged = true
			this.role = "admin"
			this.user = payload
		},
		setLogout() {
			this.logged = false;
			this.role = null;
			this.user = {};
			this.token = { access: null, refresh: null };
			localStorage.removeItem('accessToken');
			localStorage.removeItem('refreshToken');
		},
		async fetchToken(credentials: { email: string | null; password: string | null; }, rememberMe: boolean) {
			try {
				const response = await api.post('/auth/jwt/create', credentials);
				this.token.access = response.data.access;
				this.token.refresh = response.data.refresh;

				// Store access token in sessionStorage or localStorage based on rememberMe
				if (rememberMe) {
					localStorage.setItem('accessToken', response.data.access);
					localStorage.setItem('refreshToken', response.data.refresh);
				} else {
					sessionStorage.setItem('accessToken', response.data.access);
					sessionStorage.setItem('refreshToken', response.data.refresh);
				}

				this.setLogged(response.data.user);
			} catch (error) {
				console.error('Error fetching token:', error);
				throw error;
			}
		},
		async refreshToken() {
			try {

				const response = await api.post('/auth/jwt/refresh', { refresh: this.token.refresh });
				this.token.access = response.data.access;
				localStorage.setItem('accessToken', response.data.access);
			} catch (error) {
				console.error('Error refreshing token:', error);
				throw error;
			}
		},
		getToken() {
			// Check if token object and access property exist
			return this.token && this.token.access ? this.token.access : null;
		},
		getRefreshToken() {
			return this.token.refresh;
		},
		async register(payload: { email: string | null; firstName: string | null; lastName: string | null; password: string | null; }) {
			try {
				const response = await api.post('/users/register', payload);
				console.log('User registered:', response.data);
				// this.setLogged(response.data.user);
			} catch (error) {
				console.error('Error registering user:', error);
				throw error;
			}
		}
	},
	getters: {
		isLogged(state) {
			return state.logged
		},
		userRole(state) {
			return state.role
		},
		isRoleGranted(state) {
			return (roles?: Roles) => {
				if (!roles) {
					return true
				}
				if (!state.role) {
					return false
				}

				const arrRoles: Role[] = _castArray(roles)

				if (arrRoles.includes("all")) {
					return true
				}

				return arrRoles.includes(state.role)
			}
		}
	},
	persist: {
		paths: ["logged", "role", "user", "token"]
	}
})

if (import.meta.hot) {
	import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot))
}
