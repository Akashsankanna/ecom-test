import { api } from 'boot/axios'

export async function placeOrderApi(payload) {
  const response = await api.post('/orders/', payload)
  return response.data
}

export async function fetchOrdersByUser(userId) {
  const response = await api.get('/orders/', {
    params: { user_id: userId }
  })
  return response.data
}

export async function fetchOrderById(orderId, userId) {
  const response = await api.get(`/orders/${orderId}`, {
    params: { user_id: userId }
  })
  return response.data
}

// ✅ add this alias for OrderConfirmation.vue
export async function getOrderById(orderId, userId) {
  const response = await api.get(`/orders/${orderId}`, {
    params: { user_id: userId }
  })
  return response.data
}

export async function updateOrder(orderId, payload) {
  const response = await api.put(`/orders/${orderId}`, payload)
  return response.data
}

export async function cancelOrder(orderId, userId) {
  const response = await api.delete(`/orders/${orderId}`, {
    params: { user_id: userId }
  })
  return response.data
}
// =============================
// TRACK ORDER
// =============================
export async function trackOrder(orderId, userId) {
  const response = await api.get(`/orders/${orderId}`, {
    params: { user_id: userId }
  })

  return response.data
}