<template>
  <div class="card">
    <h3>Login</h3>
    <p class="sub">Welcome back! Login to continue shopping</p>

    <!-- Email not verified notice -->
    <div v-if="showVerifyMsg" class="verify-box">
      <p>📧 Please verify your email first.</p>
      <p>Check your inbox for a verification link from us.</p>
      <button class="btn" @click="showVerifyMsg = false">OK, I'll check</button>
    </div>

    <template v-else>
      <!--
        identifier = phone number (10 digits) OR email
        Backend resolves phone → email → Keycloak login
      -->
      <input
        v-model="identifier"
        type="text"
        placeholder="Phone Number or Email"
        autocomplete="username"
      />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        autocomplete="current-password"
      />

      <p class="error" v-if="error">{{ error }}</p>

      <button class="btn" @click="login" :disabled="loading">
        {{ loading ? 'LOGGING IN...' : 'LOGIN' }}
      </button>

      <!-- Forgot Password -->
      <p class="forgot" @click="$router.push('/forgot-password')">
        Forgot Password?
      </p>

      <div class="divider">or</div>

      <button class="btn btn-google" @click="loginWithGoogle">
        Continue with Google
      </button>

      <p class="switch">
        Don't have an account?
        <span @click="$router.push('/signup')">Sign Up</span>
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authAPI } from 'src/api/auth'
import { useAuthStore } from 'src/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const identifier = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showVerifyMsg = ref(false)

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
      id: res?.user?.id,
      email: res?.user?.email,
      keycloak_id: res?.user?.keycloak_id,
      name: res?.user?.name,
      id_token: res?.id_token,
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
</style>
