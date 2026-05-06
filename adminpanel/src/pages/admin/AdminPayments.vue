<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Payments</div>
          <div class="text-caption text-blue-7">Review and manage transaction records</div>
        </div>
        <div class="row items-center q-gutter-sm">
          <q-chip color="positive" text-color="white" icon="check_circle" size="sm">
            Success: {{ successTotal }}
          </q-chip>
          <q-chip color="warning" text-color="white" icon="schedule" size="sm">
            Pending: {{ pendingTotal }}
          </q-chip>
        </div>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- ── Payment Summary Cards — GET /admin/payments/summary ── -->
      <div class="row q-gutter-md q-mb-lg">
        <div
          class="col-12 col-sm-6 col-md-3"
          v-for="card in paymentSummaryCards"
          :key="card.label"
        >
          <q-card class="stat-card" flat>
            <q-card-section class="q-pa-md">
              <div class="row items-center q-gutter-sm q-mb-xs">
                <div class="stat-icon" :style="{ background: card.bg }">
                  <q-icon :name="card.icon" :color="card.color" size="18px" />
                </div>
                <div class="text-caption text-blue-7">{{ card.label }}</div>
              </div>
              <div v-if="summaryLoading" class="text-h5 text-grey-9 text-weight-bold">
                <q-skeleton type="text" width="80px" />
              </div>
              <div v-else class="text-h5 text-grey-9 text-weight-bold">{{ card.value }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Filters -->
      <div class="row q-gutter-md q-mb-md items-center">
        <div class="col-12 col-sm">
          <q-input
            v-model="search"
            placeholder="Search by transaction ID, order ID or ref..."
            dense
            standout="bg-blue-1"
            clearable
            @update:model-value="onSearchChange"
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
        <!-- Status filter -->
        <div class="col-auto">
          <q-select
            v-model="statusFilter"
            :options="statusFilterOptions"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            dense
            standout="bg-blue-1"
            style="min-width: 140px"
            label="Status"
            clearable
            @update:model-value="loadTransactions"
          />
        </div>
        <!-- Method filter -->
        <div class="col-auto">
          <q-select
            v-model="methodFilter"
            :options="methodFilterOptions"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            dense
            standout="bg-blue-1"
            style="min-width: 150px"
            label="Method"
            clearable
            @update:model-value="loadTransactions"
          />
        </div>
      </div>

      <!-- ── Transaction List — GET /admin/payments/ ── -->
      <q-card class="data-card" flat>
        <q-table
          :rows="filteredTransactions"
          :columns="columns"
          row-key="id"
          flat
          :rows-per-page-options="[10, 25, 50]"
          :loading="tableLoading"
          class="payments-table"
          wrap-cells
        >
          <!-- transaction id -->
          <template #body-cell-id="props">
            <q-td :props="props">
              <code class="txn-id">#{{ props.value }}</code>
            </q-td>
          </template>

          <!-- order_id — click to open GET /admin/payments/{order_id} -->
          <template #body-cell-order_id="props">
            <q-td :props="props">
              <span
                v-if="props.value"
                class="text-blue-7 text-weight-medium order-id-link"
                @click="viewOrderPayment(props.value)"
              >
                #{{ props.value }}
                <q-icon name="open_in_new" size="11px" class="q-ml-xs" />
              </span>
              <span v-else class="text-grey-4">—</span>
            </q-td>
          </template>

          <!-- amount -->
          <template #body-cell-amount="props">
            <q-td :props="props">
              <span class="text-green-7 text-weight-bold text-subtitle2">
                {{ formatAmount(props.value) }}
              </span>
            </q-td>
          </template>

          <!-- payment_method -->
          <template #body-cell-payment_method="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon :name="getMethodIcon(props.value)" color="blue-5" size="15px" />
                <span class="text-grey-7">{{ METHOD_LABELS[props.value] || props.value || '—' }}</span>
              </div>
            </q-td>
          </template>

          <!-- status -->
          <template #body-cell-status="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon
                  :name="getStatusIcon(props.value)"
                  :color="getStatusColor(props.value)"
                  size="14px"
                />
                <q-badge
                  :color="getStatusColor(props.value)"
                  :label="STATUS_LABELS[props.value] || props.value"
                  class="status-badge"
                />
              </div>
            </q-td>
          </template>

          <!-- currency -->
          <template #body-cell-currency="props">
            <q-td :props="props">
              <span class="text-grey-6 text-caption">{{ props.value || 'INR' }}</span>
            </q-td>
          </template>

          <!-- transaction_ref -->
          <template #body-cell-transaction_ref="props">
            <q-td :props="props">
              <code v-if="props.value" class="txn-id" style="font-size:11px;">
                {{ props.value }}
              </code>
              <span v-else class="text-grey-4">—</span>
            </q-td>
          </template>

          <!-- created_at -->
          <template #body-cell-created_at="props">
            <q-td :props="props">
              <span class="text-caption text-grey-6">{{ formatDate(props.value) }}</span>
            </q-td>
          </template>

          <!-- actions -->
          <template #body-cell-actions="props">
            <q-td :props="props">
              <!-- Process payment: only available for PENDING -->
              <div v-if="props.row.status === 'PENDING'" class="row q-gutter-xs no-wrap">
                <q-btn
                  label="Process"
                  color="primary"
                  unelevated
                  no-caps
                  size="sm"
                  icon="play_arrow"
                  @click="openProcessDialog(props.row)"
                />
              </div>
              <!-- SUCCESS: terminal -->
              <div
                v-else-if="props.row.status === 'SUCCESS'"
                class="row items-center q-gutter-xs text-positive"
              >
                <q-icon name="verified" size="18px" />
                <span class="text-caption">{{ STATUS_LABELS.SUCCESS }}</span>
              </div>
              <!-- FAILED: terminal -->
              <div
                v-else-if="props.row.status === 'FAILED'"
                class="row items-center q-gutter-xs text-negative"
              >
                <q-icon name="error" size="18px" />
                <span class="text-caption">{{ STATUS_LABELS.FAILED }}</span>
              </div>
              <!-- REFUNDED: terminal -->
              <div
                v-else-if="props.row.status === 'REFUNDED'"
                class="row items-center q-gutter-xs text-info"
              >
                <q-icon name="replay" size="18px" />
                <span class="text-caption">{{ STATUS_LABELS.REFUNDED }}</span>
              </div>
              <!-- Unknown -->
              <div v-else class="row items-center q-gutter-xs text-grey-5">
                <q-icon name="help" size="18px" />
                <span class="text-caption">{{ props.row.status }}</span>
              </div>
            </q-td>
          </template>

          <template #no-data>
            <div class="full-width column flex-center q-pa-xl text-blue-7">
              <q-icon name="account_balance_wallet" size="48px" class="q-mb-sm" />
              <div>No transactions found</div>
            </div>
          </template>

          <template #loading>
            <q-inner-loading showing color="blue-6" />
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- ── Process Payment Dialog ── -->
    <q-dialog v-model="processDialog" persistent>
      <q-card class="modal-card" style="width: 460px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6 text-grey-9 text-weight-bold">Process Payment</div>
          <div class="text-caption text-blue-7 q-mt-xs">
            Transaction ID: <strong>#{{ processTarget?.id }}</strong> |
            Order: <strong>#{{ processTarget?.order_id }}</strong> |
            Amount: <strong>{{ formatAmount(processTarget?.amount) }}</strong>
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <!-- Status selection — only valid transitions shown -->
          <q-select
            v-model="processForm.status"
            :options="processStatusOptions"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            label="New Status *"
            standout="bg-blue-1"
            dense
            class="q-mb-md"
          />
          <!-- Payment method -->
          <q-select
            v-model="processForm.payment_method"
            :options="methodFilterOptions.filter(o => o.value)"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            label="Payment Method *"
            standout="bg-blue-1"
            dense
            class="q-mb-md"
          />
          <!-- Transaction ref -->
          <q-input
            v-model="processForm.transaction_ref"
            label="Transaction Reference *"
            standout="bg-blue-1"
            dense
            placeholder="e.g. pay_ABC123xyz"
          />
        </q-card-section>

        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Confirm"
            color="primary"
            unelevated
            no-caps
            :loading="processLoading"
            :disable="!processForm.status || !processForm.payment_method || !processForm.transaction_ref"
            @click="confirmProcess"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ── Order Payment Details Modal — GET /admin/payments/{order_id} ── -->
    <q-dialog v-model="orderPaymentModal">
      <q-card class="modal-card" style="width: 520px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Order Payment Details</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>

        <q-card-section>
          <div class="text-caption text-blue-7 q-mb-md">
            Order: <strong>#{{ selectedOrderId }}</strong>
          </div>

          <q-inner-loading :showing="orderPaymentLoading" color="blue-6" />

          <div v-if="!orderPaymentLoading && orderPaymentData.length" class="detail-grid">
            <div v-for="t in orderPaymentData" :key="t.id" class="order-txn-row">
              <div class="row items-center justify-between">
                <code class="txn-id">#{{ t.id }}</code>
                <q-badge
                  :color="getStatusColor(t.status)"
                  :label="STATUS_LABELS[t.status] || t.status"
                />
              </div>
              <div class="row items-center justify-between q-mt-xs">
                <div class="row items-center q-gutter-xs">
                  <q-icon :name="getMethodIcon(t.payment_method)" color="blue-5" size="13px" />
                  <span class="text-caption text-grey-6">
                    {{ METHOD_LABELS[t.payment_method] || t.payment_method || '—' }}
                  </span>
                </div>
                <span class="text-green-7 text-weight-bold">{{ formatAmount(t.amount) }}</span>
              </div>
              <div class="row items-center justify-between q-mt-xs">
                <span class="text-caption text-grey-5">
                  Ref: {{ t.transaction_ref || '—' }}
                </span>
                <span class="text-caption text-grey-5">{{ formatDate(t.created_at) }}</span>
              </div>
              <div v-if="t.payment_gateway" class="text-caption text-grey-5 q-mt-xs">
                Gateway: {{ t.payment_gateway }}
                <span v-if="t.gateway_transaction_id"> | {{ t.gateway_transaction_id }}</span>
              </div>
            </div>
          </div>

          <div
            v-if="!orderPaymentLoading && !orderPaymentData.length"
            class="column flex-center q-pa-md text-blue-7"
          >
            <q-icon name="account_balance_wallet" size="36px" class="q-mb-sm" />
            <div>No transactions for this order</div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- ── Success Snack ── -->
    <q-dialog v-model="successSnack">
      <q-card class="modal-card" style="width: 300px">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="check_circle" color="positive" size="48px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold">Payment Processed!</div>
          <div class="text-caption text-blue-7 q-mt-xs">
            {{ successMessage }}
          </div>
        </q-card-section>
        <q-card-actions align="center">
          <q-btn label="OK" color="positive" unelevated no-caps v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Error notification -->
    <q-dialog v-model="errorDialog">
      <q-card class="modal-card" style="width: 340px">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="error_outline" color="negative" size="48px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold">Error</div>
          <div class="text-caption text-blue-7 q-mt-xs text-center">{{ errorMessage }}</div>
        </q-card-section>
        <q-card-actions align="center">
          <q-btn label="Close" color="negative" flat no-caps v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import paymentService, {
  PAYMENT_STATUSES,
  PAYMENT_METHODS,
  STATUS_LABELS,
  // STATUS_COLORS,
  // STATUS_ICONS,
  METHOD_LABELS,
  // METHOD_ICONS,
  VALID_TRANSITIONS,
} from 'src/services/paymentService'

// ── Destructure helpers from service ────────────────────────────────────────
const { getStatusColor, getStatusIcon, getMethodIcon, formatAmount } = paymentService

// ── State ────────────────────────────────────────────────────────────────────
const transactions   = ref([])      // from GET /admin/payments/
const summary        = ref(null)    // from GET /admin/payments/summary
const tableLoading   = ref(false)
const summaryLoading = ref(false)

// Filters
const search       = ref('')
const statusFilter = ref(null)
const methodFilter = ref(null)

// Order payment modal — GET /admin/payments/{order_id}
const orderPaymentModal   = ref(false)
const orderPaymentLoading = ref(false)
const selectedOrderId     = ref(null)
const orderPaymentData    = ref([])

// Process payment dialog — POST /admin/payments/process
const processDialog  = ref(false)
const processLoading = ref(false)
const processTarget  = ref(null)
const processForm    = ref({ status: null, payment_method: null, transaction_ref: '' })

// Feedback dialogs
const successSnack   = ref(false)
const successMessage = ref('')
const errorDialog    = ref(false)
const errorMessage   = ref('')

// ── Filter options built from constants (no hardcoding) ──────────────────────
const statusFilterOptions = computed(() => [
  { label: 'All Statuses', value: null },
  ...PAYMENT_STATUSES.map(s => ({ label: STATUS_LABELS[s] || s, value: s })),
])

const methodFilterOptions = computed(() => [
  { label: 'All Methods', value: null },
  ...PAYMENT_METHODS.map(m => ({ label: METHOD_LABELS[m] || m, value: m })),
])

// Process status options — only valid transitions for the target transaction
const processStatusOptions = computed(() => {
  if (!processTarget.value) return []
  const transitions = VALID_TRANSITIONS[processTarget.value.status] ?? []
  return transitions.map(s => ({ label: STATUS_LABELS[s] || s, value: s }))
})

// ── Table columns aligned to API response fields (TransactionOut) ────────────
const columns = [
  { name: 'id',              label: 'Transaction ID',  field: 'id',              align: 'left', sortable: true },
  { name: 'order_id',        label: 'Order ID',        field: 'order_id',        align: 'left' },
  { name: 'amount',          label: 'Amount',          field: 'amount',          align: 'left', sortable: true },
  { name: 'payment_method',  label: 'Method',          field: 'payment_method',  align: 'left' },
  { name: 'status',          label: 'Status',          field: 'status',          align: 'left', sortable: true },
  { name: 'currency',        label: 'Currency',        field: 'currency',        align: 'left' },
  { name: 'transaction_ref', label: 'Reference',       field: 'transaction_ref', align: 'left' },
  { name: 'created_at',      label: 'Date & Time',     field: 'created_at',      align: 'left', sortable: true },
  { name: 'actions',         label: 'Actions',         field: 'id',              align: 'left' },
]

// ── Computed filtered list (client-side search on top of server filters) ─────
const filteredTransactions = computed(() => {
  if (!search.value) return transactions.value
  const q = search.value.toLowerCase()
  return transactions.value.filter(t => {
    const idStr     = String(t.id || '').toLowerCase()
    const orderStr  = String(t.order_id || '').toLowerCase()
    const refStr    = String(t.transaction_ref || '').toLowerCase()
    return idStr.includes(q) || orderStr.includes(q) || refStr.includes(q)
  })
})

// ── Summary card data derived from API response ──────────────────────────────
const successTotal = computed(() =>
  transactions.value.filter(t => t.status === 'SUCCESS').length
)
const pendingTotal = computed(() =>
  transactions.value.filter(t => t.status === 'PENDING').length
)

const paymentSummaryCards = computed(() => {
  const s = summary.value
  return [
    {
      label: 'Total Revenue',
      value: s ? formatAmount(s.total_amount) : '—',
      icon:  'currency_rupee',
      color: 'green-6',
      bg:    'rgba(34,197,94,0.12)',
    },
    {
      label: 'Successful Amount',
      value: s ? formatAmount(s.successful_amount) : '—',
      icon:  'check_circle',
      color: 'positive',
      bg:    'rgba(34,197,94,0.12)',
    },
    {
      label: 'Total Transactions',
      value: s ? (s.total_transactions ?? '—') : '—',
      icon:  'receipt_long',
      color: 'blue-6',
      bg:    'rgba(59,130,246,0.12)',
    },
    {
      label: 'Refunded Amount',
      value: s ? formatAmount(s.refunded_amount) : '—',
      icon:  'replay',
      color: 'info',
      bg:    'rgba(14,165,233,0.12)',
    },
  ]
})

// ── Data loaders ─────────────────────────────────────────────────────────────

/**
 * Loads transactions from GET /admin/payments/ with current filters applied.
 */
async function loadTransactions () {
  tableLoading.value = true
  try {
    const filters = {}
    if (statusFilter.value) filters.status         = statusFilter.value
    if (methodFilter.value) filters.payment_method = methodFilter.value
    filters.limit = 500 // load all for client-side search; adjust as needed

    transactions.value = await paymentService.getAllPayments(filters)
  } catch (err) {
    showError(err?.message || 'Failed to load transactions')
  } finally {
    tableLoading.value = false
  }
}

/**
 * Loads revenue summary from GET /admin/payments/summary.
 */
async function loadSummary () {
  summaryLoading.value = true
  try {
    summary.value = await paymentService.getRevenueSummary()
  } catch (err) {
    // Non-critical — summary cards will show '—'
    console.error('Summary load error:', err?.message)
  } finally {
    summaryLoading.value = false
  }
}

// ── Search debounce ───────────────────────────────────────────────────────────
let searchTimeout = null
function onSearchChange () {
  // Search is purely client-side on already-loaded data; no API call needed
  clearTimeout(searchTimeout)
}

// ── Order payment details modal ───────────────────────────────────────────────

/**
 * Opens modal and fetches all transactions for the clicked order_id.
 * Calls GET /admin/payments/{order_id}
 */
async function viewOrderPayment (orderId) {
  selectedOrderId.value  = orderId
  orderPaymentData.value = []
  orderPaymentModal.value = true
  orderPaymentLoading.value = true
  try {
    orderPaymentData.value = await paymentService.getPaymentsByOrder(orderId)
  } catch (err) {
    // 404 is expected when no transactions exist yet — show empty state
    if (err?.status !== 404) {
      showError(err?.message || 'Failed to load order transactions')
    }
  } finally {
    orderPaymentLoading.value = false
  }
}

// ── Process payment dialog ────────────────────────────────────────────────────

function openProcessDialog (txn) {
  processTarget.value = txn
  processForm.value = {
    status:          null,
    payment_method:  txn.payment_method || null,
    transaction_ref: txn.transaction_ref || '',
  }
  processDialog.value = true
}

/**
 * Calls POST /admin/payments/process via sp_process_payment.
 * On SUCCESS: order.status → PAID, stock reduced by trigger.
 * On FAILED:  order.status → PAYMENT_FAILED.
 */
async function confirmProcess () {
  if (!processTarget.value) return

  processLoading.value = true
  try {
    const result = await paymentService.processPayment({
      order_id:        processTarget.value.order_id,
      payment_method:  processForm.value.payment_method,
      status:          processForm.value.status,
      transaction_ref: processForm.value.transaction_ref,
    })

    processDialog.value = false

    successMessage.value =
      `Transaction #${result.transaction_id} processed — ${STATUS_LABELS[result.status] || result.status}`
    successSnack.value = true

    // Reload both list and summary to reflect DB changes
    await Promise.all([loadTransactions(), loadSummary()])
  } catch (err) {
    showError(err?.message || 'Failed to process payment')
  } finally {
    processLoading.value = false
  }
}

// ── Utility helpers ───────────────────────────────────────────────────────────

function formatDate (dateStr) {
  if (!dateStr) return '—'
  try {
    return new Date(dateStr).toLocaleString('en-IN', {
      year:   'numeric',
      month:  'short',
      day:    '2-digit',
      hour:   '2-digit',
      minute: '2-digit',
      hour12: false,
    })
  } catch {
    return dateStr
  }
}

function showError (msg) {
  errorMessage.value = msg
  errorDialog.value  = true
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([loadTransactions(), loadSummary()])
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
.stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}
.stat-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.data-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
.payments-table {
  background: transparent !important;
}
.payments-table :deep(.q-table__container) {
  background: transparent !important;
}
.payments-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #dbeafe;
}
.payments-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}
.payments-table :deep(tr:hover td) {
  background: #eff6ff;
}
.payments-table :deep(.q-table__bottom) {
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}
.txn-id {
  font-family: monospace;
  font-size: 13px;
  color: #1e40af;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
}
.status-badge {
  text-transform: capitalize;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 20px;
}
.order-id-link {
  cursor: pointer;
  text-decoration: underline dotted;
}
.order-id-link:hover {
  color: #1d4ed8;
}
.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.order-txn-row {
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}
</style>