<template>
  <div class="callback-wrap">
    <div v-if="blocked" class="card">
      <h3>Verify Your Email</h3>
      <p class="sub">
        We sent a verification link to<br/>
        <strong>{{ blockedEmail }}</strong>
      </p>
      <p class="sub">
        Click the link in your email.<br/>
        After verifying, click <strong>Continue with Google</strong> again on the login page.
      </p>
      <button class="btn" @click="$router.push('/login')">BACK TO LOGIN</button>
    </div>
    <div v-else class="card">
      <p class="sub">Logging you in…</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()

const blocked      = ref(false)
const blockedEmail = ref('')

onMounted(async () => {
  const p = route.query

  // ── Blocked: email not verified ──────────────────────────
  if (p.blocked === 'true') {
    blocked.value      = true
    blockedEmail.value = p.email || ''
    return
  }

  const token      = p.access_token
  const idToken    = p.id_token
  const userEmail  = p.email
  const keycloakId = p.keycloak_id
  const name       = p.name || userEmail?.split('@')[0] || 'User'

  if (!token) {
    router.replace('/login')
    return
  }

  /*
    ─────────────────────────────────────────────────────────
    ROOT CAUSE FIX:

    Previously setAuth() was called with NO id/user_id field:
      authStore.setAuth(token, {
        email, keycloak_id, name, id_token   ← no id or user_id!
      })

    setAuth() resolves userId from:
      userData?.id || userData?.user_id || userData?.user?.id ...
    
    All were undefined → userId = null → setAuth() returned early
    → localStorage.setItem('token', token) NEVER ran
    → localStorage.getItem('token') = null on next read
    → reviews POST had no token → backend returned 401
    → frontend showed "Session expired. Please log in again."

    User looked logged in because authStore.token was set in
    Pinia memory, but was never written to localStorage.
    Profile/wishlist/orders worked because they used the
    Pinia store directly — reviews was reading localStorage.

    FIX: Manually persist token to localStorage BEFORE calling
    setAuth, so token is always available regardless of whether
    setAuth's userId resolution succeeds.
    Also pass a temporary user_id placeholder so setAuth does
    not bail out — the real DB user_id gets resolved by the
    backend on every authenticated request via Keycloak token.
    ─────────────────────────────────────────────────────────
  */

  // ── Step 1: Persist access_token immediately ─────────────
  // This guarantees localStorage always has the token,
  // independent of setAuth's userId resolution logic.
  localStorage.setItem('token', token)
  if (idToken) localStorage.setItem('id_token', idToken)

  // ── Step 2: Call setAuth with all available data ─────────
  // We pass keycloak_id as a stand-in identifier.
  // The backend resolves the real DB user_id from the token.
  // setAuth will also set authStore.token = token in Pinia.
  authStore.setAuth(token, {
    email        : userEmail,
    keycloak_id  : keycloakId,
    name         : name,
    id_token     : idToken,
    // Provide fallback so setAuth does not exit early on null userId.
    // keycloak_id is used as a non-null placeholder here —
    // actual integer DB user_id is not available from Google OAuth
    // callback params (backend doesn't send it in redirect URL).
    // All API auth uses the Bearer token, not this local user_id.
    user_id      : keycloakId || 'google-user',
  })

  await nextTick()
  router.replace('/profile')
})
</script>

<style scoped>
.callback-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sub { text-align: center; line-height: 1.6; }
</style>