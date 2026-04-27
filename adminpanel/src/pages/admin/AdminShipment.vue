<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Shipments</div>
          <div class="text-caption text-blue-7">Track and manage order shipments</div>
        </div>
        <q-btn
          label="Add Shipment"
          color="blue-6"
          unelevated
          no-caps
          icon="add"
          @click="openModal(null)"
        />
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

      <!-- Tabs + Search -->
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
        <q-tab name="in_transit" label="In Transit" />
        <q-tab name="delivered" label="Delivered" />
      </q-tabs>

      <div class="row q-gutter-md q-mb-md">
        <div class="col-12 col-sm">
          <q-input
            v-model="search"
            placeholder="Search shipment ID, order or tracking..."
            dense
            standout="bg-blue-1"
            clearable
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
      </div>

      <!-- Shipment list table -->
      <q-card class="data-card" flat>
        <q-table
          :rows="filteredShipments"
          :columns="cols"
          row-key="id"
          flat
          :rows-per-page-options="[10, 25]"
          class="ship-table"
          wrap-cells
        >
          <template #body-cell-id="props">
            <q-td :props="props"
              ><code class="ship-id">{{ props.value }}</code></q-td
            >
          </template>

          <template #body-cell-order_id="props">
            <q-td :props="props"
              ><span class="text-blue-8 text-weight-medium">{{ props.value }}</span></q-td
            >
          </template>

          <template #body-cell-tracking_number="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <span class="tracking-num">{{ props.value }}</span>
                <q-btn
                  round
                  flat
                  size="xs"
                  icon="content_copy"
                  color="blue-4"
                  @click="copyTracking(props.value)"
                >
                  <q-tooltip>Copy</q-tooltip>
                </q-btn>
              </div>
            </q-td>
          </template>

          <!-- courier_name column -->
          <template #body-cell-courier="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon name="local_shipping" size="14px" color="blue-5" />
                <span class="text-grey-8">{{ props.value }}</span>
              </div>
            </q-td>
          </template>

          <template #body-cell-status="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon :name="shipIcon(props.value)" :color="shipColor(props.value)" size="14px" />
                <q-badge :color="shipColor(props.value)" :label="props.value.replace('_', ' ')" />
              </div>
            </q-td>
          </template>

          <!-- estimated_delivery_date -->
          <template #body-cell-estimated_delivery="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-xs">
                <q-icon name="event" size="13px" color="blue-5" />
                <span class="text-caption text-grey-7">{{ props.value || '—' }}</span>
              </div>
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td :props="props">
              <div class="row q-gutter-xs no-wrap">
                <q-btn
                  round
                  flat
                  size="sm"
                  icon="edit"
                  color="blue-4"
                  @click="openModal(props.row)"
                >
                  <q-tooltip>Update Tracking</q-tooltip>
                </q-btn>
                <q-btn
                  round
                  flat
                  size="sm"
                  icon="visibility"
                  color="cyan-7"
                  @click="viewShipment(props.row)"
                >
                  <q-tooltip>View Details</q-tooltip>
                </q-btn>
              </div>
            </q-td>
          </template>

          <template #no-data>
            <div class="full-width column flex-center q-pa-xl text-blue-7">
              <q-icon name="local_shipping" size="48px" class="q-mb-sm" />
              <div>No shipments found</div>
            </div>
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- ── Add/Edit Shipment Modal ── -->
    <!-- POST /admin/orders/{order_id}/shipment  |  PUT /admin/shipments/{tracking_number} -->
    <q-dialog v-model="modal" persistent>
      <q-card class="modal-card" style="width: 520px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">
            {{ editing ? 'Update Tracking' : 'Add Shipment' }}
          </div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>

        <q-card-section>
          <div class="column q-gutter-md">
            <!-- order_id — required for POST /admin/orders/{order_id}/shipment -->
            <q-input
              v-model="form.order_id"
              label="Order ID *"
              standout="bg-blue-1"
              dense
              :disable="!!editing"
              :rules="[(v) => !!v || 'Order ID required']"
            />

            <!-- courier_name -->
            <q-select
              v-model="form.courier"
              :options="courierOptions"
              label="Courier Name *"
              standout="bg-blue-1"
              dense
              :rules="[(v) => !!v || 'Courier required']"
            />

            <!-- tracking_number -->
            <q-input
              v-model="form.tracking_number"
              label="Tracking Number *"
              standout="bg-blue-1"
              dense
              :rules="[(v) => !!v || 'Tracking number required']"
            />

            <!-- estimated_delivery_date -->
            <q-input
              v-model="form.estimated_delivery"
              label="Estimated Delivery Date *"
              type="date"
              standout="bg-blue-1"
              dense
              :rules="[(v) => !!v || 'Date required']"
            />

            <q-select
              v-model="form.status"
              :options="['pending', 'in_transit', 'out_for_delivery', 'delivered', 'failed']"
              label="Status"
              standout="bg-blue-1"
              dense
            />

            <q-input
              v-model="form.notes"
              label="Notes"
              standout="bg-blue-1"
              dense
              type="textarea"
              rows="2"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            :label="editing ? 'Update' : 'Create'"
            color="blue-6"
            unelevated
            no-caps
            :loading="saveLoading"
            @click="saveShipment"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ── Shipment Detail Card Modal ── -->
    <!-- GET /admin/orders/{order_id}/shipment -->
    <q-dialog v-model="detailModal">
      <q-card class="modal-card" style="width: 500px; max-width: 95vw" v-if="viewTarget">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Shipment Details</div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section>
          <!-- Shipment info card -->
          <div class="detail-grid q-mb-md">
            <div v-for="f in detailFields" :key="f.key" class="detail-row">
              <div class="detail-label">
                <q-icon :name="f.icon" size="13px" color="blue-5" class="q-mr-xs" />{{ f.label }}
              </div>
              <div class="detail-value">{{ viewTarget[f.key] || '—' }}</div>
            </div>
            <!-- Status with badge -->
            <div class="detail-row">
              <div class="detail-label">
                <q-icon name="info" size="13px" color="blue-5" class="q-mr-xs" />Status
              </div>
              <q-badge
                :color="shipColor(viewTarget.status)"
                :label="viewTarget.status.replace('_', ' ')"
              />
            </div>
          </div>

          <!-- Tracking timeline -->
          <div class="text-caption text-blue-7 text-weight-bold text-uppercase q-mb-sm">
            Tracking Timeline
          </div>
          <q-timeline color="blue" dense>
            <q-timeline-entry
              v-for="t in shipTimeline"
              :key="t.status"
              :title="t.status.replace('_', ' ')"
              :subtitle="t.time"
              :color="shipColor(t.status)"
              icon="circle"
            />
          </q-timeline>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- ── Toast ── -->
    <q-dialog v-model="toastVisible" position="bottom" seamless>
      <q-card class="toast-card row items-center q-gutter-sm q-pa-md">
        <q-icon name="check_circle" color="positive" size="20px" />
        <span class="text-grey-9 text-weight-medium">{{ toastMessage }}</span>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'

const tab = ref('all')
const search = ref('')
const modal = ref(false)
const editing = ref(null)
const detailModal = ref(false)
const viewTarget = ref(null)
const saveLoading = ref(false)
const toastVisible = ref(false)
const toastMessage = ref('')

const courierOptions = [
  'DTDC',
  'BlueDart',
  'Delhivery',
  'Ekart',
  'Amazon Logistics',
  'FedEx',
  'DHL',
]

const form = ref({
  order_id: '',
  courier: '',
  tracking_number: '',
  estimated_delivery: '',
  status: 'pending',
  notes: '',
})

const shipments = ref([
  {
    id: 'SHP-001',
    order_id: '#ORD-1001',
    tracking_number: 'DTDC12345678',
    courier: 'DTDC',
    status: 'delivered',
    created_at: '2024-01-10',
    estimated_delivery: '2024-01-13',
    notes: '',
  },
  {
    id: 'SHP-002',
    order_id: '#ORD-1003',
    tracking_number: 'BD87654321',
    courier: 'BlueDart',
    status: 'in_transit',
    created_at: '2024-01-14',
    estimated_delivery: '2024-01-17',
    notes: 'Handle with care',
  },
  {
    id: 'SHP-003',
    order_id: '#ORD-1005',
    tracking_number: 'DLV11223344',
    courier: 'Delhivery',
    status: 'out_for_delivery',
    created_at: '2024-01-15',
    estimated_delivery: '2024-01-16',
    notes: '',
  },
  {
    id: 'SHP-004',
    order_id: '#ORD-1006',
    tracking_number: 'EK99887766',
    courier: 'Ekart',
    status: 'pending',
    created_at: '2024-01-16',
    estimated_delivery: '2024-01-20',
    notes: '',
  },
  {
    id: 'SHP-005',
    order_id: '#ORD-1007',
    tracking_number: 'FX55443322',
    courier: 'FedEx',
    status: 'failed',
    created_at: '2024-01-12',
    estimated_delivery: '2024-01-15',
    notes: 'Address not found',
  },
])

// All required columns: courier_name, tracking_number, estimated_delivery_date
const cols = [
  { name: 'id', label: 'Shipment ID', field: 'id', align: 'left', sortable: true },
  { name: 'order_id', label: 'Order ID', field: 'order_id', align: 'left' },
  { name: 'courier', label: 'Courier Name', field: 'courier', align: 'left' },
  { name: 'tracking_number', label: 'Tracking Number', field: 'tracking_number', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  {
    name: 'estimated_delivery',
    label: 'Est. Delivery',
    field: 'estimated_delivery',
    align: 'left',
  },
  { name: 'actions', label: '', field: 'id', align: 'left' },
]

const filteredShipments = computed(() =>
  shipments.value.filter((s) => {
    const ms =
      !search.value ||
      s.id.toLowerCase().includes(search.value.toLowerCase()) ||
      s.order_id.toLowerCase().includes(search.value.toLowerCase()) ||
      s.tracking_number.toLowerCase().includes(search.value.toLowerCase())
    return ms && (tab.value === 'all' || s.status === tab.value)
  }),
)

const summary = computed(() => [
  {
    label: 'Total',
    value: shipments.value.length,
    icon: 'local_shipping',
    color: 'blue-4',
    bg: 'rgba(59,130,246,.12)',
  },
  {
    label: 'In Transit',
    value: shipments.value.filter((s) => s.status === 'in_transit').length,
    icon: 'directions_transit',
    color: 'cyan-4',
    bg: 'rgba(6,182,212,.12)',
  },
  {
    label: 'Delivered',
    value: shipments.value.filter((s) => s.status === 'delivered').length,
    icon: 'check_circle',
    color: 'green-4',
    bg: 'rgba(34,197,94,.12)',
  },
  {
    label: 'Failed',
    value: shipments.value.filter((s) => s.status === 'failed').length,
    icon: 'error',
    color: 'red-4',
    bg: 'rgba(239,68,68,.12)',
  },
])

const detailFields = [
  { key: 'id', label: 'Shipment ID', icon: 'tag' },
  { key: 'order_id', label: 'Order ID', icon: 'receipt' },
  { key: 'tracking_number', label: 'Tracking No.', icon: 'qr_code' },
  { key: 'courier', label: 'Courier Name', icon: 'local_shipping' },
  { key: 'estimated_delivery', label: 'Est. Delivery', icon: 'event' },
  { key: 'notes', label: 'Notes', icon: 'notes' },
]

const shipTimeline = [
  { status: 'pending', time: '2024-01-14 10:00' },
  { status: 'in_transit', time: '2024-01-15 08:30' },
  { status: 'out_for_delivery', time: '2024-01-16 09:00' },
]

const shipColor = (s) =>
  ({
    pending: 'warning',
    in_transit: 'info',
    out_for_delivery: 'purple-5',
    delivered: 'positive',
    failed: 'negative',
  })[s] || 'grey'
const shipIcon = (s) =>
  ({
    pending: 'schedule',
    in_transit: 'local_shipping',
    out_for_delivery: 'two_wheeler',
    delivered: 'check_circle',
    failed: 'error',
  })[s] || 'help'

const copyTracking = (v) => navigator.clipboard?.writeText(v)
const viewShipment = (s) => {
  viewTarget.value = s
  detailModal.value = true
}
const openModal = (s) => {
  editing.value = s
  form.value = s
    ? { ...s }
    : {
        order_id: '',
        courier: '',
        tracking_number: '',
        estimated_delivery: '',
        status: 'pending',
        notes: '',
      }
  modal.value = true
}

// Simulates POST /admin/orders/{order_id}/shipment  or  PUT /admin/shipments/{tracking_number}
const saveShipment = async () => {
  if (
    !form.value.order_id ||
    !form.value.courier ||
    !form.value.tracking_number ||
    !form.value.estimated_delivery
  )
    return
  saveLoading.value = true
  await new Promise((r) => setTimeout(r, 600))
  if (editing.value) {
    const i = shipments.value.findIndex((s) => s.id === editing.value.id)
    shipments.value[i] = { ...shipments.value[i], ...form.value }
  } else {
    shipments.value.push({
      ...form.value,
      id: 'SHP-' + String(shipments.value.length + 1).padStart(3, '0'),
      created_at: new Date().toISOString().split('T')[0],
    })
  }
  saveLoading.value = false
  modal.value = false
  showToast(editing.value ? 'Shipment updated successfully!' : 'Shipment created successfully!')
}

const showToast = (msg) => {
  toastMessage.value = msg
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
.ship-table {
  background: transparent !important;
}
.ship-table :deep(.q-table__container) {
  background: transparent !important;
}
.ship-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #dbeafe;
}
.ship-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}
.ship-table :deep(tr:hover td) {
  background: #eff6ff;
}
.ship-table :deep(.q-table__bottom) {
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}
.ship-id {
  font-family: monospace;
  color: #1e40af;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
}
.tracking-num {
  font-family: monospace;
  font-size: 13px;
  color: #0e7490;
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
.toast-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 260px;
}
</style>
