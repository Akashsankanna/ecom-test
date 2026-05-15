import { api } from 'boot/axios'

// Existing, only keep if backend has POST /orders/
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

// Alias for OrderConfirmation.vue
export async function getOrderById(orderId, userId) {
  return fetchOrderById(orderId, userId)
}

// ✅ fixed: should call /track endpoint
export async function trackOrder(orderId, userId) {
  const response = await api.get(`/orders/${orderId}/track`, {
    params: { user_id: userId }
  })
  return response.data
}

// Keep only if backend has PUT /orders/{order_id}
export async function updateOrder(orderId, payload) {
  const response = await api.put(`/orders/${orderId}`, payload)
  return response.data
}

// Keep only if backend has DELETE /orders/{order_id}
export async function cancelOrder(orderId, userId) {
  const response = await api.delete(`/orders/${orderId}`, {
    params: { user_id: userId }
  })
  return response.data
}

export async function createReturnRequest(orderId, userId, payload) {
  const response = await api.post(`/orders/${orderId}/return`, payload, {
    params: { user_id: userId }
  })
  return response.data
}
