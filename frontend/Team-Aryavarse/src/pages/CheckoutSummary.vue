<template>
  <q-page class="summary-page">
    <div class="summary-wrapper">
      <!-- LEFT SECTION -->
      <div class="summary-left">
        <!-- PRODUCT DETAILS -->
        <section class="summary-section">
          <h2 class="section-title">Product Details</h2>

          <div class="product-card" v-if="cart.length">
            <div class="delivery-strip">
              <q-icon name="local_shipping" size="20px" color="#51606f" />
              <span>{{ estimatedDeliveryText }}</span>
            </div>

            <div
              v-for="item in cart"
              :key="item.id || item.cart_item_id"
              class="product-row"
            >
              <img :src="item.image || item.image_url" :alt="item.title || item.product_name || 'Product'" class="product-image" />

              <div class="product-info">
                <div class="product-top-row">
                  <div>
                    <h3 class="product-name">{{ item.title || item.product_name || 'Selected Product' }}</h3>
                    <p class="product-price-line">
                      ₹{{ Number(item.price || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
                    </p>
                    <p class="product-return">All issue easy returns</p>
                    <p class="product-meta">
                      Size: {{ item.size || item.variant_name || 'M' }}
                      <span class="dot">•</span>
                      Qty: {{ item.qty || item.quantity || 1 }}
                    </p>
                  </div>

                  <button class="edit-link" @click="goBackToCart">EDIT</button>
                </div>
              </div>
            </div>

            <div class="seller-row">
              Sold by: <span>{{ sellerName }}</span>
            </div>
          </div>
        </section>

        <!-- DELIVERY ADDRESS -->
        <section class="summary-section">
          <div class="section-heading-row">
            <h2 class="section-title with-icon">
              <q-icon name="location_on" size="22px" color="#6c8cd5" />
              <span>Delivery Address</span>
            </h2>
          </div>

          <div class="info-card" v-if="selectedAddress">
            <div class="info-top-row">
              <div>
                <h3 class="info-name">{{ selectedAddress.full_name }}</h3>
              </div>

              <button class="edit-link" @click="goBackToAddress">EDIT</button>
            </div>

            <p class="info-text">
              {{ selectedAddress.address_line1 }}
              <span v-if="selectedAddress.address_line2">, {{ selectedAddress.address_line2 }}</span>
              <span v-if="selectedAddress.landmark">, {{ selectedAddress.landmark }}</span>,
              {{ selectedAddress.city }}, {{ selectedAddress.state }}, {{ selectedAddress.country }} -
              {{ selectedAddress.postal_code }}
            </p>

            <p class="info-phone">{{ selectedAddress.phone }}</p>
          </div>
        </section>

        <!-- PAYMENT MODE -->
        <section class="summary-section">
          <h2 class="section-title">Payment Mode</h2>

          <div class="info-card payment-card">
            <div class="info-top-row">
              <div class="payment-mode-text">{{ paymentModeLabel }}</div>
              <button class="edit-link" @click="goBackToPayment">EDIT</button>
            </div>
          </div>
        </section>
      </div>

      <!-- RIGHT SECTION -->
      <div class="summary-right">
        <div class="price-card">
          <h2 class="price-title">Price Details ({{ totalItems }} Items)</h2>

          <div class="price-row">
            <span>Subtotal</span>
            <span>₹ {{ subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="price-row">
            <span>Delivery Charges</span>
            <span>₹ {{ deliveryCharges.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="price-row">
            <span>{{ gstLabel }}</span>
            <span>₹ {{ tax.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div v-if="couponDiscount > 0" class="price-row discount-row">
            <span>Coupon Discount</span>
            <span>- ₹ {{ couponDiscount.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="price-divider"></div>

          <div class="price-row total-row">
            <span>Order Total</span>
            <span>₹ {{ finalTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div v-if="couponDiscount > 0" class="discount-box">
            <q-icon name="verified" size="18px" color="#0f8b65" />
            <span>Yay! Your total discount is ₹{{ couponDiscount.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <button class="place-order-btn" @click="placeOrder" :disabled="loading">
            {{ loading ? 'Placing Order...' : 'Place Order' }}
          </button>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { cart } from 'src/stores/shop'
import { fetchAddresses } from 'src/service/addressService'
import { placeOrderApi } from 'src/service/orderService'
import {
  getSelectedAddressId,
  getPaymentMethod,
  getCouponDiscount,
  getCouponCode,
  getUserId,
  clearCoupon,
  clearSelectedAddressId
} from 'src/utils/checkoutStorage.js'

const router = useRouter()

const selectedAddress = ref(null)
const paymentMethod = ref(getPaymentMethod())
const couponDiscount = ref(getCouponDiscount())
const couponCode = ref(getCouponCode())
const loading = ref(false)

const WAREHOUSE_PINCODE = '413005'

onMounted(async () => {
  await loadSelectedAddress()
})

async function loadSelectedAddress() {
  const userId = getUserId()
  const selectedAddressId = getSelectedAddressId()

  if (!userId) {
    router.push('/login?redirect=/checkout/summary')
    return
  }

  if (!selectedAddressId) {
    router.push('/checkout/address')
    return
  }

  try {
    const data = await fetchAddresses(userId)
    const addresses = Array.isArray(data) ? data : (data?.data || data?.items || [])

    selectedAddress.value =
      addresses.find(addr => Number(addr.id) === Number(selectedAddressId)) || null

    if (!selectedAddress.value) {
      alert('Please select delivery address first')
      router.push('/checkout/address')
    }
  } catch (error) {
    console.error('Failed to load selected address:', error)
    alert('Failed to load delivery address')
    router.push('/checkout/address')
  }
}

const subtotal = computed(() => {
  return cart.value.reduce((sum, item) => {
    const qty = Number(item.qty || item.quantity || 0)
    const price = Number(item.price || 0)
    return sum + price * qty
  }, 0)
})

const totalItems = computed(() => {
  return cart.value.reduce((sum, item) => {
    return sum + Number(item.qty || item.quantity || 0)
  }, 0)
})

function getDistanceDeliveryCharge(address) {
  if (!address?.postal_code) return 80

  const selectedPin = String(address.postal_code).trim()
  const warehousePin = String(WAREHOUSE_PINCODE).trim()

  if (selectedPin === warehousePin) return 40
  if (selectedPin.slice(0, 3) === warehousePin.slice(0, 3)) return 60
  if (selectedPin.slice(0, 2) === warehousePin.slice(0, 2)) return 90
  return 140
}

const deliveryCharges = computed(() => {
  return getDistanceDeliveryCharge(selectedAddress.value)
})

function getGstRate(unitPrice) {
  return Number(unitPrice) <= 2500 ? 0.05 : 0.18
}

const gstLabel = computed(() => {
  if (!cart.value.length) return 'Tax (GST)'

  const hasLowSlab = cart.value.some(item => Number(item.price || 0) <= 2500)
  const hasHighSlab = cart.value.some(item => Number(item.price || 0) > 2500)

  if (hasLowSlab && hasHighSlab) return 'Tax (GST)'
  if (hasLowSlab) return 'Tax (GST 5%)'
  return 'Tax (GST 18%)'
})

const tax = computed(() => {
  return cart.value.reduce((sum, item) => {
    const unitPrice = Number(item.price || 0)
    const qty = Number(item.qty || item.quantity || 0)
    const gstRate = getGstRate(unitPrice)
    return sum + unitPrice * qty * gstRate
  }, 0)
})

const finalTotal = computed(() => {
  return Math.max(subtotal.value + deliveryCharges.value + tax.value - couponDiscount.value, 0)
})

const paymentModeLabel = computed(() => {
  if (paymentMethod.value === 'upi') return 'UPI'
  if (paymentMethod.value === 'card') return 'Credit / Debit Card'
  return 'Cash on Delivery'
})

const sellerName = computed(() => 'B_fab_fab')

const estimatedDeliveryText = computed(() => {
  return 'Estimated Delivery by Saturday, 25th Apr'
})

function goBackToCart() {
  router.push('/cart')
}

function goBackToAddress() {
  router.push('/checkout/address')
}

function goBackToPayment() {
  router.push('/checkout/payment')
}

async function placeOrder() {
  const userId = getUserId()
  const selectedAddressId = getSelectedAddressId()

  if (!userId) {
    router.push('/login?redirect=/checkout/summary')
    return
  }

  if (!cart.value.length) {
    alert('Your cart is empty')
    router.push('/cart')
    return
  }

  if (!selectedAddressId || !selectedAddress.value) {
    alert('Please select delivery address first')
    router.push('/checkout/address')
    return
  }

  try {
    loading.value = true

    const payload = {
      user_id: userId,
      address_id: selectedAddressId,
      payment_method: paymentMethod.value,
      coupon_code: couponCode.value || null,
      coupon_discount: Number(couponDiscount.value || 0)
    }

    await placeOrderApi(payload)

    clearCoupon()
    clearSelectedAddressId()
    cart.value = []

    router.push('/checkout/confirmation')
  } catch (error) {
    console.error('Place order failed:', error)
    alert('Failed to place order')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.summary-page {
  background: #f5f5f5;
  min-height: 100vh;
  padding: 20px 24px 40px;
  font-family: 'DM Sans', sans-serif;
}

.summary-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 370px;
  gap: 26px;
  align-items: start;
}

.summary-left {
  padding-right: 18px;
}

.summary-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #243746;
  margin: 0 0 16px;
}

.with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-card,
.info-card {
  background: white;
  border: 1px solid #d8dbe5;
  border-radius: 12px;
  overflow: hidden;
}

.delivery-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-bottom: 1px solid #d8dbe5;
  color: #2f3443;
  font-size: 16px;
  font-weight: 600;
}

.product-row {
  display: flex;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid #d8dbe5;
}

.product-image {
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: 8px;
}

.product-info {
  flex: 1;
}

.product-top-row,
.info-top-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.product-name,
.info-name {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
  color: #243746;
}

.product-price-line {
  margin: 0 0 10px;
  font-size: 16px;
  color: #243746;
  font-weight: 700;
}

.product-return,
.product-meta,
.info-text,
.info-phone {
  margin: 0 0 8px;
  font-size: 15px;
  color: #556070;
  line-height: 1.5;
}

.dot {
  margin: 0 6px;
}

.edit-link {
  border: none;
  background: transparent;
  color: #0f6c73;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.seller-row {
  padding: 14px 20px;
  font-size: 15px;
  color: #5b6573;
}

.seller-row span {
  color: #536089;
}

.info-card {
  padding: 20px;
}

.payment-card {
  padding: 18px 20px;
}

.payment-mode-text {
  font-size: 16px;
  font-weight: 600;
  color: #243746;
}

.summary-right {
  border-left: 1px solid #d7ddde;
  padding-left: 24px;
}

.price-card {
  background: transparent;
  border-radius: 0;
}

.price-title {
  font-size: 18px;
  font-weight: 700;
  color: #2f3443;
  margin: 0 0 26px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  font-size: 16px;
  color: #53596a;
}

.discount-row {
  color: #0f8b65;
}

.price-divider {
  height: 1px;
  background: #d8dbe5;
  margin: 18px 0 20px;
}

.total-row {
  font-size: 18px;
  font-weight: 700;
  color: #2f3443;
  margin-bottom: 18px;
}

.discount-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #d7f0e5;
  color: #0f8b65;
  padding: 16px;
  border-radius: 6px;
  font-size: 15px;
  margin-bottom: 26px;
}

.place-order-btn {
  width: 100%;
  border: none;
  background: linear-gradient(90deg, #0f6c73 0%, #16697a 100%);
  color: white;
  font-size: 18px;
  font-weight: 700;
  padding: 16px;
  border-radius: 6px;
  cursor: pointer;
}

.place-order-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .summary-wrapper {
    grid-template-columns: 1fr;
  }

  .summary-right {
    border-left: none;
    padding-left: 0;
  }

  .product-top-row,
  .info-top-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
