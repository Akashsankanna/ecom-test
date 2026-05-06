<template>
  <q-page class="admin-page">

    <!-- ══════════════════════════════════════════════
         LIST VIEW
    ══════════════════════════════════════════════ -->
    <template v-if="!selectedOrder">

      <!-- Header -->
      <div class="page-header q-px-lg q-pt-lg q-pb-md">
        <div class="row items-center justify-between">
          <div>
            <div class="text-h5 text-weight-bold text-grey-9">Orders</div>
            <div class="text-caption text-blue-7">Manage and track customer orders</div>
          </div>
          <q-badge color="blue-6" class="q-pa-sm">
            <q-icon name="shopping_cart" size="14px" class="q-mr-xs" />
            {{ filteredOrders.length }} Orders
          </q-badge>
        </div>
      </div>

      <!-- Filters -->
      <div class="q-px-lg q-pt-md q-pb-sm">
        <div class="row q-gutter-md items-center">
          <div class="col-12 col-sm">
            <q-input
              v-model="search"
              placeholder="Search by order ID or user ID..."
              dense standout="bg-blue-1" clearable
            >
              <template #prepend><q-icon name="search" color="blue-4" /></template>
            </q-input>
          </div>
          <div class="col-auto">
            <q-select
              v-model="statusFilter"
              :options="['All', ...ORDER_STATUSES]"
              label="Status" dense standout="bg-blue-1"
              style="min-width: 150px"
              @update:model-value="fetchOrders"
            />
          </div>
          <div class="col-auto">
            <q-select
              v-model="paymentFilter"
              :options="['All', ...PAYMENT_STATUSES]"
              label="Payment" dense standout="bg-blue-1"
              style="min-width: 130px"
              @update:model-value="fetchOrders"
            />
          </div>
          <div class="col-auto">
            <q-btn icon="refresh" flat round color="blue-6" @click="fetchOrders">
              <q-tooltip>Refresh</q-tooltip>
            </q-btn>
          </div>
        </div>
      </div>

      <!-- Orders Table -->
      <div class="q-px-lg q-pb-lg q-pt-sm">
        <q-card class="data-card" flat>
          <q-table
            :rows="filteredOrders"
            :columns="columns"
            row-key="id"
            flat
            :loading="loadingList"
            :rows-per-page-options="[10, 25, 50]"
            rows-per-page-label="Rows:"
            class="orders-table"
          >
            <!-- Order ID -->
            <template #body-cell-id="props">
              <q-td :props="props">
                <span class="text-weight-bold text-blue-8">#{{ props.value }}</span>
              </q-td>
            </template>

            <!-- User ID -->
            <template #body-cell-user_id="props">
              <q-td :props="props">
                <span class="text-grey-8">{{ props.value ?? '—' }}</span>
              </q-td>
            </template>

            <!-- Total Amount -->
            <template #body-cell-total_amount="props">
              <q-td :props="props">
                <span class="text-weight-medium text-grey-9">₹{{ fmtNum(props.value) }}</span>
              </q-td>
            </template>

            <!-- Final Amount -->
            <template #body-cell-final_amount="props">
              <q-td :props="props">
                <span class="text-weight-bold text-teal-8">
                  {{ props.value ? '₹' + fmtNum(props.value) : '—' }}
                </span>
              </q-td>
            </template>

            <!-- Status — inline coloured dropdown -->
            <template #body-cell-status="props">
              <q-td :props="props">
                <q-select
                  v-model="props.row.status"
                  :options="ORDER_STATUSES"
                  dense borderless
                  class="status-select"
                  :class="statusSelectClass(props.row.status)"
                  style="min-width: 155px"
                  @update:model-value="val => onListStatusChange(props.row, val)"
                >
                  <template #selected-item="scope">
                    <span class="status-label">{{ scope.opt }}</span>
                  </template>
                </q-select>
              </q-td>
            </template>

            <!-- Payment Status -->
            <template #body-cell-payment_status="props">
              <q-td :props="props">
                <q-badge :color="paymentColor(props.value)" :label="props.value" class="payment-badge" />
              </q-td>
            </template>

            <!-- Date -->
            <template #body-cell-created_at="props">
              <q-td :props="props">
                <span class="text-grey-7 text-caption">{{ formatDate(props.value) }}</span>
              </q-td>
            </template>

            <!-- Actions -->
            <template #body-cell-actions="props">
              <q-td :props="props" class="text-center">
                <q-btn round flat size="sm" icon="visibility" color="blue-5" @click="openDetail(props.row)">
                  <q-tooltip>View Details</q-tooltip>
                </q-btn>
              </q-td>
            </template>

            <template #no-data>
              <div class="full-width column flex-center q-pa-xl text-blue-7">
                <q-icon name="receipt_long" size="48px" class="q-mb-sm" />
                <div>No orders found</div>
              </div>
            </template>
          </q-table>
        </q-card>
      </div>
    </template>

    <!-- ══════════════════════════════════════════════
         DETAIL VIEW
    ══════════════════════════════════════════════ -->
    <template v-else>

      <!-- Header -->
      <div class="page-header q-px-lg q-pt-lg q-pb-md">
        <div class="row items-center justify-between">
          <div class="row items-center q-gutter-sm">
            <q-btn flat round dense icon="arrow_back" color="blue-6" @click="closeDetail" />
            <div>
              <div class="text-h5 text-weight-bold text-grey-9">Order #{{ selectedOrder.id }}</div>
              <div class="text-caption text-blue-7">View and manage order details</div>
            </div>
          </div>
          <div class="row q-gutter-sm items-center">
            <q-badge :color="statusBadgeColor(selectedOrder.status)" class="q-pa-sm text-subtitle2">
              {{ selectedOrder.status }}
            </q-badge>
            <q-btn
              label="Cancel Order" outline color="negative"
              no-caps icon="cancel" size="sm"
              :disable="!canCancel"
              @click="cancelDialog = true"
            />
          </div>
        </div>
      </div>

      <!-- Loading Skeleton -->
      <div class="q-px-lg q-pb-lg q-pt-md" v-if="loadingDetail">
        <div class="row q-gutter-md">
          <div class="col-12 col-md-8">
            <q-card flat class="data-card q-mb-md">
              <q-card-section>
                <q-skeleton type="text" width="40%" class="q-mb-md" />
                <q-skeleton type="rect" height="160px" />
              </q-card-section>
            </q-card>
            <q-card flat class="data-card">
              <q-card-section>
                <q-skeleton type="rect" height="240px" />
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-md">
            <q-card flat class="data-card">
              <q-card-section>
                <q-skeleton v-for="i in 6" :key="i" type="text" class="q-mb-sm" />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Detail Content -->
      <div class="q-px-lg q-pb-lg q-pt-md" v-else>
        <div class="row q-gutter-md">

          <!-- LEFT COLUMN -->
          <div class="col-12 col-md-8">

            <!-- Order Info -->
            <q-card flat class="data-card q-mb-md">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="receipt_long" color="blue-6" size="18px" class="q-mr-xs" />
                  Order Information
                </div>
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-sm-6 col-md-4" v-for="info in orderInfoFields" :key="info.label">
                    <div class="info-block">
                      <div class="info-label">{{ info.label }}</div>
                      <div class="info-value">{{ info.value }}</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Customer & Address -->
            <q-card flat class="data-card q-mb-md">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="person" color="blue-6" size="18px" class="q-mr-xs" />
                  Customer Information
                </div>
                <div class="row items-center q-gutter-md">
                  <q-avatar size="48px" color="blue-7" text-color="white" font-size="18px">
                    {{ initials(detailOrder.customer_name) }}
                  </q-avatar>
                  <div class="col">
                    <div class="text-weight-bold text-grey-9 text-subtitle1">
                      {{ detailOrder.customer_name || '—' }}
                    </div>
                    <div class="row q-gutter-md q-mt-xs">
                      <div class="row items-center q-gutter-xs">
                        <q-icon name="email" size="13px" color="blue-5" />
                        <span class="text-caption text-grey-7">{{ detailOrder.customer_email || '—' }}</span>
                      </div>
                      <div class="row items-center q-gutter-xs">
                        <q-icon name="phone" size="13px" color="blue-5" />
                        <span class="text-caption text-grey-7">{{ detailOrder.customer_phone || '—' }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <q-separator class="q-my-md" />

                <div class="row items-start q-gutter-sm" v-if="detailOrder.address_line1">
                  <q-icon name="location_on" color="blue-5" size="16px" class="q-mt-xs" />
                  <div>
                    <div class="text-caption text-grey-6 q-mb-xs">Shipping Address</div>
                    <div class="text-grey-9">
                      <span v-if="detailOrder.address_full_name">{{ detailOrder.address_full_name }}, </span>
                      {{ detailOrder.address_line1 }}
                      <span v-if="detailOrder.address_line2">, {{ detailOrder.address_line2 }}</span>
                      <span v-if="detailOrder.landmark">, {{ detailOrder.landmark }}</span>
                      <br />
                      {{ detailOrder.city }}, {{ detailOrder.state }}
                      {{ detailOrder.postal_code }}, {{ detailOrder.country }}
                    </div>
                  </div>
                </div>
                <div v-else class="text-caption text-grey-5">No address on file</div>
              </q-card-section>
            </q-card>

            <!-- Order Items -->
            <q-card flat class="data-card q-mb-md">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="inventory_2" color="blue-6" size="18px" class="q-mr-xs" />
                  Order Items
                  <q-badge color="blue-6" class="q-ml-sm">{{ detailItems.length }}</q-badge>
                </div>

                <div class="items-table">
                  <div class="items-header row q-px-md">
                    <div class="col-5">Product</div>
                    <div class="col-2">Variant / Size</div>
                    <div class="col-1 text-center">Qty</div>
                    <div class="col-2 text-right">Price</div>
                    <div class="col-2 text-right">Subtotal</div>
                  </div>

                  <div v-for="item in detailItems" :key="item.id" class="items-row row items-center q-px-md">
                    <div class="col-5">
                      <div class="row items-center q-gutter-sm no-wrap">
                        <q-img
                          v-if="item.product_image"
                          :src="item.product_image"
                          style="width:40px;height:40px;border-radius:6px;flex-shrink:0"
                          fit="cover"
                        >
                          <template #error>
                            <div class="img-placeholder"><q-icon name="image" color="grey-4" size="18px" /></div>
                          </template>
                        </q-img>
                        <div class="img-placeholder" v-else>
                          <q-icon name="image" color="grey-4" size="18px" />
                        </div>
                        <div>
                          <div class="text-grey-9 text-weight-medium">{{ item.product_name || '—' }}</div>
                          <div class="text-caption text-grey-5">SKU: {{ item.sku || 'N/A' }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="col-2">
                      <div class="column q-gutter-xs">
                        <q-chip v-if="item.color_name" size="xs" color="indigo-1" text-color="indigo-8" dense>
                          {{ item.color_name }}
                        </q-chip>
                        <q-chip v-if="item.size" size="xs" color="teal-1" text-color="teal-8" dense>
                          {{ item.size }}
                        </q-chip>
                        <span v-if="item.variant_name && !item.color_name && !item.size" class="text-caption text-grey-7">
                          {{ item.variant_name }}
                        </span>
                      </div>
                    </div>
                    <div class="col-1 text-center text-grey-9">{{ item.quantity }}</div>
                    <div class="col-2 text-right text-grey-7">₹{{ fmtNum(item.price) }}</div>
                    <div class="col-2 text-right text-green-7 text-weight-bold">
                      ₹{{ fmtNum(Number(item.price) * item.quantity) }}
                    </div>
                  </div>

                  <div v-if="!detailItems.length" class="q-pa-md text-center text-caption text-grey-5">
                    No items found
                  </div>
                </div>

                <!-- Totals -->
                <div class="totals-section q-mt-md">
                  <div class="totals-row">
                    <span class="totals-label">Gross Amount</span>
                    <span class="totals-value">₹{{ fmtNum(detailOrder.gross_amount || detailOrder.total_amount) }}</span>
                  </div>
                  <div class="totals-row" v-if="Number(detailOrder.coupon_discount_amount) > 0">
                    <span class="totals-label">Coupon Discount</span>
                    <span class="totals-discount">− ₹{{ fmtNum(detailOrder.coupon_discount_amount) }}</span>
                  </div>
                  <div class="totals-row" v-if="Number(detailOrder.additional_discount_amount) > 0">
                    <span class="totals-label">
                      Additional Discount
                      <span v-if="detailOrder.discount_reason" class="text-caption text-grey-5">
                        ({{ detailOrder.discount_reason }})
                      </span>
                    </span>
                    <span class="totals-discount">− ₹{{ fmtNum(detailOrder.additional_discount_amount) }}</span>
                  </div>
                  <div class="totals-row">
                    <span class="totals-label">Total Amount</span>
                    <span class="totals-value">₹{{ fmtNum(detailOrder.total_amount) }}</span>
                  </div>
                  <div class="totals-row" v-if="detailOrder.final_amount">
                    <span class="totals-label">Final Payable</span>
                    <span class="totals-total">₹{{ fmtNum(detailOrder.final_amount) }}</span>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Payment Details -->
            <q-card flat class="data-card q-mb-md">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="payments" color="blue-6" size="18px" class="q-mr-xs" />
                  Payment Details
                </div>
                <div class="row q-col-gutter-md">
                  <div v-for="p in paymentFields" :key="p.label" class="col-12 col-sm-6 col-md-4">
                    <div class="info-block">
                      <div class="info-label">{{ p.label }}</div>
                      <div class="info-value">
                        <q-badge v-if="p.isBadge" :color="p.color">{{ p.value }}</q-badge>
                        <span v-else>{{ p.value || '—' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Shipment Details (existing) -->
            <q-card flat class="data-card q-mb-md" v-if="detailShipment">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="local_shipping" color="blue-6" size="18px" class="q-mr-xs" />
                  Shipment Details
                </div>
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-sm-6 col-md-3">
                    <div class="info-block">
                      <div class="info-label">Courier</div>
                      <div class="info-value">{{ detailShipment.courier_name }}</div>
                    </div>
                  </div>
                  <div class="col-12 col-sm-6 col-md-3">
                    <div class="info-block">
                      <div class="info-label">Tracking #</div>
                      <div class="info-value">{{ detailShipment.tracking_number }}</div>
                    </div>
                  </div>
                  <div class="col-12 col-sm-6 col-md-3">
                    <div class="info-block">
                      <div class="info-label">Status</div>
                      <div class="info-value">
                        <q-badge :color="shipmentStatusColor(detailShipment.shipment_status)">
                          {{ detailShipment.shipment_status }}
                        </q-badge>
                      </div>
                    </div>
                  </div>
                  <div class="col-12 col-sm-6 col-md-3">
                    <div class="info-block">
                      <div class="info-label">Est. Delivery</div>
                      <div class="info-value">{{ detailShipment.estimated_delivery || '—' }}</div>
                    </div>
                  </div>
                  <div class="col-12" v-if="detailShipment.tracking_url">
                    <div class="info-block">
                      <div class="info-label">Tracking URL</div>
                      <div class="info-value">
                        <a :href="detailShipment.tracking_url" target="_blank" class="text-blue-6">
                          {{ detailShipment.tracking_url }}
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                <q-separator class="q-my-md" />
                <div class="row q-gutter-md items-end">
                  <div class="col">
                    <q-select
                      v-model="newShipmentStatus"
                      :options="SHIPMENT_STATUSES"
                      label="Update Shipment Status"
                      dense standout="bg-blue-1"
                    />
                  </div>
                  <div class="col-auto">
                    <q-btn
                      label="Update" color="blue-6" unelevated no-caps
                      :loading="updatingShipment"
                      :disable="newShipmentStatus === detailShipment.shipment_status"
                      @click="updateShipmentStatus"
                    />
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Create Shipment -->
            <q-card flat class="data-card q-mb-md"
              v-if="!detailShipment && selectedOrder.status !== 'CANCELLED'"
            >
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="local_shipping" color="blue-6" size="18px" class="q-mr-xs" />
                  Create Shipment
                </div>
                <div class="row q-gutter-md">
                  <div class="col-12 col-sm-6">
                    <q-input v-model="shipmentForm.courier_name" label="Courier Name *" dense standout="bg-blue-1" />
                  </div>
                  <div class="col-12 col-sm-6">
                    <q-input v-model="shipmentForm.tracking_number" label="Tracking Number *" dense standout="bg-blue-1" />
                  </div>
                  <div class="col-12 col-sm-6">
                    <q-input v-model="shipmentForm.estimated_delivery" label="Estimated Delivery" dense standout="bg-blue-1" type="date" />
                  </div>
                  <div class="col-12 col-sm-6">
                    <q-input v-model="shipmentForm.tracking_url" label="Tracking URL (optional)" dense standout="bg-blue-1" />
                  </div>
                </div>
                <q-btn
                  label="Create Shipment" color="blue-6" unelevated no-caps
                  class="q-mt-md" icon="local_shipping"
                  :loading="creatingShipment"
                  :disable="!shipmentForm.courier_name || !shipmentForm.tracking_number"
                  @click="createShipment"
                />
              </q-card-section>
            </q-card>

          </div>

          <!-- RIGHT COLUMN -->
          <div class="col-12 col-md">

            <!-- Update Status -->
            <q-card flat class="data-card q-mb-md">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="update" color="blue-6" size="18px" class="q-mr-xs" />
                  Update Status
                </div>
                <q-select
                  v-model="newStatus" :options="ORDER_STATUSES"
                  label="Order Status" dense standout="bg-blue-1" class="q-mb-md"
                />
                <q-btn
                  label="Update Status" color="blue-6" unelevated no-caps full-width icon="check"
                  :loading="updatingStatus"
                  :disable="newStatus === selectedOrder.status"
                  @click="updateStatus"
                />
              </q-card-section>
            </q-card>

            <!-- Summary -->
            <q-card flat class="data-card q-mb-md">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="summarize" color="blue-6" size="18px" class="q-mr-xs" />
                  Summary
                </div>
                <div class="summary-grid">
                  <div v-for="s in summaryFields" :key="s.label" class="summary-row">
                    <span class="summary-label">{{ s.label }}</span>
                    <span class="summary-value" :class="s.highlight ? 'text-blue-8 text-weight-bold' : ''">
                      {{ s.value }}
                    </span>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Order Timeline -->
            <q-card flat class="data-card">
              <q-card-section>
                <div class="section-title q-mb-md">
                  <q-icon name="history" color="blue-6" size="18px" class="q-mr-xs" />
                  Order Timeline
                </div>
                <q-timeline color="blue" dense>
                  <q-timeline-entry
                    v-for="h in detailHistorySorted" :key="h.id"
                    :title="h.status"
                    :subtitle="formatDate(h.changed_at)"
                    :color="statusBadgeColor(h.status)"
                    icon="circle"
                  >
                    <div class="text-caption text-grey-6" v-if="h.remarks">{{ h.remarks }}</div>
                    <div class="text-caption text-grey-5" v-if="h.changed_by_name">By: {{ h.changed_by_name }}</div>
                  </q-timeline-entry>
                </q-timeline>
                <div v-if="!detailHistorySorted.length" class="text-caption text-grey-5">
                  No history available
                </div>
              </q-card-section>
            </q-card>

          </div>
        </div>
      </div>

      <!-- Cancel Dialog -->
      <q-dialog v-model="cancelDialog" persistent>
        <q-card class="modal-card" style="width: 400px; max-width: 95vw">
          <q-card-section class="column items-center q-pa-lg">
            <q-icon name="warning" color="negative" size="52px" class="q-mb-sm" />
            <div class="text-grey-9 text-weight-bold text-subtitle1">Cancel Order?</div>
            <div class="text-caption text-grey-6 text-center q-mt-xs">
              This will cancel order <strong>#{{ selectedOrder.id }}</strong>.
              This action cannot be undone.
            </div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-input
              v-model="cancelReason" label="Reason for cancellation"
              dense standout="bg-blue-1" type="textarea" rows="2"
            />
          </q-card-section>
          <q-card-actions align="right" class="q-px-md q-pb-md">
            <q-btn label="Keep Order" flat no-caps v-close-popup color="blue-4" />
            <q-btn label="Cancel Order" color="negative" unelevated no-caps :loading="cancelling" @click="confirmCancel" />
          </q-card-actions>
        </q-card>
      </q-dialog>

    </template>
  </q-page>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import orderService from '../../services/orderService'

const $q = useQuasar()

// ══════ CONSTANTS from service ══════
const { ORDER_STATUSES, PAYMENT_STATUSES, SHIPMENT_STATUSES } = orderService

// ══════ HELPERS ══════
const fmtNum = (v) => Number(v || 0).toLocaleString('en-IN')

const formatDate = (dt) => {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const initials = (name) =>
  (name ?? '?').split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)

const statusBadgeColor = (s) => ({
  PENDING:        'warning',
  PAID:           'cyan-7',
  CONFIRMED:      'blue-7',
  PROCESSING:     'info',
  SHIPPED:        'purple-6',
  DELIVERED:      'positive',
  CANCELLED:      'negative',
  PAYMENT_FAILED: 'red-9',
}[s] || 'grey-6')

const statusSelectClass = (s) =>
  'status-' + (s || 'pending').toLowerCase().replace(/_/g, '-')

const paymentColor = (s) => ({
  SUCCESS: 'positive', PENDING: 'warning', FAILED: 'negative', REFUNDED: 'orange-7'
}[s] || 'grey-6')

const shipmentStatusColor = (s) => ({
  PENDING: 'grey-6', SHIPPED: 'blue-6', OUT_FOR_DELIVERY: 'orange-7',
  DELIVERED: 'positive', FAILED: 'negative', RETURNED: 'warning'
}[s] || 'grey-6')

const notify = (message, color = 'positive') =>
  $q.notify({ message, color, position: 'top-right', timeout: 2500 })

// ══════════════════════════════════════════════════════════════
// TABLE COLUMNS
// ══════════════════════════════════════════════════════════════
const columns = [
  { name: 'id',             label: 'Order ID', field: 'id',             align: 'left',   sortable: true },
  { name: 'user_id',        label: 'User ID',  field: 'user_id',        align: 'left',   sortable: true },
  { name: 'total_amount',   label: 'Amount',   field: 'total_amount',   align: 'left',   sortable: true },
  { name: 'final_amount',   label: 'Final',    field: 'final_amount',   align: 'left',   sortable: true },
  { name: 'status',         label: 'Status',   field: 'status',         align: 'left',   sortable: true },
  { name: 'payment_status', label: 'Payment',  field: 'payment_status', align: 'left',   sortable: true },
  { name: 'created_at',     label: 'Date',     field: 'created_at',     align: 'left',   sortable: true },
  { name: 'actions',        label: '',         field: 'actions',        align: 'center' },
]

// ══════ LIST STATE ══════
const loadingList   = ref(false)
const search        = ref('')
const statusFilter  = ref('All')
const paymentFilter = ref('All')
const orders        = ref([])

const filteredOrders = computed(() => {
  const s = (search.value || '').toLowerCase()
  return orders.value.filter((o) => {
    const matchSearch =
      !s || String(o.id).includes(s) || String(o.user_id ?? '').includes(s)
    const matchStatus =
      statusFilter.value === 'All' || o.status === statusFilter.value
    const matchPayment =
      paymentFilter.value === 'All' || o.payment_status === paymentFilter.value
    return matchSearch && matchStatus && matchPayment
  })
})

const fetchOrders = async () => {
  loadingList.value = true
  try {
    const params = {}
    if (statusFilter.value  !== 'All') params.status         = statusFilter.value
    if (paymentFilter.value !== 'All') params.payment_status = paymentFilter.value

    const res = await orderService.getAllOrders(params)
    orders.value = Array.isArray(res) ? res : (res?.orders ?? [])
  } catch (err) {
    console.error('fetchOrders:', err)
    notify(err?.message || 'Failed to load orders', 'negative')
    orders.value = []
  } finally {
    loadingList.value = false
  }
}

const onListStatusChange = async (row, newVal) => {
  const original = row.status
  row.status = newVal           // optimistic update
  try {
    await orderService.updateOrderStatus(row.id, newVal)
    notify(`Order #${row.id} → ${newVal}`)
  } catch (err) {
    row.status = original       // rollback on failure
    notify(err?.message || 'Status update failed', 'negative')
  }
}

// ══════ DETAIL STATE ══════
const selectedOrder     = ref(null)
const loadingDetail     = ref(false)
const updatingStatus    = ref(false)
const updatingShipment  = ref(false)
const creatingShipment  = ref(false)
const cancelling        = ref(false)
const cancelDialog      = ref(false)
const cancelReason      = ref('')
const newStatus         = ref('')
const newShipmentStatus = ref('')

const detailOrder       = ref({})
const detailItems       = ref([])
const detailShipment    = ref(null)
const detailHistory     = ref([])
const detailTransaction = ref(null)

const shipmentForm = ref({
  courier_name: '', tracking_number: '', estimated_delivery: '', tracking_url: ''
})

const detailHistorySorted = computed(() =>
  [...detailHistory.value].sort(
    (a, b) => new Date(b.changed_at) - new Date(a.changed_at)
  )
)

const canCancel = computed(() =>
  selectedOrder.value &&
  !['CANCELLED', 'DELIVERED', 'PAYMENT_FAILED'].includes(selectedOrder.value.status)
)

// ══════ COMPUTED PANELS ══════
const orderInfoFields = computed(() => {
  const o = detailOrder.value
  if (!o?.id) return []
  return [
    { label: 'Order ID',     value: `#${o.id}` },
    { label: 'Date',         value: formatDate(o.created_at) },
    { label: 'Last Updated', value: formatDate(o.updated_at) },
    { label: 'Items',        value: String(detailItems.value.length) },
    { label: 'Address ID',   value: o.address_id     ?? '—' },
    { label: 'Coupon ID',    value: o.coupon_id      ?? '—' },
    { label: 'Transaction',  value: o.transaction_id ?? '—' },
  ]
})

const paymentFields = computed(() => {
  const o  = detailOrder.value
  const tx = detailTransaction.value
  if (!o?.id) return []
  return [
    { label: 'Payment Status', value: o.payment_status, isBadge: true, color: paymentColor(o.payment_status) },
    { label: 'Method',         value: tx?.payment_method          ?? '—' },
    { label: 'Gateway',        value: tx?.payment_gateway         ?? '—' },
    { label: 'Reference',      value: tx?.transaction_ref         ?? '—' },
    { label: 'Gateway Txn ID', value: tx?.gateway_transaction_id  ?? '—' },
    { label: 'Currency',       value: tx?.currency                ?? 'INR' },
  ]
})

const summaryFields = computed(() => {
  const o = detailOrder.value
  if (!o?.id) return []
  return [
    { label: 'Order ID',      value: `#${o.id}` },
    { label: 'User ID',       value: o.user_id ?? '—' },
    { label: 'Items',         value: detailItems.value.length },
    { label: 'Gross',         value: `₹${fmtNum(o.gross_amount || o.total_amount)}` },
    { label: 'Total',         value: `₹${fmtNum(o.total_amount)}` },
    { label: 'Final Payable', value: `₹${fmtNum(o.final_amount || o.total_amount)}`, highlight: true },
    { label: 'Status',        value: o.status },
    { label: 'Payment',       value: o.payment_status },
  ]
})

// ══════ ACTIONS ══════

/**
 * Opens the detail view for an order.
 * Always fetches fresh data from the API — never relies on cached row data.
 */
const openDetail = async (row) => {
  selectedOrder.value = { ...row }
  newStatus.value     = row.status
  loadingDetail.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })

  try {
    const res = await orderService.getOrderDetail(row.id)

    detailOrder.value       = res.order          ?? {}
    detailItems.value       = res.items          ?? []
    detailShipment.value    = res.shipment        ?? null
    detailHistory.value     = res.status_history  ?? []
    detailTransaction.value = res.transaction     ?? null

    // IMPORTANT: always overwrite selectedOrder with fresh DB data
    selectedOrder.value = { ...(res.order ?? row) }
    newStatus.value     = res.order?.status ?? row.status

    if (detailShipment.value) {
      newShipmentStatus.value = detailShipment.value.shipment_status
    }

    // Keep orders list in sync with the freshly fetched order status
    _patchOrderInList(selectedOrder.value.id, selectedOrder.value.status)

  } catch (err) {
    console.error('openDetail:', err)
    notify(err?.message || 'Failed to load order detail', 'negative')
  } finally {
    loadingDetail.value = false
  }
}

/**
 * Patches a single order's status in the list array without a full refetch.
 * Called after openDetail so the list immediately reflects the latest status.
 */
const _patchOrderInList = (orderId, newOrderStatus) => {
  const idx = orders.value.findIndex(o => o.id === orderId)
  if (idx !== -1) {
    orders.value[idx] = { ...orders.value[idx], status: newOrderStatus }
  }
}

const closeDetail = () => {
  selectedOrder.value     = null
  detailOrder.value       = {}
  detailItems.value       = []
  detailShipment.value    = null
  detailHistory.value     = []
  detailTransaction.value = null
}

const updateStatus = async () => {
  updatingStatus.value = true
  try {
    await orderService.updateOrderStatus(selectedOrder.value.id, newStatus.value)
    // Full refresh of detail + list
    await Promise.all([
      openDetail(selectedOrder.value),
      fetchOrders(),
    ])
    notify(`Status updated to "${newStatus.value}"`)
  } catch (err) {
    notify(err?.message || 'Update failed', 'negative')
  } finally {
    updatingStatus.value = false
  }
}

const confirmCancel = async () => {
  cancelling.value = true
  try {
    await orderService.cancelOrder(selectedOrder.value.id)
    cancelDialog.value = false
    cancelReason.value = ''
    await Promise.all([
      openDetail(selectedOrder.value),
      fetchOrders(),
    ])
    notify('Order cancelled successfully')
  } catch (err) {
    notify(err?.message || 'Cancel failed', 'negative')
  } finally {
    cancelling.value = false
  }
}

const createShipment = async () => {
  creatingShipment.value = true
  try {
    await orderService.createShipment(selectedOrder.value.id, shipmentForm.value)
    shipmentForm.value = { courier_name: '', tracking_number: '', estimated_delivery: '', tracking_url: '' }
    // Full refresh so order status (now SHIPPED) is reflected everywhere
    await Promise.all([
      openDetail(selectedOrder.value),
      fetchOrders(),
    ])
    notify('Shipment created successfully')
  } catch (err) {
    notify(err?.message || 'Create shipment failed', 'negative')
  } finally {
    creatingShipment.value = false
  }
}

/**
 * KEY FIX: updateShipmentStatus now:
 * 1. Reads synced_order_status from the API response
 * 2. Optimistically patches the order in the list
 * 3. Fully refreshes both detail AND list
 */
const updateShipmentStatus = async () => {
  if (!detailShipment.value) return
  updatingShipment.value = true
  try {
    // API returns { ...shipmentFields, synced_order_status, order: { id, status } }
    const result = await orderService.updateShipmentStatus(
      detailShipment.value.tracking_number,
      newShipmentStatus.value
    )

    console.log('[AdminOrders] Shipment update response:', result)

    // Optimistic patch using the synced order status from API response
    const syncedStatus = result?.order?.status ?? result?.synced_order_status
    if (syncedStatus && selectedOrder.value) {
      _patchOrderInList(selectedOrder.value.id, syncedStatus)
    }

    // Full refresh of detail view + orders list (both in parallel)
    await Promise.all([
      openDetail(selectedOrder.value),
      fetchOrders(),
    ])

    notify(`Shipment updated to "${newShipmentStatus.value}"`)
  } catch (err) {
    console.error('[AdminOrders] updateShipmentStatus error:', err)
    notify(err?.message || 'Shipment update failed', 'negative')
  } finally {
    updatingShipment.value = false
  }
}

// ══════ LIFECYCLE ══════

/**
 * Listen for cross-page shipment-updated events emitted by AdminShipments.vue.
 * When received, refresh the orders list (and detail if open) so both pages stay in sync.
 */
const onShipmentUpdated = async () => {
  console.log('[AdminOrders] shipment-updated event received — refreshing')
  await fetchOrders()
  if (selectedOrder.value) {
    await openDetail(selectedOrder.value)
  }
}

onMounted(() => {
  fetchOrders()
  window.addEventListener('shipment-updated', onShipmentUpdated)
})

onUnmounted(() => {
  window.removeEventListener('shipment-updated', onShipmentUpdated)
})
</script>

<style scoped>
.admin-page { background: #f8fafc; min-height: 100vh; }
.page-header { border-bottom: 1px solid #e2e8f0; }

.data-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }

/* Table */
.orders-table { background: transparent !important; }
.orders-table :deep(.q-table__container) { background: transparent !important; }
.orders-table :deep(th) {
  background: #eff6ff; color: #1e40af;
  font-size: 12px; font-weight: 600; letter-spacing: .05em;
  border-bottom: 1px solid #dbeafe;
}
.orders-table :deep(td) { color: #1e293b; border-bottom: 1px solid #f1f5f9; }
.orders-table :deep(tr:hover td) { background: #f0f9ff; }
.orders-table :deep(.q-table__bottom) { color: #64748b; border-top: 1px solid #e2e8f0; }

/* Inline status select */
.status-select :deep(.q-field__control) {
  border-radius: 8px !important; padding: 0 10px !important;
  min-height: 32px !important; height: 32px !important; background: #f1f5f9;
}
.status-select :deep(.q-field__native) { font-size: 13px; font-weight: 600; }
.status-select :deep(.q-field__marginal) { height: 32px; }

.status-pending        :deep(.q-field__control) { background: #fef9c3 !important; }
.status-pending        :deep(.q-field__native), .status-pending .status-label { color: #854d0e !important; }
.status-paid           :deep(.q-field__control) { background: #cffafe !important; }
.status-paid           :deep(.q-field__native), .status-paid .status-label { color: #155e75 !important; }
.status-confirmed      :deep(.q-field__control),
.status-processing     :deep(.q-field__control) { background: #dbeafe !important; }
.status-confirmed      :deep(.q-field__native), .status-confirmed .status-label,
.status-processing     :deep(.q-field__native), .status-processing .status-label { color: #1e40af !important; }
.status-shipped        :deep(.q-field__control) { background: #ede9fe !important; }
.status-shipped        :deep(.q-field__native), .status-shipped .status-label { color: #5b21b6 !important; }
.status-delivered      :deep(.q-field__control) { background: #dcfce7 !important; }
.status-delivered      :deep(.q-field__native), .status-delivered .status-label { color: #166534 !important; }
.status-cancelled      :deep(.q-field__control),
.status-payment-failed :deep(.q-field__control) { background: #fee2e2 !important; }
.status-cancelled      :deep(.q-field__native), .status-cancelled .status-label,
.status-payment-failed :deep(.q-field__native), .status-payment-failed .status-label { color: #991b1b !important; }

/* Payment badge */
.payment-badge { font-size: 12px; padding: 3px 10px; border-radius: 20px; font-weight: 600; }

/* Section title */
.section-title {
  font-size: 13px; font-weight: 700; color: #1e40af;
  text-transform: uppercase; letter-spacing: .05em;
  display: flex; align-items: center;
}

/* Info blocks */
.info-block { padding: 10px 14px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; height: 100%; }
.info-label { font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }
.info-value { font-size: 13px; color: #1e293b; font-weight: 500; word-break: break-all; }

/* Items table */
.items-table { border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; }
.items-header { background: #eff6ff; padding: 10px 16px; color: #1e40af; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.items-row { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; }
.items-row:last-child { border-bottom: none; }
.items-row:hover { background: #f8fafc; }
.img-placeholder { width: 40px; height: 40px; border-radius: 6px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

/* Totals */
.totals-section { border-top: 2px solid #e2e8f0; padding-top: 12px; }
.totals-row { display: flex; justify-content: space-between; padding: 5px 0; }
.totals-label { color: #64748b; font-size: 13px; }
.totals-value { color: #1e293b; font-size: 13px; font-weight: 500; }
.totals-discount { color: #16a34a; font-size: 13px; font-weight: 500; }
.totals-total { color: #1e40af; font-size: 16px; font-weight: 700; }

/* Summary */
.summary-grid { display: flex; flex-direction: column; gap: 8px; }
.summary-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f8fafc; border-radius: 8px; }
.summary-label { color: #64748b; font-size: 12px; }
.summary-value { color: #1e293b; font-size: 13px; font-weight: 500; }

/* Modal */
.modal-card { background: #fff; border: 1px solid #bfdbfe; border-radius: 16px; }
</style>