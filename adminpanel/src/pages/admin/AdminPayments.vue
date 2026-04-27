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
            Approved: {{ approvedTotal }}
          </q-chip>
          <q-chip color="warning" text-color="white" icon="schedule" size="sm">
            Pending: {{ pendingTotal }}
          </q-chip>
        </div>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- ── Payment Summary Card — GET /admin/payments/summary ── -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md-3" v-for="card in paymentSummary" :key="card.label">
          <q-card class="stat-card" flat>
            <q-card-section class="q-pa-md">
              <div class="row items-center q-gutter-sm q-mb-xs">
                <div class="stat-icon" :style="{ background: card.bg }">
                  <q-icon :name="card.icon" :color="card.color" size="18px" />
                </div>
                <div class="text-caption text-blue-7">{{ card.label }}</div>
              </div>
              <div class="text-h5 text-grey-9 text-weight-bold">{{ card.value }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Filters -->
      <div class="row q-gutter-md q-mb-md items-center">
        <div class="col-12 col-sm">
          <q-input
            v-model="search"
            placeholder="Search by transaction ID or order ID..."
            dense
            standout="bg-blue-1"
            clearable
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
        <div class="col-auto">
          <q-btn-toggle
            v-model="statusFilter"
            :options="[
              { label: 'All', value: 'all' },
              { label: 'Pending', value: 'pending' },
              { label: 'Approved', value: 'approved' },
              { label: 'Rejected', value: 'rejected' },
              { label: 'SUCCESS', value: 'SUCCESS' },
              { label: 'FAILED', value: 'FAILED' },
            ]"
            toggle-color="blue-6"
            color="grey-2"
            text-color="blue-8"
            dense
            no-caps
            rounded
          />
        </div>
      </div>

      <!-- ── Payment List — GET /admin/payments/view ── -->
      <q-card class="data-card" flat>
        <q-table
          :rows="filteredTransactions"
          :columns="columns"
          row-key="id"
          flat
          :rows-per-page-options="[10, 25, 50]"
          class="payments-table"
          wrap-cells
        >
          <!-- transaction_id -->
          <template #body-cell-id="props">
            <q-td :props="props"
              ><code class="txn-id">{{ props.value }}</code></q-td
            >
          </template>

          <!-- order_id — click to open GET /admin/payments/{order_id} -->
          <template #body-cell-order_id="props">
            <q-td :props="props">
              <span
                class="text-blue-7 text-weight-medium order-id-link"
                @click="viewOrderPayment(props.value)"
              >
                {{ props.value }}
                <q-icon name="open_in_new" size="11px" class="q-ml-xs" />
              </span>
            </q-td>
          </template>

          <!-- amount -->
          <template #body-cell-amount="props">
            <q-td :props="props">
              <span class="text-green-7 text-weight-bold text-subtitle2"
                >₹{{ props.value.toLocaleString() }}</span
              >
            </q-td>
          </template>

          <!-- method -->
          <template #body-cell-method="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon :name="methodIcon(props.value)" color="blue-5" size="15px" />
                <span class="text-grey-7">{{ props.value }}</span>
              </div>
            </q-td>
          </template>

          <!-- status — SUCCESS / FAILED / pending / approved / rejected -->
          <template #body-cell-status="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon
                  :name="statusIcon(props.value)"
                  :color="statusColor(props.value)"
                  size="14px"
                />
                <q-badge
                  :color="statusColor(props.value)"
                  :label="props.value"
                  class="status-badge"
                />
              </div>
            </q-td>
          </template>

          <!-- date -->
          <template #body-cell-created_at="props">
            <q-td :props="props">
              <span class="text-caption text-grey-6">{{ props.value }}</span>
            </q-td>
          </template>

          <!-- actions -->
          <template #body-cell-actions="props">
            <q-td :props="props">
              <div v-if="props.row.status === 'pending'" class="row q-gutter-xs no-wrap">
                <q-btn
                  label="Approve"
                  color="positive"
                  unelevated
                  no-caps
                  size="sm"
                  icon="check"
                  @click="approveTransaction(props.row)"
                  :loading="props.row.loading"
                />
                <q-btn
                  label="Reject"
                  color="negative"
                  flat
                  no-caps
                  size="sm"
                  icon="close"
                  @click="openRejectDialog(props.row)"
                />
              </div>
              <div
                v-else-if="props.row.status === 'approved' || props.row.status === 'SUCCESS'"
                class="row items-center q-gutter-xs text-positive"
              >
                <q-icon name="verified" size="18px" />
                <span class="text-caption">Approved</span>
              </div>
              <div
                v-else-if="props.row.status === 'FAILED'"
                class="row items-center q-gutter-xs text-negative"
              >
                <q-icon name="error" size="18px" />
                <span class="text-caption">Failed</span>
              </div>
              <div v-else class="row items-center q-gutter-xs text-negative">
                <q-icon name="cancel" size="18px" />
                <span class="text-caption">{{ props.row.reject_reason || 'Rejected' }}</span>
              </div>
            </q-td>
          </template>

          <template #no-data>
            <div class="full-width column flex-center q-pa-xl text-blue-7">
              <q-icon name="account_balance_wallet" size="48px" class="q-mb-sm" />
              <div>No transactions found</div>
            </div>
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- ── Reject Dialog ── -->
    <q-dialog v-model="rejectDialog" persistent>
      <q-card class="modal-card" style="width: 420px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6 text-grey-9 text-weight-bold">Reject Transaction</div>
          <div class="text-caption text-blue-7 q-mt-xs">Transaction: {{ rejectTarget?.id }}</div>
        </q-card-section>
        <q-card-section>
          <q-input
            v-model="rejectReason"
            label="Reason for rejection"
            standout="bg-blue-1"
            type="textarea"
            rows="3"
            autofocus
          />
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Confirm Reject"
            color="negative"
            unelevated
            no-caps
            @click="confirmReject"
            :disable="!rejectReason"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ── Order Payment Details Modal — GET /admin/payments/{order_id} ── -->
    <q-dialog v-model="orderPaymentModal">
      <q-card class="modal-card" style="width: 500px; max-width: 95vw" v-if="orderPaymentData">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Order Payment Details</div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section>
          <div class="text-caption text-blue-7 q-mb-md">
            Order: <strong>{{ selectedOrderId }}</strong>
          </div>
          <div class="detail-grid">
            <div v-for="t in orderPaymentData" :key="t.id" class="order-txn-row">
              <div class="row items-center justify-between">
                <code class="txn-id">{{ t.id }}</code>
                <q-badge :color="statusColor(t.status)" :label="t.status" />
              </div>
              <div class="row items-center justify-between q-mt-xs">
                <div class="row items-center q-gutter-xs">
                  <q-icon :name="methodIcon(t.method)" color="blue-5" size="13px" />
                  <span class="text-caption text-grey-6">{{ t.method }}</span>
                </div>
                <span class="text-green-7 text-weight-bold">₹{{ t.amount.toLocaleString() }}</span>
              </div>
              <div class="text-caption text-grey-5 q-mt-xs">{{ t.created_at }}</div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- ── Approve Snack ── -->
    <q-dialog v-model="approveSnack">
      <q-card class="modal-card" style="width: 300px">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="check_circle" color="positive" size="48px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold">Payment Approved!</div>
          <div class="text-caption text-blue-7 q-mt-xs">
            Transaction has been approved successfully.
          </div>
        </q-card-section>
        <q-card-actions align="center">
          <q-btn label="OK" color="positive" unelevated no-caps v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'

const search = ref('')
const statusFilter = ref('all')
const rejectDialog = ref(false)
const rejectTarget = ref(null)
const rejectReason = ref('')
const approveSnack = ref(false)
const orderPaymentModal = ref(false)
const selectedOrderId = ref('')
const orderPaymentData = ref(null)

// ── Transaction data — GET /admin/payments/view ───────────────
const transactions = ref([
  {
    id: 'TXN-00182',
    order_id: '#ORD-1001',
    amount: 2400,
    status: 'SUCCESS',
    method: 'UPI',
    created_at: '2024-01-15 14:30',
    loading: false,
    reject_reason: '',
  },
  {
    id: 'TXN-00183',
    order_id: '#ORD-1002',
    amount: 1850,
    status: 'pending',
    method: 'Net Banking',
    created_at: '2024-01-15 11:05',
    loading: false,
    reject_reason: '',
  },
  {
    id: 'TXN-00184',
    order_id: '#ORD-1003',
    amount: 3200,
    status: 'pending',
    method: 'Credit Card',
    created_at: '2024-01-14 09:12',
    loading: false,
    reject_reason: '',
  },
  {
    id: 'TXN-00185',
    order_id: '#ORD-1004',
    amount: 960,
    status: 'FAILED',
    method: 'UPI',
    created_at: '2024-01-14 08:00',
    loading: false,
    reject_reason: 'Insufficient funds',
  },
  {
    id: 'TXN-00186',
    order_id: '#ORD-1005',
    amount: 5100,
    status: 'approved',
    method: 'Debit Card',
    created_at: '2024-01-13 16:45',
    loading: false,
    reject_reason: '',
  },
  {
    id: 'TXN-00187',
    order_id: '#ORD-1006',
    amount: 750,
    status: 'pending',
    method: 'Wallet',
    created_at: '2024-01-12 10:22',
    loading: false,
    reject_reason: '',
  },
  {
    id: 'TXN-00188',
    order_id: '#ORD-1007',
    amount: 4200,
    status: 'SUCCESS',
    method: 'UPI',
    created_at: '2024-01-12 09:55',
    loading: false,
    reject_reason: '',
  },
])

// All required columns: transaction_id, order_id, amount, method, status, date
const columns = [
  { name: 'id', label: 'Transaction ID', field: 'id', align: 'left', sortable: true },
  { name: 'order_id', label: 'Order ID', field: 'order_id', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'left', sortable: true },
  { name: 'method', label: 'Method', field: 'method', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'created_at', label: 'Date & Time', field: 'created_at', align: 'left', sortable: true },
  { name: 'actions', label: 'Actions', field: 'id', align: 'left' },
]

const filteredTransactions = computed(() =>
  transactions.value.filter((t) => {
    const ms =
      !search.value ||
      t.id.toLowerCase().includes(search.value.toLowerCase()) ||
      t.order_id.toLowerCase().includes(search.value.toLowerCase())
    const ms2 = statusFilter.value === 'all' || t.status === statusFilter.value
    return ms && ms2
  }),
)

// ── Summary — GET /admin/payments/summary ─────────────────────
const approvedTotal = computed(
  () => transactions.value.filter((t) => t.status === 'approved' || t.status === 'SUCCESS').length,
)
const pendingTotal = computed(() => transactions.value.filter((t) => t.status === 'pending').length)

const paymentSummary = computed(() => [
  {
    label: 'Total Revenue',
    value:
      '₹' +
      transactions.value
        .filter((t) => t.status === 'approved' || t.status === 'SUCCESS')
        .reduce((s, t) => s + t.amount, 0)
        .toLocaleString(),
    icon: 'currency_rupee',
    color: 'green-6',
    bg: 'rgba(34,197,94,0.12)',
  },
  {
    label: 'Pending Amount',
    value:
      '₹' +
      transactions.value
        .filter((t) => t.status === 'pending')
        .reduce((s, t) => s + t.amount, 0)
        .toLocaleString(),
    icon: 'schedule',
    color: 'amber-6',
    bg: 'rgba(245,158,11,0.12)',
  },
  {
    label: 'Approved / SUCCESS',
    value: approvedTotal.value,
    icon: 'check_circle',
    color: 'positive',
    bg: 'rgba(34,197,94,0.12)',
  },
  {
    label: 'Failed / Rejected',
    value: transactions.value.filter((t) => t.status === 'FAILED' || t.status === 'rejected')
      .length,
    icon: 'cancel',
    color: 'negative',
    bg: 'rgba(239,68,68,0.12)',
  },
])

// ── Helpers ───────────────────────────────────────────────────
const statusColor = (s) =>
  ({
    approved: 'positive',
    pending: 'warning',
    rejected: 'negative',
    SUCCESS: 'positive',
    FAILED: 'negative',
  })[s] || 'grey'
const statusIcon = (s) =>
  ({
    approved: 'verified',
    pending: 'schedule',
    rejected: 'cancel',
    SUCCESS: 'check_circle',
    FAILED: 'error',
  })[s] || 'help'
const methodIcon = (m) =>
  ({
    UPI: 'qr_code',
    'Net Banking': 'account_balance',
    'Credit Card': 'credit_card',
    'Debit Card': 'credit_card',
    Wallet: 'account_balance_wallet',
  })[m] || 'payment'

// ── Order Payment Details — GET /admin/payments/{order_id} ────
const viewOrderPayment = (orderId) => {
  selectedOrderId.value = orderId
  orderPaymentData.value = transactions.value.filter((t) => t.order_id === orderId)
  orderPaymentModal.value = true
}

// ── Actions ───────────────────────────────────────────────────
const approveTransaction = (txn) => {
  txn.loading = true
  setTimeout(() => {
    txn.status = 'approved'
    txn.loading = false
    approveSnack.value = true
  }, 800)
}
const openRejectDialog = (txn) => {
  rejectTarget.value = txn
  rejectReason.value = ''
  rejectDialog.value = true
}
const confirmReject = () => {
  rejectTarget.value.status = 'rejected'
  rejectTarget.value.reject_reason = rejectReason.value
  rejectDialog.value = false
}
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
