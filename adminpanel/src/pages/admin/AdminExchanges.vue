<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Exchanges</div>
          <div class="text-caption text-blue-7">
            Manage product exchange requests · GET /admin/exchanges
          </div>
        </div>
        <q-chip color="warning" text-color="white" icon="swap_horiz" size="sm">
          Requested: {{ requestedCount }}
        </q-chip>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- Summary Cards -->
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
        <q-tab name="REQUESTED" label="Requested" />
        <q-tab name="APPROVED" label="Approved" />
        <q-tab name="REJECTED" label="Rejected" />
        <q-tab name="COMPLETED" label="Completed" />
      </q-tabs>

      <!-- Search + Filter -->
      <div class="row q-gutter-md q-mb-md items-center">
        <div class="col-12 col-sm">
          <q-input
            v-model="search"
            placeholder="Search exchange ID, order ID or product..."
            dense
            standout="bg-blue-1"
            clearable
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
      </div>

      <!-- Exchanges Table -->
      <q-card class="data-card" flat>
        <q-table
          :rows="filteredExchanges"
          :columns="cols"
          row-key="id"
          flat
          :rows-per-page-options="[10, 25]"
          class="exch-table"
          wrap-cells
        >
          <!-- exchange_id -->
          <template #body-cell-id="props">
            <q-td :props="props"
              ><code class="exch-id">{{ props.value }}</code></q-td
            >
          </template>

          <!-- order_id -->
          <template #body-cell-order_id="props">
            <q-td :props="props">
              <span class="text-blue-8 text-weight-medium">{{ props.value }}</span>
            </q-td>
          </template>

          <!-- product -->
          <template #body-cell-product="props">
            <q-td :props="props">
              <div class="text-grey-9 text-weight-medium">{{ props.value }}</div>
            </q-td>
          </template>

          <!-- old_variant → new_variant -->
          <template #body-cell-old_variant="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs no-wrap">
                <q-chip size="xs" color="red-1" text-color="red-8" dense>{{ props.value }}</q-chip>
                <q-icon name="arrow_forward" size="14px" color="blue-4" />
                <q-chip size="xs" color="green-1" text-color="green-8" dense>{{
                  props.row.new_variant
                }}</q-chip>
              </div>
            </q-td>
          </template>

          <!-- status badge -->
          <template #body-cell-status="props">
            <q-td :props="props">
              <q-chip
                :color="statusColor(props.value)"
                text-color="white"
                :icon="statusIcon(props.value)"
                dense
                size="sm"
              >
                {{ props.value }}
              </q-chip>
            </q-td>
          </template>

          <!-- date -->
          <template #body-cell-created_at="props">
            <q-td :props="props">
              <span class="text-caption text-grey-6">{{ props.value }}</span>
            </q-td>
          </template>

          <!-- Actions -->
          <template #body-cell-actions="props">
            <q-td :props="props">
              <!-- REQUESTED → approve / reject via PUT /admin/exchanges/{id}/status -->
              <div
                v-if="props.row.status === 'REQUESTED'"
                class="row q-gutter-xs no-wrap items-center"
              >
                <q-select
                  v-model="props.row._pendingStatus"
                  :options="['APPROVED', 'REJECTED']"
                  dense
                  standout="bg-blue-1"
                  style="min-width: 120px"
                  label="Update status"
                  @update:model-value="openStatusConfirm(props.row)"
                />
              </div>

              <!-- APPROVED → complete via POST /admin/exchanges/{id}/complete -->
              <div v-else-if="props.row.status === 'APPROVED'" class="row q-gutter-xs no-wrap">
                <q-btn
                  label="Complete Exchange"
                  unelevated
                  size="sm"
                  color="blue-6"
                  no-caps
                  icon="check_circle"
                  @click="openCompleteConfirm(props.row)"
                  :loading="props.row.loading"
                />
              </div>

              <!-- COMPLETED / REJECTED -->
              <div v-else class="row items-center q-gutter-xs">
                <q-icon
                  :name="props.row.status === 'COMPLETED' ? 'task_alt' : 'cancel'"
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
              <q-icon name="swap_horiz" size="48px" class="q-mb-sm" />
              <div>No exchanges found</div>
            </div>
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- ── Status Update Confirmation Modal (PUT /admin/exchanges/{id}/status) ── -->
    <q-dialog v-model="statusConfirmDialog" persistent>
      <q-card class="modal-card" style="width: 420px; max-width: 95vw">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon
            :name="pendingNewStatus === 'APPROVED' ? 'check_circle' : 'cancel'"
            :color="pendingNewStatus === 'APPROVED' ? 'positive' : 'negative'"
            size="48px"
            class="q-mb-sm"
          />
          <div class="text-grey-9 text-weight-bold text-subtitle1">
            {{ pendingNewStatus === 'APPROVED' ? 'Approve Exchange?' : 'Reject Exchange?' }}
          </div>
          <div class="text-caption text-blue-7 text-center q-mt-xs">
            Exchange <strong>{{ actionTarget?.id }}</strong> will be marked as
            <strong>{{ pendingNewStatus }}</strong
            >.
          </div>
          <q-input
            v-if="pendingNewStatus === 'REJECTED'"
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
          <q-btn label="Cancel" flat no-caps @click="cancelStatusChange" color="blue-4" />
          <q-btn
            :label="pendingNewStatus === 'APPROVED' ? 'Yes, Approve' : 'Yes, Reject'"
            :color="pendingNewStatus === 'APPROVED' ? 'positive' : 'negative'"
            unelevated
            no-caps
            :loading="actionLoading"
            :disable="pendingNewStatus === 'REJECTED' && !rejectReason"
            @click="executeStatusUpdate"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ── Complete Exchange Confirmation (POST /admin/exchanges/{id}/complete) ── -->
    <q-dialog v-model="completeConfirmDialog" persistent>
      <q-card class="modal-card" style="width: 420px; max-width: 95vw">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="task_alt" color="blue-6" size="48px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold text-subtitle1">Complete Exchange?</div>
          <div class="text-caption text-blue-7 text-center q-mt-xs">
            This will mark exchange <strong>{{ actionTarget?.id }}</strong> as completed and confirm
            the new variant has been dispatched.
          </div>
          <div v-if="actionTarget" class="exchange-preview q-mt-md">
            <div class="text-caption text-blue-7 q-mb-xs">Exchange summary</div>
            <div class="row items-center q-gutter-xs">
              <q-chip size="sm" color="red-1" text-color="red-8">{{
                actionTarget.old_variant
              }}</q-chip>
              <q-icon name="arrow_forward" size="15px" color="blue-5" />
              <q-chip size="sm" color="green-1" text-color="green-8">{{
                actionTarget.new_variant
              }}</q-chip>
            </div>
            <div class="text-caption text-grey-6 q-mt-xs">Product: {{ actionTarget.product }}</div>
          </div>
        </q-card-section>
        <q-card-actions align="center" class="q-pb-md q-gutter-sm">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Complete Exchange"
            color="blue-6"
            unelevated
            no-caps
            icon="task_alt"
            :loading="actionLoading"
            @click="executeComplete"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ── Toast Notification ── -->
    <q-dialog v-model="toastVisible" position="bottom" seamless>
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
const statusConfirmDialog = ref(false)
const completeConfirmDialog = ref(false)
const actionTarget = ref(null)
const pendingNewStatus = ref('')
const rejectReason = ref('')
const actionLoading = ref(false)
const toastVisible = ref(false)
const toastMessage = ref('')
const toastIcon = ref('check_circle')
const toastColor = ref('positive')

// ── Exchange data — GET /admin/exchanges ───────────────────────
const exchanges = ref([
  {
    id: 'EXC-001',
    order_id: '#ORD-1001',
    product: 'Wireless Earbuds Pro',
    old_variant: 'Black',
    new_variant: 'White',
    status: 'REQUESTED',
    created_at: '2024-01-16',
    loading: false,
    _pendingStatus: '',
  },
  {
    id: 'EXC-002',
    order_id: '#ORD-1002',
    product: 'Cotton T-Shirt Classic',
    old_variant: 'S - Blue',
    new_variant: 'M - Red',
    status: 'APPROVED',
    created_at: '2024-01-15',
    loading: false,
    _pendingStatus: '',
  },
  {
    id: 'EXC-003',
    order_id: '#ORD-1003',
    product: 'Running Shoes X1',
    old_variant: 'Size 7',
    new_variant: 'Size 8',
    status: 'COMPLETED',
    created_at: '2024-01-14',
    loading: false,
    _pendingStatus: '',
  },
  {
    id: 'EXC-004',
    order_id: '#ORD-1004',
    product: 'Mechanical Keyboard',
    old_variant: 'Brown MX',
    new_variant: 'Red MX',
    status: 'REJECTED',
    created_at: '2024-01-13',
    loading: false,
    _pendingStatus: '',
  },
  {
    id: 'EXC-005',
    order_id: '#ORD-1006',
    product: 'Cotton T-Shirt Classic',
    old_variant: 'L - White',
    new_variant: 'XL - White',
    status: 'REQUESTED',
    created_at: '2024-01-12',
    loading: false,
    _pendingStatus: '',
  },
  {
    id: 'EXC-006',
    order_id: '#ORD-1007',
    product: 'Wireless Earbuds Pro',
    old_variant: 'White',
    new_variant: 'Black',
    status: 'APPROVED',
    created_at: '2024-01-11',
    loading: false,
    _pendingStatus: '',
  },
])

// ── Columns — exchange_id, order_id, product, old_variant, new_variant, status ──
const cols = [
  { name: 'id', label: 'Exchange ID', field: 'id', align: 'left', sortable: true },
  { name: 'order_id', label: 'Order ID', field: 'order_id', align: 'left' },
  { name: 'product', label: 'Product', field: 'product', align: 'left' },
  { name: 'old_variant', label: 'Variant Change', field: 'old_variant', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'created_at', label: 'Date', field: 'created_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'id', align: 'left' },
]

// ── Filtered ──────────────────────────────────────────────────
const filteredExchanges = computed(() =>
  exchanges.value.filter((e) => {
    const ms =
      !search.value ||
      e.id.toLowerCase().includes(search.value.toLowerCase()) ||
      e.order_id.toLowerCase().includes(search.value.toLowerCase()) ||
      e.product.toLowerCase().includes(search.value.toLowerCase())
    return ms && (tab.value === 'all' || e.status === tab.value)
  }),
)

// ── Summary ───────────────────────────────────────────────────
const requestedCount = computed(
  () => exchanges.value.filter((e) => e.status === 'REQUESTED').length,
)
const summary = computed(() => [
  {
    label: 'Total',
    value: exchanges.value.length,
    icon: 'swap_horiz',
    color: 'blue-4',
    bg: 'rgba(59,130,246,.12)',
  },
  {
    label: 'Requested',
    value: requestedCount.value,
    icon: 'pending',
    color: 'amber-6',
    bg: 'rgba(245,158,11,.12)',
  },
  {
    label: 'Approved',
    value: exchanges.value.filter((e) => e.status === 'APPROVED').length,
    icon: 'check_circle',
    color: 'green-6',
    bg: 'rgba(34,197,94,.12)',
  },
  {
    label: 'Completed',
    value: exchanges.value.filter((e) => e.status === 'COMPLETED').length,
    icon: 'task_alt',
    color: 'blue-6',
    bg: 'rgba(59,130,246,.12)',
  },
])

// ── Helpers ───────────────────────────────────────────────────
const statusColor = (s) =>
  ({ REQUESTED: 'warning', APPROVED: 'positive', REJECTED: 'negative', COMPLETED: 'info' })[s] ||
  'grey'
const statusIcon = (s) =>
  ({ REQUESTED: 'schedule', APPROVED: 'check_circle', REJECTED: 'cancel', COMPLETED: 'task_alt' })[
    s
  ] || 'help'

// ── Status update — PUT /admin/exchanges/{id}/status ─────────
const openStatusConfirm = (row) => {
  if (!row._pendingStatus) return
  actionTarget.value = row
  pendingNewStatus.value = row._pendingStatus
  rejectReason.value = ''
  statusConfirmDialog.value = true
}

const cancelStatusChange = () => {
  // Reset the dropdown
  const i = exchanges.value.findIndex((e) => e.id === actionTarget.value?.id)
  if (i >= 0) exchanges.value[i]._pendingStatus = ''
  statusConfirmDialog.value = false
}

const executeStatusUpdate = async () => {
  actionLoading.value = true
  await new Promise((r) => setTimeout(r, 700))
  const i = exchanges.value.findIndex((e) => e.id === actionTarget.value.id)
  exchanges.value[i].status = pendingNewStatus.value
  exchanges.value[i]._pendingStatus = ''
  actionLoading.value = false
  statusConfirmDialog.value = false
  showToast(
    pendingNewStatus.value === 'APPROVED'
      ? `Exchange ${actionTarget.value.id} approved!`
      : `Exchange ${actionTarget.value.id} rejected.`,
    pendingNewStatus.value === 'APPROVED' ? 'positive' : 'negative',
    pendingNewStatus.value === 'APPROVED' ? 'check_circle' : 'cancel',
  )
}

// ── Complete exchange — POST /admin/exchanges/{id}/complete ───
const openCompleteConfirm = (row) => {
  actionTarget.value = row
  completeConfirmDialog.value = true
}

const executeComplete = async () => {
  actionLoading.value = true
  await new Promise((r) => setTimeout(r, 700))
  const i = exchanges.value.findIndex((e) => e.id === actionTarget.value.id)
  exchanges.value[i].status = 'COMPLETED'
  exchanges.value[i].loading = false
  actionLoading.value = false
  completeConfirmDialog.value = false
  showToast(`Exchange ${actionTarget.value.id} completed successfully!`, 'positive', 'task_alt')
}

// ── Toast ─────────────────────────────────────────────────────
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

/* ── Summary cards ── */
.stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: box-shadow 0.2s;
}
.stat-card:hover {
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
}
.stat-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Table ── */
.data-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
.exch-table {
  background: transparent !important;
}
.exch-table :deep(.q-table__container) {
  background: transparent !important;
}
.exch-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #dbeafe;
}
.exch-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}
.exch-table :deep(tr:hover td) {
  background: #eff6ff;
}
.exch-table :deep(.q-table__bottom) {
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}

/* ── Badges / codes ── */
.exch-id {
  font-family: monospace;
  color: #1e40af;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
}

/* ── Modals ── */
.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
.exchange-preview {
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 10px;
  padding: 12px 16px;
}

/* ── Toast ── */
.toast-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 260px;
}
</style>
