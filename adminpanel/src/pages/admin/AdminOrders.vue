<template>
  <q-page class="admin-page">
    <!-- Header -->
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div class="row items-center q-gutter-sm">
          <q-btn flat round dense icon="arrow_back" color="blue-6" @click="$router.back()" />
          <div>
            <div class="text-h5 text-weight-bold text-grey-9">
              Order {{ order?.id || route.params.id }}
            </div>
            <div class="text-caption text-blue-7">View and manage order details</div>
          </div>
        </div>
        <div class="row q-gutter-sm items-center">
          <q-badge :color="statusColor(order?.status)" class="q-pa-sm text-subtitle2" v-if="order">
            {{ order.status }}
          </q-badge>
          <q-btn
            label="Cancel Order"
            outline
            color="negative"
            no-caps
            icon="cancel"
            size="sm"
            :disable="!canCancel"
            @click="cancelDialog = true"
            v-if="order"
          />
        </div>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div class="q-px-lg q-pb-lg q-pt-md" v-if="loading">
      <div class="row q-gutter-md">
        <div class="col-12 col-md-8">
          <q-card flat class="data-card q-mb-md">
            <q-card-section>
              <q-skeleton type="text" width="40%" class="q-mb-md" />
              <q-skeleton type="rect" height="120px" />
            </q-card-section>
          </q-card>
          <q-card flat class="data-card">
            <q-card-section>
              <q-skeleton type="text" width="30%" class="q-mb-md" />
              <q-skeleton type="rect" height="200px" />
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md">
          <q-card flat class="data-card q-mb-md">
            <q-card-section>
              <q-skeleton type="text" width="50%" class="q-mb-md" />
              <q-skeleton v-for="i in 4" :key="i" type="text" class="q-mb-sm" />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div class="q-px-lg q-pt-lg" v-else-if="error">
      <q-banner class="bg-red-1 text-negative rounded-borders" rounded>
        <template #avatar><q-icon name="error" color="negative" /></template>
        {{ error }}
        <template #action>
          <q-btn flat label="Retry" color="negative" @click="fetchOrder" />
        </template>
      </q-banner>
    </div>

    <!-- Content -->
    <div class="q-px-lg q-pb-lg q-pt-md" v-else-if="order">
      <div class="row q-gutter-md">
        <!-- LEFT COLUMN -->
        <div class="col-12 col-md-8">
          <!-- Order Info Card -->
          <q-card flat class="data-card q-mb-md">
            <q-card-section>
              <div class="section-title q-mb-md">
                <q-icon name="receipt_long" color="blue-6" size="18px" class="q-mr-xs" />
                Order Information
              </div>
              <div class="row q-gutter-md">
                <div
                  class="col-12 col-sm-6 col-md-3"
                  v-for="info in orderInfoFields"
                  :key="info.label"
                >
                  <div class="info-block">
                    <div class="info-label">{{ info.label }}</div>
                    <div class="info-value">{{ info.value }}</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Customer Info Card -->
          <q-card flat class="data-card q-mb-md">
            <q-card-section>
              <div class="section-title q-mb-md">
                <q-icon name="person" color="blue-6" size="18px" class="q-mr-xs" />
                Customer Information
              </div>
              <div class="row items-center q-gutter-md">
                <q-avatar size="52px" color="blue-7" text-color="white" font-size="20px">
                  {{ initials(order.customer?.name) }}
                </q-avatar>
                <div class="col">
                  <div class="text-grey-9 text-weight-bold text-subtitle1">
                    {{ order.customer?.name || '—' }}
                  </div>
                  <div class="row q-gutter-md q-mt-xs">
                    <div class="row items-center q-gutter-xs">
                      <q-icon name="email" size="13px" color="blue-5" />
                      <span class="text-caption text-grey-7">{{
                        order.customer?.email || '—'
                      }}</span>
                    </div>
                    <div class="row items-center q-gutter-xs">
                      <q-icon name="phone" size="13px" color="blue-5" />
                      <span class="text-caption text-grey-7">{{
                        order.customer?.phone || '—'
                      }}</span>
                    </div>
                  </div>
                </div>
                <q-btn
                  flat
                  no-caps
                  size="sm"
                  color="blue-6"
                  label="View Profile"
                  icon="open_in_new"
                />
              </div>

              <!-- Shipping Address -->
              <q-separator class="q-my-md" />
              <div class="row items-start q-gutter-sm">
                <q-icon name="location_on" color="blue-5" size="16px" class="q-mt-xs" />
                <div>
                  <div class="text-caption text-grey-6 q-mb-xs">Shipping Address</div>
                  <div class="text-grey-9">
                    {{ order.shipping_address || '123 Main Street, Mumbai, Maharashtra 400001' }}
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Order Items -->
          <q-card flat class="data-card q-mb-md">
            <q-card-section>
              <div class="section-title q-mb-md">
                <q-icon name="inventory_2" color="blue-6" size="18px" class="q-mr-xs" />
                Order Items
                <q-badge color="blue-6" class="q-ml-sm">{{ orderItems.length }}</q-badge>
              </div>

              <div class="items-table">
                <div class="items-header row q-px-md">
                  <div class="col-5">Product</div>
                  <div class="col-2">Variant</div>
                  <div class="col-1 text-center">Qty</div>
                  <div class="col-2 text-right">Unit Price</div>
                  <div class="col-2 text-right">Subtotal</div>
                </div>
                <div
                  v-for="item in orderItems"
                  :key="item.id"
                  class="items-row row items-center q-px-md"
                >
                  <div class="col-5">
                    <div class="text-grey-9 text-weight-medium">{{ item.product_name }}</div>
                    <div class="text-caption text-grey-5">SKU: {{ item.sku || 'N/A' }}</div>
                  </div>
                  <div class="col-2">
                    <q-chip size="xs" color="indigo-1" text-color="indigo-8" dense>{{
                      item.variant
                    }}</q-chip>
                  </div>
                  <div class="col-1 text-center text-grey-9">{{ item.qty }}</div>
                  <div class="col-2 text-right text-grey-7">₹{{ item.price.toLocaleString() }}</div>
                  <div class="col-2 text-right text-green-7 text-weight-bold">
                    ₹{{ (item.price * item.qty).toLocaleString() }}
                  </div>
                </div>
              </div>

              <!-- Order Totals -->
              <div class="totals-section q-mt-md">
                <div class="totals-row" v-for="t in totalsRows" :key="t.label">
                  <span class="totals-label">{{ t.label }}</span>
                  <span :class="t.class || 'totals-value'">{{ t.value }}</span>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Payment Info -->
          <q-card flat class="data-card">
            <q-card-section>
              <div class="section-title q-mb-md">
                <q-icon name="payments" color="blue-6" size="18px" class="q-mr-xs" />
                Payment Details
              </div>
              <div class="row q-gutter-md">
                <div class="col-12 col-sm-6 col-md-3" v-for="p in paymentFields" :key="p.label">
                  <div class="info-block">
                    <div class="info-label">{{ p.label }}</div>
                    <div class="info-value">
                      <q-badge v-if="p.isBadge" :color="p.color">{{ p.value }}</q-badge>
                      <span v-else>{{ p.value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- RIGHT COLUMN -->
        <div class="col-12 col-md">
          <!-- Status Update Card -->
          <q-card flat class="data-card q-mb-md">
            <q-card-section>
              <div class="section-title q-mb-md">
                <q-icon name="update" color="blue-6" size="18px" class="q-mr-xs" />
                Update Status
              </div>
              <q-select
                v-model="newStatus"
                :options="statusOptions"
                label="Order Status"
                dense
                standout="bg-blue-1"
                class="q-mb-md"
              />
              <q-btn
                label="Update Status"
                color="blue-6"
                unelevated
                no-caps
                full-width
                icon="check"
                :loading="updatingStatus"
                :disable="newStatus === order.status"
                @click="updateStatus"
              />
            </q-card-section>
          </q-card>

          <!-- Order Summary -->
          <q-card flat class="data-card q-mb-md">
            <q-card-section>
              <div class="section-title q-mb-md">
                <q-icon name="summarize" color="blue-6" size="18px" class="q-mr-xs" />
                Summary
              </div>
              <div class="summary-grid">
                <div class="summary-row" v-for="s in summaryFields" :key="s.label">
                  <span class="summary-label">{{ s.label }}</span>
                  <span
                    class="summary-value"
                    :class="s.highlight ? 'text-blue-8 text-weight-bold' : ''"
                    >{{ s.value }}</span
                  >
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Status History / Timeline -->
          <q-card flat class="data-card">
            <q-card-section>
              <div class="section-title q-mb-md">
                <q-icon name="history" color="blue-6" size="18px" class="q-mr-xs" />
                Order Timeline
              </div>
              <div v-if="historyLoading" class="text-center q-py-md">
                <q-spinner color="blue-5" size="24px" />
              </div>
              <q-timeline color="blue" dense v-else>
                <q-timeline-entry
                  v-for="h in orderHistory"
                  :key="h.id"
                  :title="h.status"
                  :subtitle="formatDate(h.changed_at)"
                  :color="statusColor(h.status)"
                  icon="circle"
                >
                  <div class="text-caption text-grey-6" v-if="h.note">{{ h.note }}</div>
                  <div class="text-caption text-grey-5" v-if="h.changed_by">
                    By: {{ h.changed_by }}
                  </div>
                </q-timeline-entry>
                <q-timeline-entry
                  title="Order Placed"
                  :subtitle="formatDate(order.created_at)"
                  color="blue-4"
                  icon="shopping_cart"
                />
              </q-timeline>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Cancel Confirmation Dialog -->
    <q-dialog v-model="cancelDialog" persistent>
      <q-card class="modal-card" style="width: 400px; max-width: 95vw">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="warning" color="negative" size="52px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold text-subtitle1">Cancel Order?</div>
          <div class="text-caption text-grey-6 text-center q-mt-xs">
            This will cancel order <strong>{{ order?.id }}</strong
            >. This action cannot be undone.
          </div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-input
            v-model="cancelReason"
            label="Reason for cancellation"
            dense
            standout="bg-blue-1"
            type="textarea"
            rows="2"
          />
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Keep Order" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Cancel Order"
            color="negative"
            unelevated
            no-caps
            :loading="cancelling"
            @click="confirmCancel"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Status update success notification -->
    <q-dialog v-model="successDialog">
      <q-card class="modal-card" style="width: 300px">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="check_circle" color="positive" size="48px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold">{{ successMsg }}</div>
        </q-card-section>
        <q-card-actions align="center">
          <q-btn label="OK" color="blue-6" unelevated no-caps v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// ── State ──────────────────────────────────────────────────────
const loading = ref(true)
const error = ref(null)
const order = ref(null)
const orderItems = ref([])
const orderHistory = ref([])
const historyLoading = ref(false)
const updatingStatus = ref(false)
const cancelling = ref(false)
const cancelDialog = ref(false)
const cancelReason = ref('')
const successDialog = ref(false)
const successMsg = ref('')
const newStatus = ref('')

const statusOptions = ['pending', 'processing', 'shipped', 'completed', 'cancelled']

// ── Mock data (replace with real API calls) ────────────────────
const mockOrder = {
  id: route.params.id || '#ORD-1001',
  user_id: 42,
  status: 'processing',
  payment_status: 'paid',
  payment_method: 'UPI',
  transaction_id: 'TXN-00182',
  subtotal: 7897,
  discount: 500,
  tax: 394,
  shipping_fee: 0,
  total_amount: 7791,
  created_at: '2024-01-15T14:30:00',
  updated_at: '2024-01-16T09:00:00',
  shipping_address: '12, Park Avenue, Andheri West, Mumbai, Maharashtra 400058',
  customer: {
    name: 'Rahul Sharma',
    email: 'rahul@example.com',
    phone: '9876543210',
  },
}

const mockItems = [
  {
    id: 1,
    product_name: 'Wireless Earbuds Pro',
    variant: 'Black',
    sku: 'WEP-001-BLK',
    price: 2499,
    qty: 2,
  },
  {
    id: 2,
    product_name: 'Mechanical Keyboard',
    variant: 'RGB Backlit',
    sku: 'MKB-004-RGB',
    price: 2899,
    qty: 1,
  },
]

const mockHistory = [
  {
    id: 3,
    status: 'processing',
    changed_at: '2024-01-16T09:00:00',
    changed_by: 'Admin',
    note: 'Payment confirmed',
  },
  {
    id: 2,
    status: 'pending',
    changed_at: '2024-01-15T14:35:00',
    changed_by: 'System',
    note: 'Awaiting payment',
  },
]

// ── API Calls ──────────────────────────────────────────────────
const fetchOrder = async () => {
  loading.value = true
  error.value = null
  try {
    // Replace with: const res = await fetch(`/admin/orders/${route.params.id}`)
    await new Promise((r) => setTimeout(r, 600))
    order.value = mockOrder
    orderItems.value = mockItems
    newStatus.value = mockOrder.status
  } catch {
    error.value = 'Failed to load order. Please try again.'
  } finally {
    loading.value = false
  }
}

const fetchHistory = async () => {
  historyLoading.value = true
  try {
    // Replace with: const res = await fetch(`/admin/orders/${route.params.id}/history`)
    await new Promise((r) => setTimeout(r, 400))
    orderHistory.value = mockHistory
  } catch {
    console.error('Failed to load history')
  } finally {
    historyLoading.value = false
  }
}

const updateStatus = async () => {
  updatingStatus.value = true
  try {
    // Replace with: await fetch(`/admin/orders/${order.value.id}/status`, { method: 'PUT', body: JSON.stringify({ status: newStatus.value }) })
    await new Promise((r) => setTimeout(r, 600))
    order.value.status = newStatus.value
    orderHistory.value.unshift({
      id: Date.now(),
      status: newStatus.value,
      changed_at: new Date().toISOString(),
      changed_by: 'Admin',
      note: 'Status updated manually',
    })
    successMsg.value = `Order status updated to "${newStatus.value}"`
    successDialog.value = true
  } catch {
    error.value = 'Failed to update status.'
  } finally {
    updatingStatus.value = false
  }
}

const confirmCancel = async () => {
  cancelling.value = true
  try {
    // Replace with: await fetch(`/admin/orders/${order.value.id}/cancel`, { method: 'POST', body: JSON.stringify({ reason: cancelReason.value }) })
    await new Promise((r) => setTimeout(r, 600))
    order.value.status = 'cancelled'
    newStatus.value = 'cancelled'
    cancelDialog.value = false
    successMsg.value = 'Order cancelled successfully.'
    successDialog.value = true
  } catch {
    error.value = 'Failed to cancel order.'
  } finally {
    cancelling.value = false
  }
}

// ── Computed ───────────────────────────────────────────────────
const canCancel = computed(
  () => order.value && !['cancelled', 'completed'].includes(order.value.status),
)

const orderInfoFields = computed(() =>
  order.value
    ? [
        { label: 'Order ID', value: order.value.id },
        { label: 'Order Date', value: formatDate(order.value.created_at) },
        { label: 'Last Updated', value: formatDate(order.value.updated_at) },
        { label: 'Items', value: orderItems.value.length + ' items' },
      ]
    : [],
)

const paymentFields = computed(() =>
  order.value
    ? [
        {
          label: 'Payment Status',
          value: order.value.payment_status,
          isBadge: true,
          color: order.value.payment_status === 'paid' ? 'positive' : 'warning',
        },
        { label: 'Payment Method', value: order.value.payment_method },
        { label: 'Transaction ID', value: order.value.transaction_id },
        { label: 'Amount', value: '₹' + order.value.total_amount?.toLocaleString() },
      ]
    : [],
)

const totalsRows = computed(() =>
  order.value
    ? [
        { label: 'Subtotal', value: '₹' + order.value.subtotal?.toLocaleString() },
        {
          label: 'Discount',
          value: '- ₹' + order.value.discount?.toLocaleString(),
          class: 'totals-discount',
        },
        { label: 'Tax (5%)', value: '₹' + order.value.tax?.toLocaleString() },
        {
          label: 'Shipping',
          value: order.value.shipping_fee === 0 ? 'FREE' : '₹' + order.value.shipping_fee,
        },
        {
          label: 'Total',
          value: '₹' + order.value.total_amount?.toLocaleString(),
          class: 'totals-total',
        },
      ]
    : [],
)

const summaryFields = computed(() =>
  order.value
    ? [
        { label: 'Order ID', value: order.value.id },
        { label: 'Customer', value: order.value.customer?.name },
        { label: 'Items', value: orderItems.value.length },
        {
          label: 'Total',
          value: '₹' + order.value.total_amount?.toLocaleString(),
          highlight: true,
        },
      ]
    : [],
)

// ── Helpers ────────────────────────────────────────────────────
const statusColor = (s) =>
  ({
    pending: 'warning',
    processing: 'info',
    shipped: 'purple-6',
    completed: 'positive',
    cancelled: 'negative',
  })[s] || 'grey'

const initials = (name) =>
  name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || '?'

const formatDate = (dt) => {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchOrder()
  fetchHistory()
})
</script>

<style scoped>
.admin-page {
  background: #f8fafc;
  min-height: 100vh;
}
.page-header {
  border-bottom: 1px solid #e2e8f0;
}

.data-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #1e40af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
}

/* Info blocks */
.info-block {
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.info-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.info-value {
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

/* Items table */
.items-table {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}
.items-header {
  background: #eff6ff;
  padding: 10px 16px;
  color: #1e40af;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.items-row {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
}
.items-row:last-child {
  border-bottom: none;
}
.items-row:hover {
  background: #f8fafc;
}

/* Totals */
.totals-section {
  border-top: 2px solid #e2e8f0;
  padding-top: 12px;
}
.totals-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}
.totals-label {
  color: #64748b;
  font-size: 13px;
}
.totals-value {
  color: #1e293b;
  font-size: 13px;
  font-weight: 500;
}
.totals-discount {
  color: #16a34a;
  font-size: 13px;
  font-weight: 500;
}
.totals-total {
  color: #1e40af;
  font-size: 16px;
  font-weight: 700;
}

/* Summary */
.summary-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
}
.summary-label {
  color: #64748b;
  font-size: 12px;
}
.summary-value {
  color: #1e293b;
  font-size: 13px;
  font-weight: 500;
}

/* Modal */
.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
</style>
