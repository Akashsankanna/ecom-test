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
import { onMounted, ref, nextTick } from 'vue'   // ← add nextTick
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()

const blocked      = ref(false)
const blockedEmail = ref('')

onMounted(async () => {           // ← async
  const p = route.query

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
    router.replace('/login')      // ← replace, not push
    return
  }

  authStore.setAuth(token, {
    email:       userEmail,
    keycloak_id: keycloakId,
    name:        name,
    id_token:    idToken,
  })

  await nextTick()                // ← wait for Pinia reactive state to settle
  router.replace('/profile')     // ← replace so back-button doesn't loop to callback
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