import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
})

export default defineBoot(({ app, router }) => {

  // ── Request interceptor — attach token to every request ──
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // ── Response interceptor — Keycloak refresh-token flow ──
  api.interceptors.response.use(
    (response) => response,

    async (error) => {
      const status          = error?.response?.status
      const url             = error?.config?.url || ''
      const originalRequest = error?.config

      if (status === 401 && !originalRequest._retry) {

        const isAuthRoute   = url.includes('/auth/')
        const isPublicFetch = url.includes('/reviews') && originalRequest?.method === 'get'

        if (!isAuthRoute && !isPublicFetch) {
          originalRequest._retry = true  // prevent infinite retry loop

          console.warn(`[Axios] 401 on ${url} — trying token refresh`)

          const refreshed = await tryRefreshToken()

          if (refreshed) {
            // New token is now in localStorage — update header and retry
            originalRequest.headers['Authorization'] =
              `Bearer ${localStorage.getItem('token')}`
            console.info('[Axios] Token refreshed — retrying request')
            return api(originalRequest)
          }

          // Refresh genuinely failed — session is truly dead, now logout
          console.warn('[Session] Refresh failed — logging out')
          const { useAuthStore } = await import('src/stores/auth')
          const authStore = useAuthStore()
          authStore.logout()

          router.replace({ path: '/login', query: { session: 'expired' } })
        }
      }

      return Promise.reject(error)
    }
  )

  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api   = api
})

export { api }

// ─────────────────────────────────────────────────────────────────────────────
// tryRefreshToken
//
// Uses the Keycloak JS adapter if it was initialised and attached to
// window.__keycloak (your existing login flow should do this).
// Falls back to a direct refresh-token grant if the adapter is absent.
// Returns true on success (localStorage 'token' is updated), false otherwise.
// ─────────────────────────────────────────────────────────────────────────────
async function tryRefreshToken() {
  try {

    // ── Path A: Keycloak JS adapter (preferred) ───────────────────────────
    // If your existing login code stores the keycloak instance on window,
    // this will silently call updateToken() for you.
    const kc = window.__keycloak
    if (kc && typeof kc.updateToken === 'function') {
      try {
        // -1 forces a refresh regardless of remaining token lifetime
        await kc.updateToken(-1)

        if (kc.token) {
          localStorage.setItem('token', kc.token)
          if (kc.idToken)      localStorage.setItem('id_token',      kc.idToken)
          if (kc.refreshToken) localStorage.setItem('refresh_token', kc.refreshToken)

          const { useAuthStore } = await import('src/stores/auth')
          const authStore = useAuthStore()
          authStore.token    = kc.token
          authStore.id_token = kc.idToken || authStore.id_token

          console.info('[Keycloak] Token refreshed via adapter')
          return true
        }
      } catch {
        // updateToken() threw — refresh token is expired, fall through
      }
      return false
    }

    // ── Path B: Manual refresh-token grant (fallback) ─────────────────────
    // Works if your login stores the refresh_token in localStorage.
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      console.warn('[Keycloak] No refresh_token in localStorage')
      return false
    }

    const kcUrl    = import.meta.env.VITE_KEYCLOAK_URL
    const realm    = import.meta.env.VITE_KEYCLOAK_REALM
    const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT_ID

    if (!kcUrl || !realm || !clientId) {
      console.warn('[Keycloak] Missing env vars for manual refresh')
      return false
    }

    const res = await fetch(
      `${kcUrl}/realms/${realm}/protocol/openid-connect/token`,
      {
        method  : 'POST',
        headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        body    : new URLSearchParams({
          grant_type    : 'refresh_token',
          client_id     : clientId,
          refresh_token : refreshToken,
        }),
      }
    )

    if (!res.ok) {
      console.warn('[Keycloak] Manual refresh returned:', res.status)
      return false
    }

    const data = await res.json()
    if (!data.access_token) return false

    localStorage.setItem('token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
    if (data.id_token)      localStorage.setItem('id_token',      data.id_token)

    const { useAuthStore } = await import('src/stores/auth')
    const authStore = useAuthStore()
    authStore.token    = data.access_token
    authStore.id_token = data.id_token || authStore.id_token

    console.info('[Keycloak] Token refreshed via manual grant')
    return true

  } catch (err) {
    console.error('[Keycloak] tryRefreshToken error:', err)
    return false
  }
}