<template>
  <div class="login-page">
 <div class="login-card">
      <h3 class="login-title">Login</h3>
      <p class="login-sub">Welcome back! Login to continue shopping</p>

    <!-- ✅ Session expired notice — shown when auto-logged out -->
    <div v-if="sessionExpired" class="session-expired-box">
      <p>⏱️ Your session has expired.</p>
      <p>Please log in again to continue.</p>
    </div>

    <!-- Email not verified notice -->
    <div v-if="showVerifyMsg" class="verify-box">
      <p>📧 Please verify your email first.</p>
      <p>Check your inbox for a verification link from us.</p>
      <button class="btn" @click="showVerifyMsg = false">OK, I'll check</button>
    </div>

    <template v-else>
<input
  class="login-input"
  v-model="identifier"
  type="text"
  placeholder="Phone Number or Email"
  autocomplete="username"
  required

  @input="identifier = /^[0-9]*$/.test(identifier)
    ? identifier.replace(/[^0-9]/g, '').slice(0,10)
    : identifier.replace(/[^a-zA-Z0-9@.]/g, '').slice(0,30)"

  pattern="(^[0-9]{10}$)|(^[a-zA-Z0-9.]+@gmail\.com$)"

  title="Enter valid 10-digit phone number or proper @gmail.com email"
/>
<input
  class="login-input"
  v-model="password"
  type="password"
  placeholder="Password"
  autocomplete="current-password"

  required
  minlength="8"
  maxlength="20"

  title="Password must be between 8 to 20 characters"
/>

      <p class="error" v-if="error">{{ error }}</p>

      <button class="login-btn" @click="login" :disabled="loading">
        {{ loading ? 'LOGGING IN...' : 'LOGIN' }}
      </button>

      <p class="forgot" @click="$router.push('/forgot-password')">
        Forgot Password?
      </p>

      <div class="divider">or</div>

      <button class="login-btn btn-google" @click="loginWithGoogle">
        Continue with Google
      </button>

      <p class="login-switch">
        Don't have an account?
        <span @click="$router.push('/signup')">Sign Up</span>
      </p>
    </template>
  </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authAPI } from 'src/api/auth'
import { useAuthStore } from 'src/stores/auth'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()

const identifier   = ref('')
const password     = ref('')
const error        = ref('')
const loading      = ref(false)
const showVerifyMsg = ref(false)

// ✅ Show banner when redirected here due to expired session
const sessionExpired = computed(() => route.query.session === 'expired')

async function login() {
  error.value = ''

  if (!identifier.value || !password.value) {
    error.value = 'Both fields are required'
    return
  }

  loading.value = true

  try {
    const res = await authAPI.loginWithPassword(identifier.value, password.value)

    if (res.detail) {
      if (res.detail === 'EMAIL_NOT_VERIFIED') {
        showVerifyMsg.value = true
      } else {
        error.value = res.detail
      }
      return
    }

    if (!res.access_token) {
      error.value = 'Login failed. Please try again.'
      return
    }

    await authStore.setAuth(res.access_token, {
      id          : res?.user?.id,
      email       : res?.user?.email,
      keycloak_id : res?.user?.keycloak_id,
      name        : res?.user?.name,
      id_token    : res?.id_token,
    })

    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)

  } catch (e) {
    if (e?.response?.status === 403) {
      showVerifyMsg.value = true
    } else {
      error.value = 'Network error — is backend running?'
    }
  } finally {
    loading.value = false
  }
}

function loginWithGoogle() {
  const redirectPath = route.query.redirect || '/'
  window.location.href = `http://localhost:8000/auth/login/google?redirect=${encodeURIComponent(redirectPath)}`
}
</script>

<style lang="scss">
@import 'src/css/login.scss';

.error {
  color: red;
  font-size: 13px;
  margin: 4px 0;
}

.divider {
  text-align: center;
  margin: 12px 0;
  color: #aaa;
}

.btn-google {
  background: #fff;
  color: #333;
  border: 1px solid #ddd;
}

.forgot {
  text-align: right;
  font-size: 13px;
  color: #666;
  margin: 6px 0 2px;
  cursor: pointer;

  &:hover {
    color: #333;
    text-decoration: underline;
  }
}

.verify-box {
  text-align: center;
  padding: 16px;
  background: #fff8e1;
  border-radius: 8px;
  margin-bottom: 12px;

  p {
    margin: 6px 0;
    font-size: 14px;
  }
}

/* ✅ Session expired banner */
.session-expired-box {
  text-align: center;
  padding: 14px 16px;
  background: #fff3f3;
  border: 1px solid #ffcccc;
  border-radius: 8px;
  margin-bottom: 14px;

  p {
    margin: 4px 0;
    font-size: 14px;
    color: #c0392b;
  }
}
</style>