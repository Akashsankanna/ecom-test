/**
 * shipmentService.js
 *
 * KEY FIX: updateShipmentStatus() now returns { shipment, syncedOrderStatus }
 * so AdminOrders.vue can update its order list + detail panel in one shot
 * without an extra round-trip.
 *
 * Routes:
 *   GET  /admin/shipments/              → getAllShipments
 *   GET  /admin/shipments/stats         → getShipmentStats
 *   GET  /admin/shipments/{id}          → getShipmentById
 *   PUT  /admin/shipments/{tracking}    → updateShipmentStatus  ← FIXED
 *   POST /admin/orders/{id}/shipment    → createShipment
 *   GET  /admin/orders/{id}/shipment    → getShipmentByOrder
 */

import axios from 'axios'

const BASE_URL        = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const SHIPMENT_PREFIX = '/admin/shipments'
const ORDERS_PREFIX   = '/admin/orders'

const http = axios.create({ baseURL: BASE_URL, timeout: 15_000 })

function getToken () {
  return (
    localStorage.getItem('admin_token')  ||
    localStorage.getItem('token')        ||
    localStorage.getItem('access_token') ||
    localStorage.getItem('auth_token')   ||
    ''
  )
}

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['Content-Type'] = 'application/json'
  return config
})

http.interceptors.response.use(
  (res) => res,
  (error) => {
    const message =
      error?.response?.data?.detail  ||
      error?.response?.data?.message ||
      error?.message                 ||
      'Unexpected error'
    return Promise.reject({ status: error?.response?.status || 0, message, raw: error?.response?.data })
  }
)

async function request (method, url, payload = null, params = null) {
  const config = { method, url }
  if (payload) config.data   = payload
  if (params)  config.params = params
  const res = await http(config)
  return res.data
}

// ════════════════════════════════════════════════════════════
// CONSTANTS
// ════════════════════════════════════════════════════════════

export const SHIPMENT_STATUSES = [
  'PENDING',
  'SHIPPED',
  'OUT_FOR_DELIVERY',
  'DELIVERED',
  'FAILED',
  'RETURNED',
]

/** Valid next statuses per current status */
export const VALID_TRANSITIONS = {
  PENDING:          ['SHIPPED', 'FAILED'],
  SHIPPED:          ['OUT_FOR_DELIVERY', 'FAILED', 'RETURNED'],
  OUT_FOR_DELIVERY: ['DELIVERED', 'FAILED', 'RETURNED'],
  DELIVERED:        [],
  FAILED:           ['SHIPPED'],
  RETURNED:         [],
}

/** Shipment → Order status mapping (mirrors backend) */
export const SHIPMENT_TO_ORDER_STATUS = {
  PENDING:          'CONFIRMED',
  SHIPPED:          'SHIPPED',
  OUT_FOR_DELIVERY: 'SHIPPED',
  DELIVERED:        'DELIVERED',
  FAILED:           'CONFIRMED',
  RETURNED:         'RETURNED',
}

export const STATUS_LABELS = {
  PENDING:          'Pending',
  SHIPPED:          'Shipped',
  OUT_FOR_DELIVERY: 'Out for Delivery',
  DELIVERED:        'Delivered',
  FAILED:           'Failed',
  RETURNED:         'Returned',
}

export const STATUS_COLORS = {
  PENDING:          'warning',
  SHIPPED:          'info',
  OUT_FOR_DELIVERY: 'purple',
  DELIVERED:        'positive',
  FAILED:           'negative',
  RETURNED:         'orange',
}

export const STATUS_ICONS = {
  PENDING:          'schedule',
  SHIPPED:          'local_shipping',
  OUT_FOR_DELIVERY: 'two_wheeler',
  DELIVERED:        'check_circle',
  FAILED:           'error',
  RETURNED:         'assignment_return',
}

export const COURIER_OPTIONS = [
  'DTDC', 'BlueDart', 'Delhivery', 'Ekart',
  'Amazon Logistics', 'FedEx', 'DHL',
  'Shiprocket', 'Xpressbees', 'Shadowfax',
]

// ════════════════════════════════════════════════════════════
// API METHODS
// ════════════════════════════════════════════════════════════

/**
 * GET /admin/shipments/
 */
const getAllShipments = (filters = {}) =>
  request('get', `${SHIPMENT_PREFIX}/`, null, filters)

/**
 * GET /admin/shipments/stats
 * Returns { total, pending, shipped, out_for_delivery, delivered, failed, returned }
 */
const getShipmentStats = () =>
  request('get', `${SHIPMENT_PREFIX}/stats`)

/**
 * GET /admin/shipments/{shipment_id}
 */
const getShipmentById = (shipmentId) =>
  request('get', `${SHIPMENT_PREFIX}/${shipmentId}`)

/**
 * PUT /admin/shipments/{tracking_number}
 *
 * KEY FIX: Response now includes `synced_order_status`.
 * Returns: {
 *   ...shipmentFields,
 *   synced_order_status: 'SHIPPED' | 'DELIVERED' | 'CONFIRMED' | 'RETURNED'
 * }
 *
 * Usage in component:
 *   const result = await shipmentService.updateShipmentStatus(tracking, newStatus)
 *   // result.synced_order_status → use this to update order in UI immediately
 */
const updateShipmentStatus = (trackingNumber, newStatus) =>
  request('put', `${SHIPMENT_PREFIX}/${trackingNumber}`, { status: newStatus })

/**
 * POST /admin/orders/{order_id}/shipment
 */
const createShipment = (orderId, payload) =>
  request('post', `${ORDERS_PREFIX}/${orderId}/shipment`, payload)

/**
 * GET /admin/orders/{order_id}/shipment
 * Returns shipment + order_status + user_id
 */
const getShipmentByOrder = (orderId) =>
  request('get', `${ORDERS_PREFIX}/${orderId}/shipment`)

// ════════════════════════════════════════════════════════════
// HELPERS
// ════════════════════════════════════════════════════════════

/**
 * Returns valid next statuses for a given current status.
 * Use to populate the update dropdown (disables invalid options).
 */
const getValidNextStatuses = (currentStatus) =>
  VALID_TRANSITIONS[currentStatus] ?? []

/** Returns true if no further transitions are allowed */
const isTerminalStatus = (currentStatus) =>
  (VALID_TRANSITIONS[currentStatus] ?? []).length === 0

/**
 * Returns the expected order status after a shipment status change.
 * Useful for optimistic UI updates before the API responds.
 */
const getExpectedOrderStatus = (shipmentStatus) =>
  SHIPMENT_TO_ORDER_STATUS[shipmentStatus] ?? null

export default {
  getAllShipments,
  getShipmentStats,
  getShipmentById,
  updateShipmentStatus,
  createShipment,
  getShipmentByOrder,

  getValidNextStatuses,
  isTerminalStatus,
  getExpectedOrderStatus,

  SHIPMENT_STATUSES,
  VALID_TRANSITIONS,
  SHIPMENT_TO_ORDER_STATUS,
  STATUS_LABELS,
  STATUS_COLORS,
  STATUS_ICONS,
  COURIER_OPTIONS,
}