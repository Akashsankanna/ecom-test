/**
 * router/index.js
 *
 * Route guard — TEMPORARY ADMIN-ONLY MODE
 * ────────────────────────────────────────
 *
 * Rules:
 *  1. /auth/* routes (including /auth/callback) → ALWAYS allowed through.
 *     Reason: Google OAuth callback lands on /auth/callback BEFORE the token
 *     is saved. Blocking it breaks Google login every time.
 *
 *  2. /login, /signup, /forgot-password → public, but if already logged in
 *     as admin redirect to /admin/dashboard.
 *
 *  3. /admin/* → requires token AND role === 'admin'.
 *     No token → /login
 *     Token but role !== 'admin' → /login (customer trying to access admin)
 *
 *  4. Everything else → /login (no public pages in admin-only mode).
 *
 * The guard reads from localStorage directly (not Pinia) because on a hard
 * refresh the Pinia store hydrates AFTER the first beforeEach fires.
 * localStorage is always synchronously available.
 */

import { defineRouter } from '#q-app/wrappers'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from 'vue-router'
import routes from './routes'

export default defineRouter(function () {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  // ── Helper: read auth state synchronously from localStorage ──────────────
  function getAuthState() {
    return {
      token: localStorage.getItem('token') || null,
      role:  localStorage.getItem('role')  || null,   // 'admin' | 'customer' | null
    }
  }

  // ── Auth pages — paths that are always publicly accessible ────────────────
  const AUTH_PAGES = ['/login', '/signup', '/forgot-password']

  Router.beforeEach((to, _from, next) => {
    const { token, role } = getAuthState()

    // ── Rule 1: /auth/* always allowed (Google OAuth callback lives here) ──
    if (to.path.startsWith('/auth/')) {
      return next()
    }

    // ── Rule 2: Auth pages (login / signup / forgot-password) ─────────────
    if (AUTH_PAGES.some(p => to.path === p)) {
      // Already logged in as admin → skip login, go to dashboard
      if (token && role === 'admin') {
        return next('/admin/dashboard')
      }
      // Otherwise allow the auth page
      return next()
    }

    // ── Rule 3: Admin routes (/admin/*) ────────────────────────────────────
    if (to.path.startsWith('/admin')) {
      if (!token) {
        // Not logged in → login
        return next('/login')
      }
      if (role !== 'admin') {
        // Logged in but not admin (e.g. regular customer) → login
        return next('/login')
      }
      // Admin with valid token → allow
      return next()
    }

    // ── Rule 4: Everything else → /login (admin-only mode) ────────────────
    // This handles "/" (which routes.js redirects to /login anyway),
    // any leftover customer routes, and anything unexpected.
    if (!token) {
      return next('/login')
    }

    // Logged in → send to dashboard
    return next('/admin/dashboard')
  })

  return Router
})