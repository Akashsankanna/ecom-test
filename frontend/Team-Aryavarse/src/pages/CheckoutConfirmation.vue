<template>
  <q-page class="q-pa-xl flex flex-center confirmation-page">
    <div class="confirmation-card text-center">
      <q-icon
        v-if="!loading && !error"
        name="check_circle"
        size="80px"
        color="positive"
      />

      <q-spinner
        v-if="loading"
        color="primary"
        size="50px"
      />

      <q-icon
        v-if="error"
        name="error"
        size="80px"
        color="negative"
      />

      <div class="text-h4 q-mt-md">
        {{
          loading
            ? 'Loading Order...'
            : error
              ? 'Order Not Found'
              : 'Order Confirmed'
        }}
      </div>

      <div class="text-subtitle1 q-mt-sm" v-if="loading">
        Please wait while we load your order details.
      </div>

      <div class="text-subtitle1 q-mt-sm" v-else-if="error">
        {{ error }}
      </div>

      <div v-else class="q-mt-md">
        <div class="text-subtitle1">
          Your order has been placed successfully.
        </div>

        <div class="q-mt-md order-info" v-if="order">
          <div><strong>Order ID:</strong> {{ order.id || order.order_id }}</div>
          <div v-if="order.payment_method">
            <strong>Payment Method:</strong> {{ formatPaymentMethod(order.payment_method) }}
          </div>
          <div v-if="order.order_status || order.status">
            <strong>Status:</strong> {{ order.order_status || order.status }}
          </div>
          <div v-if="displayAmount !== null">
            <strong>Total Amount:</strong>
            ₹ {{ Number(displayAmount).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
          </div>
        </div>
      </div>

      <div class="q-mt-lg row justify-center q-gutter-md">
        <q-btn
          color="primary"
          label="Continue Shopping"
          @click="goHome"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchOrderById } from 'src/services/orderService.js'
import { getUserId } from 'src/utils/checkoutStorage.js'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const error = ref('')
const order = ref(null)

const orderId = computed(() => route.query.order_id || null)

const displayAmount = computed(() => {
  if (!order.value) return null

  return (
    order.value.final_amount ??
    order.value.total_amount ??
    order.value.grand_total ??
    order.value.amount_paid ??
    null
  )
})

onMounted(async () => {
  await loadOrder()
})

async function loadOrder() {
  const userId = getUserId()

  if (!userId) {
    error.value = 'User not found. Please login again.'
    return
  }

  if (!orderId.value) {
    error.value = 'Order ID not found.'
    return
  }

  try {
    loading.value = true
    error.value = ''

    const response = await fetchOrderById(orderId.value, userId)

    order.value = response?.data || response
  } catch (err) {
    console.error('Failed to fetch order:', err)
    error.value = 'We could not load your order details.'
  } finally {
    loading.value = false
  }
}

function formatPaymentMethod(method) {
  if (method === 'upi') return 'UPI'
  if (method === 'card') return 'Credit / Debit Card'
  if (method === 'cod') return 'Cash on Delivery'
  return method || '-'
}

function goHome() {
  router.push('/')
}
</script>

<style scoped>
.confirmation-page {
  background: #f5f7f8;
  min-height: 100vh;
}

.confirmation-card {
  background: white;
  padding: 40px 32px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  min-width: 320px;
  max-width: 520px;
  width: 100%;
}

.order-info {
  text-align: left;
  margin: 0 auto;
  max-width: 320px;
  background: #f8f9fb;
  border-radius: 12px;
  padding: 16px;
  line-height: 1.9;
}
</style>
