<template>
 <div class="login-card">
     <h3 class="login-title">Forgot Password</h3>
    <p class="login-sub">Reset your password using your registered phone number</p>

    <!-- Step 1: Enter phone -->
    <template v-if="step === 1">
            <input
  class="login-input"
  v-model="phone"
  placeholder="Registered Phone Number (10 digits)"
  maxlength="10"

  required

  @input="phone = phone.replace(/[^0-9]/g, '').slice(0,10)"

  pattern="[0-9]{10}"

  title="Enter valid 10-digit phone number"
/>
      <p class="error" v-if="error">{{ error }}</p>
      <button class="login-btn" @click="sendOtp" :disabled="loading">
        {{ loading ? 'SENDING...' : 'SEND OTP' }}
      </button>
    </template>

    <!-- Step 2: Verify OTP -->
    <template v-else-if="step === 2">
      <p class="sub">OTP sent to +91 {{ phone }}</p>
      <input v-model="otp" placeholder="Enter 6-digit OTP" maxlength="6" />
      <p class="error" v-if="error">{{ error }}</p>
      <button class="login-btn" @click="verifyOtp" :disabled="loading">
        {{ loading ? 'VERIFYING...' : 'VERIFY OTP' }}
      </button>
      <p class="resend" @click="sendOtp">Resend OTP</p>
    </template>

    <!-- Step 3: Set new password -->
    <template v-else-if="step === 3">
      <p class="success">✅ OTP Verified — Set your new password</p>
      <input v-model="newPassword"     type="password" placeholder="New Password (min 8 chars)" />
      <input v-model="confirmPassword" type="password" placeholder="Confirm New Password" />
      <p class="error" v-if="error">{{ error }}</p>
      <button class="login-btn" @click="resetPassword" :disabled="loading">
        {{ loading ? 'UPDATING...' : 'SET NEW PASSWORD' }}
      </button>
    </template>

    <!-- Step 4: Success -->
    <template v-else-if="step === 4">
      <div class="success-box">
        <p>🎉 Password updated successfully!</p>
        <button class="login-btn" @click="$router.push('/login')">LOGIN NOW</button>
      </div>
    </template>

    <p class="login-switch" v-if="step < 4">
      Remember your password?
      <span @click="$router.push('/login')">Login</span>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from 'src/api/auth'

const router = useRouter()

const step            = ref(1)
const phone           = ref('')
const otp             = ref('')
const resetToken      = ref('')   // from backend after OTP verify
const newPassword     = ref('')
const confirmPassword = ref('')
const error           = ref('')
const loading         = ref(false)

async function sendOtp() {
  error.value = ''
  if (!/^\d{10}$/.test(phone.value)) {
    error.value = 'Enter a valid 10-digit phone number'
    return
  }
  loading.value = true
  try {
    const res = await authAPI.forgotPasswordInit(phone.value)
    if (res.message) step.value = 2
    else error.value = res.detail || 'Failed to send OTP'
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Network error — is backend running?'
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
    const res = await authAPI.forgotPasswordVerify(phone.value, otp.value)
    if (res.reset_token) {
      resetToken.value = res.reset_token
      step.value = 3
    } else {
      error.value = res.detail || 'Invalid OTP'
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Network error'
  } finally {
    loading.value = false
  }
}

async function resetPassword() {
  error.value = ''

  if (!newPassword.value || newPassword.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  try {
    const res = await authAPI.forgotPasswordReset(
      phone.value,
      resetToken.value,
      newPassword.value,
      confirmPassword.value
    )
    if (res.message) {
      step.value = 4
    } else {
      error.value = res.detail || 'Failed to reset password'
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Network error'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss">
@import 'src/css/login.scss';

.error   { color: red;   font-size: 13px; margin: 4px 0; }
.success { color: green; font-weight: 500; margin-bottom: 12px; }
.resend  {
  text-align: center; font-size: 13px; color: #666;
  margin-top: 8px; cursor: pointer;
  &:hover { color: #333; text-decoration: underline; }
}
.success-box {
  text-align: center;
  padding: 20px;
  background: #e8f5e9;
  border-radius: 8px;
  margin-bottom: 16px;
  p { margin: 0 0 16px; font-size: 15px; font-weight: 500; }
}
</style>