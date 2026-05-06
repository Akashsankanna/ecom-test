/**
 * paymentService.js
 *
 * Production-ready service for the admin payments module.
 * Matches backend routes exactly:
 *
 *  GET    /admin/payments/            → getAllPayments
 *  GET    /admin/payments/view        → getPaymentView
 *  GET    /admin/payments/summary     → getRevenueSummary
 *  GET    /admin/payments/{order_id}  → getPaymentsByOrder
 *  POST   /admin/payments/process     → processPayment
 *
 * Status enum (matches DB chk_transaction_status constraint exactly):
 *   PENDING | SUCCESS | FAILED | REFUNDED
 *
 * Payment method enum (matches backend PaymentMethod schema exactly):
 *   UPI | CARD | NET_BANKING | NEFT | RTGS | COD | BANK_TRANSFER | RAZORPAY
 *
 * Valid transitions (enforced on both FE & BE via sp_process_payment):
 *   PENDING  → SUCCESS, FAILED
 *   SUCCESS  → (terminal — order marked PAID)
 *   FAILED   → (terminal — retry via new process_payment call)
 *   REFUNDED → (terminal)
 *
 * DB → ORM → API → Service alignment:
 *   transactions.id                     → id
 *   transactions.order_id               → order_id
 *   transactions.amount                 → amount
 *   transactions.payment_method         → payment_method
 *   transactions.status                 → status
 *   transactions.transaction_ref        → transaction_ref
 *   transactions.payment_gateway        → payment_gateway
 *   transactions.gateway_transaction_id → gateway_transaction_id
 *   transactions.currency               → currency
 *   transactions.created_at             → created_at
 *
 * payment_view (DB view) columns:
 *   transaction_id, order_id, amount, payment_method, status,
 *   user_id, total_amount, order_status
 */

import axios from 'axios'

// ── Base URL from env ────────────────────────────────────────────────────────
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const PAYMENT_PREFIX = '/admin/payments'

// ── Axios instance ───────────────────────────────────────────────────────────
const http = axios.create({
  baseURL: BASE_URL,
  timeout: 15_000,
})

// ── Auth token helper ────────────────────────────────────────────────────────
function getToken () {
  return (
    localStorage.getItem('admin_token') ||
    localStorage.getItem('token')       ||
    localStorage.getItem('access_token')||
    localStorage.getItem('auth_token')  ||
    ''
  )
}

// ── Request interceptor: inject auth header ──────────────────────────────────
http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['Content-Type'] = 'application/json'
  return config
})

// ── Response interceptor: normalise errors ───────────────────────────────────
http.interceptors.response.use(
  (res) => res,
  (error) => {
    const message =
      error?.response?.data?.detail  ||
      error?.response?.data?.message ||
      error?.message                 ||
      'Unexpected error'

    return Promise.reject({
      status:  error?.response?.status || 0,
      message,
      raw:     error?.response?.data,
    })
  }
)

// ── Generic request helper ───────────────────────────────────────────────────
async function request (method, url, payload = null, params = null) {
  const config = { method, url }
  if (payload) config.data   = payload
  if (params)  config.params = params
  const res = await http(config)
  return res.data
}


// ════════════════════════════════════════════════════════════════════════════
// CONSTANTS — export for use in Vue components
// ════════════════════════════════════════════════════════════════════════════

/**
 * All possible transaction statuses.
 * Source: transactions table CHECK constraint → chk_transaction_status.
 */
export const PAYMENT_STATUSES = [
  'PENDING',
  'SUCCESS',
  'FAILED',
  'REFUNDED',
]

/**
 * All possible payment methods.
 * Source: payment_schema.py → PaymentMethod enum.
 */
export const PAYMENT_METHODS = [
  'UPI',
  'CARD',
  'NET_BANKING',
  'NEFT',
  'RTGS',
  'COD',
  'BANK_TRANSFER',
  'RAZORPAY',
]

/**
 * Valid next statuses for each current status.
 * Governed by sp_process_payment stored procedure logic.
 * Empty array = terminal state (no further admin transitions allowed).
 *
 *   PENDING  → sp_process_payment sets SUCCESS or FAILED
 *   SUCCESS  → order.status set to PAID; terminal for payment record
 *   FAILED   → terminal (retry requires a new sp_process_payment call)
 *   REFUNDED → terminal
 */
export const VALID_TRANSITIONS = {
  PENDING:  ['SUCCESS', 'FAILED'],
  SUCCESS:  [],
  FAILED:   [],
  REFUNDED: [],
}

/**
 * UI-friendly display labels for each status.
 */
export const STATUS_LABELS = {
  PENDING:  'Pending',
  SUCCESS:  'Success',
  FAILED:   'Failed',
  REFUNDED: 'Refunded',
}

/**
 * Quasar colour token for each status badge.
 */
export const STATUS_COLORS = {
  PENDING:  'warning',
  SUCCESS:  'positive',
  FAILED:   'negative',
  REFUNDED: 'info',
}

/**
 * Material icon for each status.
 */
export const STATUS_ICONS = {
  PENDING:  'schedule',
  SUCCESS:  'check_circle',
  FAILED:   'error',
  REFUNDED: 'replay',
}

/**
 * Material icon for each payment method.
 */
export const METHOD_ICONS = {
  UPI:          'qr_code',
  CARD:         'credit_card',
  NET_BANKING:  'account_balance',
  NEFT:         'account_balance',
  RTGS:         'account_balance',
  COD:          'payments',
  BANK_TRANSFER:'sync_alt',
  RAZORPAY:     'payment',
}

/**
 * UI-friendly display labels for each payment method.
 */
export const METHOD_LABELS = {
  UPI:          'UPI',
  CARD:         'Card',
  NET_BANKING:  'Net Banking',
  NEFT:         'NEFT',
  RTGS:         'RTGS',
  COD:          'Cash on Delivery',
  BANK_TRANSFER:'Bank Transfer',
  RAZORPAY:     'Razorpay',
}


// ════════════════════════════════════════════════════════════════════════════
// API METHODS — matching router.py routes exactly
// ════════════════════════════════════════════════════════════════════════════

/**
 * GET /admin/payments/
 * Returns List of TransactionOut (direct from transactions table via ORM).
 *
 * Response shape per transaction (TransactionOut):
 *   { id, order_id, amount, payment_method, status, transaction_ref,
 *     payment_gateway, gateway_transaction_id, currency, created_at }
 *
 * @param {Object} filters
 * @param {string}  [filters.status]          - PENDING | SUCCESS | FAILED | REFUNDED
 * @param {string}  [filters.payment_method]  - UPI | CARD | NET_BANKING | etc.
 * @param {number}  [filters.limit=100]       - max 500, min 1
 */
const getAllPayments = (filters = {}) => {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== null && v !== undefined && v !== '')
  )
  return request('get', `${PAYMENT_PREFIX}/`, null, params)
}

/**
 * GET /admin/payments/view
 * Returns rows from the payment_view DB view (transactions JOIN orders).
 *
 * Response shape per row (PaymentViewOut):
 *   { transaction_id, order_id, amount, payment_method, status,
 *     user_id, total_amount, order_status }
 *
 * @param {number|null} [orderId] - optional query param: ?order_id=<id>
 */
const getPaymentView = (orderId = null) => {
  const params = orderId ? { order_id: orderId } : {}
  return request('get', `${PAYMENT_PREFIX}/view`, null, params)
}

/**
 * GET /admin/payments/summary
 * Returns revenue aggregate from raw SQL over transactions table.
 *
 * Response shape (RevenueSummaryOut):
 *   { total_transactions, total_amount, successful_amount, refunded_amount }
 */
const getRevenueSummary = () =>
  request('get', `${PAYMENT_PREFIX}/summary`)

/**
 * GET /admin/payments/{order_id}
 * Returns all transactions linked to a specific order (List[TransactionOut]).
 * Raises 404 if no transactions found for that order.
 *
 * Response shape per transaction (TransactionOut):
 *   { id, order_id, amount, payment_method, status, transaction_ref,
 *     payment_gateway, gateway_transaction_id, currency, created_at }
 *
 * @param {number} orderId
 */
const getPaymentsByOrder = (orderId) =>
  request('get', `${PAYMENT_PREFIX}/${orderId}`)

/**
 * POST /admin/payments/process
 * Invokes sp_process_payment stored procedure.
 *
 * SP side effects:
 *   - Inserts into transactions table
 *   - Updates orders.payment_status to the provided status
 *   - If SUCCESS → sets order.status = 'PAID'
 *   - If FAILED  → sets order.status = 'PAYMENT_FAILED'
 *   - fn_after_payment_success trigger fires → sp_reduce_stock on SUCCESS
 *
 * Request body (ProcessPaymentRequest):
 *   { order_id: int, payment_method: string, status: string, transaction_ref: string }
 *
 * Response:
 *   { message, transaction_id, order_id, amount, payment_method,
 *     status, transaction_ref }
 *
 * @param {Object} payload
 * @param {number}  payload.order_id
 * @param {string}  payload.payment_method  - must be a PaymentMethod enum value
 * @param {string}  payload.status          - must be a TransactionStatus enum value
 * @param {string}  payload.transaction_ref
 */
const processPayment = (payload) =>
  request('post', `${PAYMENT_PREFIX}/process`, payload)


// ════════════════════════════════════════════════════════════════════════════
// HELPERS
// ════════════════════════════════════════════════════════════════════════════

/**
 * Returns the list of valid next statuses for a given current status.
 * Used to populate (and restrict) the status update dropdown in the UI.
 *
 * @param {string} currentStatus
 * @returns {string[]}
 */
const getValidNextStatuses = (currentStatus) =>
  VALID_TRANSITIONS[currentStatus] ?? []

/**
 * Returns true if the status is terminal (no further transitions allowed).
 * Used to disable the process/update action button entirely.
 *
 * @param {string} currentStatus
 * @returns {boolean}
 */
const isTerminalStatus = (currentStatus) =>
  (VALID_TRANSITIONS[currentStatus] ?? []).length === 0

/**
 * Returns the Quasar color token for a given status.
 *
 * @param {string} status
 * @returns {string}
 */
const getStatusColor = (status) =>
  STATUS_COLORS[status] ?? 'grey'

/**
 * Returns the Material icon name for a given status.
 *
 * @param {string} status
 * @returns {string}
 */
const getStatusIcon = (status) =>
  STATUS_ICONS[status] ?? 'help'

/**
 * Returns the Material icon name for a given payment method.
 *
 * @param {string} method
 * @returns {string}
 */
const getMethodIcon = (method) =>
  METHOD_ICONS[method] ?? 'payment'

/**
 * Formats a numeric amount as Indian Rupees with 2 decimal places.
 *
 * @param {number|string} amount
 * @returns {string}  e.g. "₹4,995.00"
 */
const formatAmount = (amount) =>
  '₹' + Number(amount || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })


// ── Default export ───────────────────────────────────────────────────────────
export default {
  // API methods
  getAllPayments,
  getPaymentView,
  getRevenueSummary,
  getPaymentsByOrder,
  processPayment,

  // Helpers
  getValidNextStatuses,
  isTerminalStatus,
  getStatusColor,
  getStatusIcon,
  getMethodIcon,
  formatAmount,

  // Constants (also available as named exports above)
  PAYMENT_STATUSES,
  PAYMENT_METHODS,
  VALID_TRANSITIONS,
  STATUS_LABELS,
  STATUS_COLORS,
  STATUS_ICONS,
  METHOD_ICONS,
  METHOD_LABELS,
}