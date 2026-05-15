import { api } from 'boot/axios'

// =====================================================
// AUTH HELPERS
// =====================================================

const getAuthData = () => {
  const rawUserId = localStorage.getItem('user_id')
  const rawGuestUuid = localStorage.getItem('guest_uuid')

  const userId =
    rawUserId &&
    rawUserId !== 'null' &&
    rawUserId !== 'undefined' &&
    Number(rawUserId) > 0
      ? Number(rawUserId)
      : null

  const guestUuid =
    rawGuestUuid &&
    rawGuestUuid !== 'null' &&
    rawGuestUuid !== 'undefined'
      ? rawGuestUuid
      : null

  return {
    user_id: userId,
    guest_uuid: guestUuid,
  }
}

export const ensureGuestUuid = async () => {
  const rawUserId = localStorage.getItem('user_id')
  const existingGuestUuid = localStorage.getItem('guest_uuid')

  if (
    rawUserId &&
    rawUserId !== 'null' &&
    rawUserId !== 'undefined' &&
    Number(rawUserId) > 0
  ) {
    return null
  }

  if (
    existingGuestUuid &&
    existingGuestUuid !== 'null' &&
    existingGuestUuid !== 'undefined'
  ) {
    return existingGuestUuid
  }

  const res = await api.post('/cart/guest')
  const guestUuid = res?.data?.guest_uuid || null

  if (!guestUuid) {
    throw new Error('Guest UUID not returned from backend')
  }

  localStorage.setItem('guest_uuid', guestUuid)
  return guestUuid
}

const getAuthPayload = async () => {
  const auth = getAuthData()

  // IMPORTANT: send only user_id OR guest_uuid, not both
  if (auth.user_id) {
    return {
      user_id: auth.user_id,
    }
  }

  let guestUuid = auth.guest_uuid

  if (!guestUuid) {
    guestUuid = await ensureGuestUuid()
  }

  return {
    guest_uuid: guestUuid,
  }
}

// =====================================================
// NORMALIZERS
// =====================================================

const normalizeCartItem = (item = {}) => ({
  id: Number(item.id || item.cart_item_id || 0),
  cart_item_id: Number(item.cart_item_id || item.id || 0),
  cart_id: Number(item.cart_id || 0),
  product_id: Number(item.product_id || 0),
  variant_id: Number(item.variant_id || 0),

  quantity: Number(item.quantity || 0),
  price: Number(item.price || 0),
  customization_total: Number(item.customization_total || 0),

  line_total: Number(
    item.line_total ??
      ((Number(item.price || 0) + Number(item.customization_total || 0)) *
        Number(item.quantity || 0))
  ),

  product_name: item.product_name || 'Product',
  product_description: item.product_description || '',
  product_slug: item.product_slug || '',

  variant_name: item.variant_name || '',
  stock: Number(item.stock || 0),
  size: item.size || '',
  variant_sku: item.variant_sku || '',

  image_url: item.image_url || '',
})

const normalizeCartResponse = (data = {}) => {
  const rawItems = Array.isArray(data?.items) ? data.items : []
  const items = rawItems.map(normalizeCartItem)

  return {
    success: Boolean(data?.success),
    items,
    count: Number(data?.count ?? items.length),
  }
}

// =====================================================
// CART APIs
// =====================================================

export const addToCart = async (payload) => {
  if (!payload || !payload.variant_id) {
    throw new Error('variant_id is required')
  }

  const quantity = Number(payload.quantity || 1)

  if (quantity <= 0) {
    throw new Error('quantity must be greater than 0')
  }

  const authPayload = await getAuthPayload()

  const body = {
    variant_id: Number(payload.variant_id),
    quantity,
    ...authPayload,
  }

  console.log('ADD TO CART PAYLOAD:', body)

  const res = await api.post('/cart/add', body)
  return res.data
}

export const getCartItems = async () => {
  const auth = getAuthData()

  let res

  if (auth.user_id) {
    res = await api.get('/cart/', {
      params: {
        user_id: auth.user_id,
      },
    })
  } else {
    let guestUuid = auth.guest_uuid

    if (!guestUuid) {
      guestUuid = await ensureGuestUuid()
    }

    res = await api.get('/cart/', {
      params: {
        guest_uuid: guestUuid,
      },
    })
  }

  return normalizeCartResponse(res.data)
}

export const getCartSummary = async () => {
  const auth = getAuthData()

  if (auth.user_id) {
    const res = await api.get('/cart/summary', {
      params: {
        user_id: auth.user_id,
      },
    })

    return res.data
  }

  let guestUuid = auth.guest_uuid

  if (!guestUuid) {
    guestUuid = await ensureGuestUuid()
  }

  const res = await api.get('/cart/summary', {
    params: {
      guest_uuid: guestUuid,
    },
  })

  return res.data
}

export const updateCartQty = async (cartItemId, quantity) => {
  if (!cartItemId) {
    throw new Error('cartItemId is required')
  }

  const qty = Number(quantity)

  if (qty <= 0) {
    throw new Error('quantity must be greater than 0')
  }

  const authPayload = await getAuthPayload()

  const body = {
    cart_item_id: Number(cartItemId),
    quantity: qty,
    ...authPayload,
  }

  const res = await api.put('/cart/update', body)
  return res.data
}

export const removeCartItem = async (cartItemId) => {
  if (!cartItemId) {
    throw new Error('cartItemId is required')
  }

  const authPayload = await getAuthPayload()

  const res = await api.delete('/cart/remove', {
    data: {
      cart_item_id: Number(cartItemId),
      ...authPayload,
    },
  })

  return res.data
}

export const clearCart = async () => {
  const authPayload = await getAuthPayload()

  const res = await api.delete('/cart/clear', {
    data: {
      ...authPayload,
    },
  })

  return res.data
}

export const mergeGuestCart = async () => {
  const rawUserId = localStorage.getItem('user_id')
  const guestUuid = localStorage.getItem('guest_uuid')

  const userId =
    rawUserId &&
    rawUserId !== 'null' &&
    rawUserId !== 'undefined' &&
    Number(rawUserId) > 0
      ? Number(rawUserId)
      : null

  if (!userId || !guestUuid) {
    return null
  }

  const res = await api.post('/cart/merge', {
    user_id: userId,
    guest_uuid: guestUuid,
  })

  localStorage.removeItem('guest_uuid')
  return res.data
}

export const getCartCount = async () => {
  const data = await getCartItems()
  const items = Array.isArray(data?.items) ? data.items : []

  return items.reduce((sum, item) => sum + Number(item.quantity || 0), 0)
}

// =====================================================
// CHECKOUT / RAZORPAY APIs
// =====================================================

export async function createRazorpayOrder(payload) {
  const response = await api.post('/checkout/razorpay/create-order', {
    user_id: Number(payload.user_id),
    address_id: Number(payload.address_id),
    coupon_code: payload.coupon_code || null,
    shipping_amount: Number(payload.shipping_amount || 0),
  })

  return response.data
}

export async function verifyRazorpayPayment(payload) {
  const response = await api.post('/checkout/razorpay/verify-payment', {
    order_id: Number(payload.order_id),
    razorpay_order_id: payload.razorpay_order_id,
    razorpay_payment_id: payload.razorpay_payment_id,
    razorpay_signature: payload.razorpay_signature,
  })

  return response.data
}

// =====================================================
// ALIASES
// =====================================================

export const addToCartApi = addToCart
export const getCartApi = getCartItems
export const getCartSummaryApi = getCartSummary
export const updateCartApi = updateCartQty
export const updateCartItemApi = updateCartQty
export const removeCartItemApi = removeCartItem
export const deleteCartItemApi = removeCartItem
export const clearCartApi = clearCart
export const createGuest = ensureGuestUuid
export const mergeCartApi = mergeGuestCart
export const razorpayCreateOrderApi = createRazorpayOrder
export const razorpayVerifyPaymentApi = verifyRazorpayPayment

export default {
  ensureGuestUuid,
  createGuest,

  addToCart,
  addToCartApi,

  getCartItems,
  getCartApi,

  getCartSummary,
  getCartSummaryApi,

  updateCartQty,
  updateCartApi,
  updateCartItemApi,

  removeCartItem,
  removeCartItemApi,
  deleteCartItemApi,

  clearCart,
  clearCartApi,

  mergeGuestCart,
  mergeCartApi,

  getCartCount,

  createRazorpayOrder,
  verifyRazorpayPayment,
  razorpayCreateOrderApi,
  razorpayVerifyPaymentApi,
}
