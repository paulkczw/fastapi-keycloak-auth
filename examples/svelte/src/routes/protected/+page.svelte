<script lang="ts">
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { auth, isAuthenticated, isLoading, login, fetchApi } from '$lib/auth';

	interface ProtectedData {
		message: string;
		user: {
			id: string;
			email: string;
			username: string;
			name: string;
			roles: string[];
		};
	}

	let data: ProtectedData | null = null;
	let error: string | null = null;
	let loading = true;

	onMount(async () => {
		await auth.init();

		if (!get(isAuthenticated)) {
			login('/protected');
			return;
		}

		try {
			data = await fetchApi<ProtectedData>('/api/protected');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Unknown error';
		}
		loading = false;
	});

	$: if (!$isLoading && !$isAuthenticated && typeof window !== 'undefined') {
		login('/protected');
	}
</script>

<svelte:head>
	<title>Protected - Keycloak Demo</title>
</svelte:head>

<div class="max-w-3xl mx-auto">
	<h1 class="text-3xl font-bold text-gray-900 mb-2">Protected Page</h1>
	<p class="text-gray-600 mb-8">This content is only visible to authenticated users.</p>

	{#if $isLoading || loading}
		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center gap-3">
				<div class="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
				<p class="text-gray-600">Checking authentication...</p>
			</div>
		</div>
	{:else if error}
		<div class="bg-white rounded-lg shadow p-6 border-l-4 border-red-500 mb-6">
			<h2 class="text-xl font-semibold text-gray-900 mb-2">Error</h2>
			<p class="text-red-600 mb-4">{error}</p>
			<button
				on:click={() => location.reload()}
				class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
			>
				Try again
			</button>
		</div>
	{:else if data}
		<div class="bg-white rounded-lg shadow p-6 border-l-4 border-green-500 mb-6">
			<h2 class="text-xl font-semibold text-gray-900 mb-4">{data.message}</h2>

			<div>
				<h3 class="text-sm font-medium text-gray-500 mb-2">Your user data:</h3>
				<pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">{JSON.stringify(data.user, null, 2)}</pre>
			</div>
		</div>

		<div class="bg-white rounded-lg shadow p-6">
			<h3 class="font-semibold text-gray-900 mb-3">How it works</h3>
			<ol class="list-decimal list-inside space-y-2 text-gray-600">
				<li>This page checks if you are logged in when loading</li>
				<li>If not, you are automatically redirected to Keycloak</li>
				<li>After login, you are redirected back here</li>
				<li>The data is loaded from the protected API endpoint</li>
			</ol>
		</div>
	{/if}

	<div class="mt-8">
		<a
			href="/"
			class="inline-flex items-center text-blue-600 hover:text-blue-700 transition-colors"
		>
			<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Back to home
		</a>
	</div>
</div>