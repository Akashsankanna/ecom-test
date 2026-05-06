<template>
  <q-layout view="lHh Lpr lFf" class="admin-layout">
    <!-- Sidebar / Drawer -->
    <q-drawer
      v-model="drawer"
      :mini="miniMode && $q.screen.gt.sm"
      show-if-above
      :width="240"
      :mini-width="64"
      class="admin-drawer"
      dark
    >
      <!-- Logo -->
      <div
        class="drawer-logo row items-center q-px-md"
        :class="{ 'justify-center': miniMode && $q.screen.gt.sm }"
      >
        <div class="logo-icon">
          <q-icon name="bolt" color="white" size="20px" />
        </div>
        <div
          v-if="!miniMode || $q.screen.lt.md"
          class="text-white text-weight-bold text-subtitle1 q-ml-sm"
        >
          AdminPro
        </div>
      </div>

      <q-separator dark class="q-my-sm" style="opacity: 0.1" />

      <!-- Nav Items -->
      <q-list padding>
        <q-item
          v-for="item in navItems"
          :key="item.route"
          clickable
          v-ripple
          :to="item.route"
          exact
          active-class="nav-active"
          class="nav-item rounded-borders q-mb-xs"
          :class="{ 'justify-center': miniMode && $q.screen.gt.sm }"
        >
          <q-item-section avatar>
            <q-icon :name="item.icon" size="20px" />
          </q-item-section>
          <q-item-section v-if="!miniMode || $q.screen.lt.md">
            <q-item-label>{{ item.label }}</q-item-label>
          </q-item-section>
          <q-item-section v-if="item.badge && (!miniMode || $q.screen.lt.md)" side>
            <q-badge :color="item.badgeColor" :label="item.badge" />
          </q-item-section>
          <q-tooltip
            v-if="miniMode && $q.screen.gt.sm"
            anchor="center right"
            self="center left"
            :offset="[8, 0]"
          >
            {{ item.label }}
          </q-tooltip>
        </q-item>
      </q-list>

      <q-space />

      <!-- Bottom section: Admin user info -->
      <div class="q-pa-md">
        <q-separator dark class="q-mb-md" style="opacity: 0.1" />
        <q-item
          clickable
          v-ripple
          class="nav-item rounded-borders"
          :class="{ 'justify-center': miniMode && $q.screen.gt.sm }"
        >
          <q-item-section avatar>
            <q-avatar size="30px" color="blue-9" text-color="white" font-size="13px">
              {{ adminInitials }}
            </q-avatar>
          </q-item-section>
          <q-item-section v-if="!miniMode || $q.screen.lt.md">
            <q-item-label class="text-white text-weight-medium">{{ adminName }}</q-item-label>
            <q-item-label caption class="text-blue-4">{{ adminEmail }}</q-item-label>
          </q-item-section>
        </q-item>
      </div>
    </q-drawer>

    <!-- Top Header -->
    <q-header class="admin-header" elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          :icon="miniMode ? 'menu_open' : 'menu'"
          color="blue-4"
          @click="$q.screen.gt.sm ? (miniMode = !miniMode) : (drawer = !drawer)"
        />

        <q-toolbar-title class="text-white text-subtitle1 text-weight-medium">
          {{ currentPageTitle }}
        </q-toolbar-title>

        <q-space />

        <!-- Right side actions -->
        <div class="row items-center q-gutter-sm">

          <!-- NOTIFICATIONS BUTTON with dropdown -->
          <q-btn round flat dense icon="notifications" color="blue-4" size="sm">
            <q-badge color="negative" floating rounded>{{ notificationCount }}</q-badge>
            <q-menu anchor="bottom right" self="top right" :offset="[0, 8]" class="notif-menu">
              <div class="notif-header row items-center justify-between q-px-md q-pt-md q-pb-sm">
                <span class="text-weight-bold text-white text-subtitle2">Notifications</span>
                <q-badge color="negative" rounded :label="notificationCount" />
              </div>
              <q-separator dark style="opacity: 0.1" />
              <q-list style="min-width: 300px; max-height: 360px; overflow-y: auto">
                <q-item
                  v-for="notif in recentNotifications"
                  :key="notif.id"
                  clickable
                  v-ripple
                  class="notif-item"
                  :class="{ 'notif-unread': !notif.read }"
                >
                  <q-item-section avatar>
                    <q-avatar :color="notif.color" text-color="white" size="36px" icon-size="18px">
                      <q-icon :name="notif.icon" size="18px" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-white text-caption text-weight-medium">
                      {{ notif.title }}
                    </q-item-label>
                    <q-item-label caption class="text-blue-3" style="font-size: 11px">
                      {{ notif.time }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side v-if="!notif.read">
                    <div class="notif-dot" />
                  </q-item-section>
                </q-item>
              </q-list>
              <q-separator dark style="opacity: 0.1" />
              <div class="q-pa-sm text-center">
                <q-btn
                  flat dense no-caps
                  color="blue-4"
                  label="View all notifications"
                  :to="'/admin/notifications'"
                  size="sm"
                />
              </div>
            </q-menu>
          </q-btn>

          <!-- REFRESH BUTTON -->
          <q-btn
            round flat dense
            icon="refresh"
            color="blue-4"
            size="sm"
            :loading="refreshing"
            @click="handleRefresh"
          >
            <q-tooltip anchor="bottom middle" self="top middle" :offset="[0, 4]">
              Refresh page
            </q-tooltip>
          </q-btn>

          <!-- ADMIN AVATAR with dropdown -->
          <q-avatar
            size="32px"
            color="blue-8"
            text-color="white"
            font-size="13px"
            class="cursor-pointer"
          >
            {{ adminInitials }}
            <q-menu anchor="bottom right" self="top right" :offset="[0, 8]" class="account-menu">
              <!-- Account header -->
              <div class="account-header q-px-md q-pt-md q-pb-sm">
                <div class="row items-center q-gutter-sm">
                  <q-avatar size="40px" color="blue-8" text-color="white" font-size="15px">
                    {{ adminInitials }}
                  </q-avatar>
                  <div>
                    <div class="text-white text-weight-bold text-body2">{{ adminName }}</div>
                    <div class="text-blue-4 text-caption">{{ adminEmail }}</div>
                  </div>
                </div>
              </div>
              <q-separator dark style="opacity: 0.1" class="q-my-xs" />
              <q-list style="min-width: 220px">
                <q-item clickable v-ripple class="account-menu-item" :to="'/admin/profile'">
                  <q-item-section avatar>
                    <q-icon name="person" color="blue-4" size="18px" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-white text-caption">My Profile</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item clickable v-ripple class="account-menu-item" :to="'/admin/settings'">
                  <q-item-section avatar>
                    <q-icon name="settings" color="blue-4" size="18px" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-white text-caption">Settings</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              <q-separator dark style="opacity: 0.1" class="q-my-xs" />
              <q-list>
                <!-- ★ LOGOUT — clears store + localStorage, goes to /login ★ -->
                <q-item
                  clickable
                  v-ripple
                  class="account-menu-item logout-item"
                  @click="handleLogout"
                >
                  <q-item-section avatar>
                    <q-icon name="logout" color="negative" size="18px" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-negative text-caption text-weight-medium">
                      Logout
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-avatar>

        </div>
      </q-toolbar>
    </q-header>

    <!-- Main Page Content -->
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

const $q       = useQuasar()
const route    = useRoute()
const router   = useRouter()
const authStore = useAuthStore()

const drawer    = ref(false)
const miniMode  = ref(false)
const refreshing = ref(false)

// ── Admin user info from Pinia store (set at login) ──────────────────────────
const adminName = computed(() => authStore.displayName || 'Admin User')
const adminEmail = computed(() => authStore.displayEmail || 'admin@example.com')
const adminInitials = computed(() => {
  const n = adminName.value.trim()
  const parts = n.split(' ').filter(Boolean)
  return parts.length >= 2
    ? (parts[0][0] + parts[1][0]).toUpperCase()
    : n.slice(0, 2).toUpperCase() || 'AD'
})

// ── Nav items — identical to your original ───────────────────────────────────
const navItems = [
  { label: 'Dashboard',    icon: 'dashboard',          route: '/admin/dashboard',     badge: null },
  { label: 'Users',        icon: 'group',              route: '/admin/users',         badge: '12K', badgeColor: 'blue-8' },
  { label: 'Roles',        icon: 'admin_panel_settings',route: '/admin/roles',        badge: null },
  { label: 'Products',     icon: 'inventory_2',        route: '/admin/products',      badge: null },
  { label: 'Orders',       icon: 'shopping_cart',      route: '/admin/orders',        badge: null,  badgeColor: 'warning' },
  { label: 'Payments',     icon: 'payments',           route: '/admin/payments',      badge: null,  badgeColor: 'negative' },
  { label: 'Analytics',    icon: 'analytics',          route: '/admin/analytics',     badge: null },
  { label: 'Inventory',    icon: 'inventory',          route: '/admin/inventory',     badge: null },
  { label: 'Reviews',      icon: 'star',               route: '/admin/reviews',       badge: null },
  { label: 'Coupons',      icon: 'local_offer',        route: '/admin/coupons',       badge: null },
  { label: 'Returns',      icon: 'undo',               route: '/admin/returns',       badge: null },
  { label: 'Shipments',    icon: 'local_shipping',     route: '/admin/shipments',     badge: null },
  { label: 'Notifications',icon: 'notifications',      route: '/admin/notifications', badge: null },
  { label: 'Exchanges',    icon: 'swap_horiz',         route: '/admin/exchanges',     badge: null },
  { label: 'Bulk Order',   icon: 'shopping_cart',      route: '/admin/bulkorders',    badge: null },
]

const currentPageTitle = computed(
  () => navItems.find(n => route.path.startsWith(n.route))?.label || 'Admin',
)

// ── Notifications — identical to your original ───────────────────────────────
const recentNotifications = ref([
  { id: 1, title: 'New order #8821 received',        time: '2 min ago',  icon: 'shopping_cart', color: 'blue-8',   read: false },
  { id: 2, title: 'Payment failed for order #8819',  time: '15 min ago', icon: 'payments',      color: 'negative', read: false },
  { id: 3, title: 'User John Doe registered',        time: '1 hr ago',   icon: 'person_add',    color: 'positive', read: false },
  { id: 4, title: 'Low stock alert: Product XYZ',    time: '3 hr ago',   icon: 'inventory',     color: 'warning',  read: true  },
  { id: 5, title: 'Return request #221 submitted',   time: '5 hr ago',   icon: 'undo',          color: 'purple-6', read: true  },
])

const notificationCount = computed(
  () => recentNotifications.value.filter(n => !n.read).length,
)

// ── Refresh ──────────────────────────────────────────────────────────────────
function handleRefresh() {
  refreshing.value = true
  setTimeout(() => { window.location.reload() }, 400)
}

// ── LOGOUT ───────────────────────────────────────────────────────────────────
// 1. Clears Pinia store (reactive state)
// 2. Removes all auth keys from localStorage
// 3. Redirects to /login
// The guard in index.js will prevent going back to /admin without re-login.
function handleLogout() {
  authStore.logout()
  router.replace('/login')
}
</script>

<style>
/* Global styles for admin layout */
body {
  background: #080f1e !important;
}
</style>

<style scoped>
.admin-layout {
  background: #080f1e;
}

.admin-header {
  background: rgba(8, 15, 30, 0.95) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  height: 56px;
}

.admin-drawer {
  background: linear-gradient(180deg, #080f1e 0%, #0a1628 100%) !important;
  border-right: 1px solid rgba(59, 130, 246, 0.12) !important;
}

.drawer-logo {
  height: 64px;
  gap: 0;
}

.logo-icon {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-item {
  color: #64748b;
  transition: all 0.15s;
  border-radius: 8px !important;
  min-height: 42px;
}
.nav-item:hover {
  background: rgba(59, 130, 246, 0.08) !important;
  color: #93c5fd !important;
}
.nav-active {
  background: rgba(59, 130, 246, 0.15) !important;
  color: #60a5fa !important;
  border-left: 3px solid #3b82f6;
}
.nav-active :deep(.q-icon) {
  color: #60a5fa !important;
}

/* Notification menu */
.notif-menu {
  background: #0d1b35 !important;
  border: 1px solid rgba(59, 130, 246, 0.18) !important;
  border-radius: 12px !important;
}
.notif-header { background: transparent; }
.notif-item   { color: #94a3b8; transition: background 0.15s; }
.notif-item:hover { background: rgba(59, 130, 246, 0.08) !important; }
.notif-unread { background: rgba(59, 130, 246, 0.05); }
.notif-dot    { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; }

/* Account menu */
.account-menu {
  background: #0d1b35 !important;
  border: 1px solid rgba(59, 130, 246, 0.18) !important;
  border-radius: 12px !important;
}
.account-header {
  background: rgba(59, 130, 246, 0.06);
  border-radius: 12px 12px 0 0;
}
.account-menu-item {
  color: #94a3b8;
  transition: background 0.15s;
  min-height: 40px;
}
.account-menu-item:hover { background: rgba(59, 130, 246, 0.08) !important; }
.logout-item:hover        { background: rgba(239, 68, 68, 0.08) !important; }
</style>