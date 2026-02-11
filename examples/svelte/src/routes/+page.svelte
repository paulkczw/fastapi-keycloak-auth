<script lang="ts">
	import { isAuthenticated, isLoading, user, login, hasRole, fetchApi } from '$lib/auth';

	let greeting = '';
	let loadingGreeting = false;

	async function loadGreeting() {
		loadingGreeting = true;
		try {
			const data = await fetchApi<{ message: string }>('/api/greeting');
			greeting = data.message;
		} catch (e) {
			greeting = 'Error loading greeting';
		}
		loadingGreeting = false;
	}
</script>

<svelte:head>
	<title>Home - Keycloak Demo</title>
</svelte:head>

<div class="max-w-3xl mx-auto">
	<h1 class="text-3xl font-bold text-gray-900 mb-2">FastAPI + Keycloak + Svelte</h1>
	<p class="text-gray-600 mb-8">Example application with OAuth2 authentication</p>

	{#if $isLoading}
		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center gap-3">
				<div class="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
				<p class="text-gray-600">Checking authentication...</p>
			</div>
		</div>
	{:else if $isAuthenticated}
		<div class="bg-white rounded-lg shadow p-6 border-l-4 border-green-500 mb-6">
			<h2 class="text-xl font-semibold text-gray-900 mb-4">Logged In</h2>

			<div class="space-y-2 text-gray-700 mb-4">
				<p><span class="font-medium">Name:</span> {$user?.name || '-'}</p>
				<p><span class="font-medium">Email:</span> {$user?.email || '-'}</p>
				<p><span class="font-medium">Username:</span> {$user?.username || '-'}</p>
				<p><span class="font-medium">Roles:</span> {$user?.roles.join(', ') || 'none'}</p>
			</div>

			<div class="flex flex-wrap gap-2">
				{#if hasRole($user, 'admin')}
					<span class="px-3 py-1 text-sm font-medium bg-amber-100 text-amber-800 rounded-full">
						Admin
					</span>
				{/if}
				{#if hasRole($user, 'moderator')}
					<span class="px-3 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded-full">
						Moderator
					</span>
				{/if}
				{#if hasRole($user, 'user')}
					<span class="px-3 py-1 text-sm font-medium bg-gray-100 text-gray-800 rounded-full">
						User
					</span>
				{/if}
			</div>
		</div>

		<div class="mb-8">
			<a
				href="/protected"
				class="inline-flex items-center px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors font-medium"
			>
				Protected Page
				<svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
			</a>
		</div>
	{:else}
		<div class="bg-white rounded-lg shadow p-6 mb-8">
			<h2 class="text-xl font-semibold text-gray-900 mb-3">Welcome</h2>
			<p class="text-gray-600 mb-4">You are not logged in. Click the button below to sign in with Keycloak.</p>
			<button
				on:click={() => login()}
				class="px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors font-medium"
			>
				Sign in with Keycloak
			</button>
		</div>
	{/if}

	<hr class="my-8 border-gray-200" />

	<section class="mb-8">
		<h2 class="text-xl font-semibold text-gray-900 mb-3">API Test</h2>
		<p class="text-gray-600 mb-4">Test the API endpoints:</p>

		<div class="flex items-center gap-4">
			<button
				on:click={loadGreeting}
				disabled={loadingGreeting}
				class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
			>
				{loadingGreeting ? 'Loading...' : 'GET /api/greeting'}
			</button>
			{#if greeting}
				<code class="px-3 py-2 bg-gray-100 rounded text-sm">{greeting}</code>
			{/if}
		</div>
	</section>

	<hr class="my-8 border-gray-200" />

	<section>
		<h2 class="text-xl font-semibold text-gray-900 mb-3">Endpoints</h2>
		<div class="bg-white rounded-lg shadow overflow-hidden">
			<table class="w-full">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-900">Endpoint</th>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-900">Description</th>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-900">Auth</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200">
					<tr>
						<td class="px-4 py-3"><code class="text-sm bg-gray-100 px-2 py-1 rounded">/auth/login</code></td>
						<td class="px-4 py-3 text-gray-600">Redirect to Keycloak login</td>
						<td class="px-4 py-3 text-gray-400">-</td>
					</tr>
					<tr>
						<td class="px-4 py-3"><code class="text-sm bg-gray-100 px-2 py-1 rounded">/auth/logout</code></td>
						<td class="px-4 py-3 text-gray-600">Logout and clear session</td>
						<td class="px-4 py-3 text-gray-400">-</td>
					</tr>
					<tr>
						<td class="px-4 py-3"><code class="text-sm bg-gray-100 px-2 py-1 rounded">/auth/me</code></td>
						<td class="px-4 py-3 text-gray-600">Current user info</td>
						<td class="px-4 py-3 text-green-600">Required</td>
					</tr>
					<tr>
						<td class="px-4 py-3"><code class="text-sm bg-gray-100 px-2 py-1 rounded">/auth/status</code></td>
						<td class="px-4 py-3 text-gray-600">Auth status (no 401)</td>
						<td class="px-4 py-3 text-gray-400">-</td>
					</tr>
					<tr>
						<td class="px-4 py-3"><code class="text-sm bg-gray-100 px-2 py-1 rounded">/api/public</code></td>
						<td class="px-4 py-3 text-gray-600">Public data</td>
						<td class="px-4 py-3 text-gray-400">-</td>
					</tr>
					<tr>
						<td class="px-4 py-3"><code class="text-sm bg-gray-100 px-2 py-1 rounded">/api/protected</code></td>
						<td class="px-4 py-3 text-gray-600">Protected data</td>
						<td class="px-4 py-3 text-green-600">Required</td>
					</tr>
					<tr>
						<td class="px-4 py-3"><code class="text-sm bg-gray-100 px-2 py-1 rounded">/api/admin</code></td>
						<td class="px-4 py-3 text-gray-600">Admin area</td>
						<td class="px-4 py-3 text-amber-600">admin role</td>
					</tr>
				</tbody>
			</table>
		</div>
	</section>
</div>