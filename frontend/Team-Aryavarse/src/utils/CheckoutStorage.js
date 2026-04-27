const PROFILE_KEY = 'checkout_profile'
const SELECTED_ADDRESS_ID_KEY = 'checkout_selected_address_id'
const PAYMENT_METHOD_KEY = 'checkout_payment_method'
const COUPON_KEY = 'checkout_coupon'

export function getUserId() {
  const userId = localStorage.getItem('user_id')
  return userId ? Number(userId) : null
}

export function getGuestUuid() {
  return localStorage.getItem('guest_uuid')
}

export function isGuest() {
  return !getUserId() && !!getGuestUuid()
}

export function hasCheckoutProfile() {
  const profile = localStorage.getItem(PROFILE_KEY)

  if (!profile) return false

  try {
    const parsedProfile = JSON.parse(profile)

    return !!(
      parsedProfile?.name &&
      parsedProfile?.email &&
      parsedProfile?.phone
    )
  } catch (error) {
    return false
  }
}

export function saveCheckoutProfile(profile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile))
}

export function getCheckoutProfile() {
  const data = localStorage.getItem(PROFILE_KEY)
  return data ? JSON.parse(data) : null
}

export function saveSelectedAddressId(addressId) {
  localStorage.setItem(SELECTED_ADDRESS_ID_KEY, String(addressId))
}

export function getSelectedAddressId() {
  const data = localStorage.getItem(SELECTED_ADDRESS_ID_KEY)
  return data ? Number(data) : null
}

export function clearSelectedAddressId() {
  localStorage.removeItem(SELECTED_ADDRESS_ID_KEY)
}

export function savePaymentMethod(method) {
  localStorage.setItem(PAYMENT_METHOD_KEY, method || 'upi')
}

export function getPaymentMethod() {
  return localStorage.getItem(PAYMENT_METHOD_KEY) || 'upi'
}

export function saveCoupon(code, discount) {
  localStorage.setItem(
    COUPON_KEY,
    JSON.stringify({
      code: code || '',
      discount: Number(discount || 0)
    })
  )
}

export function getCoupon() {
  const data = localStorage.getItem(COUPON_KEY)
  return data ? JSON.parse(data) : null
}

export function getCouponCode() {
  const coupon = getCoupon()
  return coupon?.code || ''
}

export function getCouponDiscount() {
  const coupon = getCoupon()
  return Number(coupon?.discount || 0)
}

export function clearCoupon() {
  localStorage.removeItem(COUPON_KEY)
}
