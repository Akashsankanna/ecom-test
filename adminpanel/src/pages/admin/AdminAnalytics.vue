<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Analytics</div>
          <div class="text-caption text-blue-7">Sales, orders, users & top products</div>
        </div>
        <div class="row q-gutter-sm items-center">
          <q-btn-toggle
            v-model="period"
            :options="[
              { label: '7D', value: '7d' },
              { label: '30D', value: '30d' },
              { label: '3M', value: '3m' },
              { label: 'YTD', value: 'ytd' },
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
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- Summary Cards -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md-3" v-for="s in summaryCards" :key="s.label">
          <q-card class="stat-card" flat>
            <q-card-section class="q-pa-md">
              <div class="row items-center justify-between q-mb-sm">
                <div class="stat-icon" :style="{ background: s.bg }">
                  <q-icon :name="s.icon" :color="s.color" size="20px" />
                </div>
                <q-badge :color="s.change > 0 ? 'positive' : 'negative'">
                  <q-icon
                    :name="s.change > 0 ? 'trending_up' : 'trending_down'"
                    size="12px"
                    class="q-mr-xs"
                  />{{ Math.abs(s.change) }}%
                </q-badge>
              </div>
              <div class="text-h5 text-grey-9 text-weight-bold">{{ s.value }}</div>
              <div class="text-caption text-blue-7">{{ s.label }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Charts Row 1 -->
      <div class="row q-gutter-md q-mb-md">
        <!-- Sales Line Chart -->
        <div class="col-12 col-md-7">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="text-subtitle1 text-grey-9 text-weight-bold q-mb-xs">Sales Revenue</div>
              <div class="text-caption text-blue-7 q-mb-md">GET /admin/analytics/sales</div>
              <svg viewBox="0 0 560 200" class="chart-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="salesG" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#3b82f6" stop-opacity=".4" />
                    <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
                  </linearGradient>
                  <linearGradient id="ordersG" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#8b5cf6" stop-opacity=".3" />
                    <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <line
                  v-for="i in 4"
                  :key="i"
                  :x1="0"
                  :y1="i * 40"
                  :x2="560"
                  :y2="i * 40"
                  stroke="#e2e8f0"
                  stroke-width="1"
                />
                <path :d="salesArea" fill="url(#salesG)" />
                <path
                  :d="salesLine"
                  fill="none"
                  stroke="#3b82f6"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <circle
                  v-for="(p, i) in salesPts"
                  :key="i"
                  :cx="p.x"
                  :cy="p.y"
                  r="4"
                  fill="#3b82f6"
                  stroke="#ffffff"
                  stroke-width="2"
                />
                <text
                  v-for="(l, i) in chartLabels"
                  :key="'l' + i"
                  :x="i * 80 + 20"
                  y="195"
                  fill="#64748b"
                  font-size="10"
                  text-anchor="middle"
                >
                  {{ l }}
                </text>
              </svg>
              <!-- Legend -->
              <div class="row q-gutter-md q-mt-xs">
                <div class="row items-center q-gutter-xs">
                  <div
                    style="width: 12px; height: 3px; background: #3b82f6; border-radius: 2px"
                  ></div>
                  <span class="text-caption text-blue-7">Revenue</span>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Orders Bar Chart -->
        <div class="col-12 col-md">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="text-subtitle1 text-grey-9 text-weight-bold q-mb-xs">Orders / Day</div>
              <div class="text-caption text-blue-7 q-mb-md">GET /admin/analytics/orders</div>
              <svg viewBox="0 0 260 200" class="chart-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="barG" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#6366f1" />
                    <stop offset="100%" stop-color="#3b82f6" />
                  </linearGradient>
                </defs>
                <rect
                  v-for="(b, i) in barData"
                  :key="i"
                  :x="i * 34 + 8"
                  :y="180 - b.h"
                  :width="24"
                  :height="b.h"
                  rx="4"
                  fill="url(#barG)"
                  opacity=".9"
                />
                <text
                  v-for="(b, i) in barData"
                  :key="'t' + i"
                  :x="i * 34 + 20"
                  y="197"
                  fill="#64748b"
                  font-size="9"
                  text-anchor="middle"
                >
                  {{ b.day }}
                </text>
              </svg>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Charts Row 2 -->
      <div class="row q-gutter-md q-mb-md">
        <!-- User Growth -->
        <div class="col-12 col-md-5">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="text-subtitle1 text-grey-9 text-weight-bold q-mb-xs">User Growth</div>
              <div class="text-caption text-blue-7 q-mb-md">GET /admin/analytics/users</div>
              <svg viewBox="0 0 380 160" class="chart-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="userG" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#10b981" stop-opacity=".4" />
                    <stop offset="100%" stop-color="#10b981" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <line
                  v-for="i in 3"
                  :key="i"
                  :x1="0"
                  :y1="i * 40"
                  :x2="380"
                  :y2="i * 40"
                  stroke="#e2e8f0"
                  stroke-width="1"
                />
                <path :d="userArea" fill="url(#userG)" />
                <path
                  :d="userLine"
                  fill="none"
                  stroke="#10b981"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <text
                  v-for="(l, i) in monthLabels"
                  :key="l"
                  :x="i * 58 + 20"
                  y="155"
                  fill="#64748b"
                  font-size="9"
                  text-anchor="middle"
                >
                  {{ l }}
                </text>
              </svg>
            </q-card-section>
          </q-card>
        </div>

        <!-- Top Products -->
        <div class="col-12 col-md">
          <q-card class="chart-card" flat>
            <q-card-section>
              <div class="text-subtitle1 text-grey-9 text-weight-bold q-mb-xs">Top Products</div>
              <div class="text-caption text-blue-7 q-mb-md">GET /admin/analytics/top-products</div>
              <div v-for="(p, i) in topProducts" :key="p.name" class="q-mb-sm">
                <div class="row items-center justify-between q-mb-xs">
                  <div class="row items-center q-gutter-xs">
                    <q-badge :color="rankColors[i]" :label="'#' + (i + 1)" size="xs" />
                    <span class="text-grey-9 text-caption">{{ p.name }}</span>
                  </div>
                  <span class="text-green-4 text-caption text-weight-bold"
                    >₹{{ p.revenue.toLocaleString() }}</span
                  >
                </div>
                <q-linear-progress
                  :value="p.revenue / topProducts[0].revenue"
                  :color="rankColors[i]"
                  track-color="grey-2"
                  rounded
                  style="height: 5px"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Analytics Summary Table -->
      <q-card class="chart-card" flat>
        <q-card-section>
          <div class="text-subtitle1 text-grey-9 text-weight-bold q-mb-md">
            Monthly Summary — GET /admin/analytics/summary
          </div>
          <q-table
            :rows="monthlySummary"
            :columns="sumCols"
            row-key="month"
            flat
            dense
            :rows-per-page-options="[12]"
            class="sum-table"
            hide-bottom
          >
            <template #body-cell-revenue="props">
              <q-td :props="props"
                ><span class="text-green-4 text-weight-medium">{{ props.value }}</span></q-td
              >
            </template>
            <template #body-cell-growth="props">
              <q-td :props="props">
                <span :class="props.row.growthVal > 0 ? 'text-positive' : 'text-negative'">
                  <q-icon
                    :name="props.row.growthVal > 0 ? 'arrow_upward' : 'arrow_downward'"
                    size="12px"
                  />
                  {{ props.value }}
                </span>
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
const period = ref('7d')

const rawSales = [35, 65, 50, 90, 70, 110, 85, 95, 60, 120, 100, 130]
const chartLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const monthLabels = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const barData = [
  { day: 'M', h: 70 },
  { day: 'T', h: 110 },
  { day: 'W', h: 55 },
  { day: 'T', h: 140 },
  { day: 'F', h: 95 },
  { day: 'S', h: 160 },
  { day: 'S', h: 45 },
]
const rankColors = ['amber-6', 'blue-5', 'cyan-5', 'purple-5', 'green-5']

const salesPts = computed(() =>
  chartLabels.map((l, i) => ({ x: i * 80 + 20, y: 160 - rawSales[i] * 1.2 })),
)
const salesLine = computed(() =>
  salesPts.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' '),
)
const salesArea = computed(() => {
  const pts = salesPts.value
  return `${salesLine.value} L${pts[pts.length - 1].x},170 L${pts[0].x},170 Z`
})

const userRaw = [20, 45, 35, 65, 50, 80]
const userPts = computed(() =>
  monthLabels.map((l, i) => ({ x: i * 58 + 20, y: 130 - userRaw[i] * 1.3 })),
)
const userLine = computed(() =>
  userPts.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' '),
)
const userArea = computed(() => {
  const pts = userPts.value
  return `${userLine.value} L${pts[pts.length - 1].x},140 L${pts[0].x},140 Z`
})

const summaryCards = ref([
  {
    label: 'Total Revenue',
    value: '₹4.82L',
    icon: 'currency_rupee',
    color: 'amber-4',
    bg: 'rgba(245,158,11,.12)',
    change: 12.4,
  },
  {
    label: 'Total Orders',
    value: '2,854',
    icon: 'shopping_cart',
    color: 'blue-4',
    bg: 'rgba(59,130,246,.12)',
    change: 8.1,
  },
  {
    label: 'New Users',
    value: '1,248',
    icon: 'person_add',
    color: 'green-4',
    bg: 'rgba(34,197,94,.12)',
    change: 5.6,
  },
  {
    label: 'Avg Order Value',
    value: '₹1,688',
    icon: 'analytics',
    color: 'purple-4',
    bg: 'rgba(139,92,246,.12)',
    change: -2.3,
  },
])

const topProducts = ref([
  { name: 'Wireless Earbuds Pro', revenue: 124800, units: 50 },
  { name: 'Mechanical Keyboard', revenue: 119800, units: 20 },
  { name: 'Running Shoes X1', revenue: 87475, units: 25 },
  { name: 'Cotton T-Shirt Classic', revenue: 35940, units: 60 },
  { name: 'Python Programming', revenue: 24950, units: 50 },
])

const monthlySummary = ref([
  { month: 'Jan 2024', revenue: '₹82,400', orders: 48, users: 210, growth: '+12%', growthVal: 12 },
  { month: 'Dec 2023', revenue: '₹73,500', orders: 42, users: 185, growth: '+8%', growthVal: 8 },
  { month: 'Nov 2023', revenue: '₹68,100', orders: 38, users: 160, growth: '+5%', growthVal: 5 },
  { month: 'Oct 2023', revenue: '₹64,800', orders: 36, users: 150, growth: '-2%', growthVal: -2 },
  { month: 'Sep 2023', revenue: '₹66,200', orders: 37, users: 155, growth: '+3%', growthVal: 3 },
])

const sumCols = [
  { name: 'month', label: 'Month', field: 'month', align: 'left' },
  { name: 'revenue', label: 'Revenue', field: 'revenue', align: 'left' },
  { name: 'orders', label: 'Orders', field: 'orders', align: 'center' },
  { name: 'users', label: 'New Users', field: 'users', align: 'center' },
  { name: 'growth', label: 'Growth', field: 'growth', align: 'center' },
]
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
  transition: transform 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
}
.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}
.chart-svg {
  width: 100%;
  display: block;
}
.sum-table {
  background: transparent !important;
}
.sum-table :deep(.q-table__container) {
  background: transparent !important;
}
.sum-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  border-bottom: 1px solid #dbeafe;
}
.sum-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}
</style>
