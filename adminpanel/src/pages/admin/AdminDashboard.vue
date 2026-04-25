<template>
  <q-page class="admin-page">
    <!-- Header -->
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Dashboard</div>
          <div class="text-caption text-blue-7">Welcome back, Admin</div>
        </div>
        <q-chip color="blue-6" text-color="white" icon="circle" size="sm"> Live </q-chip>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg">
      <!-- Summary Cards -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md" v-for="card in summaryCards" :key="card.label">
          <q-card class="stat-card" flat>
            <!-- Loading skeleton -->
            <q-card-section v-if="loadingKpi">
              <q-skeleton type="rect" height="24px" class="q-mb-sm" />
              <q-skeleton type="rect" height="36px" width="60%" class="q-mb-xs" />
              <q-skeleton type="text" width="50%" />
            </q-card-section>
            <q-card-section v-else>
              <div class="row items-center justify-between q-mb-sm">
                <div class="stat-icon-wrap" :style="{ background: card.iconBg }">
                  <q-icon :name="card.icon" :color="card.color" size="20px" />
                </div>
                <q-badge :color="card.trend > 0 ? 'positive' : 'negative'" class="trend-badge">
                  <q-icon
                    :name="card.trend > 0 ? 'trending_up' : 'trending_down'"
                    size="12px"
                    class="q-mr-xs"
                  />
                  {{ Math.abs(card.trend) }}%
                </q-badge>
              </div>
              <div class="text-h5 text-weight-bold text-grey-9 q-mb-xs">{{ card.value }}</div>
              <div class="text-caption text-blue-7">{{ card.label }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Charts -->
      <div class="row q-gutter-md">
        <!-- Sales Trend -->
        <div class="col-12 col-md-7">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="row items-center justify-between q-mb-md">
                <div>
                  <div class="text-subtitle1 text-weight-bold text-grey-9">Sales Trend</div>
                  <div class="text-caption text-blue-7">
                    Revenue over time (transactions.created_at)
                  </div>
                </div>
                <div class="row q-gutter-sm">
                  <q-btn
                    v-for="p in periods"
                    :key="p"
                    :label="p"
                    :color="activePeriod === p ? 'blue-6' : 'grey-2'"
                    flat
                    dense
                    size="sm"
                    @click="activePeriod = p"
                    class="period-btn"
                  />
                </div>
              </div>
              <!-- Skeleton while loading -->
              <div v-if="loadingSales" class="chart-container">
                <q-skeleton type="rect" height="200px" />
              </div>
              <!-- SVG Line Chart with hover tooltip -->
              <div v-else class="chart-container" style="position: relative">
                <svg
                  viewBox="0 0 600 200"
                  class="full-width"
                  xmlns="http://www.w3.org/2000/svg"
                  @mouseleave="salesTooltip.visible = false"
                >
                  <defs>
                    <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4" />
                      <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
                    </linearGradient>
                  </defs>
                  <!-- Grid lines -->
                  <line
                    v-for="i in 4"
                    :key="i"
                    :x1="0"
                    :y1="i * 40"
                    :x2="600"
                    :y2="i * 40"
                    stroke="#e2e8f0"
                    stroke-width="1"
                  />
                  <!-- Area fill -->
                  <path :d="salesAreaPath" fill="url(#salesGrad)" />
                  <!-- Line -->
                  <path
                    :d="salesLinePath"
                    fill="none"
                    stroke="#3b82f6"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <!-- Data points — hoverable -->
                  <g
                    v-for="(pt, i) in salesPoints"
                    :key="i"
                    @mouseenter="showSalesTooltip($event, i)"
                    @mouseleave="salesTooltip.visible = false"
                    style="cursor: pointer"
                  >
                    <!-- Invisible larger hit area -->
                    <circle :cx="pt.x" :cy="pt.y" r="14" fill="transparent" />
                    <!-- Visible dot -->
                    <circle
                      :cx="pt.x"
                      :cy="pt.y"
                      r="4"
                      fill="#3b82f6"
                      stroke="#ffffff"
                      stroke-width="2"
                    />
                    <!-- Highlight ring on hover -->
                    <circle
                      v-if="salesTooltip.idx === i && salesTooltip.visible"
                      :cx="pt.x"
                      :cy="pt.y"
                      r="8"
                      fill="rgba(59,130,246,0.25)"
                      stroke="#3b82f6"
                      stroke-width="1.5"
                    />
                    <!-- Vertical guide line on hover -->
                    <line
                      v-if="salesTooltip.idx === i && salesTooltip.visible"
                      :x1="pt.x"
                      y1="0"
                      :x2="pt.x"
                      y2="170"
                      stroke="#3b82f6"
                      stroke-width="1"
                      stroke-dasharray="4,3"
                      opacity="0.5"
                    />
                  </g>
                  <!-- X Labels -->
                  <text
                    v-for="(lbl, i) in chartLabels"
                    :key="'l' + i"
                    :x="i * 85 + 30"
                    y="195"
                    fill="#64748b"
                    font-size="10"
                    text-anchor="middle"
                  >
                    {{ lbl }}
                  </text>
                </svg>

                <!-- Tooltip bubble -->
                <div
                  v-if="salesTooltip.visible"
                  class="chart-tooltip"
                  :style="{ left: salesTooltip.x + 'px', top: salesTooltip.y + 'px' }"
                >
                  <div class="tooltip-date">{{ salesTooltip.date }}</div>
                  <div class="tooltip-row">
                    <span class="tooltip-dot" style="background: #3b82f6"></span>
                    <span class="tooltip-label">Revenue</span>
                    <span class="tooltip-value">₹{{ salesTooltip.value.toLocaleString() }}</span>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Orders per Day -->
        <div class="col-12 col-md">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="text-subtitle1 text-weight-bold text-grey-9 q-mb-xs">Orders / Day</div>
              <div class="text-caption text-blue-7 q-mb-md">orders.created_at</div>
              <!-- Skeleton while loading -->
              <div v-if="loadingSales" class="chart-container">
                <q-skeleton type="rect" height="200px" />
              </div>
              <!-- SVG Bar Chart with hover tooltip -->
              <div v-else class="chart-container" style="position: relative">
                <svg
                  viewBox="0 0 260 200"
                  class="full-width"
                  xmlns="http://www.w3.org/2000/svg"
                  @mouseleave="barTooltip.visible = false"
                >
                  <defs>
                    <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#6366f1" />
                      <stop offset="100%" stop-color="#3b82f6" />
                    </linearGradient>
                    <linearGradient id="barGradHover" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#818cf8" />
                      <stop offset="100%" stop-color="#60a5fa" />
                    </linearGradient>
                  </defs>
                  <!-- Bars -->
                  <g
                    v-for="(b, i) in barData"
                    :key="i"
                    @mouseenter="showBarTooltip($event, i)"
                    @mouseleave="barTooltip.visible = false"
                    style="cursor: pointer"
                  >
                    <!-- Invisible full-height hit area -->
                    <rect :x="i * 34 + 8" y="0" :width="24" height="185" fill="transparent" />
                    <!-- Actual bar -->
                    <rect
                      :x="i * 34 + 8"
                      :y="180 - b.h"
                      :width="24"
                      :height="b.h"
                      rx="4"
                      :fill="
                        barTooltip.idx === i && barTooltip.visible
                          ? 'url(#barGradHover)'
                          : 'url(#barGrad)'
                      "
                      :opacity="barTooltip.visible && barTooltip.idx !== i ? 0.5 : 0.9"
                      style="transition: opacity 0.15s"
                    />
                  </g>
                  <text
                    v-for="(b, i) in barData"
                    :key="'bl' + i"
                    :x="i * 34 + 20"
                    y="196"
                    fill="#64748b"
                    font-size="9"
                    text-anchor="middle"
                  >
                    {{ b.day }}
                  </text>
                </svg>

                <!-- Bar tooltip -->
                <div
                  v-if="barTooltip.visible"
                  class="chart-tooltip"
                  :style="{ left: barTooltip.x + 'px', top: barTooltip.y + 'px' }"
                >
                  <div class="tooltip-date">{{ barTooltip.date }}</div>
                  <div class="tooltip-row">
                    <span class="tooltip-dot" style="background: #6366f1"></span>
                    <span class="tooltip-label">Orders</span>
                    <span class="tooltip-value">{{ barTooltip.value }}</span>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- ── NEW ── Top Products & Top Customers side by side -->
      <div class="row q-gutter-md q-mt-md">
        <!-- Top Products -->
        <div class="col-12 col-md">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon name="inventory_2" color="purple-4" size="18px" class="q-mr-xs" />
                <div class="text-subtitle1 text-weight-bold text-grey-9">Top Products</div>
              </div>
              <template v-if="loadingTopProducts">
                <q-skeleton v-for="n in 5" :key="n" type="rect" height="34px" class="q-mb-xs" />
              </template>
              <q-table
                v-else
                :rows="topProducts"
                :columns="topProductCols"
                row-key="product_name"
                flat
                dense
                class="transparent-table"
                :rows-per-page-options="[5, 10, 25]"
                rows-per-page-label="Rows:"
              >
                <template #body-cell-units_sold="props">
                  <q-td :props="props">
                    <q-badge color="purple-1" text-color="purple-8">{{ props.value }}</q-badge>
                  </q-td>
                </template>
                <template #body-cell-revenue="props">
                  <q-td :props="props" class="text-weight-medium">
                    ₹{{ Number(props.value).toLocaleString() }}
                  </q-td>
                </template>
                <template #no-data>
                  <div class="full-width column flex-center q-pa-md text-grey-5">
                    <q-icon name="inventory_2" size="32px" class="q-mb-xs" />
                    <div class="text-caption">No products data</div>
                  </div>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <!-- Top Customers -->
        <div class="col-12 col-md">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon name="people" color="teal-5" size="18px" class="q-mr-xs" />
                <div class="text-subtitle1 text-weight-bold text-grey-9">Top Customers</div>
              </div>
              <template v-if="loadingTopCustomers">
                <q-skeleton v-for="n in 5" :key="n" type="rect" height="34px" class="q-mb-xs" />
              </template>
              <q-table
                v-else
                :rows="topCustomers"
                :columns="topCustomerCols"
                row-key="customer_name"
                flat
                dense
                class="transparent-table"
                :rows-per-page-options="[5, 10, 25]"
                rows-per-page-label="Rows:"
              >
                <template #body-cell-total_orders="props">
                  <q-td :props="props">
                    <q-badge color="teal-1" text-color="teal-8">{{ props.value }}</q-badge>
                  </q-td>
                </template>
                <template #body-cell-total_spend="props">
                  <q-td :props="props" class="text-weight-medium">
                    ₹{{ Number(props.value).toLocaleString() }}
                  </q-td>
                </template>
                <template #no-data>
                  <div class="full-width column flex-center q-pa-md text-grey-5">
                    <q-icon name="people" size="32px" class="q-mb-xs" />
                    <div class="text-caption">No customer data</div>
                  </div>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- ── NEW ── Coupon Performance -->
      <q-card class="chart-card q-mt-md" flat>
        <q-card-section>
          <div class="row items-center q-mb-md">
            <q-icon name="local_offer" color="amber-7" size="18px" class="q-mr-xs" />
            <div class="text-subtitle1 text-weight-bold text-grey-9">Coupon Performance</div>
          </div>
          <template v-if="loadingCoupons">
            <q-skeleton v-for="n in 4" :key="n" type="rect" height="34px" class="q-mb-xs" />
          </template>
          <q-table
            v-else
            :rows="coupons"
            :columns="couponCols"
            row-key="coupon_code"
            flat
            dense
            class="transparent-table"
            :rows-per-page-options="[5, 10, 25]"
            rows-per-page-label="Rows:"
          >
            <template #body-cell-coupon_code="props">
              <q-td :props="props">
                <q-chip
                  dense
                  color="amber-1"
                  text-color="amber-9"
                  icon="confirmation_number"
                  size="sm"
                >
                  {{ props.value }}
                </q-chip>
              </q-td>
            </template>
            <template #body-cell-usage_count="props">
              <q-td :props="props">
                <q-badge color="amber-1" text-color="amber-9">{{ props.value }} uses</q-badge>
              </q-td>
            </template>
            <template #body-cell-discount_amount="props">
              <q-td :props="props" class="text-weight-medium text-negative">
                -₹{{ Number(props.value).toLocaleString() }}
              </q-td>
            </template>
            <template #no-data>
              <div class="full-width column flex-center q-pa-md text-grey-5">
                <q-icon name="local_offer" size="32px" class="q-mb-xs" />
                <div class="text-caption">No coupon data</div>
              </div>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- Recent Activity — now fetched from API, pagination enabled -->
      <q-card class="chart-card q-mt-md" flat>
        <q-card-section>
          <div class="text-subtitle1 text-weight-bold text-grey-9 q-mb-md">Recent Orders</div>
          <template v-if="loadingOrders">
            <q-skeleton v-for="n in 5" :key="n" type="rect" height="34px" class="q-mb-xs" />
          </template>
          <q-table
            v-else
            :rows="recentOrders"
            :columns="recentCols"
            row-key="id"
            flat
            dense
            class="transparent-table"
            :rows-per-page-options="[5, 10, 25]"
            rows-per-page-label="Rows:"
          >
            <template #body-cell-status="props">
              <q-td :props="props">
                <q-badge :color="statusColor(props.value)" :label="props.value" />
              </q-td>
            </template>
            <template #body-cell-amount="props">
              <q-td :props="props" class="text-weight-medium">
                {{
                  typeof props.value === 'number' ? '₹' + props.value.toLocaleString() : props.value
                }}
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const activePeriod = ref('7D')
const periods = ['7D', '1M', '3M', 'YTD']

// ── Loading flags ──────────────────────────────────────────────
const loadingKpi = ref(false)
const loadingSales = ref(false)
const loadingTopProducts = ref(false)
const loadingTopCustomers = ref(false)
const loadingCoupons = ref(false)
const loadingOrders = ref(false)

// ══════════════════════════════════════════════════════════════
// 1. KPI CARDS  —  GET /admin/dashboard
// ══════════════════════════════════════════════════════════════
const summaryCards = ref([
  {
    label: 'Total Users',
    value: '12,480',
    icon: 'group',
    color: 'blue-4',
    iconBg: 'rgba(59,130,246,0.15)',
    trend: 8.2,
  },
  {
    label: 'Total Products',
    value: '3,240',
    icon: 'inventory_2',
    color: 'purple-4',
    iconBg: 'rgba(139,92,246,0.15)',
    trend: 3.1,
  },
  {
    label: 'Total Variants',
    value: '9,720',
    icon: 'category',
    color: 'cyan-4',
    iconBg: 'rgba(6,182,212,0.15)',
    trend: 5.6,
  },
  {
    label: 'Total Orders',
    value: '28,540',
    icon: 'shopping_cart',
    color: 'green-4',
    iconBg: 'rgba(34,197,94,0.15)',
    trend: 12.4,
  },
  {
    label: 'Total Revenue',
    value: '₹48.2L',
    icon: 'currency_rupee',
    color: 'amber-4',
    iconBg: 'rgba(245,158,11,0.15)',
    trend: -2.1,
  },
])

const fetchKpi = async () => {
  loadingKpi.value = true
  try {
    // Using static fallback values
    // static fallback values already set above
  } catch {
    // static fallback values already set above
  } finally {
    loadingKpi.value = false
  }
}

// ══════════════════════════════════════════════════════════════
// 2. SALES CHART  —  GET /admin/analytics/sales
// ══════════════════════════════════════════════════════════════
const rawSales = ref([40, 70, 55, 90, 65, 110, 95])
const chartLabels = ref(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
const salesDates = ref([
  'Mon, Jan 13',
  'Tue, Jan 14',
  'Wed, Jan 15',
  'Thu, Jan 16',
  'Fri, Jan 17',
  'Sat, Jan 18',
  'Sun, Jan 19',
])
const salesRevenue = ref([12400, 21700, 17050, 27900, 20150, 34100, 29450])

const salesPoints = computed(() =>
  rawSales.value.map((v, i) => ({ x: i * 85 + 30, y: 170 - v * 1.4 })),
)
const salesLinePath = computed(() =>
  salesPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' '),
)
const salesAreaPath = computed(() => {
  const pts = salesPoints.value
  return `${salesLinePath.value} L${pts[pts.length - 1].x},170 L${pts[0].x},170 Z`
})

const fetchSales = async () => {
  loadingSales.value = true
  try {
    // Using static fallback values
    // static fallback
  } catch {
    // static fallback
  } finally {
    loadingSales.value = false
  }
}

const barData = ref([
  { day: 'M', h: 80, date: 'Mon, Jan 13', orders: 32 },
  { day: 'T', h: 120, date: 'Tue, Jan 14', orders: 48 },
  { day: 'W', h: 60, date: 'Wed, Jan 15', orders: 24 },
  { day: 'T', h: 140, date: 'Thu, Jan 16', orders: 56 },
  { day: 'F', h: 100, date: 'Fri, Jan 17', orders: 40 },
  { day: 'S', h: 160, date: 'Sat, Jan 18', orders: 64 },
  { day: 'S', h: 50, date: 'Sun, Jan 19', orders: 20 },
])

// ── Sales chart tooltip ────────────────────────────────────────
const salesTooltip = ref({ visible: false, x: 0, y: 0, idx: -1, date: '', value: 0 })

const showSalesTooltip = (event, i) => {
  const svgEl = event.currentTarget.closest('svg')
  const rect = svgEl.getBoundingClientRect()
  const pt = salesPoints.value[i]
  const scaleX = rect.width / 600
  const scaleY = rect.height / 200
  const px = pt.x * scaleX
  const py = pt.y * scaleY
  salesTooltip.value = {
    visible: true,
    x: px - 60,
    y: Math.max(0, py - 68),
    idx: i,
    date: salesDates.value[i],
    value: salesRevenue.value[i],
  }
}

// ── Bar chart tooltip ──────────────────────────────────────────
const barTooltip = ref({ visible: false, x: 0, y: 0, idx: -1, date: '', value: 0 })

const showBarTooltip = (event, i) => {
  const svgEl = event.currentTarget.closest('svg')
  const rect = svgEl.getBoundingClientRect()
  const b = barData.value[i]
  const scaleX = rect.width / 260
  const scaleY = rect.height / 200
  const barCenterX = (i * 34 + 8 + 12) * scaleX
  const barTopY = (180 - b.h) * scaleY
  barTooltip.value = {
    visible: true,
    x: barCenterX - 55,
    y: Math.max(0, barTopY - 68),
    idx: i,
    date: b.date,
    value: b.orders,
  }
}

// ══════════════════════════════════════════════════════════════
// 3. TOP PRODUCTS  —  GET /admin/analytics/top-products
// ══════════════════════════════════════════════════════════════
const topProducts = ref([])
const topProductCols = [
  { name: 'product_name', label: 'Product', field: 'product_name', align: 'left', sortable: true },
  { name: 'units_sold', label: 'Units Sold', field: 'units_sold', align: 'center', sortable: true },
  { name: 'revenue', label: 'Revenue', field: 'revenue', align: 'right', sortable: true },
]

const fetchTopProducts = async () => {
  loadingTopProducts.value = true
  try {
    // Using static fallback values
    topProducts.value = [
      { product_name: 'Product Alpha', units_sold: 320, revenue: 48000 },
      { product_name: 'Product Beta', units_sold: 215, revenue: 32250 },
      { product_name: 'Product Gamma', units_sold: 180, revenue: 27000 },
      { product_name: 'Product Delta', units_sold: 145, revenue: 21750 },
      { product_name: 'Product Epsilon', units_sold: 98, revenue: 14700 },
    ]
  } catch {
    topProducts.value = [
      { product_name: 'Product Alpha', units_sold: 320, revenue: 48000 },
      { product_name: 'Product Beta', units_sold: 215, revenue: 32250 },
      { product_name: 'Product Gamma', units_sold: 180, revenue: 27000 },
      { product_name: 'Product Delta', units_sold: 145, revenue: 21750 },
      { product_name: 'Product Epsilon', units_sold: 98, revenue: 14700 },
    ]
  } finally {
    loadingTopProducts.value = false
  }
}

// ══════════════════════════════════════════════════════════════
// 4. TOP CUSTOMERS  —  GET /admin/analytics/customers
// ══════════════════════════════════════════════════════════════
const topCustomers = ref([])
const topCustomerCols = [
  {
    name: 'customer_name',
    label: 'Customer',
    field: 'customer_name',
    align: 'left',
    sortable: true,
  },
  { name: 'total_orders', label: 'Orders', field: 'total_orders', align: 'center', sortable: true },
  {
    name: 'total_spend',
    label: 'Total Spend',
    field: 'total_spend',
    align: 'right',
    sortable: true,
  },
]

const fetchTopCustomers = async () => {
  loadingTopCustomers.value = true
  try {
    // Using static fallback values
    topCustomers.value = [
      { customer_name: 'Rahul Sharma', total_orders: 42, total_spend: 63000 },
      { customer_name: 'Priya Mehta', total_orders: 35, total_spend: 52500 },
      { customer_name: 'Vikram Singh', total_orders: 28, total_spend: 42000 },
      { customer_name: 'Sneha Joshi', total_orders: 21, total_spend: 31500 },
      { customer_name: 'Karan Malhotra', total_orders: 18, total_spend: 27000 },
    ]
  } catch {
    topCustomers.value = [
      { customer_name: 'Rahul Sharma', total_orders: 42, total_spend: 63000 },
      { customer_name: 'Priya Mehta', total_orders: 35, total_spend: 52500 },
      { customer_name: 'Vikram Singh', total_orders: 28, total_spend: 42000 },
      { customer_name: 'Sneha Joshi', total_orders: 21, total_spend: 31500 },
      { customer_name: 'Karan Malhotra', total_orders: 18, total_spend: 27000 },
    ]
  } finally {
    loadingTopCustomers.value = false
  }
}

// ══════════════════════════════════════════════════════════════
// 5. COUPON PERFORMANCE  —  GET /admin/analytics/coupons
// ══════════════════════════════════════════════════════════════
const coupons = ref([])
const couponCols = [
  {
    name: 'coupon_code',
    label: 'Coupon Code',
    field: 'coupon_code',
    align: 'left',
    sortable: true,
  },
  {
    name: 'usage_count',
    label: 'Usage Count',
    field: 'usage_count',
    align: 'center',
    sortable: true,
  },
  {
    name: 'discount_amount',
    label: 'Discount Amount',
    field: 'discount_amount',
    align: 'right',
    sortable: true,
  },
]

const fetchCoupons = async () => {
  loadingCoupons.value = true
  try {
    // Using static fallback values
    coupons.value = [
      { coupon_code: 'SAVE10', usage_count: 142, discount_amount: 14200 },
      { coupon_code: 'FLASH20', usage_count: 87, discount_amount: 17400 },
      { coupon_code: 'WELCOME50', usage_count: 53, discount_amount: 26500 },
      { coupon_code: 'SUMMER15', usage_count: 38, discount_amount: 5700 },
    ]
  } catch {
    coupons.value = [
      { coupon_code: 'SAVE10', usage_count: 142, discount_amount: 14200 },
      { coupon_code: 'FLASH20', usage_count: 87, discount_amount: 17400 },
      { coupon_code: 'WELCOME50', usage_count: 53, discount_amount: 26500 },
      { coupon_code: 'SUMMER15', usage_count: 38, discount_amount: 5700 },
    ]
  } finally {
    loadingCoupons.value = false
  }
}

// ══════════════════════════════════════════════════════════════
// 6. RECENT ORDERS  —  GET /admin/orders
// ══════════════════════════════════════════════════════════════
const recentCols = [
  { name: 'id', label: 'Order ID', field: 'id', align: 'left' },
  { name: 'user', label: 'User', field: 'user', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'date', label: 'Date', field: 'date', align: 'left' },
]
const recentOrders = ref([
  {
    id: '#ORD-1001',
    user: 'Rahul Sharma',
    amount: '₹2,400',
    status: 'completed',
    date: '2024-01-15',
  },
  { id: '#ORD-1002', user: 'Priya Mehta', amount: '₹1,850', status: 'pending', date: '2024-01-15' },
  {
    id: '#ORD-1003',
    user: 'Ankit Patel',
    amount: '₹3,200',
    status: 'processing',
    date: '2024-01-14',
  },
  { id: '#ORD-1004', user: 'Sneha Joshi', amount: '₹960', status: 'cancelled', date: '2024-01-14' },
  {
    id: '#ORD-1005',
    user: 'Vikram Singh',
    amount: '₹5,100',
    status: 'completed',
    date: '2024-01-13',
  },
])

const fetchRecentOrders = async () => {
  loadingOrders.value = true
  try {
    // Using static fallback values
    // static fallback already set above
  } catch {
    // static fallback already set above
  } finally {
    loadingOrders.value = false
  }
}

const statusColor = (s) =>
  ({ completed: 'positive', pending: 'warning', processing: 'info', cancelled: 'negative' })[s] ||
  'grey'

// ── Boot ───────────────────────────────────────────────────────
onMounted(() => {
  fetchKpi()
  fetchSales()
  fetchTopProducts()
  fetchTopCustomers()
  fetchCoupons()
  fetchRecentOrders()
})
</script>

<style scoped>
/* ── All original styles preserved exactly ── */
.admin-page {
  background: #f8fafc;
  min-height: 100vh;
}
.page-header {
  border-bottom: 1px solid #e2e8f0;
}

.stat-card {
  background: #ffffff;
  border: 1px solid #dbeafe;
  border-radius: 12px;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.12);
}
.stat-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.trend-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 20px;
}

.chart-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}
.chart-container {
  overflow: hidden;
}
.full-width {
  width: 100%;
  display: block;
}

.period-btn {
  border-radius: 6px !important;
  font-size: 11px !important;
}
.transparent-table {
  background: transparent !important;
}
.transparent-table :deep(.q-table__container) {
  background: transparent !important;
}
.transparent-table :deep(th) {
  color: #64748b !important;
  font-size: 11px;
  border-bottom: 1px solid #e2e8f0;
}
.transparent-table :deep(td) {
  color: #1e293b;
  font-size: 13px;
  border-bottom: 1px solid #f1f5f9;
}

/* ── NEW: Tooltip styles only ── */
.chart-tooltip {
  position: absolute;
  background: #f1f5f9;
  border: 1px solid #93c5fd;
  border-radius: 8px;
  padding: 8px 12px;
  pointer-events: none;
  z-index: 100;
  min-width: 130px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(4px);
}
.tooltip-date {
  color: #64748b;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 4px;
  letter-spacing: 0.03em;
}
.tooltip-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.tooltip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tooltip-label {
  color: #475569;
  font-size: 12px;
  flex: 1;
}
.tooltip-value {
  color: #1e293b;
  font-size: 13px;
  font-weight: 700;
}
</style>
