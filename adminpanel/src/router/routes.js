/**
 * router/routes.js
 *
 * TEMPORARY ADMIN-ONLY MODE
 * ─────────────────────────
 * - Root "/" redirects to "/login"
 * - No homepage, no profile, no cart, no wishlist, no public pages
 * - Auth pages (login / signup / forgot-password) under AuthLayout
 * - All admin pages under AdminLayout
 * - Google OAuth callback kept (needed for Google login flow)
 * - 404 catch-all at the end
 *
 * When you're ready to add customer-facing pages back, add them here
 * under a MainLayout block and update the guard in index.js.
 */

import AdminLayout       from '../layouts/AdminLayout.vue'
import AdminDashboard    from '../pages/admin/AdminDashboard.vue'
import AdminRoles        from '../pages/admin/AdminRole.vue'
import AdminProducts     from '../pages/admin/AdminProducts.vue'
import AdminOrders       from '../pages/admin/AdminOrders.vue'
import AdminPayments     from '../pages/admin/AdminPayments.vue'
import AdminInventory    from '../pages/admin/AdminInventory.vue'
import AdminReviews      from '../pages/admin/AdminReviews.vue'
import AdminCoupons      from '../pages/admin/AdminCoupons.vue'
import AdminReturns      from '../pages/admin/AdminReturns.vue'
import AdminShipment     from '../pages/admin/AdminShipment.vue'
import AdminNotification from '../pages/admin/AdminNotification.vue'
import AdminAnalytics    from '../pages/admin/AdminAnalytics.vue'
import AdminUsers        from '../pages/admin/AdminUsers.vue'
import AdminExchanges    from '../pages/admin/AdminExchanges.vue'
import BulkOrders        from '../pages/admin/BulkOrders.vue'

const routes = [

  // ══════════════════════════════════════════════════════════════
  //  ROOT → /login
  //  App always opens at login in temporary admin-only mode
  // ══════════════════════════════════════════════════════════════
  {
    path: '/',
    redirect: '/login',
  },

  // ══════════════════════════════════════════════════════════════
  //  AUTH PAGES  (AuthLayout — background image + card)
  // ══════════════════════════════════════════════════════════════
  {
    path: '/',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      { path: 'login',           component: () => import('pages/auth/LoginPage.vue') },
      { path: 'signup',          component: () => import('pages/auth/SignupPage.vue') },
      { path: 'forgot-password', component: () => import('pages/auth/ForgotPassword.vue') },
    ],
  },

  // ══════════════════════════════════════════════════════════════
  //  GOOGLE OAUTH CALLBACK
  //  Backend redirects here after Keycloak token exchange.
  //  MUST be a top-level route — no AuthLayout wrapper.
  //  Guard in index.js whitelists /auth/* so this is never blocked.
  // ══════════════════════════════════════════════════════════════
  {
    path: '/auth/callback',
    component: () => import('pages/AuthCallback.vue'),
  },

  // ══════════════════════════════════════════════════════════════
  //  ADMIN PANEL  (AdminLayout — sidebar + header)
  //  All /admin/* routes are protected by the guard in index.js.
  //  Requires: token present AND role === 'admin'
  // ══════════════════════════════════════════════════════════════
  {
    path: '/admin',
    component: AdminLayout,
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard',    name: 'AdminDashboard',    component: AdminDashboard,    meta: { title: 'Dashboard' } },
      { path: 'analytics',    name: 'AdminAnalytics',    component: AdminAnalytics,    meta: { title: 'Analytics' } },
      { path: 'roles',        name: 'AdminRoles',        component: AdminRoles,        meta: { title: 'Roles & Permissions' } },
      { path: 'products',     name: 'AdminProducts',     component: AdminProducts,     meta: { title: 'Products' } },
      { path: 'orders',       name: 'AdminOrders',       component: AdminOrders,       meta: { title: 'Orders' } },
      { path: 'payments',     name: 'AdminPayments',     component: AdminPayments,     meta: { title: 'Payments' } },
      { path: 'inventory',    name: 'AdminInventory',    component: AdminInventory,    meta: { title: 'Inventory' } },
      { path: 'reviews',      name: 'AdminReviews',      component: AdminReviews,      meta: { title: 'Reviews' } },
      { path: 'coupons',      name: 'AdminCoupons',      component: AdminCoupons,      meta: { title: 'Coupons' } },
      { path: 'returns',      name: 'AdminReturns',      component: AdminReturns,      meta: { title: 'Returns' } },
      { path: 'shipments',    name: 'AdminShipment',     component: AdminShipment,     meta: { title: 'Shipment' } },
      { path: 'notifications',name: 'AdminNotification', component: AdminNotification, meta: { title: 'Notifications' } },
      { path: 'users',        name: 'AdminUsers',        component: AdminUsers,        meta: { title: 'Users' } },
      { path: 'exchanges',    name: 'AdminExchanges',    component: AdminExchanges,    meta: { title: 'Exchanges' } },
      { path: 'bulkorders',   name: 'BulkOrders',        component: BulkOrders,        meta: { title: 'Bulk Orders' } },
    ],
  },

  // ══════════════════════════════════════════════════════════════
  //  404 — catch-all
  // ══════════════════════════════════════════════════════════════
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

/**
 * inventoryRoutes.js
 * ─────────────────────────────────────────────────────────────
 * Vue Router route definitions for the Inventory Admin Module.
 *
 * Add these to your main router/routes.js inside the admin
 * layout children array.
 *
 * Example:
 *   import { inventoryRoutes } from '@/router/inventoryRoutes'
 *   // Inside your admin layout route:
 *   { path: '/admin', component: AdminLayout, children: [...inventoryRoutes] }
 * ─────────────────────────────────────────────────────────────
 */

export const inventoryRoutes = [
  {
    /**
     * Main Inventory page — tabs: All Variants | Low Stock | Logs | Adjustments
     * Route: /admin/inventory
     */
    path: 'inventory',
    name: 'admin-inventory',
    component: () => import('../pages/admin/AdminInventory.vue'),
    meta: {
      title: 'Inventory Management',
      requiresAuth: true,
      requiredPermissions: ['view_inventory'],
      breadcrumb: [
        { label: 'Admin', to: '/admin' },
        { label: 'Inventory' },
      ],
    },
  },

  {
    /**
     * Inventory page pre-selected on the Low Stock tab.
     * Achieved via route query; the component reads ?tab=lowstock on mount.
     * Route: /admin/inventory/low-stock
     */
    path: 'inventory/low-stock',
    name: 'admin-inventory-lowstock',
    component: () => import('../pages/admin/AdminInventory.vue'),
    props: () => ({ defaultTab: 'lowstock' }),
    meta: {
      title: 'Low Stock Alerts',
      requiresAuth: true,
      requiredPermissions: ['view_inventory'],
      breadcrumb: [
        { label: 'Admin', to: '/admin' },
        { label: 'Inventory', to: '/admin/inventory' },
        { label: 'Low Stock' },
      ],
    },
  },

  {
    /**
     * Inventory page pre-selected on the Logs tab.
     * Route: /admin/inventory/logs
     */
    path: 'inventory/logs',
    name: 'admin-inventory-logs',
    component: () => import('../pages/admin/AdminInventory.vue'),
    props: () => ({ defaultTab: 'logs' }),
    meta: {
      title: 'Inventory Logs',
      requiresAuth: true,
      requiredPermissions: ['view_inventory'],
      breadcrumb: [
        { label: 'Admin', to: '/admin' },
        { label: 'Inventory', to: '/admin/inventory' },
        { label: 'Logs' },
      ],
    },
  },

  {
    /**
     * Inventory page pre-selected on the Adjustments tab.
     * Route: /admin/inventory/adjustments
     */
    path: 'inventory/adjustments',
    name: 'admin-inventory-adjustments',
    component: () => import('../pages/admin/AdminInventory.vue'),
    props: () => ({ defaultTab: 'adjustments' }),
    meta: {
      title: 'Stock Adjustments',
      requiresAuth: true,
      requiredPermissions: ['manage_inventory'],
      breadcrumb: [
        { label: 'Admin', to: '/admin' },
        { label: 'Inventory', to: '/admin/inventory' },
        { label: 'Adjustments' },
      ],
    },
  },

  // ── Deep-link to a specific variant's detail drawer ─────────────────────────
  // These are handled inside InventoryPage.vue by reading the route params on
  // mount and auto-opening the variant drawer. The page component itself does
  // not need a separate route for a dedicated "variant detail page" because
  // variant detail is shown in a slide-over drawer.
  //
  // If your team prefers a full page for variant detail, uncomment below:
  //
  // {
  //   path: 'inventory/variant/:variantId',
  //   name: 'admin-inventory-variant',
  //   component: () => import('@/pages/admin/InventoryVariantPage.vue'),
  //   props: true,
  //   meta: {
  //     title: 'Variant Detail',
  //     requiresAuth: true,
  //     requiredPermissions: ['view_inventory'],
  //   },
  // },
]

/**
 * Helper — generates the route path for a specific inventory tab.
 * Useful in sidebar navigation and programmatic router.push().
 *
 * @param {'variants'|'lowstock'|'logs'|'adjustments'} tab
 * @returns {string}
 */
export function inventoryTabRoute(tab) {
  const map = {
    variants:    '/admin/inventory',
    lowstock:    '/admin/inventory/low-stock',
    logs:        '/admin/inventory/logs',
    adjustments: '/admin/inventory/adjustments',
  }
  return map[tab] ?? '/admin/inventory'
}

/**
 * Sidebar navigation item definitions.
 * Add these to your admin sidebar nav config.
 */
export const inventorySidebarItems = [
  {
    label: 'Inventory',
    icon:  'inventory_2',
    to:    '/admin/inventory',
    name:  'admin-inventory',
    permission: 'view_inventory',
    children: [
      { label: 'All Variants',  icon: 'list',          to: '/admin/inventory',             name: 'admin-inventory' },
      { label: 'Low Stock',     icon: 'warning_amber',  to: '/admin/inventory/low-stock',   name: 'admin-inventory-lowstock' },
      { label: 'Logs',          icon: 'history',        to: '/admin/inventory/logs',        name: 'admin-inventory-logs' },
      { label: 'Adjustments',   icon: 'tune',           to: '/admin/inventory/adjustments', name: 'admin-inventory-adjustments', permission: 'manage_inventory' },
    ],
  },
]
export default routes