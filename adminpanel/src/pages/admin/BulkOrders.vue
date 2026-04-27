<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Bulk Order Management</div>
          <div class="text-caption text-blue-7">Manage organizations, bulk requests & orders</div>
        </div>
        <div class="row q-gutter-sm">
          <q-chip color="warning" text-color="white" icon="pending" size="sm">
            Pending Requests: {{ pendingRequestCount }}
          </q-chip>
          <q-chip color="blue-6" text-color="white" icon="business" size="sm">
            Orgs: {{ organizations.length }}
          </q-chip>
        </div>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- Tabs -->
      <q-tabs
        v-model="tab"
        dense
        align="left"
        active-color="blue-4"
        indicator-color="blue-5"
        class="q-mb-md"
      >
        <q-tab name="organizations" label="Organizations" icon="business" />
        <q-tab name="requests" label="Bulk Requests" icon="list_alt" />
        <q-tab name="orders" label="Bulk Orders" icon="shopping_bag" />
      </q-tabs>

      <!-- ===================== ORGANIZATIONS TAB ===================== -->
      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="organizations" class="q-pa-none">
          <div class="row items-center justify-between q-mb-md">
            <q-input
              v-model="orgSearch"
              placeholder="Search organizations..."
              dense
              standout="bg-blue-1"
              clearable
              style="min-width: 260px"
            >
              <template #prepend><q-icon name="search" color="blue-4" /></template>
            </q-input>
            <q-btn
              label="Add Organization"
              color="blue-6"
              unelevated
              no-caps
              icon="add_business"
              @click="addOrgModal = true"
            />
          </div>

          <q-card flat class="table-card">
            <q-table
              :rows="filteredOrgs"
              :columns="orgColumns"
              row-key="id"
              flat
              :loading="loadingOrgs"
              hide-bottom
              :rows-per-page-options="[0]"
            >
              <template #body-cell-status="props">
                <q-td :props="props">
                  <q-badge
                    :color="props.row.status === 'active' ? 'positive' : 'grey-5'"
                    :label="props.row.status"
                  />
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props">
                  <q-btn flat round size="xs" icon="edit" color="blue-4">
                    <q-tooltip>Edit</q-tooltip>
                  </q-btn>
                  <q-btn
                    flat
                    round
                    size="xs"
                    icon="delete"
                    color="negative"
                    @click="confirmDeleteOrg(props.row)"
                  >
                    <q-tooltip>Delete</q-tooltip>
                  </q-btn>
                </q-td>
              </template>
              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-blue-7">
                  <q-icon name="business_center" size="56px" class="q-mb-sm" />
                  <div>No organizations found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ===================== BULK REQUESTS TAB ===================== -->
        <q-tab-panel name="requests" class="q-pa-none">
          <div class="row items-center justify-between q-mb-md">
            <div class="row q-gutter-sm items-center">
              <q-input
                v-model="reqSearch"
                placeholder="Search requests..."
                dense
                standout="bg-blue-1"
                clearable
                style="min-width: 240px"
              >
                <template #prepend><q-icon name="search" color="blue-4" /></template>
              </q-input>
              <q-select
                v-model="reqStatusFilter"
                :options="['All Status', 'pending', 'approved', 'rejected', 'converted']"
                dense
                standout="bg-blue-1"
                style="min-width: 140px"
              />
            </div>
          </div>

          <q-card flat class="table-card">
            <q-table
              :rows="filteredRequests"
              :columns="requestColumns"
              row-key="id"
              flat
              :loading="loadingRequests"
              hide-bottom
              :rows-per-page-options="[0]"
            >
              <template #body-cell-status="props">
                <q-td :props="props">
                  <q-badge :color="statusColor(props.row.status)" :label="props.row.status" />
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props">
                  <template v-if="props.row.status === 'pending'">
                    <q-btn
                      label="Approve"
                      flat
                      size="xs"
                      color="positive"
                      no-caps
                      icon="check_circle"
                      class="q-mr-xs"
                      @click="openConfirm('approve', 'request', props.row)"
                    />
                    <q-btn
                      label="Reject"
                      flat
                      size="xs"
                      color="negative"
                      no-caps
                      icon="cancel"
                      class="q-mr-xs"
                      @click="openConfirm('reject', 'request', props.row)"
                    />
                  </template>
                  <template v-if="props.row.status === 'approved'">
                    <q-btn
                      label="Convert"
                      flat
                      size="xs"
                      color="blue-6"
                      no-caps
                      icon="swap_horiz"
                      @click="openConfirm('convert', 'request', props.row)"
                    />
                  </template>
                  <q-btn
                    flat
                    round
                    size="xs"
                    icon="visibility"
                    color="blue-4"
                    @click="viewRequestDetail(props.row)"
                  >
                    <q-tooltip>View Details</q-tooltip>
                  </q-btn>
                </q-td>
              </template>
              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-blue-7">
                  <q-icon name="list_alt" size="56px" class="q-mb-sm" />
                  <div>No bulk requests found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ===================== BULK ORDERS TAB ===================== -->
        <q-tab-panel name="orders" class="q-pa-none">
          <div class="row items-center justify-between q-mb-md">
            <div class="row q-gutter-sm items-center">
              <q-input
                v-model="orderSearch"
                placeholder="Search orders..."
                dense
                standout="bg-blue-1"
                clearable
                style="min-width: 240px"
              >
                <template #prepend><q-icon name="search" color="blue-4" /></template>
              </q-input>
              <q-select
                v-model="orderStatusFilter"
                :options="['All Status', 'processing', 'shipped', 'delivered', 'cancelled']"
                dense
                standout="bg-blue-1"
                style="min-width: 140px"
              />
            </div>
          </div>

          <q-card flat class="table-card">
            <q-table
              :rows="filteredOrders"
              :columns="orderColumns"
              row-key="id"
              flat
              :loading="loadingOrders"
              hide-bottom
              :rows-per-page-options="[0]"
            >
              <template #body-cell-urgent="props">
                <q-td :props="props">
                  <q-badge
                    v-if="props.row.urgent"
                    color="red-5"
                    label="Urgent"
                    icon="priority_high"
                  />
                  <span v-else class="text-grey-5 text-caption">—</span>
                </q-td>
              </template>
              <template #body-cell-status="props">
                <q-td :props="props">
                  <q-badge :color="orderStatusColor(props.row.status)" :label="props.row.status" />
                </q-td>
              </template>
              <template #body-cell-total_amount="props">
                <q-td :props="props">
                  <span class="text-weight-medium text-grey-9"
                    >₹{{ props.row.total_amount.toLocaleString() }}</span
                  >
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props">
                  <!-- Update Status -->
                  <q-btn-dropdown
                    flat
                    size="xs"
                    color="blue-4"
                    no-caps
                    icon="edit_note"
                    label="Status"
                    auto-close
                  >
                    <q-list>
                      <q-item
                        v-for="s in ['processing', 'shipped', 'delivered', 'cancelled']"
                        :key="s"
                        clickable
                        @click="openUpdateStatus(props.row, s)"
                      >
                        <q-item-section>
                          <q-item-label :class="`text-${orderStatusColor(s)}`">{{
                            s
                          }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-btn-dropdown>

                  <!-- View History -->
                  <q-btn
                    flat
                    round
                    size="xs"
                    icon="history"
                    color="blue-4"
                    class="q-mx-xs"
                    @click="viewOrderHistory(props.row)"
                  >
                    <q-tooltip>View History</q-tooltip>
                  </q-btn>

                  <!-- Toggle Urgent -->
                  <q-btn
                    flat
                    round
                    size="xs"
                    :icon="props.row.urgent ? 'notifications_off' : 'priority_high'"
                    :color="props.row.urgent ? 'grey-5' : 'red-4'"
                    @click="toggleUrgent(props.row)"
                  >
                    <q-tooltip>{{ props.row.urgent ? 'Remove Urgent' : 'Mark Urgent' }}</q-tooltip>
                  </q-btn>
                </q-td>
              </template>
              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-blue-7">
                  <q-icon name="shopping_bag" size="56px" class="q-mb-sm" />
                  <div>No bulk orders found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- ===== ADD ORGANIZATION MODAL ===== -->
    <q-dialog v-model="addOrgModal" persistent>
      <q-card class="modal-card" style="width: 480px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Add Organization</div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section>
          <div class="column q-gutter-md">
            <q-input
              v-model="orgForm.name"
              label="Organization Name"
              standout="bg-blue-1"
              dense
              :rules="[(v) => !!v || 'Required']"
            />
            <q-input
              v-model="orgForm.email"
              label="Email"
              standout="bg-blue-1"
              dense
              type="email"
              :rules="[(v) => !!v || 'Required']"
            />
            <q-input v-model="orgForm.phone" label="Phone" standout="bg-blue-1" dense />
            <q-input
              v-model="orgForm.address"
              label="Address"
              standout="bg-blue-1"
              dense
              type="textarea"
              rows="2"
            />
            <q-select
              v-model="orgForm.status"
              :options="['active', 'inactive']"
              label="Status"
              standout="bg-blue-1"
              dense
            />
          </div>
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Add Organization"
            color="blue-6"
            unelevated
            no-caps
            icon="add_business"
            :loading="savingOrg"
            :disable="!orgForm.name || !orgForm.email"
            @click="addOrganization"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ===== CONFIRMATION DIALOG ===== -->
    <q-dialog v-model="confirmDialog" persistent>
      <q-card class="modal-card" style="width: 400px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Confirm Action</div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section>
          <div class="row items-center q-gutter-md">
            <q-icon :name="confirmMeta.icon" :color="confirmMeta.color" size="40px" />
            <div>
              <div class="text-grey-9 text-weight-medium">{{ confirmMeta.title }}</div>
              <div class="text-caption text-grey-6 q-mt-xs">{{ confirmMeta.message }}</div>
            </div>
          </div>
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            :label="confirmMeta.btnLabel"
            :color="confirmMeta.color"
            unelevated
            no-caps
            :loading="confirmLoading"
            @click="executeConfirm"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ===== ORDER HISTORY MODAL ===== -->
    <q-dialog v-model="historyModal">
      <q-card class="modal-card" style="width: 540px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div>
            <div class="text-h6 text-grey-9 text-weight-bold">Order History</div>
            <div class="text-caption text-blue-7">{{ selectedOrder?.order_number }}</div>
          </div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section>
          <q-timeline color="blue-4" v-if="orderHistory.length">
            <q-timeline-entry
              v-for="h in orderHistory"
              :key="h.id"
              :title="h.status"
              :subtitle="h.created_at"
              :color="orderStatusColor(h.status)"
              :icon="orderStatusIcon(h.status)"
            >
              <div class="text-caption text-grey-6">{{ h.note }}</div>
            </q-timeline-entry>
          </q-timeline>
          <div v-else class="column flex-center q-pa-lg text-blue-7">
            <q-icon name="history" size="40px" class="q-mb-sm" />
            <div>No history available</div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- ===== REQUEST DETAIL MODAL ===== -->
    <q-dialog v-model="requestDetailModal">
      <q-card class="modal-card" style="width: 500px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div>
            <div class="text-h6 text-grey-9 text-weight-bold">Request Details</div>
            <div class="text-caption text-blue-7">{{ selectedRequest?.request_id }}</div>
          </div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section v-if="selectedRequest">
          <div class="column q-gutter-sm">
            <div class="row justify-between items-center detail-row">
              <span class="text-caption text-grey-6">Organization</span>
              <span class="text-grey-9 text-weight-medium">{{ selectedRequest.organization }}</span>
            </div>
            <q-separator style="opacity: 0.1" />
            <div class="row justify-between items-center detail-row">
              <span class="text-caption text-grey-6">Status</span>
              <q-badge
                :color="statusColor(selectedRequest.status)"
                :label="selectedRequest.status"
              />
            </div>
            <q-separator style="opacity: 0.1" />
            <div class="row justify-between items-center detail-row">
              <span class="text-caption text-grey-6">Total Items</span>
              <span class="text-grey-9 text-weight-medium">{{ selectedRequest.total_items }}</span>
            </div>
            <q-separator style="opacity: 0.1" />
            <div class="row justify-between items-center detail-row">
              <span class="text-caption text-grey-6">Requested On</span>
              <span class="text-grey-9">{{ selectedRequest.created_at }}</span>
            </div>
            <q-separator style="opacity: 0.1" />
            <div class="detail-row">
              <div class="text-caption text-grey-6 q-mb-xs">Notes</div>
              <div class="text-grey-7 text-caption">{{ selectedRequest.notes || '—' }}</div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()

// ── Tabs ──────────────────────────────────────────────────────────────
const tab = ref('organizations')

// ── Search & Filter ───────────────────────────────────────────────────
const orgSearch = ref('')
const reqSearch = ref('')
const reqStatusFilter = ref('All Status')
const orderSearch = ref('')
const orderStatusFilter = ref('All Status')

// ── Modals ────────────────────────────────────────────────────────────
const addOrgModal = ref(false)
const confirmDialog = ref(false)
const historyModal = ref(false)
const requestDetailModal = ref(false)
const confirmLoading = ref(false)
const savingOrg = ref(false)

// ── Selected rows ─────────────────────────────────────────────────────
const selectedOrder = ref(null)
const selectedRequest = ref(null)
const orderHistory = ref([])

// ── Confirm meta ──────────────────────────────────────────────────────
const confirmMeta = ref({ icon: '', color: '', title: '', message: '', btnLabel: '', action: null })

// ── Org Form ──────────────────────────────────────────────────────────
const orgForm = ref({ name: '', email: '', phone: '', address: '', status: 'active' })

// ── Loading states ────────────────────────────────────────────────────
const loadingOrgs = ref(false)
const loadingRequests = ref(false)
const loadingOrders = ref(false)

// ── Mock Data ─────────────────────────────────────────────────────────
const organizations = ref([
  {
    id: 1,
    name: 'TechCorp Solutions',
    email: 'procurement@techcorp.com',
    phone: '9876543210',
    contact_person: 'Arjun Mehta',
    total_orders: 14,
    status: 'active',
  },
  {
    id: 2,
    name: 'Bharat Retail Ltd',
    email: 'orders@bharatretail.in',
    phone: '9123456789',
    contact_person: 'Sunita Rao',
    total_orders: 8,
    status: 'active',
  },
  {
    id: 3,
    name: 'Greenway Exports',
    email: 'bulk@greenway.co',
    phone: '9988776655',
    contact_person: 'Kiran Nair',
    total_orders: 3,
    status: 'inactive',
  },
  {
    id: 4,
    name: 'Swift Logistics',
    email: 'info@swiftlog.in',
    phone: '9911223344',
    contact_person: 'Priya Singh',
    total_orders: 21,
    status: 'active',
  },
])

const bulkRequests = ref([
  {
    id: 1,
    request_id: 'REQ-0021',
    organization: 'TechCorp Solutions',
    status: 'pending',
    total_items: 120,
    created_at: '2024-01-15',
    notes: 'Urgent delivery required before quarter end.',
  },
  {
    id: 2,
    request_id: 'REQ-0020',
    organization: 'Bharat Retail Ltd',
    status: 'approved',
    total_items: 85,
    created_at: '2024-01-14',
    notes: 'Standard delivery terms.',
  },
  {
    id: 3,
    request_id: 'REQ-0019',
    organization: 'Greenway Exports',
    status: 'rejected',
    total_items: 200,
    created_at: '2024-01-13',
    notes: 'Items currently out of stock.',
  },
  {
    id: 4,
    request_id: 'REQ-0018',
    organization: 'Swift Logistics',
    status: 'converted',
    total_items: 60,
    created_at: '2024-01-12',
    notes: null,
  },
  {
    id: 5,
    request_id: 'REQ-0017',
    organization: 'TechCorp Solutions',
    status: 'pending',
    total_items: 45,
    created_at: '2024-01-11',
    notes: 'Sample request for Q1.',
  },
])

const bulkOrders = ref([
  {
    id: 1,
    order_number: 'BO-10045',
    organization: 'TechCorp Solutions',
    total_amount: 184500,
    status: 'processing',
    urgent: true,
  },
  {
    id: 2,
    order_number: 'BO-10044',
    organization: 'Bharat Retail Ltd',
    total_amount: 92000,
    status: 'shipped',
    urgent: false,
  },
  {
    id: 3,
    order_number: 'BO-10043',
    organization: 'Swift Logistics',
    total_amount: 67800,
    status: 'delivered',
    urgent: false,
  },
  {
    id: 4,
    order_number: 'BO-10042',
    organization: 'TechCorp Solutions',
    total_amount: 23500,
    status: 'cancelled',
    urgent: false,
  },
  {
    id: 5,
    order_number: 'BO-10041',
    organization: 'Greenway Exports',
    total_amount: 112000,
    status: 'processing',
    urgent: true,
  },
])

// ── Table columns ─────────────────────────────────────────────────────
const orgColumns = [
  { name: 'name', label: 'Organization', field: 'name', align: 'left', sortable: true },
  { name: 'contact_person', label: 'Contact Person', field: 'contact_person', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'phone', label: 'Phone', field: 'phone', align: 'left' },
  {
    name: 'total_orders',
    label: 'Total Orders',
    field: 'total_orders',
    align: 'center',
    sortable: true,
  },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const requestColumns = [
  { name: 'request_id', label: 'Request ID', field: 'request_id', align: 'left', sortable: true },
  { name: 'organization', label: 'Organization', field: 'organization', align: 'left' },
  {
    name: 'total_items',
    label: 'Total Items',
    field: 'total_items',
    align: 'center',
    sortable: true,
  },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'created_at', label: 'Date', field: 'created_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'left' },
]

const orderColumns = [
  {
    name: 'order_number',
    label: 'Order Number',
    field: 'order_number',
    align: 'left',
    sortable: true,
  },
  { name: 'organization', label: 'Organization', field: 'organization', align: 'left' },
  {
    name: 'total_amount',
    label: 'Total Amount',
    field: 'total_amount',
    align: 'left',
    sortable: true,
  },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'urgent', label: 'Priority', field: 'urgent', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'left' },
]

// ── Computed ──────────────────────────────────────────────────────────
const filteredOrgs = computed(() =>
  organizations.value.filter(
    (o) =>
      !orgSearch.value ||
      o.name.toLowerCase().includes(orgSearch.value.toLowerCase()) ||
      o.email.toLowerCase().includes(orgSearch.value.toLowerCase()),
  ),
)

const filteredRequests = computed(() =>
  bulkRequests.value.filter((r) => {
    const ms =
      !reqSearch.value ||
      r.request_id.toLowerCase().includes(reqSearch.value.toLowerCase()) ||
      r.organization.toLowerCase().includes(reqSearch.value.toLowerCase())
    const mf = reqStatusFilter.value === 'All Status' || r.status === reqStatusFilter.value
    return ms && mf
  }),
)

const filteredOrders = computed(() =>
  bulkOrders.value.filter((o) => {
    const ms =
      !orderSearch.value ||
      o.order_number.toLowerCase().includes(orderSearch.value.toLowerCase()) ||
      o.organization.toLowerCase().includes(orderSearch.value.toLowerCase())
    const mf = orderStatusFilter.value === 'All Status' || o.status === orderStatusFilter.value
    return ms && mf
  }),
)

const pendingRequestCount = computed(
  () => bulkRequests.value.filter((r) => r.status === 'pending').length,
)

// ── Helpers ───────────────────────────────────────────────────────────
const statusColor = (s) =>
  ({ approved: 'positive', pending: 'warning', rejected: 'negative', converted: 'blue-6' })[s] ||
  'grey'

const orderStatusColor = (s) =>
  ({ processing: 'blue-5', shipped: 'cyan-6', delivered: 'positive', cancelled: 'negative' })[s] ||
  'grey'

const orderStatusIcon = (s) =>
  ({
    processing: 'autorenew',
    shipped: 'local_shipping',
    delivered: 'check_circle',
    cancelled: 'cancel',
  })[s] || 'circle'

// ── Organization actions ───────────────────────────────────────────────
const addOrganization = async () => {
  savingOrg.value = true
  try {
    // await api.post('/admin/organizations', orgForm.value)
    organizations.value.push({
      id: Date.now(),
      ...orgForm.value,
      contact_person: '—',
      total_orders: 0,
    })
    orgForm.value = { name: '', email: '', phone: '', address: '', status: 'active' }
    addOrgModal.value = false
    $q.notify({
      type: 'positive',
      message: 'Organization added successfully',
      position: 'top-right',
    })
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to add organization', position: 'top-right' })
  } finally {
    savingOrg.value = false
  }
}

const confirmDeleteOrg = (org) => {
  confirmMeta.value = {
    icon: 'delete_forever',
    color: 'negative',
    title: `Delete "${org.name}"?`,
    message: 'This action cannot be undone. All associated data will be removed.',
    btnLabel: 'Delete',
    action: () => {
      organizations.value = organizations.value.filter((o) => o.id !== org.id)
      $q.notify({ type: 'positive', message: 'Organization deleted', position: 'top-right' })
    },
  }
  confirmDialog.value = true
}

// ── Request actions ────────────────────────────────────────────────────
const openConfirm = (action, type, row) => {
  const configs = {
    approve: {
      icon: 'check_circle',
      color: 'positive',
      title: `Approve ${type === 'request' ? row.request_id : ''}?`,
      message: 'This will approve the request and notify the organization.',
      btnLabel: 'Approve',
      action: () => {
        const i = bulkRequests.value.findIndex((r) => r.id === row.id)
        bulkRequests.value[i].status = 'approved'
        // await api.post(`/admin/bulk-requests/${row.id}/approve`)
        $q.notify({ type: 'positive', message: 'Request approved', position: 'top-right' })
      },
    },
    reject: {
      icon: 'cancel',
      color: 'negative',
      title: `Reject ${row.request_id}?`,
      message: 'The organization will be notified of the rejection.',
      btnLabel: 'Reject',
      action: () => {
        const i = bulkRequests.value.findIndex((r) => r.id === row.id)
        bulkRequests.value[i].status = 'rejected'
        // await api.post(`/admin/bulk-requests/${row.id}/reject`)
        $q.notify({ type: 'warning', message: 'Request rejected', position: 'top-right' })
      },
    },
    convert: {
      icon: 'swap_horiz',
      color: 'blue-6',
      title: `Convert ${row.request_id} to Order?`,
      message: 'This will create a bulk order from this approved request.',
      btnLabel: 'Convert',
      action: () => {
        const i = bulkRequests.value.findIndex((r) => r.id === row.id)
        bulkRequests.value[i].status = 'converted'
        // await api.post(`/admin/bulk-requests/${row.id}/convert`)
        bulkOrders.value.unshift({
          id: Date.now(),
          order_number: `BO-${10046 + bulkOrders.value.length}`,
          organization: row.organization,
          total_amount: row.total_items * 850,
          status: 'processing',
          urgent: false,
        })
        $q.notify({ type: 'positive', message: 'Converted to bulk order', position: 'top-right' })
      },
    },
  }
  confirmMeta.value = configs[action]
  confirmDialog.value = true
}

const executeConfirm = async () => {
  confirmLoading.value = true
  try {
    await confirmMeta.value.action()
  } finally {
    confirmLoading.value = false
    confirmDialog.value = false
  }
}

const viewRequestDetail = (row) => {
  selectedRequest.value = row
  requestDetailModal.value = true
}

// ── Order actions ──────────────────────────────────────────────────────
const openUpdateStatus = (order, newStatus) => {
  confirmMeta.value = {
    icon: orderStatusIcon(newStatus),
    color: orderStatusColor(newStatus),
    title: `Update status to "${newStatus}"?`,
    message: `Order ${order.order_number} status will be changed to ${newStatus}.`,
    btnLabel: 'Update',
    action: () => {
      const i = bulkOrders.value.findIndex((o) => o.id === order.id)
      bulkOrders.value[i].status = newStatus
      // await api.put(`/admin/bulk-orders/${order.id}/status`, { status: newStatus })
      $q.notify({
        type: 'positive',
        message: `Status updated to ${newStatus}`,
        position: 'top-right',
      })
    },
  }
  confirmDialog.value = true
}

const viewOrderHistory = (order) => {
  selectedOrder.value = order
  // Simulated GET /admin/bulk-orders/{id}/history
  orderHistory.value = [
    {
      id: 1,
      status: 'processing',
      created_at: '2024-01-15 10:30 AM',
      note: 'Order created and sent to warehouse.',
    },
    {
      id: 2,
      status: 'shipped',
      created_at: '2024-01-16 02:15 PM',
      note: 'Dispatched via BlueDart. AWB: BD9988776.',
    },
  ].filter(() => order.status !== 'processing')
  if (order.status === 'delivered') {
    orderHistory.value.push({
      id: 3,
      status: 'delivered',
      created_at: '2024-01-18 11:00 AM',
      note: 'Delivered and signed by Arjun Mehta.',
    })
  }
  historyModal.value = true
}

const toggleUrgent = (order) => {
  const i = bulkOrders.value.findIndex((o) => o.id === order.id)
  bulkOrders.value[i].urgent = !bulkOrders.value[i].urgent
  // await api.patch(`/admin/bulk-orders/${order.id}/urgent`)
  $q.notify({
    type: bulkOrders.value[i].urgent ? 'warning' : 'info',
    message: bulkOrders.value[i].urgent ? 'Marked as urgent' : 'Urgent flag removed',
    position: 'top-right',
  })
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
.table-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
.detail-row {
  padding: 6px 0;
}
</style>
