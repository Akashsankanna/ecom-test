<template>
  <q-page class="payment-page">
    <div class="payment-wrapper">
      <div class="payment-left">
        <button class="back-link" @click="goBackToAddress">
          ← BACK TO DELIVERY ADDRESS
        </button>

        <h1 class="page-title">Payment Method</h1>
        <p class="page-subtitle">Select your preferred payment method.</p>

        <!-- UPI -->
        <div
          class="method-card"
          :class="{ 'method-card--active': selectedMethod === 'upi' }"
          @click="selectedMethod = 'upi'"
        >
          <div class="method-left">
            <div class="method-icon-box">
              <q-icon name="account_balance" size="22px" color="teal" />
            </div>

            <div>
              <div class="method-title">Unified Payments Interface (UPI)</div>
              <div class="method-desc">Pay via GPay, PhonePe, or BHIM</div>
            </div>
          </div>

          <div class="radio-circle" :class="{ 'radio-circle--active': selectedMethod === 'upi' }">
            <div v-if="selectedMethod === 'upi'" class="radio-dot"></div>
          </div>
        </div>

        <!-- CARD -->
        <div
          class="method-card"
          :class="{ 'method-card--active': selectedMethod === 'card' }"
          @click="selectedMethod = 'card'"
        >
          <div class="method-left">
            <div class="method-icon-box">
              <q-icon name="credit_card" size="22px" color="teal" />
            </div>

            <div>
              <div class="method-title">Credit / Debit Card</div>
              <div class="method-desc">Secure card payment</div>
            </div>
          </div>

          <div class="radio-circle" :class="{ 'radio-circle--active': selectedMethod === 'card' }">
            <div v-if="selectedMethod === 'card'" class="radio-dot"></div>
          </div>
        </div>

        <!-- CARD FORM -->
        <div v-if="selectedMethod === 'card'" class="card-form-box">
          <div class="field-group">
            <label class="field-label">CARDHOLDER NAME</label>
            <input
              v-model="cardName"
              class="field-input"
              placeholder="Enter cardholder name"
              type="text"
            />
          </div>

          <div class="field-group">
            <label class="field-label">CARD NUMBER</label>
            <div class="input-with-icon">
              <input
                v-model="cardNumber"
                class="field-input"
                placeholder="XXXX XXXX XXXX XXXX"
                maxlength="19"
                type="text"
                @input="formatCardNumber"
              />
              <q-icon name="lock" size="20px" color="grey-7" class="input-lock" />
            </div>
          </div>

          <div class="field-row">
            <div class="field-group field-half">
              <label class="field-label">EXPIRY DATE</label>
              <input
                v-model="expiry"
                class="field-input"
                placeholder="MM/YY"
                maxlength="5"
                type="text"
                @input="formatExpiry"
              />
            </div>

            <div class="field-group field-half">
              <label class="field-label">CVV</label>
              <input
                v-model="cvv"
                class="field-input"
                placeholder="***"
                maxlength="3"
                type="password"
                @input="formatCvv"
              />
            </div>
          </div>

          <div class="security-note">
            <q-icon name="verified_user" size="16px" color="positive" />
            <span>Your payment details are secured.</span>
          </div>
        </div>

        <!-- COD -->
        <div
          class="method-card"
          :class="{ 'method-card--active': selectedMethod === 'cod' }"
          @click="selectedMethod = 'cod'"
        >
          <div class="method-left">
            <div class="method-icon-box">
              <q-icon name="payments" size="22px" color="teal" />
            </div>

            <div>
              <div class="method-title">Cash on Delivery</div>
              <div class="method-desc">Pay when your order is delivered</div>
            </div>
          </div>

          <div class="radio-circle" :class="{ 'radio-circle--active': selectedMethod === 'cod' }">
            <div v-if="selectedMethod === 'cod'" class="radio-dot"></div>
          </div>
        </div>
      </div>

      <div class="payment-right">
        <div class="price-card">
          <h2 class="summary-title">Price Details ({{ totalItems }} Items)</h2>

          <div class="summary-row">
            <span>Subtotal</span>
            <span>₹ {{ subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="summary-row">
            <span>Delivery Charges</span>
            <span>₹ {{ deliveryCharges.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="summary-row">
            <span>{{ gstLabel }}</span>
            <span>₹ {{ tax.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div v-if="couponDiscount > 0" class="summary-row discount-row">
            <span>Coupon Discount</span>
            <span>- ₹ {{ Number(couponDiscount).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="summary-divider"></div>

          <div class="summary-row total-row">
            <span>Total</span>
            <span>₹ {{ finalPayable.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="coupon-section">
            <div class="coupon-title">Apply Coupon</div>

            <div class="coupon-input-row">
              <input
                v-model="couponCode"
                type="text"
                class="coupon-input"
                placeholder="Enter coupon code"
              />
              <button class="coupon-btn" @click="applyCoupon">
                Apply
              </button>
            </div>

            <div v-if="appliedCoupon" class="coupon-success">
              Coupon <b>{{ appliedCoupon }}</b> applied successfully
              <span class="remove-coupon" @click="removeCoupon">Remove</span>
            </div>

            <div v-if="couponError" class="coupon-error">
              {{ couponError }}
            </div>
          </div>

          <button class="continue-btn solid-btn" @click="continueToSummary" :disabled="loading">
            {{ loading ? 'Processing...' : 'Proceed to Checkout' }}
          </button>

          <button class="continue-shopping-btn" @click="goBackToAddress">
            Back to Address
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
import { fetchAddresses } from 'src/service/addressService.js'
import {
  createCheckoutSession,
  createRazorpayOrder,
  verifyRazorpayPayment
} from 'src/service/checkoutService'
import {
  getSelectedAddressId,
  getPaymentMethod,
  savePaymentMethod,
  getCouponCode,
  getCouponDiscount,
  saveCoupon,
  clearCoupon,
  getUserId
} from 'src/utils/checkoutStorage'
import { loadRazorpayScript } from 'src/utils/loadRazorpay'

const router = useRouter()

const selectedMethod = ref(getPaymentMethod() || 'upi')
const couponCode = ref('')
const appliedCoupon = ref(getCouponCode() || '')
const couponError = ref('')
const couponDiscount = ref(Number(getCouponDiscount() || 0))

const selectedAddress = ref(null)
const loading = ref(false)

const cardName = ref('')
const cardNumber = ref('')
const expiry = ref('')
const cvv = ref('')

const currentOrderId = ref(null)

const WAREHOUSE_PINCODE = '413005'

onMounted(async () => {
  await loadSelectedAddress()
})

function getErrorMessage(error, fallback = 'Something went wrong') {
  const data = error?.response?.data

  if (!data) return error?.message || fallback
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail

  if (Array.isArray(data.detail)) {
    return data.detail.map(item => item?.msg || JSON.stringify(item)).join(', ')
  }

  if (typeof data.detail === 'object' && data.detail !== null) {
    return JSON.stringify(data.detail)
  }

  return error?.message || fallback
}

async function loadSelectedAddress() {
  const userId = getUserId()
  const selectedAddressId = getSelectedAddressId()

  if (!userId) {
    router.push('/login?redirect=/checkout/payment')
    return
  }

  if (!selectedAddressId) {
    router.push('/checkout/address')
    return
  }

  try {
    const data = await fetchAddresses()
    const addresses = Array.isArray(data) ? data : (data?.data || data?.items || [])

    selectedAddress.value =
      addresses.find(addr => Number(addr.id) === Number(selectedAddressId)) || null

    if (!selectedAddress.value) {
      alert('Please select delivery address first')
      router.push('/checkout/address')
    }
  } catch (error) {
    console.error('Failed to load selected address:', error)
    alert(getErrorMessage(error, 'Failed to load address'))
    router.push('/checkout/address')
  }
}

const subtotal = computed(() => {
  return cart.value.reduce((sum, item) => {
    return sum + Number(item.price || 0) * Number(item.qty || 0)
  }, 0)
})

const totalItems = computed(() => {
  return cart.value.reduce((sum, item) => sum + Number(item.qty || 0), 0)
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
    const qty = Number(item.qty || 0)
    const gstRate = getGstRate(unitPrice)
    return sum + unitPrice * qty * gstRate
  }, 0)
})

const total = computed(() => {
  return subtotal.value + deliveryCharges.value + tax.value
})

const finalPayable = computed(() => {
  return Math.max(total.value - couponDiscount.value, 0)
})

function applyCoupon() {
  couponError.value = ''
  const code = couponCode.value.trim().toUpperCase()

  if (!code) {
    couponError.value = 'Please enter coupon code'
    return
  }

  let discount = 0

  if (code === 'SAVE50') {
    discount = 50
  } else if (code === 'WELCOME10') {
    discount = 10
  } else if (code === 'FIRST20') {
    discount = 20
  } else {
    couponError.value = 'Invalid coupon code'
    return
  }

  appliedCoupon.value = code
  couponDiscount.value = discount
  saveCoupon(code, discount)
}

function removeCoupon() {
  appliedCoupon.value = ''
  couponCode.value = ''
  couponDiscount.value = 0
  couponError.value = ''
  clearCoupon()
}

function goBackToAddress() {
  router.push('/checkout/address')
}

function formatCardNumber() {
  const digits = cardNumber.value.replace(/\D/g, '').slice(0, 16)
  cardNumber.value = digits.replace(/(\d{4})(?=\d)/g, '$1 ').trim()
}

function formatExpiry() {
  const digits = expiry.value.replace(/\D/g, '').slice(0, 4)
  if (digits.length >= 3) {
    expiry.value = `${digits.slice(0, 2)}/${digits.slice(2)}`
  } else {
    expiry.value = digits
  }
}

function formatCvv() {
  cvv.value = cvv.value.replace(/\D/g, '').slice(0, 3)
}

async function openRazorpay(orderData) {
  const sdkLoaded = await loadRazorpayScript()

  if (!sdkLoaded || !window.Razorpay) {
    alert('Razorpay SDK failed to load')
    return
  }

  const razorpayOrderId = orderData?.razorpay_order_id

  if (!razorpayOrderId) {
    alert('Invalid Razorpay order response')
    return
  }

  const options = {
    key: orderData.key || orderData.key_id, // ✅ USE BACKEND KEY

    amount: orderData.amount,
    currency: orderData.currency || 'INR',
    name: 'Parallel',
    description: 'Order Payment',
    order_id: razorpayOrderId,

    handler: async function (response) {
  try {
    loading.value = true

    console.log('PAYMENT SUCCESS =', response)

    const verifyPayload = {
      order_id: Number(currentOrderId.value),
      razorpay_order_id: response.razorpay_order_id,
      razorpay_payment_id: response.razorpay_payment_id,
      razorpay_signature: response.razorpay_signature
    }

    const verifyResponse = await verifyRazorpayPayment(verifyPayload)
    console.log('VERIFY PAYMENT RESPONSE =', verifyResponse)

    await router.push('/checkout/summary')
  } catch (error) {
    console.error('Payment verification failed:', error)
    console.error('Verification response:', error?.response?.data)
    alert(getErrorMessage(error, 'Payment verification failed'))
  } finally {
    loading.value = false
  }
},

    theme: {
      color: '#0b5f63'
    }
  }

  console.log("RAZORPAY OPTIONS =", options)

  const rzp = new window.Razorpay(options)
  rzp.open()
}

async function continueToSummary() {
  const userId = getUserId()
  const selectedAddressId = getSelectedAddressId()

  if (!userId) {
    router.push('/login?redirect=/checkout/payment')
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
    savePaymentMethod(selectedMethod.value)

    const payload = {
      user_id: Number(userId),
      address_id: Number(selectedAddressId),
      payment_method: selectedMethod.value.toUpperCase(),
      coupon_code: appliedCoupon.value || null,
      shipping_amount: Number(deliveryCharges.value || 0)
    }

    const checkoutResponse = await createCheckoutSession(payload)
    console.log('CHECKOUT RESPONSE =', checkoutResponse)

    currentOrderId.value =
      checkoutResponse?.order?.id ||
      checkoutResponse?.order_id ||
      null

    if (!currentOrderId.value) {
      alert('Order ID not received from backend')
      return
    }

    if (selectedMethod.value === 'cod') {
      router.push('/checkout/summary')
      return
    }

    const payableAmount =
      Number(
        checkoutResponse?.pricing?.total_amount ||
        checkoutResponse?.total_amount ||
        finalPayable.value ||
        0
      )

    if (!payableAmount || payableAmount <= 0) {
      alert('Invalid payment amount')
      return
    }

    const orderData = await createRazorpayOrder({
      userId: Number(userId),
      amount: payableAmount,
      currency: 'INR',
      receipt: `order_${currentOrderId.value}`
    })

    console.log('RAZORPAY ORDER DATA =', orderData)

    await openRazorpay(orderData)
  } catch (error) {
    console.error('Checkout create failed:', error)
    console.error('Backend error response:', error?.response?.data)
    alert(getErrorMessage(error, 'Failed to continue checkout'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.payment-page {
  background: #f5f5f5;
  min-height: 100vh;
  padding: 10px 0 30px;
  font-family: 'DM Sans', sans-serif;
}

.payment-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 370px;
  gap: 28px;
  align-items: start;
}

.payment-left {
  padding: 0 18px 0 12px;
}

.back-link {
  border: none;
  background: transparent;
  color: #2c3b3d;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  cursor: pointer;
  margin-bottom: 26px;
  padding: 0;
}

.page-title {
  font-size: 34px;
  line-height: 1.1;
  font-weight: 700;
  color: #0b5f63;
  margin: 0 0 10px;
}

.page-subtitle {
  font-size: 16px;
  color: #40464e;
  margin: 0 0 28px;
}

.method-card {
  background: white;
  border-radius: 0;
  border: 1px solid transparent;
  padding: 28px 24px;
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.method-card--active {
  border-left: 2px solid #0b5f63;
  border-top: 1px solid #dbe2e3;
  border-right: 1px solid #dbe2e3;
  border-bottom: 1px solid #dbe2e3;
}

.method-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.method-icon-box {
  width: 46px;
  height: 46px;
  border-radius: 8px;
  background: #eef5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.method-title {
  font-size: 18px;
  font-weight: 700;
  color: #111315;
  margin-bottom: 4px;
}

.method-desc {
  font-size: 14px;
  color: #4c4f57;
}

.radio-circle {
  width: 26px;
  height: 26px;
  border: 2px solid #b7c0c2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.radio-circle--active {
  border-color: #0b5f63;
}

.radio-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #0b5f63;
}

.card-form-box {
  background: white;
  padding: 28px 38px 34px;
  margin-top: -18px;
  margin-bottom: 24px;
  border-left: 1px solid #e3e7e8;
  border-right: 1px solid #e3e7e8;
  border-bottom: 1px solid #e3e7e8;
}

.field-group {
  margin-bottom: 28px;
}

.field-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #1f252a;
  margin-bottom: 12px;
}

.field-input {
  width: 100%;
  height: 66px;
  border: none;
  background: #f7f7f7;
  border-radius: 10px;
  padding: 0 20px;
  font-size: 18px;
  color: #5d6674;
  outline: none;
  box-sizing: border-box;
}

.field-input::placeholder {
  color: #7f8794;
}

.input-with-icon {
  position: relative;
}

.input-lock {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.field-half {
  margin-bottom: 0;
}

.security-note {
  margin-top: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2d3338;
  font-size: 15px;
}

.payment-right {
  border-left: 1px solid #d7ddde;
  padding-left: 24px;
  margin-top: 16px;
}

.price-card {
  background: #f8f9f9;
  border-radius: 18px;
  padding: 26px 24px;
}

.summary-title {
  font-size: 22px;
  font-weight: 700;
  color: #243746;
  margin: 0 0 24px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 18px;
  color: #4f5d73;
}

.discount-row {
  color: #0f8b65;
}

.summary-divider {
  height: 1px;
  background: #9098a0;
  margin: 18px 0 18px;
  opacity: 0.6;
}

.total-row {
  font-size: 22px;
  font-weight: 800;
  color: #101828;
  margin-bottom: 24px;
}

.coupon-section {
  margin-top: 12px;
  margin-bottom: 22px;
}

.coupon-title {
  font-size: 14px;
  font-weight: 700;
  color: #243746;
  margin-bottom: 10px;
}

.coupon-input-row {
  display: flex;
  gap: 10px;
}

.coupon-input {
  flex: 1;
  height: 44px;
  border: 1px solid #cfd8da;
  border-radius: 8px;
  padding: 0 14px;
  font-size: 14px;
  outline: none;
  background: white;
}

.coupon-input:focus {
  border-color: #0b5f63;
}

.coupon-btn {
  height: 44px;
  padding: 0 18px;
  border: none;
  border-radius: 8px;
  background: #0b5f63;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.coupon-success {
  margin-top: 10px;
  background: #d8f3e8;
  color: #0f8b65;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
}

.remove-coupon {
  margin-left: 10px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
}

.coupon-error {
  margin-top: 10px;
  color: #d64545;
  font-size: 14px;
}

.solid-btn {
  width: 100%;
  border: none;
  border-radius: 14px;
  background: linear-gradient(90deg, #36c2be 0%, #24b2ae 100%);
  color: white;
  font-size: 17px;
  font-weight: 700;
  padding: 16px;
  cursor: pointer;
  margin-top: 8px;
}

.continue-shopping-btn {
  width: 100%;
  border: none;
  background: transparent;
  color: #18a7a2;
  font-size: 16px;
  font-weight: 700;
  padding: 16px 0 0;
  cursor: pointer;
}

@media (max-width: 900px) {
  .payment-wrapper {
    grid-template-columns: 1fr;
  }

  .payment-right {
    border-left: none;
    padding-left: 0;
  }

  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
