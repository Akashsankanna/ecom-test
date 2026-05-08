<template>
  <div class="profile-page">
    <div class="profile-card">

      <!-- ── LEFT PANEL ── -->
      <div class="profile-left">
        <div class="avatar-circle">{{ initials }}</div>
        <h2 class="profile-name">{{ displayName }}</h2>
        <p class="profile-email">{{ user?.email || '—' }}</p>

        <div class="profile-divider" />

        <span class="verified-badge">
          <q-icon name="verified_user" size="14px" />
          Verified Account
        </span>

        <button class="logout-btn" @click="handleLogout">
          <q-icon name="logout" size="16px" />
          Logout
        </button>
      </div>

      <!-- ── RIGHT PANEL ── -->
      <div class="profile-right">

        <p class="section-label">Account Info</p>
        <div class="profile-details">
          <div class="detail-row">
            <q-icon name="person" size="18px" class="detail-icon" />
            <span class="detail-label">Name</span>
            <span class="detail-value">{{ displayName }}</span>
          </div>
          <div class="detail-row">
            <q-icon name="mail" size="18px" class="detail-icon" />
            <span class="detail-label">Email</span>
            <span class="detail-value">{{ user?.email || '—' }}</span>
          </div>
          <div class="detail-row">
            <q-icon name="verified_user" size="18px" class="detail-icon" />
            <span class="detail-label">Account</span>
            <span class="detail-value verified">Verified ✓</span>
          </div>
        </div>

        <div class="profile-divider" />

        <p class="section-label">Quick Links</p>
        <div class="profile-links">
          <div class="profile-link" @click="$router.push('/cart')">
            <span class="link-icon" style="background:#EEF3FF">
              <q-icon name="shopping_cart" size="18px" style="color:#5b8cde" />
            </span>
            <span>My Cart</span>
            <q-icon name="chevron_right" size="18px" class="chevron" />
          </div>
          <div class="profile-link" @click="$router.push('/wishlist')">
            <span class="link-icon" style="background:#FFF0F7">
              <q-icon name="favorite" size="18px" style="color:#e06aa0" />
            </span>
            <span>My Wishlist</span>
            <q-icon name="chevron_right" size="18px" class="chevron" />
          </div>
          <div class="profile-link" @click="goToOrders">
            <span class="link-icon" style="background:#E8F8F5">
              <q-icon name="receipt_long" size="18px" style="color:#1a7a6e" />
            </span>
            <span>My Orders</span>
            <q-icon name="chevron_right" size="18px" class="chevron" />
          </div>
          <div class="profile-link" @click="$router.push('/')">
            <span class="link-icon" style="background:#FFF8E8">
              <q-icon name="storefront" size="18px" style="color:#e09040" />
            </span>
            <span>Continue Shopping</span>
            <q-icon name="chevron_right" size="18px" class="chevron" />
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const router    = useRouter()
const authStore = useAuthStore()

function goToOrders() {
  router.push('/orders')
}

// ✅ Check token expiry on mount — don't just check if token exists
function isTokenExpired(token) {
  if (!token) return true
  try {
    // Decode payload without verification — just to read exp claim
    const base64Payload = token.split('.')[1]
    const padding = '='.repeat((4 - base64Payload.length % 4) % 4)
    const payload = JSON.parse(atob(base64Payload + padding))
    const now = Math.floor(Date.now() / 1000)
    // Add 10s buffer to catch tokens expiring very soon
    return payload.exp < now + 10
  } catch {
    return true
  }
}

onMounted(() => {
  const token = authStore.token || localStorage.getItem('token')

  if (!token || isTokenExpired(token)) {
    // Token missing or expired — clear and redirect
    authStore.logout()
    router.replace({ path: '/login', query: { session: 'expired' } })
    return
  }
})

const user = computed(() => authStore.user)

const displayName = computed(() => {
  return user.value?.name
    || user.value?.email?.split('@')[0]
    || 'User'
})

const initials = computed(() => {
  const n = displayName.value
  const parts = n.trim().split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return n.slice(0, 2).toUpperCase()
})

function handleLogout() {
  const idToken = authStore.id_token
  authStore.logout()
  if (idToken) {
    window.location.href =
      `http://localhost:8000/auth/logout?id_token_hint=${idToken}`
  } else {
    router.push('/login')
  }
}
</script>
<style scoped>
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* ══════════════════════════════════════
   PAGE — stretches to fill Quasar's
   router-view area (below the navbar)
══════════════════════════════════════ */
.profile-page {
  --teal:    #1a7a6e;
  --teal-lt: #e6f5f2;
  --border:  #e4e9e8;
  --text:    #1a1a1a;
  --muted:   #888;
  --r:       13px;

  /* fill full remaining height below navbar */
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 64px);
  display: flex;
  background: #f0f5f4;
  animation: pageFadeIn 0.35s ease both;
}

@keyframes pageFadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* ══════════════════════════════════════
   CARD — fills the whole page area
══════════════════════════════════════ */
.profile-card {
  width: 100%;
  display: grid;
  grid-template-columns: 300px 1fr;
  min-height: calc(100vh - 64px);
  animation: cardIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ══════════════════════════════════════
   LEFT PANEL — teal sidebar
══════════════════════════════════════ */
.profile-left {
  background: linear-gradient(175deg, #1a7a6e 0%, #0e4d45 100%);
  padding: 64px 36px 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: sticky;
  top: 0;
  height: calc(100vh - 64px);
}

/* ══════════════════════════════════════
   RIGHT PANEL — content area
══════════════════════════════════════ */
.profile-right {
  padding: 60px 64px;
  display: flex;
  flex-direction: column;
  background: #f7faf9;
  overflow-y: auto;
}

/* ══════════════════════════════════════
   AVATAR
══════════════════════════════════════ */
.avatar-circle {
  width: 104px;
  height: 104px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.16);
  border: 3px solid rgba(255, 255, 255, 0.38);
  color: #fff;
  font-size: 36px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-bottom: 24px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  animation: avatarPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.15s both;
}

@keyframes avatarPop {
  from { opacity: 0; transform: scale(0.6); }
  to   { opacity: 1; transform: scale(1); }
}

.avatar-circle:hover {
  transform: scale(1.06);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.profile-name {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
  word-break: break-word;
}

.profile-email {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.62);
  margin: 0 0 32px;
  word-break: break-all;
  line-height: 1.55;
}

/* ══════════════════════════════════════
   DIVIDERS
══════════════════════════════════════ */
.profile-left .profile-divider {
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.14);
  margin: 0 0 28px;
}

.profile-right .profile-divider {
  width: 100%;
  height: 1px;
  background: var(--border);
  margin: 32px 0;
}

/* ══════════════════════════════════════
   VERIFIED BADGE
══════════════════════════════════════ */
.verified-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.13);
  color: #9fe8de;
  font-size: 12px;
  font-weight: 600;
  padding: 7px 16px;
  border-radius: 20px;
  margin-bottom: auto;
}

/* ══════════════════════════════════════
   LOGOUT BUTTON
══════════════════════════════════════ */
.logout-btn {
  margin-top: 36px;
  width: 100%;
  padding: 13px;
  border: 1.5px solid rgba(255, 255, 255, 0.28);
  border-radius: 12px;
  background: transparent;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.11);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.55);
}

.logout-btn:active { transform: scale(0.98); }

/* ══════════════════════════════════════
   SECTION LABEL
══════════════════════════════════════ */
.section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 14px;
}

/* ══════════════════════════════════════
   DETAIL ROWS
══════════════════════════════════════ */
.profile-details {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  padding: 14px 16px;
  border-radius: var(--r);
  border: 1px solid transparent;
  background: #fff;
  transition: background 0.15s, border-color 0.15s;
  min-width: 0;
}

.detail-row:hover {
  background: var(--teal-lt);
  border-color: #c4e0dc;
}

.detail-icon { color: var(--muted); flex-shrink: 0; }

.detail-label {
  color: var(--muted);
  width: 70px;
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.detail-value {
  color: var(--text);
  font-weight: 500;
  min-width: 0;
  word-break: break-word;
  font-size: 14px;
}

.detail-value.verified {
  color: var(--teal);
  font-weight: 700;
}

/* ══════════════════════════════════════
   QUICK LINKS — 2×2 grid
══════════════════════════════════════ */
.profile-links {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.profile-link {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 16px;
  border-radius: var(--r);
  border: 1px solid var(--border);
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  transition: background 0.15s, border-color 0.15s, transform 0.15s, box-shadow 0.15s;
  min-width: 0;
}

.profile-link:hover {
  background: var(--teal-lt);
  border-color: #a8d8d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(26, 122, 110, 0.1);
}

.link-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-link span:not(.link-icon) {
  min-width: 0;
  word-break: break-word;
}

.profile-link .chevron {
  margin-left: auto;
  color: #ccc;
  flex-shrink: 0;
  transition: transform 0.15s, color 0.15s;
}

.profile-link:hover .chevron {
  transform: translateX(4px);
  color: var(--teal);
}

/* ══════════════════════════════════════
   TABLET 681px – 960px
══════════════════════════════════════ */
@media (min-width: 681px) and (max-width: 960px) {
  .profile-card {
    grid-template-columns: 240px 1fr;
  }

  .profile-left {
    padding: 48px 24px 40px;
  }

  .profile-right {
    padding: 40px 36px;
  }

  .profile-links {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}

/* ══════════════════════════════════════
   MOBILE ≤ 680px — vertical stack
══════════════════════════════════════ */
@media (max-width: 680px) {
  .profile-page {
    min-height: 100vh;
    flex-direction: column;
  }

  .profile-card {
    grid-template-columns: 1fr;
    min-height: 100vh;
  }

  .profile-left {
    position: relative;
    height: auto;
    padding: 44px 24px 36px;
    min-height: unset;
  }

  .profile-right {
    padding: 32px 20px 48px;
    flex: 1;
  }

  .profile-links {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .logout-btn {
    margin-top: 28px;
  }
}

/* ══════════════════════════════════════
   SMALL MOBILE ≤ 420px
══════════════════════════════════════ */
@media (max-width: 420px) {
  .profile-left {
    padding: 36px 18px 28px;
  }

  .avatar-circle {
    width: 84px;
    height: 84px;
    font-size: 28px;
    margin-bottom: 16px;
  }

  .profile-name  { font-size: 19px; }
  .profile-email { font-size: 12px; }

  .profile-right {
    padding: 24px 16px 36px;
  }

  .detail-row {
    padding: 11px 10px;
    gap: 8px;
  }

  .detail-label  { width: 56px; font-size: 10px; }
  .detail-value  { font-size: 13px; }

  .profile-link {
    padding: 14px 10px;
    font-size: 13px;
    gap: 10px;
  }

  .link-icon {
    width: 34px;
    height: 34px;
  }
}
</style>
