import { api } from 'boot/axios'

// ==========================
// CHECKOUT APIs
// ==========================
export async function createCheckoutSession(payload) {
  const response = await api.post('/checkout/', {
    user_id: Number(payload.user_id),
    address_id: Number(payload.address_id),
    coupon_code: payload.coupon_code || null,
    shipping_amount: Number(payload.shipping_amount || 0),
    payment_method: payload.payment_method
  })
  return response.data
}

export async function fetchCheckoutSummary(
  userId,
  addressId,
  couponCode = null,
  paymentMethod = null
) {
  const response = await api.get('/checkout/summary', {
    params: {
      user_id: Number(userId),
      address_id: Number(addressId),
      coupon_code: couponCode || null,
      payment_method: paymentMethod || null
    }
  })
  return response.data
}

// ==========================
// RAZORPAY APIs
// ==========================
export async function createRazorpayOrder({
  amount,
  currency = 'INR',
  receipt
}) {
  const response = await api.post('/razorpay/create-order', {
    amount: Number(amount),
    currency,
    receipt: receipt || `receipt_${Date.now()}`
  })
  return response.data
}

export async function verifyRazorpayPayment({
  razorpay_order_id,
  razorpay_payment_id,
  razorpay_signature
}) {
  const response = await api.post('/razorpay/verify-payment', {
    razorpay_order_id,
    razorpay_payment_id,
    razorpay_signature
  })
  return response.data
}
