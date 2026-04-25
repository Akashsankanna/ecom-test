/**
 * inventoryService.js
 * ───────────────────────────────────────────────────────────────
 * Centralised API layer for the Inventory Admin Module.
 *
 * Usage:
 *   import inventoryService from '@/services/inventoryService'
 *   const variants = await inventoryService.getVariants({ search: 'apron' })
 *
 * All functions throw on non-2xx responses with a human-readable message.
 * ───────────────────────────────────────────────────────────────
 */

const BASE = '/admin/inventory'

// ─── Core fetch wrapper ────────────────────────────────────────────────────────

/**
 * @param {string} path   — relative to BASE, e.g. '/low-stock'
 * @param {RequestInit} opts
 * @returns {Promise<any>}
 */
async function request(path, opts = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      // Add auth header here if needed, e.g.:
      // 'Authorization': `Bearer ${useAuthStore().token}`,
      ...opts.headers,
    },
    ...opts,
  })

  if (!response.ok) {
    let message = `HTTP ${response.status}`
    try {
      const body = await response.json()
      // FastAPI validation errors
      if (Array.isArray(body?.detail)) {
        message = body.detail.map((e) => e.msg).join(', ')
      } else if (typeof body?.detail === 'string') {
        message = body.detail
      }
    } catch {
      // non-JSON error body — keep the status message
    }
    throw new Error(message)
  }

  // 204 No Content
  if (response.status === 204) return null

  return response.json()
}

// ─── GET endpoints ─────────────────────────────────────────────────────────────

/**
 * GET /admin/inventory/
 * Returns all inventory variants with optional search and low_stock_only filter.
 *
 * @param {{ search?: string, low_stock_only?: boolean }} params
 */
export function getVariants(params = {}) {
  const qs = new URLSearchParams()
  if (params.search)         qs.append('search', params.search)
  if (params.low_stock_only) qs.append('low_stock_only', 'true')
  const query = qs.toString() ? `?${qs.toString()}` : ''
  return request(`/${query}`)
}

/**
 * GET /admin/inventory/low-stock
 * Returns all variants at or below their low_stock_threshold.
 */
export function getLowStockVariants() {
  return request('/low-stock')
}

/**
 * GET /admin/inventory/full-view
 * Returns inventory joined with product, category, color, and image info.
 */
export function getFullInventoryView() {
  return request('/full-view')
}

/**
 * GET /admin/inventory/{variant_id}
 * Returns a single variant's inventory detail.
 *
 * @param {number} variantId
 */
export function getVariant(variantId) {
  return request(`/${variantId}`)
}

/**
 * GET /admin/inventory/logs/all
 * Returns all inventory change logs.
 *
 * @param {{ variant_id?: number, change_type?: string, limit?: number }} params
 */
export function getAllLogs(params = {}) {
  const qs = new URLSearchParams()
  if (params.variant_id)  qs.append('variant_id', params.variant_id)
  if (params.change_type) qs.append('change_type', params.change_type)
  qs.append('limit', params.limit ?? 100)
  return request(`/logs/all?${qs.toString()}`)
}

/**
 * GET /admin/inventory/logs/{variant_id}
 * Returns logs for a specific variant.
 *
 * @param {number} variantId
 */
export function getVariantLogs(variantId) {
  return request(`/logs/${variantId}`)
}

// ─── POST endpoints ─────────────────────────────────────────────────────────────

/**
 * POST /admin/inventory/add-stock
 * Increases stock for a variant.
 *
 * @param {{ variant_id: number, quantity: number, change_type: string, reference_id?: number, notes?: string }} payload
 *
 * Allowed change_type values for adding: RESTOCK, ADJUSTMENT, RETURN
 */
export function addStock(payload) {
  _validateStockPayload(payload)
  return request('/add-stock', {
    method: 'POST',
    body: JSON.stringify(_sanitisePayload(payload)),
  })
}

/**
 * POST /admin/inventory/remove-stock
 * Decreases stock for a variant.
 *
 * @param {{ variant_id: number, quantity: number, change_type: string, reference_id?: number, notes?: string }} payload
 *
 * Allowed change_type values for removing: ORDER, ORDER_CANCELLED, EXCHANGE, ADJUSTMENT
 */
export function removeStock(payload) {
  _validateStockPayload(payload)
  return request('/remove-stock', {
    method: 'POST',
    body: JSON.stringify(_sanitisePayload(payload)),
  })
}

/**
 * POST /admin/inventory/reserve-stock
 * Moves units into reserved_stock, reducing available count.
 *
 * @param {{ variant_id: number, quantity: number, change_type: string, reference_id?: number, notes?: string }} payload
 */
export function reserveStock(payload) {
  _validateStockPayload(payload)
  return request('/reserve-stock', {
    method: 'POST',
    body: JSON.stringify(_sanitisePayload(payload)),
  })
}

/**
 * POST /admin/inventory/release-stock
 * Releases previously reserved units back to available stock.
 *
 * @param {{ variant_id: number, quantity: number, change_type: string, reference_id?: number, notes?: string }} payload
 */
export function releaseStock(payload) {
  _validateStockPayload(payload)
  return request('/release-stock', {
    method: 'POST',
    body: JSON.stringify(_sanitisePayload(payload)),
  })
}

// ─── PUT endpoints ─────────────────────────────────────────────────────────────

/**
 * PUT /admin/inventory/{variant_id}
 * Updates stock count and / or low_stock_threshold for a variant.
 *
 * @param {number} variantId
 * @param {{ stock?: number, low_stock_threshold?: number }} payload
 */
export function updateVariantSettings(variantId, payload) {
  if (!variantId) throw new Error('variant_id is required')
  const clean = {}
  if (payload.stock !== undefined && payload.stock !== null)
    clean.stock = Number(payload.stock)
  if (payload.low_stock_threshold !== undefined && payload.low_stock_threshold !== null)
    clean.low_stock_threshold = Number(payload.low_stock_threshold)
  if (!Object.keys(clean).length) throw new Error('No settings to update')
  return request(`/${variantId}`, {
    method: 'PUT',
    body: JSON.stringify(clean),
  })
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

/** Valid change_type values as defined in the DB constraint */
export const CHANGE_TYPES = ['ORDER', 'ORDER_CANCELLED', 'RETURN', 'RESTOCK', 'EXCHANGE', 'ADJUSTMENT']

/** Change types that reduce stock (used for UI sign rendering) */
export const DEDUCTION_TYPES = new Set(['ORDER', 'ORDER_CANCELLED', 'EXCHANGE', 'ADJUSTMENT'])

/** Returns true if the given change_type is a deduction (stock goes down) */
export function isDeduction(changeType) {
  return DEDUCTION_TYPES.has(changeType)
}

function _validateStockPayload(payload) {
  if (!payload.variant_id) throw new Error('variant_id is required')
  if (!payload.quantity || payload.quantity < 1) throw new Error('quantity must be ≥ 1')
  if (!payload.change_type) throw new Error('change_type is required')
  if (!CHANGE_TYPES.includes(payload.change_type)) {
    throw new Error(`Invalid change_type "${payload.change_type}". Allowed: ${CHANGE_TYPES.join(', ')}`)
  }
}

function _sanitisePayload(payload) {
  return {
    variant_id:   Number(payload.variant_id),
    quantity:     Number(payload.quantity),
    change_type:  payload.change_type,
    reference_id: payload.reference_id ? Number(payload.reference_id) : null,
    notes:        payload.notes?.trim() || null,
  }
}

// ─── Default export (object form for easy mocking in tests) ────────────────────
export default {
  getVariants,
  getLowStockVariants,
  getFullInventoryView,
  getVariant,
  getAllLogs,
  getVariantLogs,
  addStock,
  removeStock,
  reserveStock,
  releaseStock,
  updateVariantSettings,
  CHANGE_TYPES,
  DEDUCTION_TYPES,
  isDeduction,
}