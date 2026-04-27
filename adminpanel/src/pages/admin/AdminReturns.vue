<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Returns</div>
          <div class="text-caption text-blue-7">
            Manage return & refund requests · GET /admin/returns/view
          </div>
        </div>
        <q-chip color="warning" text-color="white" icon="pending" size="sm"
          >Pending: {{ pendingCount }}</q-chip
        >
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- Summary -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md-3" v-for="s in summary" :key="s.label">
          <q-card class="stat-card" flat>
            <q-card-section class="q-pa-md">
              <div class="row items-center q-gutter-sm q-mb-xs">
                <div class="stat-icon" :style="{ background: s.bg }">
                  <q-icon :name="s.icon" :color="s.color" size="18px" />
                </div>
                <span class="text-caption text-blue-7">{{ s.label }}</span>
              </div>
              <div class="text-h5 text-grey-9 text-weight-bold">{{ s.value }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Tabs -->
      <q-tabs
        v-model="tab"
        dense
        align="left"
        active-color="blue-6"
        indicator-color="blue-5"
        class="q-mb-md text-blue-8"
      >
        <q-tab name="all" label="All" />
        <q-tab name="pending" label="Pending" />
        <q-tab name="approved" label="Approved" />
        <q-tab name="rejected" label="Rejected" />
        <q-tab name="refunded" label="Refunded" />
      </q-tabs>

      <!-- Search -->
      <div class="row q-gutter-md q-mb-md">
        <div class="col-12 col-sm-6">
          <q-input
            v-model="search"
            placeholder="Search return ID, order ID or email..."
            dense
            standout="bg-blue-1"
            clearable
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
      </div>

      <q-card class="data-card" flat>
        <q-table
          :rows="filteredReturns"
          :columns="cols"
          row-key="id"
          flat
          :rows-per-page-options="[10, 25]"
          class="ret-table"
          wrap-cells
        >
          <!-- return_id -->
          <template #body-cell-id="props">
            <q-td :props="props"
              ><code class="ret-id">{{ props.value }}</code></q-td
            >
          </template>

          <!-- order_id -->
          <template #body-cell-order_id="props">
            <q-td :props="props"
              ><span class="text-blue-8 text-weight-medium">{{ props.value }}</span></q-td
            >
          </template>

          <!-- customer_email -->
          <template #body-cell-customer_email="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon name="email" size="13px" color="blue-5" />
                <span class="text-caption text-grey-7">{{ props.value }}</span>
              </div>
            </q-td>
          </template>

          <!-- refund_amount -->
          <template #body-cell-refund_amount="props">
            <q-td :props="props">
              <span class="text-green-7 text-weight-bold">₹{{ props.value.toLocaleString() }}</span>
            </q-td>
          </template>

          <!-- reason -->
          <template #body-cell-reason="props">
            <q-td :props="props">
              <div class="reason-text">{{ props.value }}</div>
            </q-td>
          </template>

          <!-- status badge -->
          <template #body-cell-status="props">
            <q-td :props="props">
              <q-chip
                :color="statusColor(props.value)"
                text-color="white"
                dense
                size="sm"
                :icon="statusIcon(props.value)"
              >
                {{ props.value }}
              </q-chip>
            </q-td>
          </template>

          <!-- actions -->
          <template #body-cell-actions="props">
            <q-td :props="props">
              <div v-if="props.row.status === 'pending'" class="row q-gutter-xs no-wrap">
                <q-btn
                  label="Approve"
                  unelevated
                  size="sm"
                  color="positive"
                  no-caps
                  icon="check"
                  @click="openConfirm('approve', props.row)"
                  :loading="props.row.loading"
                />
                <q-btn
                  label="Reject"
                  flat
                  size="sm"
                  color="negative"
                  no-caps
                  icon="close"
                  @click="openConfirm('reject', props.row)"
                />
              </div>
              <div v-else-if="props.row.status === 'approved'" class="row q-gutter-xs no-wrap">
                <q-btn
                  label="Refund"
                  unelevated
                  size="sm"
                  color="blue-6"
                  no-caps
                  icon="currency_rupee"
                  @click="openConfirm('refund', props.row)"
                  :loading="props.row.loading"
                />
              </div>
              <div v-else class="row items-center q-gutter-xs">
                <q-icon
                  :name="props.row.status === 'refunded' ? 'payments' : 'cancel'"
                  :color="statusColor(props.row.status)"
                  size="16px"
                />
                <span class="text-caption" :class="`text-${statusColor(props.row.status)}`">
                  {{ props.row.status }}
                </span>
              </div>
            </q-td>
          </template>

          <template #no-data>
            <div class="full-width column flex-center q-pa-xl text-blue-7">
              <q-icon name="assignment_return" size="48px" class="q-mb-sm" />
              <div>No returns found</div>
            </div>
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- ── Confirmation Dialog ── -->
    <q-dialog v-model="confirmDialog" persistent>
      <q-card class="modal-card" style="width: 420px; max-width: 95vw">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon
            :name="confirmConfig.icon"
            :color="confirmConfig.color"
            size="48px"
            class="q-mb-sm"
          />
          <div class="text-grey-9 text-weight-bold text-subtitle1">{{ confirmConfig.title }}</div>
          <div class="text-caption text-blue-7 text-center q-mt-xs">
            {{ confirmConfig.message }}
          </div>
          <!-- Reject reason input -->
          <q-input
            v-if="confirmAction === 'reject'"
            v-model="rejectReason"
            label="Reason for rejection *"
            standout="bg-blue-1"
            type="textarea"
            rows="2"
            class="full-width q-mt-md"
            :rules="[(v) => !!v || 'Required']"
          />
        </q-card-section>
        <q-card-actions align="center" class="q-pb-md q-gutter-sm">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            :label="confirmConfig.btnLabel"
            :color="confirmConfig.color"
            unelevated
            no-caps
            :loading="actionLoading"
            :disable="confirmAction === 'reject' && !rejectReason"
            @click="executeAction"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ── Toast ── -->
    <q-dialog v-model="toastVisible" :no-backdrop-dismiss="false" position="bottom" seamless>
      <q-card class="toast-card row items-center q-gutter-sm q-pa-md">
        <q-icon :name="toastIcon" :color="toastColor" size="20px" />
        <span class="text-grey-9 text-weight-medium">{{ toastMessage }}</span>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'

const tab = ref('all')
const search = ref('')
const confirmDialog = ref(false)
const confirmAction = ref('')
const confirmTarget = ref(null)
const rejectReason = ref('')
const actionLoading = ref(false)
const toastVisible = ref(false)
const toastMessage = ref('')
const toastIcon = ref('check_circle')
const toastColor = ref('positive')

// ── Data ──────────────────────────────────────────────────────
const returns = ref([
  {
    id: 'RET-001',
    order_id: '#ORD-1001',
    customer_email: 'rahul@example.com',
    product: 'Wireless Earbuds Pro',
    refund_amount: 2400,
    reason: 'Product not working as described',
    status: 'pending',
    created_at: '2024-01-16',
    loading: false,
  },
  {
    id: 'RET-002',
    order_id: '#ORD-1003',
    customer_email: 'ankit@example.com',
    product: 'Running Shoes X1',
    refund_amount: 3499,
    reason: 'Wrong size delivered',
    status: 'approved',
    created_at: '2024-01-15',
    loading: false,
  },
  {
    id: 'RET-003',
    order_id: '#ORD-1005',
    customer_email: 'vikram@example.com',
    product: 'Mechanical Keyboard',
    refund_amount: 5999,
    reason: 'Duplicate order placed by mistake',
    status: 'pending',
    created_at: '2024-01-14',
    loading: false,
  },
  {
    id: 'RET-004',
    order_id: '#ORD-1002',
    customer_email: 'priya@example.com',
    product: 'Cotton T-Shirt',
    refund_amount: 1199,
    reason: 'Quality not as shown in image',
    status: 'rejected',
    created_at: '2024-01-13',
    loading: false,
  },
  {
    id: 'RET-005',
    order_id: '#ORD-1007',
    customer_email: 'karan@example.com',
    product: 'Python Book',
    refund_amount: 499,
    reason: 'Pages missing in book',
    status: 'refunded',
    created_at: '2024-01-12',
    loading: false,
  },
])

// ── Columns — all required fields ─────────────────────────────
const cols = [
  { name: 'id', label: 'Return ID', field: 'id', align: 'left', sortable: true },
  { name: 'order_id', label: 'Order ID', field: 'order_id', align: 'left' },
  { name: 'customer_email', label: 'Customer Email', field: 'customer_email', align: 'left' },
  { name: 'product', label: 'Product', field: 'product', align: 'left' },
  { name: 'reason', label: 'Reason', field: 'reason', align: 'left' },
  {
    name: 'refund_amount',
    label: 'Refund Amount',
    field: 'refund_amount',
    align: 'left',
    sortable: true,
  },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'created_at', label: 'Date', field: 'created_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'id', align: 'left' },
]

// ── Filtered rows ─────────────────────────────────────────────
const filteredReturns = computed(() =>
  returns.value.filter((r) => {
    const ms =
      !search.value ||
      r.id.toLowerCase().includes(search.value.toLowerCase()) ||
      r.order_id.toLowerCase().includes(search.value.toLowerCase()) ||
      r.customer_email.toLowerCase().includes(search.value.toLowerCase())
    return ms && (tab.value === 'all' || r.status === tab.value)
  }),
)

// ── Summary cards ─────────────────────────────────────────────
const pendingCount = computed(() => returns.value.filter((r) => r.status === 'pending').length)
const summary = computed(() => [
  {
    label: 'Total Returns',
    value: returns.value.length,
    icon: 'assignment_return',
    color: 'blue-4',
    bg: 'rgba(59,130,246,.12)',
  },
  {
    label: 'Pending',
    value: pendingCount.value,
    icon: 'pending',
    color: 'amber-4',
    bg: 'rgba(245,158,11,.12)',
  },
  {
    label: 'Approved',
    value: returns.value.filter((r) => r.status === 'approved').length,
    icon: 'check_circle',
    color: 'green-4',
    bg: 'rgba(34,197,94,.12)',
  },
  {
    label: 'Refunded',
    value: returns.value.filter((r) => r.status === 'refunded').length,
    icon: 'payments',
    color: 'purple-4',
    bg: 'rgba(139,92,246,.12)',
  },
])

// ── Helpers ───────────────────────────────────────────────────
const statusColor = (s) =>
  ({ pending: 'warning', approved: 'positive', rejected: 'negative', refunded: 'purple-5' })[s] ||
  'grey'
const statusIcon = (s) =>
  ({ pending: 'schedule', approved: 'check_circle', rejected: 'cancel', refunded: 'payments' })[
    s
  ] || 'help'

// ── Confirm dialog ────────────────────────────────────────────
const confirmConfigs = {
  approve: {
    title: 'Approve Return?',
    message: 'This will approve the return request.',
    icon: 'check_circle',
    color: 'positive',
    btnLabel: 'Approve',
  },
  reject: {
    title: 'Reject Return?',
    message: 'Please provide a reason for rejection.',
    icon: 'cancel',
    color: 'negative',
    btnLabel: 'Reject',
  },
  refund: {
    title: 'Process Refund?',
    message: 'This will initiate a refund to the customer.',
    icon: 'payments',
    color: 'purple-5',
    btnLabel: 'Refund Now',
  },
}
const confirmConfig = computed(() => confirmConfigs[confirmAction.value] || {})

const openConfirm = (action, row) => {
  confirmAction.value = action
  confirmTarget.value = row
  rejectReason.value = ''
  confirmDialog.value = true
}

// Simulates POST /admin/returns/{id}/approve|reject|refund
const executeAction = async () => {
  actionLoading.value = true
  await new Promise((r) => setTimeout(r, 700)) // simulate API call
  const i = returns.value.findIndex((r) => r.id === confirmTarget.value.id)
  if (confirmAction.value === 'approve') returns.value[i].status = 'approved'
  else if (confirmAction.value === 'reject') returns.value[i].status = 'rejected'
  else if (confirmAction.value === 'refund') returns.value[i].status = 'refunded'
  actionLoading.value = false
  confirmDialog.value = false
  showToast(
    confirmAction.value === 'approve'
      ? 'Return approved successfully!'
      : confirmAction.value === 'reject'
        ? 'Return rejected.'
        : 'Refund processed successfully!',
    confirmAction.value === 'reject' ? 'negative' : 'positive',
    confirmAction.value === 'reject' ? 'cancel' : 'check_circle',
  )
}

const showToast = (msg, color = 'positive', icon = 'check_circle') => {
  toastMessage.value = msg
  toastColor.value = color
  toastIcon.value = icon
  toastVisible.value = true
  setTimeout(() => {
    toastVisible.value = false
  }, 3000)
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
.ret-table {
  background: transparent !important;
}
.ret-table :deep(.q-table__container) {
  background: transparent !important;
}
.ret-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #dbeafe;
}
.ret-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}
.ret-table :deep(tr:hover td) {
  background: #eff6ff;
}
.ret-table :deep(.q-table__bottom) {
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}

.ret-id {
  font-family: monospace;
  color: #1e40af;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
}
.reason-text {
  color: #475569;
  font-size: 12px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
.toast-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 260px;
}
</style>
