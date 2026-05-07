<template>
  <q-dialog v-model="show" persistent maximized-mobile>
    <q-card class="track-modal">

      <!-- Header -->
      <div class="track-header">
        <div class="track-header-left">
          <q-icon name="local_shipping" size="22px" color="white" />
          <div>
            <div class="track-title">Track Order</div>
            <div class="track-subtitle"># {{ order?.id }}</div>
          </div>
        </div>

        <q-btn
          flat
          round
          dense
          icon="close"
          color="white"
          @click="show = false"
        />
      </div>

      <!-- Loading -->
      <div v-if="loading" class="track-loading">
        <q-spinner-dots color="teal-6" size="40px" />
        <div class="q-mt-sm text-grey-6 text-caption">
          Fetching tracking info…
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="track-error">
        <q-icon name="error_outline" size="40px" color="negative" />

        <div class="q-mt-sm text-negative">
          {{ error }}
        </div>

        <q-btn
          flat
          color="teal-7"
          label="Retry"
          icon="refresh"
          no-caps
          class="q-mt-sm"
          @click="fetchTracking"
        />
      </div>

      <!-- Content -->
      <div v-else class="track-body">

        <!-- Current Status -->
        <div class="status-card" :class="statusCardClass">

          <div class="status-card-icon">
            <q-icon :name="currentStatusIcon" size="28px" />
          </div>

          <div>
            <div class="status-card-label">
              Current Status
            </div>

            <div class="status-card-value">
              {{ formatStatusLabel(currentStatus) }}
            </div>

            <div
              v-if="lastUpdated"
              class="status-card-time"
            >
              Updated {{ formatDate(lastUpdated) }}
            </div>
          </div>

        </div>

        <!-- Shipment Info -->
        <div
          v-if="tracking?.shipment"
          class="shipment-info"
        >

          <div class="info-row">
            <q-icon
              name="local_shipping"
              size="16px"
              color="teal-6"
            />

            <span class="info-label">
              Courier:
            </span>

            <span class="info-value">
              {{ tracking.shipment.courier_name }}
            </span>
          </div>

          <div class="info-row">
            <q-icon
              name="pin"
              size="16px"
              color="teal-6"
            />

            <span class="info-label">
              Tracking #:
            </span>

            <span class="info-value mono">
              {{ tracking.shipment.tracking_number }}
            </span>
          </div>

          <div
            v-if="tracking.shipment.estimated_delivery"
            class="info-row"
          >
            <q-icon
              name="event"
              size="16px"
              color="teal-6"
            />

            <span class="info-label">
              Est. Delivery:
            </span>

            <span class="info-value">
              {{
                formatSimpleDate(
                  tracking.shipment.estimated_delivery
                )
              }}
            </span>
          </div>

          <div
            v-if="tracking.shipment.tracking_url"
            class="info-row"
          >
            <q-icon
              name="open_in_new"
              size="16px"
              color="teal-6"
            />

            <a
              :href="tracking.shipment.tracking_url"
              target="_blank"
              class="track-link"
            >
              Track on courier site
            </a>
          </div>

        </div>

        <!-- Timeline -->
        <div class="timeline-section">

          <div class="timeline-heading">
            Order Journey
          </div>

          <div class="timeline">

            <div
              v-for="(step, idx) in timelineSteps"
              :key="step.status"
              class="timeline-item"
              :class="{
                'is-completed': step.state === 'completed',
                'is-active': step.state === 'active',
                'is-pending': step.state === 'pending',
                'is-cancelled': step.state === 'cancelled',
                'is-failed': step.state === 'failed'
              }"
            >

              <!-- Connector -->
              <div
                v-if="idx < timelineSteps.length - 1"
                class="tl-connector"
              />

              <!-- Dot -->
              <div class="tl-dot">

                <q-icon
                  v-if="step.state === 'completed'"
                  name="check"
                  size="14px"
                  color="white"
                />

                <q-icon
                  v-else-if="step.state === 'active'"
                  name="radio_button_checked"
                  size="14px"
                  color="white"
                />

                <q-icon
                  v-else-if="step.state === 'cancelled'"
                  name="close"
                  size="14px"
                  color="white"
                />

                <q-icon
                  v-else-if="step.state === 'failed'"
                  name="error"
                  size="14px"
                  color="white"
                />

                <div
                  v-else
                  class="tl-empty-dot"
                />

              </div>

              <!-- Content -->
              <div class="tl-content">

                <div class="tl-label">
                  {{ formatStatusLabel(step.status) }}
                </div>

                <div
                  class="tl-status-text"
                  :class="{
                    active: step.state === 'active',
                    completed: step.state === 'completed'
                  }"
                >

                  <span v-if="step.state === 'completed'">
                    Completed
                  </span>

                  <span v-else-if="step.state === 'active'">
                    In Progress
                  </span>

                  <span v-else>
                    Pending
                  </span>

                </div>

              </div>

            </div>

          </div>

        </div>

      </div>

      <!-- Footer -->
      <div class="track-footer">

        <q-btn
          unelevated
          no-caps
          color="teal-7"
          label="Close"
          style="min-width: 120px"
          @click="show = false"
        />

      </div>

    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import * as orderService from 'src/service/orderService'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },

  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits([
  'update:modelValue'
])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const error = ref(null)
const tracking = ref(null)

/* ─────────────────────────────────────────────
   FLOW
───────────────────────────────────────────── */
const FLOW = [
  'PROCESSING',
  'SHIPPED',
  'OUT_FOR_DELIVERY',
  'DELIVERED'
]

/* ─────────────────────────────────────────────
   LABELS
───────────────────────────────────────────── */
const STATUS_LABELS = {

  PROCESSING: 'Order Processing',

  SHIPPED: 'Shipped',

  OUT_FOR_DELIVERY: 'Out For Delivery',

  DELIVERED: 'Delivered',

  CANCELLED: 'Cancelled',

  PAYMENT_FAILED: 'Payment Failed'
}

/* ─────────────────────────────────────────────
   ICONS
───────────────────────────────────────────── */
const STATUS_ICONS = {

  PROCESSING: 'inventory_2',

  SHIPPED: 'local_shipping',

  OUT_FOR_DELIVERY: 'delivery_dining',

  DELIVERED: 'check_circle',

  CANCELLED: 'cancel',

  PAYMENT_FAILED: 'error'
}

/* ─────────────────────────────────────────────
   CURRENT STATUS
───────────────────────────────────────────── */
const currentStatus = computed(() => {

  // ✅ Shipment status is highest priority
  const shipmentStatus =
    tracking.value?.shipment?.shipment_status

  if (shipmentStatus) {

    // map shipment pending to processing
    if (shipmentStatus === 'PENDING') {
      return 'PROCESSING'
    }

    return shipmentStatus
  }

  // fallback to order status
  const rawStatus =
    tracking.value?.order?.status ||
    tracking.value?.status ||
    props.order?.status ||
    'PROCESSING'

  // old ecommerce statuses
  if (
    ['PENDING', 'PAID', 'CONFIRMED']
      .includes(rawStatus)
  ) {
    return 'PROCESSING'
  }

  return rawStatus
})
/* ─────────────────────────────────────────────
   LAST UPDATED
───────────────────────────────────────────── */
const lastUpdated = computed(() => {

  const history =
    tracking.value?.status_history || []

  if (!history.length) {
    return null
  }

  return history[
    history.length - 1
  ]?.changed_at
})

const currentStatusIcon = computed(() => {
  return (
    STATUS_ICONS[currentStatus.value]
    || 'info'
  )
})

const statusCardClass = computed(() => {

  const status =
    currentStatus.value

  if (status === 'DELIVERED') {
    return 'status-delivered'
  }

  if (status === 'SHIPPED') {
    return 'status-shipped'
  }

  if (status === 'OUT_FOR_DELIVERY') {
    return 'status-shipped'
  }

  if (status === 'CANCELLED') {
    return 'status-cancelled'
  }

  if (status === 'PAYMENT_FAILED') {
    return 'status-failed'
  }

  if (status === 'PROCESSING') {
    return 'status-processing'
  }

  return 'status-default'
})

/* ─────────────────────────────────────────────
   TIMELINE
───────────────────────────────────────────── */
const timelineSteps = computed(() => {

  const status =
    currentStatus.value

  const activeIndex =
    FLOW.indexOf(status)

  return FLOW.map((step, index) => {

    let state = 'pending'

    if (index < activeIndex) {
      state = 'completed'
    }

    else if (index === activeIndex) {

      // ✅ final delivered state
      if (status === 'DELIVERED') {
        state = 'completed'
      }

      else {
        state = 'active'
      }

    }

    return {
      status: step,
      state
    }

  })

})
/* ─────────────────────────────────────────────
   FETCH TRACKING
───────────────────────────────────────────── */
async function fetchTracking() {

  if (!props.order?.id) {
    return
  }

  loading.value = true
  error.value = null
  tracking.value = null

  try {

    const user = JSON.parse(
      localStorage.getItem('user') || '{}'
    )

    const response =
      await orderService.trackOrder(
        props.order.id,
        user?.id
      )

    tracking.value = response

  } catch (err) {

    error.value =
      err?.response?.data?.detail ||
      err?.message ||
      'Failed to load tracking information'

  } finally {

    loading.value = false

  }

}

/* ─────────────────────────────────────────────
   HELPERS
───────────────────────────────────────────── */
function formatStatusLabel(status) {
  return STATUS_LABELS[status] || status
}

function formatDate(date) {

  if (!date) {
    return ''
  }

  return new Date(date)
    .toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })

}

function formatSimpleDate(date) {

  if (!date) {
    return ''
  }

  return new Date(date)
    .toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })

}

/* ─────────────────────────────────────────────
   WATCH
───────────────────────────────────────────── */
watch(
  () => props.modelValue,
  (val) => {

    if (
      val &&
      props.order?.id
    ) {
      fetchTracking()
    }

  }
)
</script>

<style scoped>
.track-modal {
  width: 480px;
  max-width: 96vw;
  max-height: 90vh;
  border-radius: 18px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #f8fafa;
}

.track-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: linear-gradient(135deg, #1a7a6e, #007f8c);
}

.track-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.track-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.track-subtitle {
  font-size: 12px;
  color: rgba(255,255,255,0.75);
}

.track-loading,
.track-error {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.track-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 14px;
}

.status-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-card-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  opacity: 0.75;
}

.status-card-value {
  font-size: 20px;
  font-weight: 800;
}

.status-card-time {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 4px;
}

.status-delivered {
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: #fff;
}

.status-shipped {
  background: linear-gradient(135deg, #0369a1, #0284c7);
  color: #fff;
}

.status-processing {
  background: linear-gradient(135deg, #b45309, #d97706);
  color: #fff;
}

.status-cancelled {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  color: #fff;
}

.status-failed {
  background: linear-gradient(135deg, #9f1239, #be123c);
  color: #fff;
}

.status-default {
  background: linear-gradient(135deg, #1a7a6e, #007f8c);
  color: #fff;
}

.shipment-info {
  background: #fff;
  border: 1px solid #e2ece9;
  border-radius: 12px;
  padding: 14px 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.timeline-section {
  background: #fff;
  border: 1px solid #e2ece9;
  border-radius: 12px;
  padding: 16px;
}

.timeline-heading {
  font-size: 12px;
  font-weight: 700;
  color: #5a7470;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  position: relative;
  padding-bottom: 20px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.tl-connector {
  position: absolute;
  left: 15px;
  top: 28px;
  width: 2px;
  bottom: 0;
  background: #e2ece9;
  z-index: 0;
}

.is-completed .tl-connector {
  background: #16a34a;
}

.is-active .tl-connector {

  background:
    linear-gradient(
      to bottom,
      #007f8c 0%,
      #e2ece9 100%
    );
}

.tl-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e2ece9;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  position: relative;
}

.tl-empty-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #c9d8d5;
}

.is-completed .tl-dot {
  background: #16a34a;
}

.is-active .tl-dot {

  background: #007f8c;

  box-shadow:
    0 0 0 4px rgba(0,127,140,0.14),
    0 0 0 8px rgba(0,127,140,0.08);

  animation: pulseTrack 1.8s infinite;
}

.is-cancelled .tl-dot {
  background: #dc2626;
}

.is-failed .tl-dot {
  background: #9f1239;
}

.tl-content {
  flex: 1;
  padding-top: 5px;
}

.tl-label {
  font-size: 14px;
  font-weight: 600;
  color: #1a2e2b;
}

.tl-status-text {

  margin-top: 4px;

  font-size: 12px;

  font-weight: 500;

  color: #94a3a0;
}

.tl-status-text.completed {
  color: #16a34a;
}

.tl-status-text.active {
  color: #007f8c;
}

.is-pending .tl-label {
  color: #94a3a0;
}

.track-footer {
  padding: 14px 20px;
  border-top: 1px solid #e2ece9;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

@keyframes pulseTrack {

  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.08);
  }

  100% {
    transform: scale(1);
  }

}

@media (max-width: 540px) {

  .track-modal {
    border-radius: 0;
    max-height: 100vh;
    height: 100vh;
  }

}
</style>