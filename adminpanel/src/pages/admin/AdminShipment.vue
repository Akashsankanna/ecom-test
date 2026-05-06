<template>
  <q-page class="admin-page">

    <!-- ── Page header ──────────────────────────────────────────────── -->
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Shipments</div>
          <div class="text-caption text-blue-7">Track and manage order shipments</div>
        </div>
        <div class="row q-gutter-sm">
          <q-btn
            flat
            round
            icon="refresh"
            color="blue-5"
            :loading="loading"
            @click="loadAll"
          >
            <q-tooltip>Refresh</q-tooltip>
          </q-btn>
          <q-btn
            label="Add Shipment"
            color="blue-6"
            unelevated
            no-caps
            icon="add"
            @click="openCreateModal"
          />
        </div>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">

      <!-- ── Stats ──────────────────────────────────────────────────── -->
      <div class="row q-gutter-md q-mb-lg">
        <div
          v-for="s in summaryCards"
          :key="s.label"
          class="col-12 col-sm-6 col-md-2"
        >
          <q-card class="stat-card" flat>
            <q-card-section class="q-pa-md">
              <div class="row items-center q-gutter-sm q-mb-xs">
                <div class="stat-icon" :style="{ background: s.bg }">
                  <q-icon :name="s.icon" :color="s.color" size="18px" />
                </div>
                <span class="text-caption text-blue-7">{{ s.label }}</span>
              </div>
              <div class="text-h5 text-grey-9 text-weight-bold">
                <q-skeleton v-if="statsLoading" type="text" width="40px" />
                <span v-else>{{ s.value }}</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- ── Tabs ───────────────────────────────────────────────────── -->
      <q-tabs
        v-model="activeTab"
        dense
        align="left"
        active-color="blue-6"
        indicator-color="blue-5"
        class="q-mb-md text-blue-8"
      >
        <q-tab name="ALL"             label="All" />
        <q-tab name="PENDING"         label="Pending" />
        <q-tab name="SHIPPED"         label="Shipped" />
        <q-tab name="OUT_FOR_DELIVERY" label="Out for Delivery" />
        <q-tab name="DELIVERED"       label="Delivered" />
        <q-tab name="FAILED"          label="Failed" />
        <q-tab name="RETURNED"        label="Returned" />
      </q-tabs>

      <!-- ── Search ─────────────────────────────────────────────────── -->
      <div class="row q-gutter-md q-mb-md">
        <div class="col-12 col-sm-6">
          <q-input
            v-model="search"
            placeholder="Search tracking, order ID, courier…"
            dense
            standout="bg-blue-1"
            clearable
            @clear="search = ''"
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
      </div>

      <!-- ── Error banner ───────────────────────────────────────────── -->
      <q-banner
        v-if="loadError"
        rounded
        class="bg-red-1 text-negative q-mb-md"
        icon="error"
        dense
      >
        {{ loadError }}
        <template #action>
          <q-btn flat label="Retry" @click="loadAll" />
        </template>
      </q-banner>

      <!-- ── Table ──────────────────────────────────────────────────── -->
      <q-card class="data-card" flat>
        <q-table
          :rows="filteredShipments"
          :columns="columns"
          row-key="id"
          flat
          :loading="loading"
          :rows-per-page-options="[10, 25, 50]"
          class="ship-table"
          wrap-cells
        >
          <!-- Shipment ID -->
          <template #body-cell-id="props">
            <q-td :props="props">
              <code class="ship-id">SHP-{{ String(props.value).padStart(4, '0') }}</code>
            </q-td>
          </template>

          <!-- Order ID -->
          <template #body-cell-order_id="props">
            <q-td :props="props">
              <span class="text-blue-8 text-weight-medium">#ORD-{{ props.value }}</span>
            </q-td>
          </template>

          <!-- Tracking number -->
          <template #body-cell-tracking_number="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs no-wrap">
                <span class="tracking-num">{{ props.value }}</span>
                <q-btn
                  round flat size="xs"
                  icon="content_copy"
                  color="blue-4"
                  @click="copyToClipboard(props.value)"
                >
                  <q-tooltip>Copy</q-tooltip>
                </q-btn>
              </div>
            </q-td>
          </template>

          <!-- Courier -->
          <template #body-cell-courier_name="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon name="local_shipping" size="14px" color="blue-5" />
                <span class="text-grey-8">{{ props.value }}</span>
              </div>
            </q-td>
          </template>

          <!-- Status -->
          <template #body-cell-shipment_status="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon
                  :name="STATUS_ICONS[props.value]"
                  :color="STATUS_COLORS[props.value]"
                  size="14px"
                />
                <q-badge
                  :color="STATUS_COLORS[props.value]"
                  :label="STATUS_LABELS[props.value]"
                />
              </div>
            </q-td>
          </template>

          <!-- Estimated delivery -->
          <template #body-cell-estimated_delivery="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon name="event" size="13px" color="blue-5" />
                <span class="text-caption text-grey-7">{{ props.value || '—' }}</span>
              </div>
            </q-td>
          </template>

          <!-- Delivered at -->
          <template #body-cell-delivered_at="props">
            <q-td :props="props">
              <span class="text-caption text-grey-7">
                {{ props.value ? formatDateTime(props.value) : '—' }}
              </span>
            </q-td>
          </template>

          <!-- Actions -->
          <template #body-cell-actions="props">
            <q-td :props="props">
              <div class="row q-gutter-xs no-wrap">
                <!-- Update status — disabled for terminal states -->
                <q-btn
                  round flat size="sm"
                  icon="edit"
                  color="blue-4"
                  :disable="isTerminalStatus(props.row.shipment_status)"
                  @click="openUpdateModal(props.row)"
                >
                  <q-tooltip>
                    {{
                      isTerminalStatus(props.row.shipment_status)
                        ? `Status '${STATUS_LABELS[props.row.shipment_status]}' is final`
                        : 'Update Status'
                    }}
                  </q-tooltip>
                </q-btn>

                <!-- View detail -->
                <q-btn
                  round flat size="sm"
                  icon="visibility"
                  color="cyan-7"
                  @click="openDetailModal(props.row)"
                >
                  <q-tooltip>View Details</q-tooltip>
                </q-btn>
              </div>
            </q-td>
          </template>

          <!-- Empty state -->
          <template #no-data>
            <div class="full-width column flex-center q-pa-xl text-blue-7">
              <q-icon name="local_shipping" size="48px" class="q-mb-sm" />
              <div>No shipments found</div>
            </div>
          </template>

          <!-- Loading state -->
          <template #loading>
            <q-inner-loading showing color="blue-5" />
          </template>
        </q-table>
      </q-card>
    </div>


    <!-- ════════════════════════════════════════════════════════════════
         CREATE SHIPMENT MODAL
         POST /admin/orders/{order_id}/shipment
         ════════════════════════════════════════════════════════════ -->
    <q-dialog v-model="createModal" persistent>
      <q-card class="modal-card" style="width: 520px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Add Shipment</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>

        <q-card-section>
          <q-form ref="createFormRef" class="column q-gutter-md">

            <q-input
              v-model.number="createForm.order_id"
              label="Order ID *"
              standout="bg-blue-1"
              dense
              type="number"
              :rules="[v => !!v || 'Order ID is required']"
            />

            <q-select
              v-model="createForm.courier_name"
              :options="COURIER_OPTIONS"
              label="Courier Name *"
              standout="bg-blue-1"
              dense
              use-input
              input-debounce="0"
              @filter="courierFilter"
              :rules="[v => !!v || 'Courier is required']"
            >
              <template #no-option>
                <q-item>
                  <q-item-section class="text-grey">No results</q-item-section>
                </q-item>
              </template>
            </q-select>

            <q-input
              v-model="createForm.tracking_number"
              label="Tracking Number *"
              standout="bg-blue-1"
              dense
              :rules="[v => !!v || 'Tracking number is required']"
            />

            <q-input
              v-model="createForm.estimated_delivery"
              label="Estimated Delivery Date"
              type="date"
              standout="bg-blue-1"
              dense
            />

            <q-input
              v-model="createForm.tracking_url"
              label="Tracking URL (optional)"
              standout="bg-blue-1"
              dense
              type="url"
              placeholder="https://…"
            />

            <q-banner
              v-if="createError"
              dense rounded
              class="bg-red-1 text-negative"
              icon="error"
            >
              {{ createError }}
            </q-banner>
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Create Shipment"
            color="blue-6"
            unelevated no-caps
            :loading="saving"
            @click="submitCreate"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>


    <!-- ════════════════════════════════════════════════════════════════
         UPDATE STATUS MODAL
         PUT /admin/shipments/{tracking_number}
         ════════════════════════════════════════════════════════════ -->
    <q-dialog v-model="updateModal" persistent>
      <q-card class="modal-card" style="width: 440px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Update Shipment Status</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>

        <q-card-section v-if="updateTarget">
          <div class="column q-gutter-md">

            <!-- Current info -->
            <div class="detail-row">
              <span class="detail-label">Tracking Number</span>
              <code class="tracking-num">{{ updateTarget.tracking_number }}</code>
            </div>
            <div class="detail-row">
              <span class="detail-label">Current Status</span>
              <q-badge
                :color="STATUS_COLORS[updateTarget.shipment_status]"
                :label="STATUS_LABELS[updateTarget.shipment_status]"
              />
            </div>

            <q-separator />

            <!-- New status -->
            <q-select
              v-model="updateForm.status"
              :options="availableNextStatuses"
              label="New Status *"
              standout="bg-blue-1"
              dense
              emit-value map-options
              :rules="[v => !!v || 'Status is required']"
            >
              <template #option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section avatar>
                    <q-icon
                      :name="STATUS_ICONS[scope.opt.value]"
                      :color="STATUS_COLORS[scope.opt.value]"
                    />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ scope.opt.label }}</q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-select>

            <!-- Delivery note -->
            <q-banner
              v-if="updateForm.status === 'DELIVERED'"
              dense rounded
              class="bg-green-1 text-positive"
              icon="info"
            >
              Setting to DELIVERED will automatically update the linked order status.
            </q-banner>

            <q-banner
              v-if="updateError"
              dense rounded
              class="bg-red-1 text-negative"
              icon="error"
            >
              {{ updateError }}
            </q-banner>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Update Status"
            color="blue-6"
            unelevated no-caps
            :loading="saving"
            :disable="!updateForm.status"
            @click="submitUpdate"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>


    <!-- ════════════════════════════════════════════════════════════════
         DETAIL MODAL
         GET /admin/orders/{order_id}/shipment
         ════════════════════════════════════════════════════════════ -->
    <q-dialog v-model="detailModal">
      <q-card class="modal-card" style="width: 500px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Shipment Details</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>

        <q-card-section v-if="detailTarget">
          <q-inner-loading :showing="detailLoading" color="blue-5" />

          <div class="detail-grid q-mb-md">
            <div
              v-for="f in detailFields"
              :key="f.key"
              class="detail-row"
            >
              <div class="detail-label">
                <q-icon :name="f.icon" size="13px" color="blue-5" class="q-mr-xs" />
                {{ f.label }}
              </div>
              <div class="detail-value">{{ resolveField(detailTarget, f) }}</div>
            </div>

            <!-- Status badge row -->
            <div class="detail-row">
              <div class="detail-label">
                <q-icon name="info" size="13px" color="blue-5" class="q-mr-xs" />
                Status
              </div>
              <q-badge
                :color="STATUS_COLORS[detailTarget.shipment_status]"
                :label="STATUS_LABELS[detailTarget.shipment_status]"
              />
            </div>
          </div>

          <!-- Tracking URL link -->
          <div v-if="detailTarget.tracking_url" class="q-mb-md">
            <q-btn
              flat dense no-caps
              icon="open_in_new"
              color="blue-5"
              label="Open Tracking Page"
              :href="detailTarget.tracking_url"
              target="_blank"
            />
          </div>

          <!-- Timeline -->
          <div class="text-caption text-blue-7 text-weight-bold text-uppercase q-mb-sm">
            Status Timeline
          </div>
          <q-timeline color="blue" dense>
            <q-timeline-entry
              v-for="step in buildTimeline(detailTarget)"
              :key="step.status"
              :title="STATUS_LABELS[step.status]"
              :subtitle="step.time"
              :color="step.active ? STATUS_COLORS[step.status] : 'grey-4'"
              :icon="step.active ? STATUS_ICONS[step.status] : 'radio_button_unchecked'"
            />
          </q-timeline>
        </q-card-section>
      </q-card>
    </q-dialog>


    <!-- ── Toast notification ────────────────────────────────────────── -->
    <q-dialog v-model="toastVisible" position="bottom" seamless>
      <q-card class="toast-card row items-center q-gutter-sm q-pa-md">
        <q-icon
          :name="toastType === 'error' ? 'error' : 'check_circle'"
          :color="toastType === 'error' ? 'negative' : 'positive'"
          size="20px"
        />
        <span class="text-grey-9 text-weight-medium">{{ toastMessage }}</span>
      </q-card>
    </q-dialog>

  </q-page>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import shipmentService, {
  // SHIPMENT_STATUSES,
  STATUS_LABELS,
  STATUS_COLORS,
  STATUS_ICONS,
  COURIER_OPTIONS,
  // VALID_TRANSITIONS,
} from 'src/services/shipmentService.js'

// ── State ────────────────────────────────────────────────────────────────────
const shipments    = ref([])
const stats        = ref({})
const loading      = ref(false)
const statsLoading = ref(false)
const loadError    = ref('')

const activeTab = ref('ALL')
const search    = ref('')

// Create modal
const createModal   = ref(false)
const createFormRef = ref(null)
const createError   = ref('')
const saving        = ref(false)
const createForm    = ref(emptyCreateForm())

// Update modal
const updateModal  = ref(false)
const updateTarget = ref(null)
const updateForm   = ref({ status: '' })
const updateError  = ref('')

// Detail modal
const detailModal   = ref(false)
const detailTarget  = ref(null)
const detailLoading = ref(false)

// Toast
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType    = ref('success')

// Courier filter (for q-select use-input)
const courierFilteredOptions = ref([...COURIER_OPTIONS])

// ── Helpers ──────────────────────────────────────────────────────────────────
function emptyCreateForm () {
  return {
    order_id:           '',
    courier_name:       '',
    tracking_number:    '',
    estimated_delivery: '',
    tracking_url:       '',
  }
}

function isTerminalStatus (s) {
  return shipmentService.isTerminalStatus(s)
}

function getValidNextStatuses (s) {
  return shipmentService.getValidNextStatuses(s)
}

function formatDateTime (dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', {
    day:    '2-digit',
    month:  'short',
    year:   'numeric',
    hour:   '2-digit',
    minute: '2-digit',
  })
}

function copyToClipboard (text) {
  navigator.clipboard?.writeText(text)
  showToast('Tracking number copied!', 'success')
}

function showToast (msg, type = 'success') {
  toastMessage.value = msg
  toastType.value    = type
  toastVisible.value = true
  setTimeout(() => { toastVisible.value = false }, 3000)
}

function resolveField (obj, f) {
  const val = obj[f.key]
  if (val === null || val === undefined || val === '') return '—'
  if (f.isDate) return val
  if (f.isDateTime) return formatDateTime(val)
  return val
}

// ── Computed ─────────────────────────────────────────────────────────────────
const summaryCards = computed(() => [
  {
    label: 'Total',
    value: stats.value.total ?? 0,
    icon: 'local_shipping', color: 'blue-4', bg: 'rgba(59,130,246,.12)',
  },
  {
    label: 'Pending',
    value: stats.value.pending ?? 0,
    icon: 'schedule', color: 'amber-7', bg: 'rgba(245,158,11,.12)',
  },
  {
    label: 'Shipped',
    value: stats.value.shipped ?? 0,
    icon: 'local_shipping', color: 'cyan-5', bg: 'rgba(6,182,212,.12)',
  },
  {
    label: 'Out for Delivery',
    value: stats.value.out_for_delivery ?? 0,
    icon: 'two_wheeler', color: 'purple-5', bg: 'rgba(139,92,246,.12)',
  },
  {
    label: 'Delivered',
    value: stats.value.delivered ?? 0,
    icon: 'check_circle', color: 'green-5', bg: 'rgba(34,197,94,.12)',
  },
  {
    label: 'Failed',
    value: stats.value.failed ?? 0,
    icon: 'error', color: 'red-4', bg: 'rgba(239,68,68,.12)',
  },
])

const filteredShipments = computed(() => {
  const term = (search.value || '').toLowerCase()
  return shipments.value.filter(s => {
    // Tab filter
    if (activeTab.value !== 'ALL' && s.shipment_status !== activeTab.value) return false
    // Search filter
    if (term) {
      const hay = [
        String(s.id),
        String(s.order_id),
        (s.tracking_number || '').toLowerCase(),
        (s.courier_name    || '').toLowerCase(),
      ].join(' ')
      if (!hay.includes(term)) return false
    }
    return true
  })
})

const availableNextStatuses = computed(() => {
  if (!updateTarget.value) return []
  return getValidNextStatuses(updateTarget.value.shipment_status).map(s => ({
    label: STATUS_LABELS[s],
    value: s,
  }))
})

// ── Table columns ─────────────────────────────────────────────────────────────
const columns = [
  { name: 'id',                 label: 'Shipment ID',    field: 'id',                 align: 'left', sortable: true },
  { name: 'order_id',           label: 'Order ID',       field: 'order_id',           align: 'left', sortable: true },
  { name: 'courier_name',       label: 'Courier',        field: 'courier_name',       align: 'left' },
  { name: 'tracking_number',    label: 'Tracking No.',   field: 'tracking_number',    align: 'left' },
  { name: 'shipment_status',    label: 'Status',         field: 'shipment_status',    align: 'left', sortable: true },
  { name: 'estimated_delivery', label: 'Est. Delivery',  field: 'estimated_delivery', align: 'left' },
  { name: 'delivered_at',       label: 'Delivered At',   field: 'delivered_at',       align: 'left' },
  { name: 'actions',            label: '',               field: 'id',                 align: 'left' },
]

// ── Detail fields config ──────────────────────────────────────────────────────
const detailFields = [
  { key: 'id',                 label: 'Shipment ID',    icon: 'tag' },
  { key: 'order_id',           label: 'Order ID',       icon: 'receipt' },
  { key: 'tracking_number',    label: 'Tracking No.',   icon: 'qr_code' },
  { key: 'courier_name',       label: 'Courier',        icon: 'local_shipping' },
  { key: 'estimated_delivery', label: 'Est. Delivery',  icon: 'event',       isDate: true },
  { key: 'shipped_at',         label: 'Shipped At',     icon: 'flight_takeoff', isDateTime: true },
  { key: 'delivered_at',       label: 'Delivered At',   icon: 'done_all',    isDateTime: true },
  { key: 'created_at',         label: 'Created At',     icon: 'schedule',    isDateTime: true },
]

// ── Timeline builder ─────────────────────────────────────────────────────────
const STATUS_ORDER = ['PENDING', 'SHIPPED', 'OUT_FOR_DELIVERY', 'DELIVERED']

function buildTimeline (shipment) {
  const current = shipment.shipment_status
  const isSpecial = ['FAILED', 'RETURNED'].includes(current)

  const base = STATUS_ORDER.map(s => ({
    status: s,
    time:   '',
    active: false,
  }))

  // Mark reached steps
  const idx = STATUS_ORDER.indexOf(current)
  base.forEach((step, i) => {
    if (i <= idx) step.active = true
  })

  // Timestamps
  if (shipment.shipped_at)    base[1].time = formatDateTime(shipment.shipped_at)
  if (shipment.delivered_at)  base[3].time = formatDateTime(shipment.delivered_at)

  if (isSpecial) {
    base.push({ status: current, time: '', active: true })
  }

  return base
}

// ── Data loading ─────────────────────────────────────────────────────────────
async function loadShipments () {
  loading.value  = true
  loadError.value = ''
  try {
    const data = await shipmentService.getAllShipments({ limit: 200 })
    // API returns array directly (List[ShipmentListItem])
    shipments.value = Array.isArray(data) ? data : (data.items ?? data.shipments ?? [])
  } catch (err) {
    loadError.value = err.message || 'Failed to load shipments'
  } finally {
    loading.value = false
  }
}

async function loadStats () {
  statsLoading.value = true
  try {
    stats.value = await shipmentService.getShipmentStats()
  } catch {
    // Stats non-critical — silently ignore
  } finally {
    statsLoading.value = false
  }
}

async function loadAll () {
  await Promise.all([loadShipments(), loadStats()])
}

onMounted(loadAll)

// ── Courier select filter ─────────────────────────────────────────────────────
function courierFilter (val, update) {
  update(() => {
    if (!val) {
      courierFilteredOptions.value = [...COURIER_OPTIONS]
    } else {
      const needle = val.toLowerCase()
      courierFilteredOptions.value = COURIER_OPTIONS.filter(o =>
        o.toLowerCase().includes(needle)
      )
    }
  })
}

// ── Create modal ─────────────────────────────────────────────────────────────
function openCreateModal () {
  createForm.value  = emptyCreateForm()
  createError.value = ''
  createModal.value = true
}

async function submitCreate () {
  const valid = await createFormRef.value?.validate()
  if (!valid) return

  saving.value       = true
  createError.value  = ''
  try {
    const payload = {
      courier_name:       createForm.value.courier_name,
      tracking_number:    createForm.value.tracking_number,
      estimated_delivery: createForm.value.estimated_delivery || undefined,
      tracking_url:       createForm.value.tracking_url       || undefined,
    }
    await shipmentService.createShipment(createForm.value.order_id, payload)
    createModal.value = false
    showToast('Shipment created successfully!')
    await loadAll()
  } catch (err) {
    createError.value = err.message || 'Failed to create shipment'
  } finally {
    saving.value = false
  }
}

// ── Update modal ──────────────────────────────────────────────────────────────
function openUpdateModal (row) {
  updateTarget.value = row
  updateForm.value   = { status: '' }
  updateError.value  = ''
  updateModal.value  = true
}

async function submitUpdate () {
  if (!updateForm.value.status) return

  saving.value      = true
  updateError.value = ''
  try {
    await shipmentService.updateShipmentStatus(
      updateTarget.value.tracking_number,
      updateForm.value.status
    )
    window.dispatchEvent(new Event('shipment-updated'))

    updateModal.value = false
    showToast(`Shipment updated to ${STATUS_LABELS[updateForm.value.status]}`)
    await loadAll()
  } catch (err) {
    updateError.value = err.message || 'Failed to update shipment'
  } finally {
    saving.value = false
  }
}

// ── Detail modal ──────────────────────────────────────────────────────────────
async function openDetailModal (row) {
  detailTarget.value  = { ...row }
  detailLoading.value = true
  detailModal.value   = true
  try {
    // Fetch full detail (includes order_status, user_id, tracking_url, etc.)
    const detail = await shipmentService.getShipmentByOrder(row.order_id)
    detailTarget.value = detail
  } catch {
    // Fall back to list-row data if detail fetch fails
  } finally {
    detailLoading.value = false
  }
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

/* ── Stat cards ── */
.stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: box-shadow .18s;
}
.stat-card:hover { box-shadow: 0 4px 16px rgba(59,130,246,.1); }
.stat-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Data table ── */
.data-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
.ship-table { background: transparent !important; }
.ship-table :deep(.q-table__container) { background: transparent !important; }
.ship-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .05em;
  border-bottom: 1px solid #dbeafe;
}
.ship-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}
.ship-table :deep(tr:hover td) { background: #eff6ff; }
.ship-table :deep(.q-table__bottom) {
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}

/* ── Badges ── */
.ship-id {
  font-family: monospace;
  color: #1e40af;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}
.tracking-num {
  font-family: monospace;
  font-size: 13px;
  color: #0e7490;
}

/* ── Modals ── */
.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}

/* ── Detail grid ── */
.detail-grid { display: flex; flex-direction: column; gap: 10px; }
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #eff6ff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.detail-label {
  color: #64748b;
  font-size: 13px;
  display: flex;
  align-items: center;
}
.detail-value {
  color: #1e293b;
  font-size: 13px;
  font-weight: 500;
}

/* ── Toast ── */
.toast-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,.1);
  min-width: 260px;
}
</style>