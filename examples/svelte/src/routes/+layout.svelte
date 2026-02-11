<script lang="ts">
    import "../app.css";
	import { onMount } from 'svelte';
	import { auth, isAuthenticated, isLoading, user, login, logout, hasRole } from '$lib/auth';

	onMount(() => {
		auth.init();
	});
</script>

<div class="min-h-screen flex flex-col bg-gray-50">
	<header class="bg-white shadow-sm sticky top-0 z-50">
		<nav class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex items-center justify-between h-16">
				<div class="flex items-center gap-8">
					<a href="/" class="text-xl font-semibold text-gray-900">
						Keycloak Demo
					</a>

					<div class="hidden sm:flex items-center gap-6">
						<a href="/" class="text-gray-600 hover:text-blue-600 transition-colors">
							Home
						</a>
						<a href="/protected" class="text-gray-600 hover:text-blue-600 transition-colors">
							Protected
						</a>
						{#if $isAuthenticated && hasRole($user, 'admin')}
							<a href="/admin" class="text-gray-600 hover:text-blue-600 transition-colors">
								Admin
							</a>
						{/if}
					</div>
				</div>

				<div class="flex items-center gap-4">
					{#if $isLoading}
						<span class="text-sm text-gray-500">Loading...</span>
					{:else if $isAuthenticated}
						<span class="text-sm text-gray-600">
							{$user?.name || $user?.username}
						</span>
						<button
							on:click={() => logout()}
							class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
						>
							Logout
						</button>
					{:else}
						<button
							on:click={() => login()}
							class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
						>
							Login
						</button>
					{/if}
				</div>
			</div>
		</nav>
	</header>

	<main class="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
		<slot />
	</main>

	<footer class="bg-white border-t border-gray-200 py-4">
		<p class="text-center text-sm text-gray-500">
			FastAPI + Keycloak + Svelte Example
		</p>
	</footer>
</div>