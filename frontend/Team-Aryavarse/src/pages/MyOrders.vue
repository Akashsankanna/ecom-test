<template>
  <div class="orders-page">

    <!-- Page Header -->
    <div class="orders-header">
      <div class="header-left">
        <div class="header-icon">
          <q-icon name="receipt_long" size="22px" />
        </div>
        <div>
          <h1 class="page-title">My Orders</h1>
          <p class="page-sub">{{ orders.length }} order{{ orders.length !== 1 ? 's' : '' }} placed</p>
        </div>
      </div>

      <div v-if="orders.length > 0" class="header-right">
        <div class="filter-tabs">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            class="filter-tab"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="orders-list">
      <div v-for="n in 3" :key="n" class="order-card skeleton-card">
        <q-skeleton type="rect" height="80px" />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredOrders.length === 0" class="empty-state">
      <div class="empty-icon">
        <q-icon name="shopping_bag" size="52px" />
      </div>
      <p class="empty-title">No orders found</p>
      <p class="empty-sub">
        {{ activeTab === 'all' ? "You haven't placed any orders yet." : 'No orders with this status.' }}
      </p>
      <button class="btn-shop" @click="$router.push('/')">
        <q-icon name="storefront" size="16px" />
        Start Shopping
      </button>
    </div>

    <!-- Orders List -->
    <div v-else class="orders-list">
      <div
        v-for="(order, index) in filteredOrders"
        :key="order.id"
        class="order-card"
        :style="{ animationDelay: `${index * 0.07}s` }"
      >

        <!-- Card Header -->
        <div class="card-header">
          <div class="order-meta">
            <span class="order-id"># {{ order.id }}</span>
            <span class="order-dot" />
            <span class="order-date">
              <q-icon name="calendar_today" size="12px" />
              {{ formatDate(order.date) }}
            </span>
          </div>
          <div class="status-badge" :class="statusClass(order.rawStatus)">
            <span class="status-dot" />
            {{ statusLabel(order.rawStatus) }}
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <!-- Products -->
          <div class="products-list">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="product-row"
            >
              <div class="product-img-wrap">
                <img
                  :src="item.image"
                  :alt="item.name"
                  class="product-img"
                  @error="handleImgError"
                />
              </div>
              <div class="product-info">
                <p class="product-name">{{ item.name }}</p>
                <p class="product-meta">
                  <span>Qty: {{ item.qty }}</span>
                  <span v-if="item.size" class="meta-sep">·</span>
                  <span v-if="item.size">Size: {{ item.size }}</span>
                  <span v-if="item.color" class="meta-sep">·</span>
                  <span v-if="item.color">{{ item.color }}</span>
                </p>
              </div>
              <div class="product-price">₹{{ item.price.toLocaleString() }}</div>
            </div>
          </div>

          <!-- Divider + Total -->
          <div class="card-footer">
            <div class="total-row">
              <span class="total-label">Order Total</span>
              <span class="total-amount">₹{{ order.total.toLocaleString() }}</span>
            </div>

            <div class="action-btns">
              <button class="btn btn-outline" @click="viewOrder(order)">
                <q-icon name="visibility" size="15px" />
                View
              </button>

              <!-- Invoice Button -->
              <button class="btn btn-outline" @click="downloadInvoice(order)">
                <q-icon name="picture_as_pdf" size="15px" />
                Invoice
              </button>

              <button
                class="btn btn-outline"
                :disabled="!isTrackable(order.rawStatus)"
                @click="openTrack(order)"
              >
                <q-icon name="local_shipping" size="15px" />
                Track
              </button>

              <button class="btn btn-primary" @click="buyAgain(order)">
                <q-icon name="replay" size="15px" />
                Buy Again
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Track Order Modal -->
    <TrackOrderModal
      v-model="showTrackModal"
      :order="selectedOrder"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

import { fetchOrdersByUser } from 'src/service/orderService'
import { getUserId } from 'src/utils/CheckoutStorage'
import TrackOrderModal from 'src/components/Trackordermodal.vue'

const router = useRouter()

// ─── State ────────────────────────────────────────────────────────
const activeTab       = ref('all')
const orders          = ref([])
const loading         = ref(false)
const showTrackModal  = ref(false)
const selectedOrder   = ref(null)

// ─── Status config ────────────────────────────────────────────────
const STATUS_LABEL_MAP = {
  PENDING:        'Pending',
  PAID:           'Paid',
  CONFIRMED:      'Confirmed',
  PROCESSING:     'Processing',
  SHIPPED:        'Shipped',
  DELIVERED:      'Delivered',
  CANCELLED:      'Cancelled',
  PAYMENT_FAILED: 'Payment Failed',
}

const STATUS_TAB_MAP = {
  PENDING:        'Pending',
  PAID:           'Processing',
  CONFIRMED:      'Processing',
  PROCESSING:     'Processing',
  SHIPPED:        'Shipped',
  DELIVERED:      'Delivered',
  CANCELLED:      'Cancelled',
  PAYMENT_FAILED: 'Cancelled',
}

const TRACKABLE_STATUSES = new Set([
  'PENDING',
  'CONFIRMED',
  'PROCESSING',
  'SHIPPED',
  'DELIVERED'
])

const statusTabs = [
  { label: 'All',        value: 'all' },
  { label: 'Processing', value: 'Processing' },
  { label: 'Shipped',    value: 'Shipped' },
  { label: 'Delivered',  value: 'Delivered' },
  { label: 'Cancelled',  value: 'Cancelled' },
]

// ─── Load orders ──────────────────────────────────────────────────
onMounted(loadOrders)

async function loadOrders() {
  try {
    const userId = Number(getUserId())

    if (!userId) {
      router.push('/login')
      return
    }

    loading.value = true

    const res = await fetchOrdersByUser(userId)

    const rawOrders = Array.isArray(res)
      ? res
      : (res?.orders || res?.data || res?.items || [])

    orders.value = rawOrders.map(order => {
      const rawStatus = (order.status || 'PENDING').toUpperCase()

      return {
        id: order.id,
        date: order.created_at || order.date,
        rawStatus,
        tabStatus: STATUS_TAB_MAP[rawStatus] || 'Processing',
        total: Number(
          order.final_amount ||
          order.total_amount ||
          order.gross_amount ||
          0
        ),
        items: (order.items || order.order_items || []).map(item => ({
          id: item.id,
          variant_id: item.variant_id || null,
          name: item.product_name || item.name || 'Product',
          qty: Number(item.quantity || item.qty || 1),
          price: Number(item.price || 0),
          size: item.variant_name || item.size || '',
          color: item.color_name || item.color || '',
          image:
            item.image ||
            item.image_url ||
            item.product_image ||
            'https://via.placeholder.com/80x80?text=IMG'
        }))
      }
    })

  } catch (err) {
    console.error('loadOrders error:', err)
    orders.value = []
  } finally {
    loading.value = false
  }
}

// ─── Filtering ────────────────────────────────────────────────────
const filteredOrders = computed(() => {
  if (activeTab.value === 'all') return orders.value
  return orders.value.filter(o => o.tabStatus === activeTab.value)
})

// ─── Helpers ──────────────────────────────────────────────────────
function statusLabel(rawStatus) {
  return STATUS_LABEL_MAP[rawStatus] || rawStatus
}

function statusClass(rawStatus) {
  const s = rawStatus || ''

  return {
    'status-delivered':  s === 'DELIVERED',
    'status-shipped':    s === 'SHIPPED',
    'status-processing': ['PENDING', 'PAID', 'CONFIRMED', 'PROCESSING'].includes(s),
    'status-cancelled':  ['CANCELLED', 'PAYMENT_FAILED'].includes(s),
  }
}

function isTrackable(rawStatus) {
  return TRACKABLE_STATUSES.has(rawStatus)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'

  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

function handleImgError(e) {
  e.target.src = 'https://via.placeholder.com/80x80?text=IMG'
}

// ─── Actions ──────────────────────────────────────────────────────
function viewOrder(order) {
  router.push(`/order-confirmation/${order.id}`)
}

function openTrack(order) {
  selectedOrder.value = {
    id: order.id,
    status: order.rawStatus
  }

  showTrackModal.value = true
}

function buyAgain(order) {
  console.log('Buy again:', order.id)
}

// ─── Invoice Download ─────────────────────────────────────────────
// This works for:
// 1. New orders: invoice already generated after payment.
// 2. Old orders: if invoice PDF not found, it calls /invoice/generate/order/{order_id}, then downloads.
async function downloadInvoice(order) {
  try {
    if (!order?.id) {
      console.error('Order id missing for invoice:', order)
      return
    }

    const invoiceNo = `INV-ORDER-${order.id}`

    try {
      const response = await api.get(`/invoice/download/${invoiceNo}`, {
        responseType: 'blob'
      })

      downloadInvoiceBlob(response, invoiceNo)
      return

    } catch (downloadError) {
      console.warn('Invoice PDF not found. Trying to generate invoice now...', downloadError)
    }

    await api.post(`/invoice/generate/order/${order.id}`)

    const response = await api.get(`/invoice/download/${invoiceNo}`, {
      responseType: 'blob'
    })

    downloadInvoiceBlob(response, invoiceNo)

  } catch (error) {
    console.error('INVOICE DOWNLOAD ERROR:', error)

    const backendMessage =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      'Invoice not available for this order.'

    alert(backendMessage)
  }
}

function downloadInvoiceBlob(response, invoiceNo) {
  const blob = new Blob([response.data], {
    type: response.headers['content-type'] || 'application/pdf'
  })

  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `${invoiceNo}.pdf`

  document.body.appendChild(link)
  link.click()

  link.remove()
  window.URL.revokeObjectURL(url)
}
</script>

<style scoped>
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* ══ PAGE SHELL ═══════════════════════════════════════════════ */
.orders-page {
  --teal:       #1a7a6e;
  --teal-dk:    #0e4d45;
  --teal-lt:    #e6f5f2;
  --teal-mid:   #2dbbaa;
  --peacock:    #007f8c;
  --peacock-lt: #e0f4f6;
  --border:     #e2ecea;
  --text:       #1a1a1a;
  --muted:      #7a8c8a;
  --r:          14px;

  width: 100%;
  min-height: calc(100vh - 64px);
  background: #f0f5f4;
  padding: 40px 48px 60px;
  animation: pageIn 0.35s ease both;
}

@keyframes pageIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ══ HEADER ═══════════════════════════════════════════════════ */
.orders-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 36px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--teal), var(--peacock));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.page-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  margin: 0 0 2px;
  letter-spacing: -0.3px;
}

.page-sub {
  font-size: 13px;
  color: var(--muted);
  margin: 0;
}

/* ══ FILTER TABS ══════════════════════════════════════════════ */
.filter-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 7px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  background: #fff;
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.filter-tab:hover {
  border-color: var(--teal-mid);
  color: var(--teal);
}

.filter-tab.active {
  background: var(--teal);
  border-color: var(--teal);
  color: #fff;
}

/* ══ EMPTY STATE ═════════════════════════════════════════════ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
}

.empty-icon {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: var(--teal-lt);
  color: var(--teal);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 6px;
}

.empty-sub {
  font-size: 14px;
  color: var(--muted);
  margin: 0 0 24px;
}

.btn-shop {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 24px;
  border-radius: 12px;
  border: none;
  background: var(--teal);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}

.btn-shop:hover {
  background: var(--teal-dk);
  transform: translateY(-1px);
}

/* ══ ORDERS LIST ═════════════════════════════════════════════ */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ══ ORDER CARD ══════════════════════════════════════════════ */
.order-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 18px;
  overflow: hidden;
  animation: cardIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
  transition: box-shadow 0.2s, transform 0.2s;
}

.order-card:hover {
  box-shadow: 0 6px 24px rgba(26, 122, 110, 0.1);
  transform: translateY(-2px);
}

.skeleton-card {
  padding: 16px;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ─ Card Header ─ */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 22px;
  background: linear-gradient(90deg, #f0f9f7 0%, #f7fdfc 100%);
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
  gap: 10px;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.order-id {
  font-size: 14px;
  font-weight: 700;
  color: var(--teal-dk);
  letter-spacing: 0.3px;
}

.order-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--muted);
  opacity: 0.5;
}

.order-date {
  font-size: 13px;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ─ Status Badge ─ */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 13px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-delivered {
  background: #e6f9f0;
  color: #0e7a45;
}

.status-delivered .status-dot {
  background: #0e7a45;
}

.status-shipped {
  background: var(--peacock-lt);
  color: var(--peacock);
}

.status-shipped .status-dot {
  background: var(--peacock);
}

.status-processing {
  background: #fff8e6;
  color: #b87a00;
}

.status-processing .status-dot {
  background: #f0a500;
}

.status-cancelled {
  background: #fff0f0;
  color: #c0392b;
}

.status-cancelled .status-dot {
  background: #c0392b;
}

/* ─ Card Body ─ */
.card-body {
  padding: 20px 22px;
}

/* ─ Products ─ */
.products-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 18px;
}

.product-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: var(--r);
  border: 1px solid var(--border);
  background: #fbfdfc;
  transition: background 0.15s;
}

.product-row:hover {
  background: var(--teal-lt);
  border-color: #c4deda;
}

.product-img-wrap {
  width: 64px;
  height: 64px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f0f5f4;
  border: 1px solid var(--border);
}

.product-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-meta {
  font-size: 12px;
  color: var(--muted);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.meta-sep {
  opacity: 0.4;
}

.product-price {
  font-size: 15px;
  font-weight: 700;
  color: var(--teal-dk);
  flex-shrink: 0;
}

/* ─ Footer ─ */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.total-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.total-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--muted);
}

.total-amount {
  font-size: 20px;
  font-weight: 800;
  color: var(--teal-dk);
  letter-spacing: -0.3px;
}

/* ─ Buttons ─ */
.action-btns {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  border: 1.5px solid transparent;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.38;
  cursor: not-allowed;
  pointer-events: none;
}

.btn-outline {
  background: #fff;
  border-color: var(--border);
  color: var(--text);
}

.btn-outline:hover {
  background: var(--teal-lt);
  border-color: var(--teal-mid);
  color: var(--teal);
}

.btn-primary {
  background: linear-gradient(135deg, var(--teal), var(--peacock));
  border-color: transparent;
  color: #fff;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--teal-dk), #005f6b);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(26, 122, 110, 0.28);
}

.btn-primary:active {
  transform: scale(0.97);
}

/* ══ RESPONSIVE ══════════════════════════════════════════════ */
@media (min-width: 681px) and (max-width: 1024px) {
  .orders-page {
    padding: 32px 28px 48px;
  }

  .orders-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 680px) {
  .orders-page {
    padding: 24px 16px 48px;
  }

  .orders-header {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 24px;
  }

  .page-title {
    font-size: 22px;
  }

  .card-header {
    padding: 14px 16px;
  }

  .card-body {
    padding: 16px;
  }

  .product-row {
    gap: 10px;
    padding: 10px 12px;
  }

  .product-img-wrap {
    width: 54px;
    height: 54px;
  }

  .card-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-btns {
    width: 100%;
    justify-content: stretch;
  }

  .btn {
    flex: 1;
    justify-content: center;
    padding: 9px 10px;
    font-size: 12px;
  }

  .total-amount {
    font-size: 18px;
  }
}

@media (max-width: 390px) {
  .orders-page {
    padding: 20px 12px 40px;
  }

  .product-img-wrap {
    width: 46px;
    height: 46px;
  }
}
</style>
