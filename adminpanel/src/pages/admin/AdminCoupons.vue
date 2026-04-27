<template>
  <q-page class="admin-page">

    <!-- ── Page Header ── -->
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Coupons</div>
          <div class="text-caption text-blue-7">
            Manage discount codes and promotions 
          </div>
        </div>
        <div class="row q-gutter-sm">
          <q-btn
            label="Usage History"
            color="blue-3"
            text-color="blue-9"
            unelevated no-caps
            icon="history"
            @click="openUsageDialog(null)"
          />
          <q-btn
            label="Performance"
            color="blue-3"
            text-color="blue-9"
            unelevated no-caps
            icon="bar_chart"
            @click="openPerformanceDialog"
          />
          <q-btn
            label="Create Coupon"
            color="blue-6"
            unelevated no-caps
            icon="add"
            @click="openModal(null)"
          />
        </div>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">

      <!-- ── Stats Cards ── -->
      <div class="row q-gutter-md q-mb-lg">
        <template v-if="statsLoading">
          <div class="col-12 col-sm-6 col-md-4" v-for="i in 3" :key="i">
            <q-card flat class="stat-card">
              <q-card-section><q-skeleton type="rect" height="70px" /></q-card-section>
            </q-card>
          </div>
        </template>
        <template v-else-if="statsData">
          <div class="col-12 col-sm-6 col-md-4" v-for="card in statCards" :key="card.label">
            <q-card flat class="stat-card">
              <q-card-section class="q-pa-md">
                <div class="row items-center justify-between q-mb-sm">
                  <div class="stat-label">{{ card.label }}</div>
                  <q-icon :name="card.icon" :color="card.color" size="20px" />
                </div>
                <div class="text-h5 text-weight-bold" :class="`text-${card.color}`">{{ card.value }}</div>
                <div class="text-caption text-grey-6 q-mt-xs">{{ card.sub }}</div>
              </q-card-section>
            </q-card>
          </div>
        </template>
      </div>

      <!-- ── Expiry Warning Banner ── -->
      <q-banner
        v-if="expiringSoon.length"
        class="q-mb-md expiry-banner"
        rounded inline-actions
      >
        <template #avatar><q-icon name="schedule" color="orange-7" /></template>
        <span class="text-orange-9 text-weight-medium">
          {{ expiringSoon.length }} coupon{{ expiringSoon.length > 1 ? 's' : '' }}
          expiring within 7 days:
          <strong>{{ expiringSoon.map(c => c.code).join(', ') }}</strong>
        </span>
      </q-banner>

      <!-- ── Filters ── -->
      <div class="row q-gutter-md q-mb-md items-center">
        <div class="col-12 col-sm">
          <q-input
            v-model="search"
            placeholder="Search coupon code or description..."
            dense standout="bg-blue-1" clearable
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
        <div class="col-auto">
          <q-btn-toggle
            v-model="statusFilter"
            :options="filterOptions"
            toggle-color="blue-6"
            color="grey-2"
            text-color="blue-8"
            dense no-caps rounded
          />
        </div>
        <div class="col-auto">
          <q-btn flat round icon="refresh" color="blue-4" :loading="loading" @click="fetchCoupons">
            <q-tooltip>Refresh</q-tooltip>
          </q-btn>
        </div>
      </div>

      <!-- ── Main Table ── -->
      <q-card class="data-card" flat>
        <q-table
          :rows="filteredCoupons"
          :columns="cols"
          row-key="id"
          flat
          :rows-per-page-options="[10, 25, 50]"
          class="coupon-table"
          wrap-cells
          :loading="loading"
        >
          <template #body-cell-code="props">
            <q-td :props="props">
              <div class="coupon-code">{{ props.value }}</div>
            </q-td>
          </template>

          <template #body-cell-discount_type="props">
            <q-td :props="props">
              <q-badge :color="props.value === 'PERCENTAGE' ? 'purple-6' : 'blue-6'" outline>
                <q-icon
                  :name="props.value === 'PERCENTAGE' ? 'percent' : 'currency_rupee'"
                  size="12px" class="q-mr-xs"
                />
                {{ props.value === 'PERCENTAGE' ? 'Percentage' : 'Fixed' }}
              </q-badge>
            </q-td>
          </template>

          <template #body-cell-discount_value="props">
            <q-td :props="props">
              <span class="text-green-7 text-weight-bold">
                {{ props.row.discount_type === 'PERCENTAGE'
                    ? props.value + '%'
                    : '₹' + props.value }}
              </span>
            </q-td>
          </template>

          <template #body-cell-max_discount_amount="props">
            <q-td :props="props">
              <span class="text-blue-8">{{ props.value != null ? '₹' + props.value : '—' }}</span>
            </q-td>
          </template>

          <template #body-cell-min_order_amount="props">
            <q-td :props="props">
              {{ Number(props.value) > 0 ? '₹' + props.value : '—' }}
            </q-td>
          </template>

          <template #body-cell-usage="props">
            <q-td :props="props">
              <div v-if="props.row.usage_limit" class="column" style="min-width:110px;gap:3px">
                <q-linear-progress
                  :value="usageRatio(props.row)"
                  :color="usageBarColor(props.row)"
                  track-color="grey-2"
                  rounded style="height:6px"
                />
                <span class="text-caption text-blue-7">
                  {{ props.row.used_count }}/{{ props.row.usage_limit }} used
                  <span v-if="props.row.remaining_usage != null" class="text-grey-5">
                    ({{ props.row.remaining_usage }} left)
                  </span>
                </span>
              </div>
              <span v-else class="text-caption text-grey-5">
                {{ props.row.used_count }} / Unlimited
              </span>
            </q-td>
          </template>

          <template #body-cell-is_active="props">
            <q-td :props="props">
              <q-toggle
                :model-value="props.value"
                color="blue-6" dense
                :loading="togglingId === props.row.id"
                @update:model-value="toggleActive(props.row)"
              />
            </q-td>
          </template>

          <template #body-cell-status="props">
            <q-td :props="props">
              <q-chip
                :color="statusColor(props.value)"
                text-color="white"
                dense size="sm"
                :icon="statusIcon(props.value)"
              >
                {{ props.value }}
              </q-chip>
            </q-td>
          </template>

          <template #body-cell-valid_to="props">
            <q-td :props="props">
              <span v-if="props.value" :class="expiryClass(props.value)">
                {{ formatDate(props.value) }}
                <q-icon
                  v-if="isExpiringSoon(props.value)"
                  name="schedule" size="14px" color="orange-6" class="q-ml-xs"
                ><q-tooltip>Expiring soon!</q-tooltip></q-icon>
              </span>
              <span v-else class="text-grey-4">No expiry</span>
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td :props="props">
              <div class="row q-gutter-xs no-wrap">
                <q-btn round flat size="sm" icon="edit" color="blue-4" @click="openModal(props.row)">
                  <q-tooltip>Edit</q-tooltip>
                </q-btn>
                <q-btn round flat size="sm" icon="history" color="teal-5" @click="openUsageDialog(props.row.id)">
                  <q-tooltip>Usage history</q-tooltip>
                </q-btn>
                <q-btn round flat size="sm" icon="delete" color="negative" @click="confirmDelete(props.row)">
                  <q-tooltip>Deactivate</q-tooltip>
                </q-btn>
              </div>
            </q-td>
          </template>

          <template #no-data>
            <div class="full-width column flex-center q-pa-xl text-blue-7">
              <q-icon name="confirmation_number" size="48px" class="q-mb-sm" />
              <div class="text-body2">No coupons found</div>
              <div class="text-caption text-grey-5 q-mt-xs">
                Verify your API connection or create a new coupon.
              </div>
            </div>
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- ══════════════════════ ADD / EDIT MODAL ══════════════════════ -->
    <q-dialog v-model="modal" persistent>
      <q-card class="modal-card" style="width:580px;max-width:95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">
            {{ editing ? 'Edit Coupon' : 'Create Coupon' }}
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>

        <q-card-section>
          <q-form ref="formRef">
            <div class="column q-gutter-md">

              <div class="row q-gutter-md">
                <q-input
                  v-model="form.code"
                  label="Coupon Code *"
                  standout="bg-blue-1" dense class="col"
                  :rules="[v => !!v || 'Required', v => v.length >= 3 || 'Min 3 chars']"
                  @update:model-value="v => form.code = (v || '').toUpperCase()"
                >
                  <template #append>
                    <q-btn flat dense size="xs" icon="auto_fix_high" color="blue-4" @click="form.code = genCode()">
                      <q-tooltip>Auto Generate</q-tooltip>
                    </q-btn>
                  </template>
                </q-input>

                <q-select
                  v-model="form.discount_type"
                  :options="discountTypeOptions"
                  emit-value map-options
                  label="Discount Type *"
                  standout="bg-blue-1" dense class="col"
                  :rules="[v => !!v || 'Required']"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.discount_value"
                  :label="form.discount_type === 'PERCENTAGE' ? 'Discount % *' : 'Discount Amount ₹ *'"
                  type="number"
                  standout="bg-blue-1" dense class="col"
                  :suffix="form.discount_type === 'PERCENTAGE' ? '%' : ''"
                  :prefix="form.discount_type === 'FIXED' ? '₹' : ''"
                  :rules="[
                    v => v > 0 || 'Must be > 0',
                    v => form.discount_type !== 'PERCENTAGE' || v <= 100 || 'Max 100%'
                  ]"
                />
                <q-input
                  v-model.number="form.max_discount_amount"
                  label="Max Discount ₹"
                  type="number"
                  standout="bg-blue-1" dense class="col"
                  prefix="₹"
                  hint="Cap for percentage discounts"
                  :disable="form.discount_type === 'FIXED'"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.min_order_amount"
                  label="Min Order Amount ₹"
                  type="number"
                  standout="bg-blue-1" dense class="col"
                  prefix="₹" hint="0 = no minimum"
                />
                <q-input
                  v-model.number="form.usage_limit"
                  label="Usage Limit"
                  type="number"
                  standout="bg-blue-1" dense class="col"
                  hint="Leave empty for unlimited"
                  :rules="[v => !v || v > 0 || 'Must be > 0']"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model="form.valid_from"
                  label="Valid From"
                  type="date"
                  standout="bg-blue-1" dense class="col"
                  stack-label
                />
                <q-input
                  v-model="form.valid_to"
                  label="Valid To"
                  type="date"
                  standout="bg-blue-1" dense class="col"
                  stack-label
                  :rules="[v => !v || !form.valid_from || v >= form.valid_from || 'Must be after Valid From']"
                />
              </div>

              <q-input
                v-model="form.description"
                label="Description (optional)"
                standout="bg-blue-1" dense
                type="textarea" rows="2"
              />

              <div class="row items-center q-gutter-sm">
                <q-toggle v-model="form.is_active" color="blue-6" label="Active" />
                <span class="text-caption text-blue-7">Toggle to enable / disable this coupon</span>
              </div>

              <q-banner v-if="editing" class="bg-blue-1 rounded-borders text-blue-9" dense>
                <template #avatar><q-icon name="info" color="blue-5" /></template>
                Used <strong>{{ editing.used_count ?? 0 }}</strong> times ·
                Created {{ formatDate(editing.created_at) }} ·
                Updated {{ formatDate(editing.updated_at) }}
              </q-banner>

            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            :label="editing ? 'Update' : 'Create'"
            color="blue-6" unelevated no-caps
            @click="saveCoupon"
            :loading="saveLoading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════ DELETE CONFIRM ══════════════════════ -->
    <q-dialog v-model="deleteDialog">
      <q-card style="min-width:340px" class="modal-card">
        <q-card-section>
          <div class="text-h6 text-negative">Deactivate Coupon</div>
          <p class="q-mt-sm text-grey-8">
            Are you sure you want to deactivate
            <strong class="text-blue-8">{{ deleteTarget?.code }}</strong>?<br>
            <span class="text-caption text-grey-6">
              (Sets is_active = false — coupon data is preserved)
            </span>
          </p>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup color="blue-4" no-caps />
          <q-btn unelevated label="Deactivate" color="negative" no-caps @click="doDelete" :loading="deleteLoading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════ USAGE HISTORY ══════════════════════ -->
    <!-- coupon_usage_view cols: id, code, email, order_id, used_at -->
    <q-dialog v-model="usageDialog" maximized transition-show="slide-up" transition-hide="slide-down">
      <q-card>
        <q-bar class="bg-blue-6 text-white">
          <q-icon name="history" />
          <div class="text-weight-bold q-ml-sm">Coupon Usage History</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup />
        </q-bar>
        <q-card-section>
          <q-table
            :rows="usageRows"
            :columns="usageCols"
            row-key="id" flat
            :loading="usageLoading"
            :rows-per-page-options="[15, 30, 50]"
          >
            <template #body-cell-used_at="props">
              <q-td :props="props">{{ formatDateTime(props.value) }}</q-td>
            </template>
            <template #no-data>
              <div class="full-width column flex-center q-pa-xl text-blue-7">
                <q-icon name="history" size="40px" class="q-mb-sm" />
                <div>No usage records found</div>
              </div>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════ PERFORMANCE ══════════════════════ -->
    <!--
      coupon_performance view cols:
        coupon_id, code, discount_type, discount_value,
        used_count, total_usages, total_revenue_generated
    -->
    <q-dialog v-model="perfDialog" maximized transition-show="slide-up" transition-hide="slide-down">
      <q-card>
        <q-bar class="bg-blue-6 text-white">
          <q-icon name="bar_chart" />
          <div class="text-weight-bold q-ml-sm">Coupon Performance Analytics</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup />
        </q-bar>
        <q-card-section>
          <q-table
            :rows="perfRows"
            :columns="perfCols"
            row-key="coupon_id" flat
            :loading="perfLoading"
            :rows-per-page-options="[15, 30]"
          >
            <template #body-cell-discount_type="props">
              <q-td :props="props">
                <q-badge :color="props.value === 'PERCENTAGE' ? 'purple-6' : 'blue-6'" outline>
                  {{ props.value === 'PERCENTAGE' ? 'Percentage' : 'Fixed' }}
                </q-badge>
              </q-td>
            </template>
            <template #body-cell-total_revenue_generated="props">
              <q-td :props="props">
                <span class="text-green-7 text-weight-bold">
                  {{ props.value != null ? '₹' + Number(props.value).toLocaleString('en-IN') : '—' }}
                </span>
              </q-td>
            </template>
            <template #no-data>
              <div class="full-width column flex-center q-pa-xl text-blue-7">
                <q-icon name="bar_chart" size="40px" class="q-mb-sm" />
                <div>No performance data available</div>
              </div>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import couponService from 'src/services/couponService'

const $q = useQuasar()

// ── State ─────────────────────────────────────────────────────────
const coupons      = ref([])
const loading      = ref(false)
const search       = ref('')
const statusFilter = ref('all')
const togglingId   = ref(null)

const modal       = ref(false)
const editing     = ref(null)
const saveLoading = ref(false)
const formRef     = ref(null)

const deleteDialog  = ref(false)
const deleteTarget  = ref(null)
const deleteLoading = ref(false)

const usageDialog  = ref(false)
const usageRows    = ref([])
const usageLoading = ref(false)

const perfDialog  = ref(false)
const perfRows    = ref([])
const perfLoading = ref(false)

const statsData    = ref(null)
const statsLoading = ref(false)

// ── Form ──────────────────────────────────────────────────────────
const defaultForm = () => ({
  code:                '',
  description:         '',
  discount_type:       'PERCENTAGE',
  discount_value:      0,
  min_order_amount:    0,
  max_discount_amount: null,
  usage_limit:         null,
  valid_from:          '',
  valid_to:            '',
  is_active:           true,
})
const form = ref(defaultForm())

// ── Options ───────────────────────────────────────────────────────
const discountTypeOptions = [
  { label: 'Percentage (%)', value: 'PERCENTAGE' },
  { label: 'Fixed Amount (₹)', value: 'FIXED' },
]

const filterOptions = [
  { label: 'All',       value: 'all' },
  { label: 'Active',    value: 'active' },
  { label: 'Expired',   value: 'expired' },
  { label: 'Exhausted', value: 'exhausted' },
  { label: 'Disabled',  value: 'disabled' },
]

// ── Table columns — exactly matching backend response keys ─────────
const cols = [
  { name: 'code',                label: 'Code',      field: 'code',               align: 'left',   sortable: true },
  { name: 'discount_type',       label: 'Type',      field: 'discount_type',      align: 'left' },
  { name: 'discount_value',      label: 'Discount',  field: 'discount_value',     align: 'left',   sortable: true },
  { name: 'max_discount_amount', label: 'Max Disc.', field: 'max_discount_amount',align: 'left' },
  { name: 'min_order_amount',    label: 'Min Order', field: 'min_order_amount',   align: 'left' },
  { name: 'usage',               label: 'Usage',     field: 'used_count',         align: 'left' },
  { name: 'is_active',           label: 'Active',    field: 'is_active',          align: 'center' },
  { name: 'status',              label: 'Status',    field: 'status',             align: 'left' },
  { name: 'valid_to',            label: 'Expires',   field: 'valid_to',           align: 'left',   sortable: true },
  { name: 'actions',             label: '',          field: 'id',                 align: 'right' },
]

// coupon_usage_view: id, code, email, order_id, used_at
const usageCols = [
  { name: 'id',       label: '#',         field: 'id',       align: 'left' },
  { name: 'code',     label: 'Coupon',    field: 'code',     align: 'left' },
  { name: 'email',    label: 'User Email',field: 'email',    align: 'left' },
  { name: 'order_id', label: 'Order ID',  field: 'order_id', align: 'left' },
  { name: 'used_at',  label: 'Used At',   field: 'used_at',  align: 'left' },
]

// coupon_performance view: coupon_id, code, discount_type, discount_value,
//                          used_count, total_usages, total_revenue_generated
const perfCols = [
  { name: 'coupon_id',               label: 'ID',           field: 'coupon_id',               align: 'left' },
  { name: 'code',                    label: 'Code',         field: 'code',                    align: 'left' },
  { name: 'discount_type',           label: 'Type',         field: 'discount_type',           align: 'left' },
  { name: 'discount_value',          label: 'Value',        field: 'discount_value',          align: 'left' },
  { name: 'used_count',              label: 'DB Count',     field: 'used_count',              align: 'left', sortable: true },
  { name: 'total_usages',            label: 'Total Usages', field: 'total_usages',            align: 'left', sortable: true },
  { name: 'total_revenue_generated', label: 'Revenue on Orders', field: 'total_revenue_generated', align: 'left', sortable: true },
]

// ── Stats cards
// Backend /stats returns: { total_coupons, active_coupons, inactive_coupons }
const statCards = computed(() => {
  if (!statsData.value) return []
  const s = statsData.value
  return [
    { label: 'Total Coupons', value: s.total_coupons   ?? 0, icon: 'confirmation_number', color: 'blue-6',  sub: 'All time' },
    { label: 'Active',        value: s.active_coupons  ?? 0, icon: 'check_circle',        color: 'positive',sub: 'Currently enabled' },
    { label: 'Inactive',      value: s.inactive_coupons ?? 0, icon: 'block',              color: 'negative',sub: 'Disabled or expired' },
  ]
})

// ── Enriched rows with computed status ───────────────────────────
const enriched = computed(() =>
  coupons.value.map(c => ({ ...c, status: deriveStatus(c) }))
)

const filteredCoupons = computed(() =>
  enriched.value.filter(c => {
    const matchSearch =
      !search.value ||
      c.code.toLowerCase().includes(search.value.toLowerCase()) ||
      (c.description || '').toLowerCase().includes(search.value.toLowerCase())
    const matchStatus = statusFilter.value === 'all' || c.status === statusFilter.value
    return matchSearch && matchStatus
  })
)

const expiringSoon = computed(() =>
  enriched.value.filter(c => c.is_active && isExpiringSoon(c.valid_to))
)

// ── Pure helpers ──────────────────────────────────────────────────
// status is NOT a DB column — we compute it from is_active + valid_to + used_count
const deriveStatus = (c) => {
  if (!c.is_active) return 'disabled'
  if (c.valid_to && new Date(c.valid_to) < new Date()) return 'expired'
  if (c.usage_limit && c.used_count >= c.usage_limit) return 'exhausted'
  return 'active'
}

const genCode = () => 'PROMO' + Math.random().toString(36).substring(2, 7).toUpperCase()

const formatDate = (d) =>
  d ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'

const formatDateTime = (d) => d ? new Date(d).toLocaleString('en-IN') : '—'

const isExpiringSoon = (dateStr) => {
  if (!dateStr) return false
  const diff = new Date(dateStr) - new Date()
  return diff > 0 && diff < 7 * 24 * 60 * 60 * 1000
}

const expiryClass = (dateStr) => {
  if (!dateStr) return 'text-grey-7'
  if (new Date(dateStr) < new Date()) return 'text-negative text-weight-medium'
  if (isExpiringSoon(dateStr)) return 'text-orange-7 text-weight-medium'
  return 'text-grey-7'
}

const usageRatio = (row) => {
  if (!row.usage_limit) return 0
  return Math.min(row.used_count / row.usage_limit, 1)
}

const usageBarColor = (row) => {
  const r = usageRatio(row)
  if (r >= 1)   return 'negative'
  if (r >= 0.8) return 'orange-6'
  return 'blue-5'
}

const statusColor = (s) =>
  ({ active: 'positive', expired: 'grey-6', disabled: 'negative', exhausted: 'orange-7' }[s] || 'grey')

const statusIcon = (s) =>
  ({ active: 'check_circle', expired: 'event_busy', disabled: 'block', exhausted: 'do_not_disturb' }[s] || '')

// ── Map form → payload (matches CouponCreate / CouponUpdate schema) ──
const toPayload = (f) => ({
  code:                (f.code || '').trim().toUpperCase(),
  description:         f.description || null,
  discount_type:       f.discount_type,           // 'PERCENTAGE' | 'FIXED'
  discount_value:      Number(f.discount_value),
  min_order_amount:    Number(f.min_order_amount) || 0,
  max_discount_amount: f.max_discount_amount ? Number(f.max_discount_amount) : null,
  usage_limit:         f.usage_limit ? Number(f.usage_limit) : null,
  valid_from:          f.valid_from ? new Date(f.valid_from).toISOString() : null,
  valid_to:            f.valid_to   ? new Date(f.valid_to).toISOString()   : null,
  is_active:           Boolean(f.is_active),
})

// ── API calls ─────────────────────────────────────────────────────

// GET /admin/coupons/ → returns plain array []
// Each item has all coupon cols + remaining_usage from backend
const fetchCoupons = async () => {
  loading.value = true
  try {
    const params = {}
    // Backend only supports Optional[bool] is_active filter
    if (statusFilter.value === 'active')   params.is_active = true
    if (statusFilter.value === 'disabled') params.is_active = false

    const data = await couponService.list(params)
    coupons.value = Array.isArray(data) ? data : []
    console.debug('[CouponPage] loaded', coupons.value.length, 'coupons')
  } catch (err) {
    console.error('[CouponPage] fetchCoupons:', err)
    $q.notify({ type: 'negative', message: err.message || 'Failed to load coupons' })
  } finally {
    loading.value = false
  }
}

// GET /admin/coupons/stats → { total_coupons, active_coupons, inactive_coupons }
/* ─────────────────────────────────────────────
1. SMART LOCAL STATS RECALC (instant frontend)
───────────────────────────────────────────── */
const rebuildStatsFromRows = () => {
  const rows = Array.isArray(coupons.value) ? coupons.value : []

  const total = rows.length

  const active = rows.filter(row => {
    const status = deriveStatus(row)
    return status === 'active'
  }).length

  const inactive = total - active

  statsData.value = {
    total_coupons: total,
    active_coupons: active,
    inactive_coupons: inactive
  }
}

/* ─────────────────────────────────────────────
2. IMPROVED FETCH STATS
───────────────────────────────────────────── */
const fetchStats = async (silent = false) => {
  if (!silent) statsLoading.value = true

  try {
    const data = await couponService.stats()

    statsData.value = {
      total_coupons: Number(data?.total_coupons || 0),
      active_coupons: Number(data?.active_coupons || 0),
      inactive_coupons: Number(data?.inactive_coupons || 0)
    }
  } catch (err) {
    /* fallback from local rows */
    rebuildStatsFromRows()
    console.warn('[CouponPage] stats fallback:', err)
  } finally {
    if (!silent) statsLoading.value = false
  }
}


// ── Modal open ────────────────────────────────────────────────────
const openModal = (c) => {
  editing.value = c || null
  if (c) {
    form.value = {
      code:                c.code,
      description:         c.description || '',
      discount_type:       c.discount_type,
      discount_value:      Number(c.discount_value),
      min_order_amount:    Number(c.min_order_amount) || 0,
      max_discount_amount: c.max_discount_amount ? Number(c.max_discount_amount) : null,
      usage_limit:         c.usage_limit ?? null,
      // slice to YYYY-MM-DD for <input type="date">
      valid_from: c.valid_from ? String(c.valid_from).substring(0, 10) : '',
      valid_to:   c.valid_to   ? String(c.valid_to).substring(0, 10)   : '',
      is_active:  c.is_active,
    }
  } else {
    form.value = defaultForm()
  }
  modal.value = true
}

// POST /admin/coupons → { message, id }
// PUT  /admin/coupons/{id} → { message, id }
const saveCoupon = async () => {
  const valid = await formRef.value?.validate()
  if (valid === false) return

  if (form.value.valid_from && form.value.valid_to && form.value.valid_to < form.value.valid_from) {
    $q.notify({ type: 'warning', message: 'Valid To must be after Valid From' })
    return
  }

  saveLoading.value = true
  try {
    const payload = toPayload(form.value)
    if (editing.value) {
      await couponService.update(editing.value.id, payload)
      $q.notify({ type: 'positive', message: `Coupon "${payload.code}" updated` })
    } else {
      await couponService.create(payload)
      $q.notify({ type: 'positive', message: `Coupon "${payload.code}" created` })
    }
    modal.value = false
    await fetchCoupons()
    await fetchStats()
  } catch (err) {
    console.error('[CouponPage] saveCoupon:', err)
    $q.notify({
      type: 'negative',
      message: err.message || 'Save failed',
      ...(err.status === 409 && { caption: 'Coupon code already exists' }),
    })
  } finally {
    saveLoading.value = false
  }
}

// PUT /admin/coupons/{id} with { is_active: !current }
const toggleActive = async (row) => {
  if (!row?.id) return

  togglingId.value = row.id

  const index = coupons.value.findIndex(c => c.id === row.id)
  if (index === -1) {
    togglingId.value = null
    return
  }

  const oldValue = coupons.value[index].is_active
  const newValue = !oldValue

  /* optimistic instant UI update */
  coupons.value[index] = {
    ...coupons.value[index],
    is_active: newValue
  }

  rebuildStatsFromRows()

  try {
    await couponService.update(row.id, {
      is_active: newValue
    })

    /* optional silent sync */
    fetchStats(true)

    $q.notify({
      type: 'positive',
      message: `Coupon ${newValue ? 'enabled' : 'disabled'}`
    })

  } catch (err) {
    /* rollback */
    coupons.value[index] = {
      ...coupons.value[index],
      is_active: oldValue
    }

    rebuildStatsFromRows()

    $q.notify({
      type: 'negative',
      message: err.message || 'Toggle failed'
    })
  } finally {
    togglingId.value = null
  }
}

// DELETE /admin/coupons/{id} — backend does soft-deactivate (is_active = false)
const confirmDelete = (row) => {
  deleteTarget.value = row
  deleteDialog.value = true
}

const doDelete = async () => {
  deleteLoading.value = true
  try {
    await couponService.remove(deleteTarget.value.id)
    $q.notify({ type: 'positive', message: `Coupon "${deleteTarget.value.code}" deactivated` })
    deleteDialog.value = false
    await fetchCoupons()
    await fetchStats()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Delete failed' })
  } finally {
    deleteLoading.value = false
  }
}

// GET /admin/coupons/usage → coupon_usage_view
// View cols: id, code, email, order_id, used_at
// Filter client-side by coupon code when called from a row
const openUsageDialog = async (couponId = null) => {
  usageDialog.value = true
  usageLoading.value = true
  usageRows.value = []
  try {
    const data = await couponService.usage()
    const rows = Array.isArray(data) ? data : []
    if (couponId) {
      const code = coupons.value.find(c => c.id === couponId)?.code
      usageRows.value = code ? rows.filter(r => r.code === code) : rows
    } else {
      usageRows.value = rows
    }
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Failed to load usage history' })
  } finally {
    usageLoading.value = false
  }
}

// GET /admin/coupons/performance → coupon_performance view
const openPerformanceDialog = async () => {
  perfDialog.value = true
  perfLoading.value = true
  perfRows.value = []
  try {
    const data = await couponService.performance()
    perfRows.value = Array.isArray(data) ? data : []
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Failed to load performance data' })
  } finally {
    perfLoading.value = false
  }
}

onMounted(async () => {
  await fetchCoupons()
  await fetchStats()
})
</script>

<style scoped>
.admin-page {
  background: #f0f4f8;
  min-height: 100vh;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* ─── 2. PAGE HEADER ─────────────────────────────────────────── */
.page-header {
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  padding: 20px 28px !important;
}
.page-header .text-h5 {
  font-size: 21px !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  line-height: 1.25;
}
.page-header .text-caption {
  font-size: 12.5px !important;
  color: #64748b !important;
  margin-top: 2px;
  display: block;
}
.page-header .q-btn {
  border-radius: 9px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 7px 15px !important;
  min-height: 36px !important;
}

/* ─── 3. STATS CARDS ─────────────────────────────────────────── */
.stat-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 14px !important;
  box-shadow: 0 1px 4px rgba(0,0,0,.05) !important;
  transition: box-shadow .2s, transform .2s !important;
  overflow: visible !important;
}
.stat-card:hover {
  box-shadow: 0 6px 20px rgba(37,99,235,.1) !important;
  transform: translateY(-2px);
}
.stat-card .q-card__section { padding: 20px 22px !important; }
.stat-label {
  font-size: 11px !important;
  font-weight: 700 !important;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: #94a3b8 !important;
  line-height: 1;
}
.stat-card .text-h5 {
  font-size: 30px !important;
  font-weight: 800 !important;
  line-height: 1 !important;
  margin-top: 8px !important;
}
.stat-card .text-caption {
  font-size: 12px !important;
  color: #94a3b8 !important;
  margin-top: 4px !important;
  display: block;
}

/* Keep 3 cards in one row — fix Quasar gutter math */
.q-px-lg .row.q-gutter-md.q-mb-lg > .col-12.col-sm-6.col-md-4 {
  flex: 0 0 calc(33.333% - 16px) !important;
  max-width: calc(33.333% - 16px) !important;
}
@media (max-width: 900px) {
  .q-px-lg .row.q-gutter-md.q-mb-lg > .col-12.col-sm-6.col-md-4 {
    flex: 0 0 calc(50% - 16px) !important;
    max-width: calc(50% - 16px) !important;
  }
}
@media (max-width: 599px) {
  .q-px-lg .row.q-gutter-md.q-mb-lg > .col-12.col-sm-6.col-md-4 {
    flex: 0 0 100% !important;
    max-width: 100% !important;
  }
}

/* ─── 4. EXPIRY BANNER ───────────────────────────────────────── */
.expiry-banner {
  background: #fff7ed !important;
  border: 1px solid #fed7aa !important;
  border-radius: 10px !important;
  min-height: unset !important;
}
.expiry-banner :deep(.q-banner__avatar) { padding-right: 10px; align-self: center; }
.expiry-banner :deep(.q-banner__content) { font-weight: 500; color: #92400e; align-self: center; }

/* ─── 5. FILTER TOOLBAR ──────────────────────────────────────── */

/* Search box — plain outlined style, strip standout */
.q-px-lg .row.q-gutter-md.q-mb-md .q-input :deep(.q-field__control) {
  background: #ffffff !important;
  border-radius: 10px !important;
  border: 1.5px solid #e2e8f0 !important;
  min-height: 40px !important;
  padding: 0 12px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.04) !important;
}
.q-px-lg .row.q-gutter-md.q-mb-md .q-input :deep(.q-field__control::before),
.q-px-lg .row.q-gutter-md.q-mb-md .q-input :deep(.q-field__control::after),
.q-px-lg .row.q-gutter-md.q-mb-md .q-input :deep(.q-field__shadow) {
  display: none !important;
  opacity: 0 !important;
}
.q-px-lg .row.q-gutter-md.q-mb-md .q-input :deep(.q-field__native) {
  color: #0f172a !important;
  font-size: 13.5px !important;
  padding: 0 !important;
  min-height: 40px !important;
}
.q-px-lg .row.q-gutter-md.q-mb-md .q-input :deep(.q-field__native::placeholder) {
  color: #94a3b8 !important;
}

/* Filter btn-toggle pill */
.q-btn-toggle {
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 10px !important;
  padding: 3px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.04) !important;
  overflow: hidden;
}
.q-btn-toggle :deep(.q-btn) {
  border-radius: 7px !important;
  font-size: 12.5px !important;
  font-weight: 500 !important;
  padding: 5px 13px !important;
  min-height: 30px !important;
  height: 30px !important;
  color: #475569 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  transition: background .13s, color .13s !important;
}
.q-btn-toggle :deep(.q-btn:hover) {
  background: #eff6ff !important;
  color: #1d4ed8 !important;
}
.q-btn-toggle :deep(.q-btn.bg-blue-6),
.q-btn-toggle :deep(.q-btn.text-white) {
  background: #2563eb !important;
  color: #ffffff !important;
  font-weight: 600 !important;
}

/* ─── 6. DATA TABLE ──────────────────────────────────────────── */
.data-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 14px !important;
  overflow: hidden !important;
  box-shadow: 0 1px 4px rgba(0,0,0,.05) !important;
}
.coupon-table { background: transparent !important; }
.coupon-table :deep(.q-table__container) { background: transparent !important; }

.coupon-table :deep(thead tr:first-child th) {
  background: #f8faff !important;
  border-bottom: 2px solid #e8eef8 !important;
  padding: 12px 16px !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  letter-spacing: .07em !important;
  text-transform: uppercase !important;
  color: #3b5bdb !important;
  white-space: nowrap !important;
}
.coupon-table :deep(tbody tr td) {
  padding: 12px 16px !important;
  font-size: 13.5px !important;
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
  vertical-align: middle !important;
  white-space: nowrap !important;
}
.coupon-table :deep(tbody tr:last-child td) { border-bottom: none !important; }
.coupon-table :deep(tbody tr:hover td) { background: #f5f8ff !important; }
.coupon-table :deep(.q-table__bottom) {
  border-top: 1px solid #e2e8f0 !important;
  padding: 10px 16px !important;
  background: #fafbfc !important;
  color: #64748b !important;
  font-size: 12.5px !important;
  min-height: 44px !important;
}
.coupon-table :deep(.q-table__middle) { overflow-x: auto !important; }

.coupon-code {
  font-family: 'Courier New', monospace;
  font-size: 12.5px;
  font-weight: 700;
  color: #1d4ed8;
  background: #dbeafe;
  padding: 4px 10px;
  border-radius: 6px;
  letter-spacing: .09em;
  display: inline-block;
  line-height: 1.4;
}

/* Status chips */
.coupon-table :deep(.q-chip) {
  border-radius: 999px !important;
  font-size: 11.5px !important;
  font-weight: 600 !important;
  padding: 0 10px !important;
  height: 22px !important;
  min-height: unset !important;
}
.coupon-table :deep(.q-chip.bg-positive)  { background: #dcfce7 !important; color: #15803d !important; }
.coupon-table :deep(.q-chip.bg-negative)  { background: #fee2e2 !important; color: #b91c1c !important; }
.coupon-table :deep(.q-chip.bg-grey-6)    { background: #f1f5f9 !important; color: #475569 !important; }
.coupon-table :deep(.q-chip.bg-orange-7)  { background: #fff7ed !important; color: #c2410c !important; }

/* Toggle */
.coupon-table :deep(.q-toggle) { min-height: unset !important; }
.coupon-table :deep(.q-toggle__inner) { font-size: 36px !important; }

/* Row action btns */
.coupon-table :deep(td .q-btn.q-btn--round) {
  width: 30px !important; height: 30px !important;
  min-height: unset !important;
  border-radius: 7px !important;
}

/* ─── 7. MODAL CARD ──────────────────────────────────────────── */
.modal-card {
  background: #ffffff !important;
  border-radius: 16px !important;
  border: 1px solid #bfdbfe !important;
  box-shadow: 0 24px 64px rgba(0,0,0,.15) !important;
  overflow: hidden !important;
}
.modal-card > .q-card__section:first-child {
  padding: 20px 24px 16px !important;
  border-bottom: 1px solid #f1f5f9 !important;
  background: #fafbff !important;
}
.modal-card .text-h6 {
  font-size: 17px !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  line-height: 1.3 !important;
}
.modal-card > .q-card__section:not(:first-child):not(:last-child) {
  padding: 22px 24px !important;
}
.modal-card .q-card__actions {
  padding: 14px 24px !important;
  border-top: 1px solid #f1f5f9 !important;
  background: #fafbff !important;
}
.modal-card .q-card__actions .q-btn {
  border-radius: 9px !important;
  font-weight: 600 !important;
  font-size: 13.5px !important;
  padding: 8px 22px !important;
  min-height: 38px !important;
}
.modal-card .q-card__actions .q-btn[color="blue-6"] {
  background: #2563eb !important;
  color: #fff !important;
  box-shadow: 0 2px 8px rgba(37,99,235,.3) !important;
}

/* ─── 8. FORM FIELD — THE BIG FIX ───────────────────────────── */
/*
  Root problem:
  Quasar "standout" fields render a .q-field__shadow element that
  creates the visible inner floating box / second border.
  The fix: hide the shadow element entirely, then paint our own
  clean border directly on .q-field__control.
*/

/* 8a. Kill the shadow element that causes the inner box */
.modal-card :deep(.q-field__shadow) {
  display: none !important;
  opacity: 0 !important;
  visibility: hidden !important;
}

/* 8b. Kill ::before / ::after standout borders */
.modal-card :deep(.q-field__control::before),
.modal-card :deep(.q-field__control::after) {
  display: none !important;
  border: none !important;
  box-shadow: none !important;
  background: none !important;
}

/* 8c. Our own clean, single-border control */
.modal-card :deep(.q-field__control) {
  background: #f8fafc !important;
  border-radius: 10px !important;
  border: 1.5px solid #dde3ed !important;
  min-height: 56px !important;      /* enough room: label 18px + value 20px + padding */
  padding: 0 14px !important;
  box-shadow: none !important;
  transition: border-color .15s, box-shadow .15s, background .15s !important;
  position: relative !important;
  overflow: hidden !important;
}

/* 8d. Focus */
.modal-card :deep(.q-field--focused .q-field__control) {
  background: #ffffff !important;
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,.12) !important;
}

/* 8e. Error — fix black-bg bug */
.modal-card :deep(.q-field--error .q-field__control) {
  background: #fff8f8 !important;
  border-color: #f87171 !important;
  box-shadow: 0 0 0 3px rgba(239,68,68,.1) !important;
}

/* 8f. Disabled */
.modal-card :deep(.q-field--disabled .q-field__control) {
  background: #f1f5f9 !important;
  border-color: #e2e8f0 !important;
  opacity: .65 !important;
}

/* 8g. Label — always visible, floats up on focus/value */
.modal-card :deep(.q-field__label) {
  font-size: 12px !important;
  font-weight: 600 !important;
  color: #64748b !important;
  top: 10px !important;          /* resting position */
  left: 0 !important;
  line-height: 1.2 !important;
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: unset !important;
  pointer-events: none !important;
  transition: top .12s ease, font-size .12s ease, color .12s ease !important;
}
.modal-card :deep(.q-field--float .q-field__label) {
  top: 7px !important;
  font-size: 10.5px !important;
  color: #3b82f6 !important;
}
.modal-card :deep(.q-field--error .q-field__label) { color: #ef4444 !important; }

/* 8h. Native input — sits below the floated label */
.modal-card :deep(.q-field__native),
.modal-card :deep(.q-field__input) {
  color: #0f172a !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding-top: 20px !important;   /* push below label */
  padding-bottom: 6px !important;
  min-height: 56px !important;
  line-height: 1.3 !important;
  background: transparent !important;
  caret-color: #2563eb !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}
.modal-card :deep(.q-field__native::placeholder) {
  color: #b0bcc8 !important;
  font-weight: 400 !important;
}

/* 8i. Textarea */
.modal-card :deep(.q-field--type-textarea .q-field__native) {
  min-height: 72px !important;
  padding-top: 24px !important;
  resize: vertical !important;
}

/* 8j. Prefix & suffix — must align with the value text */
.modal-card :deep(.q-field__prefix),
.modal-card :deep(.q-field__suffix) {
  color: #475569 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  /* Use flex alignment on the control row, not padding-top hack */
  align-self: flex-end !important;
  padding-bottom: 6px !important;
  padding-top: 0 !important;
  line-height: 1.3 !important;
}

/* 8k. Append slot (icon buttons, dropdown arrow) */
.modal-card :deep(.q-field__append) {
  align-self: center !important;
  padding-top: 0 !important;
}
.modal-card :deep(.q-select__dropdown-icon) {
  color: #64748b !important;
}

/* 8l. Hint / error message row */
.modal-card :deep(.q-field__bottom) {
  padding: 4px 2px 0 !important;
  min-height: unset !important;
}
.modal-card :deep(.q-field__messages) {
  font-size: 11.5px !important;
  color: #94a3b8 !important;
  line-height: 1.4 !important;
}
.modal-card :deep(.q-field--error .q-field__messages) {
  color: #ef4444 !important;
}

/* 8m. Remove number spinners */
.modal-card :deep(input[type="number"]) {
  -moz-appearance: textfield !important;
}
.modal-card :deep(input[type="number"]::-webkit-outer-spin-button),
.modal-card :deep(input[type="number"]::-webkit-inner-spin-button) {
  -webkit-appearance: none !important;
  margin: 0 !important;
}

/* 8n. Date inputs */
.modal-card :deep(input[type="date"]) {
  color: #0f172a !important;
  font-size: 14px !important;
}
.modal-card :deep(input[type="date"]::-webkit-calendar-picker-indicator) {
  opacity: .45;
  cursor: pointer;
}

/* 8o. Form row layout: 2 cols with gap */
.modal-card .column.q-gutter-md > .row {
  gap: 14px !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}
.modal-card .column.q-gutter-md > .row > .col {
  min-width: 0 !important;
  flex: 1 1 0 !important;
  padding: 0 !important;
}

/* 8p. Banner inside modal */
.modal-card .q-banner {
  border-radius: 8px !important;
  font-size: 12.5px !important;
  padding: 10px 14px !important;
  min-height: unset !important;
  line-height: 1.5 !important;
}
.modal-card .q-banner.bg-blue-1 {
  background: #eff6ff !important;
  color: #1e40af !important;
}

/* ─── 9. FULL-PAGE DIALOGS ───────────────────────────────────── */
:deep(.q-dialog__inner--maximized .q-card) { border-radius: 0 !important; }
.q-bar.bg-blue-6 {
  background: #2563eb !important;
  padding: 0 20px !important;
  height: 52px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
}
:deep(.q-dialog__inner--maximized .q-table thead th) {
  background: #f8faff !important;
  color: #3b5bdb !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  padding: 12px 16px !important;
  border-bottom: 2px solid #e8eef8 !important;
}
:deep(.q-dialog__inner--maximized .q-table tbody td) {
  font-size: 13.5px !important;
  padding: 12px 16px !important;
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
:deep(.q-dialog__inner--maximized .q-table tbody tr:hover td) {
  background: #f5f8ff !important;
}

/* ─── 10. RESPONSIVE ─────────────────────────────────────────── */
@media (max-width: 768px) {
  .page-header { padding: 14px 16px !important; }
  .page-header .row { flex-direction: column !important; gap: 12px !important; }
  .q-px-lg { padding-left: 14px !important; padding-right: 14px !important; }
  .modal-card > .q-card__section:not(:first-child):not(:last-child) { padding: 16px !important; }
  .modal-card .column.q-gutter-md > .row {
    flex-direction: column !important;
    gap: 0 !important;
  }
  .modal-card .column.q-gutter-md > .row > .col {
    width: 100% !important;
    flex: none !important;
    margin-bottom: 14px !important;
  }
  .coupon-table :deep(tbody tr td),
  .coupon-table :deep(thead tr th) {
    padding: 10px !important;
    font-size: 12px !important;
  }
}
@media (max-width: 480px) {
  .q-btn-toggle :deep(.q-btn) { font-size: 11px !important; padding: 4px 8px !important; }
}
</style>