/**
 * Keycloak Authentication for Svelte/SvelteKit.
 *
 * Usage:
 *   import { auth, login, logout, isAuthenticated, user } from '$lib/auth';
 *
 *   // In +layout.svelte: Initialize auth
 *   onMount(() => auth.init());
 *
 *   // Login/Logout
 *   <button on:click={() => login()}>Login</button>
 *   <button on:click={() => logout()}>Logout</button>
 *
 *   // User info
 *   {#if $isAuthenticated}
 *     <p>Hello {$user?.name}!</p>
 *   {/if}
 */

import { writable, derived, type Readable } from 'svelte/store';

// API URL from environment variable or default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const AUTH_PATH = import.meta.env.VITE_AUTH_PATH || '/auth';
const API_AUTH_URL = API_URL + AUTH_PATH;

// =============================================================================
// Types
// =============================================================================

export interface User {
	id: string;
	email: string | null;
	email_verified: boolean;
	username: string | null;
	name: string | null;
	first_name: string | null;
	last_name: string | null;
	roles: string[];
}

export interface AuthStatus {
	authenticated: boolean;
	user: User | null;
}

interface AuthState {
	user: User | null;
	loading: boolean;
	initialized: boolean;
	error: string | null;
}

// =============================================================================
// Auth Functions
// =============================================================================

/**
 * Redirect to Keycloak login.
 * @param redirectPath - Path to redirect after login (optional)
 */
export function login(redirectPath?: string): void {
	const url = new URL(`${API_AUTH_URL}/login`);
	if (redirectPath) {
		url.searchParams.set('redirect', `${window.location.origin}${redirectPath}`);
	}
	window.location.href = url.toString();
}

/**
 * Logout - clears session and redirects to Keycloak.
 * @param redirectPath - Path to redirect after logout (optional)
 */
export function logout(redirectPath?: string): void {
	const url = new URL(`${API_AUTH_URL}/logout`);
	if (redirectPath) {
		url.searchParams.set('redirect', `${window.location.origin}${redirectPath}`);
	}
	window.location.href = url.toString();
}

/**
 * Get current user from backend.
 * @returns User or null if not logged in
 */
export async function getUser(): Promise<User | null> {
	try {
		const response = await fetch(`${API_AUTH_URL}/me`, {
			credentials: 'include'
		});
		if (!response.ok) return null;
		return response.json();
	} catch {
		return null;
	}
}

/**
 * Check auth status (doesn't throw 401).
 * @returns AuthStatus object
 */
export async function getAuthStatus(): Promise<AuthStatus> {
	try {
		const response = await fetch(`${API_AUTH_URL}/status`, {
			credentials: 'include'
		});
		return response.json();
	} catch {
		return { authenticated: false, user: null };
	}
}

// =============================================================================
// API Helper
// =============================================================================

/**
 * Authenticated API request.
 * Automatically redirects to login on 401.
 *
 * @param endpoint - API endpoint (e.g. '/api/todos')
 * @param options - Fetch options
 * @returns Response data
 */
export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
	const response = await fetch(`${API_URL}${endpoint}`, {
		...options,
		credentials: 'include',
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		}
	});

	if (response.status === 401) {
		login(window.location.pathname);
		throw new Error('Not authenticated');
	}

	if (response.status === 403) {
		throw new Error('Access denied');
	}

	if (!response.ok) {
		throw new Error(`API error: ${response.status}`);
	}

	return response.json();
}

// =============================================================================
// Role Helpers
// =============================================================================

/**
 * Check if user has a specific role.
 */
export function hasRole(user: User | null, role: string): boolean {
	return user?.roles.includes(role) ?? false;
}

/**
 * Check if user has any of the specified roles.
 */
export function hasAnyRole(user: User | null, roles: string[]): boolean {
	return roles.some((role) => hasRole(user, role));
}

/**
 * Check if user has all specified roles.
 */
export function hasAllRoles(user: User | null, roles: string[]): boolean {
	return roles.every((role) => hasRole(user, role));
}

// =============================================================================
// Svelte Store
// =============================================================================

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		loading: true,
		initialized: false,
		error: null
	});

	return {
		subscribe,

		/**
		 * Initialize auth state.
		 * Call once in +layout.svelte!
		 */
		async init(): Promise<User | null> {
			update((state) => ({ ...state, loading: true, error: null }));

			try {
				const status = await getAuthStatus();
				set({
					user: status.user,
					loading: false,
					initialized: true,
					error: null
				});
				return status.user;
			} catch (e) {
				set({
					user: null,
					loading: false,
					initialized: true,
					error: e instanceof Error ? e.message : 'Unknown error'
				});
				return null;
			}
		},

		/**
		 * Refresh user data.
		 */
		async refresh(): Promise<User | null> {
			const user = await getUser();
			update((state) => ({ ...state, user }));
			return user;
		},

		/**
		 * Clear auth state (on logout).
		 */
		clear(): void {
			set({
				user: null,
				loading: false,
				initialized: true,
				error: null
			});
		}
	};
}

// Singleton store
export const auth = createAuthStore();

// Derived stores for easier access
export const user: Readable<User | null> = derived(auth, ($auth) => $auth.user);
export const isAuthenticated: Readable<boolean> = derived(auth, ($auth) => $auth.user !== null);
export const isLoading: Readable<boolean> = derived(auth, ($auth) => $auth.loading);
export const isInitialized: Readable<boolean> = derived(auth, ($auth) => $auth.initialized);
export const authError: Readable<string | null> = derived(auth, ($auth) => $auth.error);