/**
 * auth.js — Frontend API wrapper for all auth endpoints
 *
 * Uses status-aware fetch: if the server returns a 4xx/5xx,
 * we still parse the JSON body so callers can read res.detail.
 */

const BASE = 'http://localhost:8000/auth'

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  })
  try {
    // Always parse JSON — FastAPI returns {detail: ...} even on errors
    return await res.json()
  } catch {
    return { detail: `Server error (${res.status})` }
  }
}

export const authAPI = {

  // ── SIGNUP ──────────────────────────────────────────────────────────────

  /** Step 1: Send OTP to phone number */
  initiateSignup(phone) {
    return post('/signup/initiate', { phone })
  },

  /** Step 2: Verify OTP */
  verifyOtp(phone, otp) {
    return post('/signup/verify', { phone, otp })
  },

  /**
   * Step 3: Complete signup
   * Backend creates Keycloak user (emailVerified=false) and sends verification email.
   * User must click the email link before they can login.
   */
  completeSignup(name, email, password, phone) {
    return post('/signup/complete', { name, email, password, phone })
  },

  // ── LOGIN ────────────────────────────────────────────────────────────────

  /**
   * Login with phone-or-email + password.
   * `identifier` can be a 10-digit phone number OR an email address.
   * Field name is "identifier" — NOT "email".
   */
  loginWithPassword(identifier, password) {
    return post('/login/password', { identifier, password })
  },

  // ── FORGOT PASSWORD ──────────────────────────────────────────────────────

  /** Step 1: Send OTP to registered phone */
  forgotPasswordInit(phone) {
    return post('/forgot-password/initiate', { phone })
  },

  /** Step 2: Verify OTP → receive reset_token */
  forgotPasswordVerify(phone, otp) {
    return post('/forgot-password/verify', { phone, otp })
  },

  /**
   * Step 3: Reset password using the one-time reset_token.
   * Backend resets password in Keycloak via Admin API (no DB password stored).
   */
  forgotPasswordReset(phone, reset_token, new_password, confirm_password) {
    return post('/forgot-password/reset', {
      phone,
      reset_token,
      new_password,
      confirm_password,
    })
  },
}