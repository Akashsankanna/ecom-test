/**
 * stores/auth.js
 *
 * Pinia auth store — works for both admin and regular users.
 * Persists token, user object, id_token, and role to localStorage
 * so the router guard can read them synchronously on every page load.
 *
 * role values:
 *   'admin'    → redirect to /admin/dashboard after login
 *   'customer' → redirect to /profile after login  (future use)
 *   null       → not logged in
 */
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => {
    // Safe localStorage reads — handles null / corrupted JSON
    let user = null
    try {
      const raw = localStorage.getItem('user')
      if (raw && raw !== 'undefined' && raw !== 'null') {
        user = JSON.parse(raw)
      }
    } catch { user = null }

    return {
      token:    localStorage.getItem('token')    || null,
      id_token: localStorage.getItem('id_token') || null,
      role:     localStorage.getItem('role')      || null,  // 'admin' | 'customer' | null
      user,
    }
  },

  getters: {
    isLoggedIn:  (state) => !!state.token,
    isAdmin:     (state) => state.role === 'admin',
    displayName: (state) =>
      state.user?.name || state.user?.email?.split('@')[0] || 'User',
    displayEmail:(state) => state.user?.email || '',
  },

  actions: {
    /**
     * setAuth — called after successful login (password OR Google OAuth).
     *
     * @param {string} token     - Keycloak access token
     * @param {object} userData  - { email, name, keycloak_id, id_token }
     * @param {string} role      - 'admin' | 'customer'
     */
    setAuth(token, userData, role = 'customer') {
      this.token    = token
      this.user     = userData
      this.id_token = userData?.id_token || null
      this.role     = role

      // Write synchronously so router guard finds token immediately
      localStorage.setItem('token',    token)
      localStorage.setItem('user',     JSON.stringify(userData))
      localStorage.setItem('id_token', userData?.id_token || '')
      localStorage.setItem('role',     role)
    },

    /**
     * logout — clears all auth state and localStorage keys.
     */
    logout() {
      this.token    = null
      this.user     = null
      this.id_token = null
      this.role     = null

      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('id_token')
      localStorage.removeItem('role')
    },
  },
})