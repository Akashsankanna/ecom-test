<template>
  <div class="card">
    <h3>Admin Login</h3>
    <p class="sub">Sign in to access the admin panel</p>

    <!-- Email verify message -->
    <div v-if="showVerifyMsg" class="verify-box">
      <p>📧 Please verify your email first.</p>
      <p>Check your inbox for the verification link.</p>

      <button class="btn" @click="showVerifyMsg = false">
        OK, I'll check
      </button>
    </div>

    <template v-else>
      <input
        v-model="identifier"
        type="text"
        placeholder="Email or Phone Number"
        autocomplete="username"
      />

      <input
        v-model="password"
        type="password"
        placeholder="Password"
        autocomplete="current-password"
        @keyup.enter="login"
      />

      <p class="error" v-if="error">{{ error }}</p>

      <button class="btn" @click="login" :disabled="loading">
        {{ loading ? 'SIGNING IN...' : 'SIGN IN' }}
      </button>

      <p class="forgot" @click="$router.push('/forgot-password')">
        Forgot Password?
      </p>

      <div class="divider">or</div>

      <button class="btn btn-google" @click="loginWithGoogle">
        <img
          src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
          width="18"
          height="18"
          alt="Google"
          style="margin-right:8px"
        />
        Continue with Google
      </button>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from 'src/api/auth'
import { useAuthStore } from 'src/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const identifier = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showVerifyMsg = ref(false)

async function login() {
  error.value = ''

  if (!identifier.value.trim() || !password.value.trim()) {
    error.value = 'Both fields are required'
    return
  }

  loading.value = true

  try {
    const res = await authAPI.loginWithPassword(
      identifier.value.trim(),
      password.value
    )

    // backend custom error
    if (res.detail) {
      if (res.detail === 'EMAIL_NOT_VERIFIED') {
        showVerifyMsg.value = true
      } else {
        error.value = res.detail
      }
      return
    }

    if (!res.access_token) {
      error.value = 'Login failed'
      return
    }

    // role from backend
    const role = (
      res.user?.user_type ||
      res.user?.role ||
      'customer'
    ).toLowerCase()

    // only admin allowed
    if (role !== 'admin') {
      error.value = 'Access denied. Admin credentials required.'
      return
    }

    // save auth
    authStore.setAuth(
      res.access_token,
      {
        email: res.user.email,
        name: res.user.name,
        keycloak_id: res.user.keycloak_id,
        id_token: res.id_token
      },
      role
    )

    // redirect admin dashboard
    router.replace('/admin/dashboard')

  } catch (err) {
    if (err?.response?.status === 403) {
      showVerifyMsg.value = true
    } else {
      error.value = 'Invalid credentials or server error'
    }
  } finally {
    loading.value = false
  }
}

function loginWithGoogle() {
  window.location.href = 'http://localhost:8000/auth/login/google'
}
</script>

<style lang="scss">
@import 'src/css/login.scss';

.error {
  color: #e53935;
  font-size: 13px;
  margin: 6px 0;
}

.divider {
  text-align: center;
  margin: 14px 0;
  color: #aaa;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e0e0e0;
  }
}

.btn-google {
  background: #fff;
  color: #333;
  border: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
}

.forgot {
  text-align: right;
  font-size: 13px;
  color: #666;
  margin: 8px 0 4px;
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
  border-radius: 10px;
  margin-bottom: 12px;

  p {
    margin: 6px 0;
    font-size: 14px;
  }
}
</style>