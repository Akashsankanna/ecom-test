import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const ADMIN_PREFIX = '/admin/orders'
const USER_PREFIX  = '/orders'

const http = axios.create({
  baseURL: BASE_URL,
  timeout: 15000
})

function getToken() {
  return (
    localStorage.getItem('admin_token') ||
    localStorage.getItem('token') ||
    localStorage.getItem('access_token') ||
    localStorage.getItem('auth_token') ||
    ''
  )
}

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  config.headers['Content-Type'] = 'application/json'
  return config
})

http.interceptors.response.use(
  (res) => res,
  (error) => {
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      'Unexpected error'

    return Promise.reject({
      status:  error?.response?.status || 0,
      message
    })
  }
)

async function request(method, url, payload = null, params = null) {
  const config = { method, url }
  if (payload) config.data   = payload
  if (params)  config.params = params
  const res = await http(config)
  return res.data
}

// ════════════════════════════════════════════════════════════
// ADMIN — ORDERS
// ════════════════════════════════════════════════════════════

/**
 * GET /admin/orders/
 * filters: { status, payment_status, user_id }
 */
const getAllOrders = (filters = {}) =>
  request('get', `${ADMIN_PREFIX}/`, null, filters)

const listOrders = getAllOrders

/**
 * GET /admin/orders/{order_id}
 * Returns: { order, items, shipment, status_history, transaction }
 */
const getOrderDetail = (orderId) =>
  request('get', `${ADMIN_PREFIX}/${orderId}`)

/**
 * GET /admin/orders/{order_id}/history
 */
const getOrderHistory = (orderId) =>
  request('get', `${ADMIN_PREFIX}/${orderId}/history`)

/**
 * PUT /admin/orders/{order_id}/status
 * payload: { status: 'PENDING' | 'PAID' | 'CONFIRMED' | 'PROCESSING' |
 *                    'SHIPPED' | 'DELIVERED' | 'CANCELLED' | 'PAYMENT_FAILED' }
 */
const updateOrderStatus = (orderId, status) =>
  request('put', `${ADMIN_PREFIX}/${orderId}/status`, { status })

/**
 * POST /admin/orders/{order_id}/cancel
 */
const cancelOrder = (orderId) =>
  request('post', `${ADMIN_PREFIX}/${orderId}/cancel`)

// ════════════════════════════════════════════════════════════
// ADMIN — SHIPMENT
// ════════════════════════════════════════════════════════════

/**
 * POST /admin/orders/{order_id}/shipment
 * payload: { courier_name, tracking_number, estimated_delivery?, tracking_url? }
 */
const createShipment = (orderId, payload) =>
  request('post', `${ADMIN_PREFIX}/${orderId}/shipment`, payload)

/**
 * GET /admin/orders/{order_id}/shipment
 */
const getShipment = (orderId) =>
  request('get', `${ADMIN_PREFIX}/${orderId}/shipment`)

/**
 * PUT /admin/orders/shipments/{tracking_number}/status
 * payload: { status: 'PENDING' | 'SHIPPED' | 'OUT_FOR_DELIVERY' |
 *                    'DELIVERED' | 'FAILED' | 'RETURNED' }
 */
const updateShipmentStatus = (trackingNumber, status) =>
  request(
    'put',
    `${ADMIN_PREFIX}/shipments/${trackingNumber}/status`,
    { status }
  )

// ════════════════════════════════════════════════════════════
// ADMIN — RETURN REQUESTS
// ════════════════════════════════════════════════════════════

/**
 * GET /admin/orders/returns
 * filters: { status }
 */
const getAllReturns = (filters = {}) =>
  request('get', `${ADMIN_PREFIX}/returns`, null, filters)

const listReturns = getAllReturns

/**
 * GET /admin/orders/returns/{return_id}
 */
const getReturn = (returnId) =>
  request('get', `${ADMIN_PREFIX}/returns/${returnId}`)

/**
 * POST /admin/orders/returns/{return_id}/approve
 * payload: { refund_method: 'ORIGINAL_PAYMENT' | 'STORE_CREDIT' | 'BANK_TRANSFER' }
 */
const approveReturn = (returnId, refundMethod) =>
  request(
    'post',
    `${ADMIN_PREFIX}/returns/${returnId}/approve`,
    { refund_method: refundMethod }
  )

/**
 * POST /admin/orders/returns/{return_id}/reject
 */
const rejectReturn = (returnId) =>
  request('post', `${ADMIN_PREFIX}/returns/${returnId}/reject`)

/**
 * POST /admin/orders/returns/{return_id}/complete-refund
 */
const completeRefund = (returnId) =>
  request('post', `${ADMIN_PREFIX}/returns/${returnId}/complete-refund`)

// ════════════════════════════════════════════════════════════
// ADMIN — EXCHANGE REQUESTS
// ════════════════════════════════════════════════════════════

/**
 * GET /admin/orders/exchanges
 * filters: { status }
 */
const getAllExchanges = (filters = {}) =>
  request('get', `${ADMIN_PREFIX}/exchanges`, null, filters)

const listExchanges = getAllExchanges

/**
 * POST /admin/orders/exchanges
 * payload: { order_id, order_item_id, reason }
 */
const createExchange = (payload) =>
  request('post', `${ADMIN_PREFIX}/exchanges`, payload)

/**
 * GET /admin/orders/exchanges/{exchange_id}
 */
const getExchange = (exchangeId) =>
  request('get', `${ADMIN_PREFIX}/exchanges/${exchangeId}`)

/**
 * PUT /admin/orders/exchanges/{exchange_id}/status
 * payload: { status: 'REQUESTED' | 'APPROVED' | 'REJECTED' | 'COMPLETED' }
 */
const updateExchangeStatus = (exchangeId, status) =>
  request(
    'put',
    `${ADMIN_PREFIX}/exchanges/${exchangeId}/status`,
    { status }
  )

/**
 * POST /admin/orders/exchanges/{exchange_id}/complete
 * payload: { new_variant_id }
 */
const completeExchange = (exchangeId, newVariantId) =>
  request(
    'post',
    `${ADMIN_PREFIX}/exchanges/${exchangeId}/complete`,
    { new_variant_id: newVariantId }
  )

// ════════════════════════════════════════════════════════════
// ADMIN — DISCOUNTS / COUPONS
// ════════════════════════════════════════════════════════════

/**
 * POST /admin/orders/{order_id}/apply-discount
 * payload: { order_id, discount_amount, reason? }
 */
const applyDiscount = (orderId, discountAmount, reason = 'Manual discount') =>
  request(
    'post',
    `${ADMIN_PREFIX}/${orderId}/apply-discount`,
    { order_id: orderId, discount_amount: discountAmount, reason }
  )

/**
 * POST /admin/orders/apply-coupon
 * payload: { order_id, coupon_code, user_id, order_amount, additional_discount? }
 */
const applyCoupon = (payload) =>
  request('post', `${ADMIN_PREFIX}/apply-coupon`, payload)

// ════════════════════════════════════════════════════════════
// ADMIN — ANALYTICS
// ════════════════════════════════════════════════════════════

/**
 * GET /admin/orders/analytics/top-selling
 */
const getTopSelling = () =>
  request('get', `${ADMIN_PREFIX}/analytics/top-selling`)

const topSelling = getTopSelling

/**
 * GET /admin/orders/analytics/returns
 */
const getReturnsAnalytics = () =>
  request('get', `${ADMIN_PREFIX}/analytics/returns`)

const returnsAnalytics = getReturnsAnalytics

/**
 * GET /admin/orders/analytics/exchanges
 */
const getExchangesAnalytics = () =>
  request('get', `${ADMIN_PREFIX}/analytics/exchanges`)

const exchangesAnalytics = getExchangesAnalytics

// ════════════════════════════════════════════════════════════
// USER — ORDERS
// ════════════════════════════════════════════════════════════

/**
 * GET /orders/?user_id={userId}
 * Returns: { success, orders: [...] }
 * Each order has: id, status, payment_status, total_amount,
 * final_amount, gross_amount, items[], shipment
 */
const fetchOrdersByUser = (userId) =>
  request('get', `${USER_PREFIX}/`, null, { user_id: userId })

/**
 * GET /orders/{order_id}
 * Returns: { order, items, shipment, status_history, transaction }
 */
const fetchOrderDetail = (orderId) =>
  request('get', `${USER_PREFIX}/${orderId}`)

/**
 * GET /orders/{order_id}/track
 * Returns: { order_id, status, shipment, status_history }
 */
const trackOrder = (orderId) =>
  request('get', `${USER_PREFIX}/${orderId}/track`)

/**
 * POST /orders/{order_id}/return?user_id={userId}
 * payload: { order_id, order_item_id, quantity, reason }
 */
const submitReturnRequest = (orderId, userId, payload) =>
  request(
    'post',
    `${USER_PREFIX}/${orderId}/return`,
    payload,
    { user_id: userId }
  )

// ════════════════════════════════════════════════════════════
// CONSTANTS (shared between admin UI and user UI)
// ════════════════════════════════════════════════════════════

const ORDER_STATUSES = [
  'PENDING',
  'PAID',
  'CONFIRMED',
  'PROCESSING',
  'SHIPPED',
  'DELIVERED',
  'CANCELLED',
  'PAYMENT_FAILED'
]

const PAYMENT_STATUSES = ['PENDING', 'SUCCESS', 'FAILED', 'REFUNDED']

const SHIPMENT_STATUSES = [
  'PENDING',
  'SHIPPED',
  'OUT_FOR_DELIVERY',
  'DELIVERED',
  'FAILED',
  'RETURNED'
]

const REFUND_METHODS = [
  'ORIGINAL_PAYMENT',
  'STORE_CREDIT',
  'BANK_TRANSFER'
]

const EXCHANGE_STATUSES = [
  'REQUESTED',
  'APPROVED',
  'REJECTED',
  'COMPLETED'
]

const RETURN_STATUSES = [
  'REQUESTED',
  'APPROVED',
  'REJECTED',
  'REFUNDED',
  'COMPLETED'
]

export default {
  // ── Admin: Orders ──────────────────────────────
  getAllOrders,
  listOrders,
  getOrderDetail,
  getOrderHistory,
  updateOrderStatus,
  cancelOrder,

  // ── Admin: Shipment ────────────────────────────
  createShipment,
  getShipment,
  updateShipmentStatus,

  // ── Admin: Returns ─────────────────────────────
  getAllReturns,
  listReturns,
  getReturn,
  approveReturn,
  rejectReturn,
  completeRefund,

  // ── Admin: Exchanges ───────────────────────────
  getAllExchanges,
  listExchanges,
  createExchange,
  getExchange,
  updateExchangeStatus,
  completeExchange,

  // ── Admin: Discounts ───────────────────────────
  applyDiscount,
  applyCoupon,

  // ── Admin: Analytics ───────────────────────────
  getTopSelling,
  topSelling,
  getReturnsAnalytics,
  returnsAnalytics,
  getExchangesAnalytics,
  exchangesAnalytics,

  // ── User: Orders ───────────────────────────────
  fetchOrdersByUser,
  fetchOrderDetail,
  trackOrder,
  submitReturnRequest,

  // ── Constants ──────────────────────────────────
  ORDER_STATUSES,
  PAYMENT_STATUSES,
  SHIPMENT_STATUSES,
  REFUND_METHODS,
  EXCHANGE_STATUSES,
  RETURN_STATUSES
}