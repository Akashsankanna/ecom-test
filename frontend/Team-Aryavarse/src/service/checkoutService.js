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
    payment_method: payload.payment_method || null
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
  user_id,
  address_id,
  coupon_code = null,
  currency = 'INR'
}) {
  const response = await api.post('/razorpay/create-order', {
    user_id: Number(user_id),
    address_id: Number(address_id),
    coupon_code: coupon_code || null,
    currency
  })

  return response.data
}


export async function verifyRazorpayPayment({
  order_id = null,
  razorpay_order_id,
  razorpay_payment_id,
  razorpay_signature,
  user_id,
  address_id
}) {
  const payload = {
    razorpay_order_id,
    razorpay_payment_id,
    razorpay_signature,
    user_id: Number(user_id),
    address_id: Number(address_id)
  }

  if (order_id !== null && order_id !== undefined && order_id !== '') {
    payload.order_id = Number(order_id)
  }

  const response = await api.post('/razorpay/verify-payment', payload)

  return response.data
}
