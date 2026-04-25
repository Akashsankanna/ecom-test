<template>
  <div class="card">
    <h3>Sign Up</h3>
    <p class="sub">Create your account to start shopping</p>

    <!-- Step 1: Enter phone -->
    <template v-if="step === 1">
      <input v-model="phone" placeholder="Phone Number (10 digits)" maxlength="10" />
      <p class="error" v-if="error">{{ error }}</p>
      <button class="btn" @click="sendOtp" :disabled="loading">
        {{ loading ? 'SENDING...' : 'SEND OTP' }}
      </button>
    </template>

    <!-- Step 2: Verify OTP -->
    <template v-else-if="step === 2">
      <p class="sub">OTP sent to +91 {{ phone }}</p>
      <input v-model="otp" placeholder="Enter 6-digit OTP" maxlength="6" />
      <p class="error" v-if="error">{{ error }}</p>
      <button class="btn" @click="verifyOtp" :disabled="loading">
        {{ loading ? 'VERIFYING...' : 'VERIFY OTP' }}
      </button>
      <p class="resend" @click="sendOtp">Resend OTP</p>
    </template>

    <!-- Step 3: Fill details -->
    <template v-else-if="step === 3">
      <p class="success">✅ Phone Verified — Fill in your details</p>
      <input v-model="name"     placeholder="Full Name" />
      <input v-model="email"    type="email"    placeholder="Email Address" />
      <input v-model="password" type="password" placeholder="Password (min 8 chars)" />
      <p class="error" v-if="error">{{ error }}</p>
      <button class="btn" @click="completeSignup" :disabled="loading">
        {{ loading ? 'CREATING...' : 'CREATE ACCOUNT' }}
      </button>
    </template>

    <!-- Step 4: Email verification notice -->
    <template v-else-if="step === 4">
      <div class="verify-box">
        <p>🎉 Account created successfully!</p>
        <p>
          We've sent a <strong>verification link</strong> to<br/>
          <strong>{{ email }}</strong>
        </p>
        <p>Please verify your email before logging in.</p>
        <button class="btn" @click="$router.push('/login')">GO TO LOGIN</button>
      </div>
    </template>

    <p class="switch" v-if="step < 4">
      Already have an account?
      <span @click="$router.push('/login')">Login</span>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
// import { useRouter } from 'vue-router'
import { authAPI } from 'src/api/auth'

// const router = useRouter()

const step     = ref(1)
const phone    = ref('')
const otp      = ref('')
const name     = ref('')
const email    = ref('')
const password = ref('')
const error    = ref('')
const loading  = ref(false)

async function sendOtp() {
  error.value = ''
  if (!/^\d{10}$/.test(phone.value)) {
    error.value = 'Enter a valid 10-digit phone number'
    return
  }
  loading.value = true
  try {
    const res = await authAPI.initiateSignup(phone.value)
    if (res.message) step.value = 2
    else error.value = res.detail || 'Failed to send OTP'
  } catch {
    error.value = 'Network error — is backend running?'
  } finally {
    loading.value = false
  }
}

async function verifyOtp() {
  error.value = ''
  if (otp.value.length !== 6) {
    error.value = 'Enter the 6-digit OTP'
    return
  }
  loading.value = true
  try {
    const res = await authAPI.verifyOtp(phone.value, otp.value)
    if (res.message) step.value = 3
    else error.value = res.detail || 'Invalid OTP'
  } catch {
    error.value = 'Network error'
  } finally {
    loading.value = false
  }
}

async function completeSignup() {
  error.value = ''

  if (!name.value.trim()) {
    error.value = 'Full name is required'
    return
  }
  if (!email.value) {
    error.value = 'Email is required'
    return
  }
  if (!password.value || password.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  loading.value = true
  try {
    const res = await authAPI.completeSignup(
      name.value.trim(),
      email.value,
      password.value,
      phone.value
    )

    if (!res.keycloak_id) {
      error.value = res.detail || 'Signup failed'
      return
    }

    // Account created — show "verify your email" message
    step.value = 4

  } catch {
    error.value = 'Network error'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss">
@import 'src/css/sign.scss';

.error   { color: red;   font-size: 13px; margin: 4px 0; }
.success { color: green; font-weight: 500; margin-bottom: 12px; }
.resend  {
  text-align: center; font-size: 13px; color: #666;
  margin-top: 8px; cursor: pointer;
  &:hover { color: #333; text-decoration: underline; }
}

.verify-box {
  text-align: center;
  padding: 20px;
  background: #e8f5e9;
  border-radius: 8px;
  margin-bottom: 12px;
  p { margin: 8px 0; font-size: 14px; }
}
</style>