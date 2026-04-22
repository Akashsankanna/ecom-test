import { api } from 'boot/axios'

// GET dropdown options
export async function fetchBulkOrderOptions() {
  const response = await api.get('/bulk-orders/options')
  return response.data
}

// SUBMIT bulk request
export async function submitBulkOrderRequest(payload) {
  const response = await api.post('/bulk-orders/request', payload)
  return response.data
}
