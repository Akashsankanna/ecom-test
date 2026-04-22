<template>
  <q-page class="checkout-page">
    <div class="checkout-wrapper">
      <!-- LEFT -->
      <div class="address-section">
        <div class="section-header">
          <h1 class="page-title">Select Delivery Address</h1>
          <button class="add-address-link" @click="openAddAddress">
            + ADD NEW ADDRESS
          </button>
        </div>

        <div
          v-for="address in addresses"
          :key="address.id"
          class="address-card"
          :class="{ 'address-card--active': selectedAddressId === address.id }"
        >
          <div class="address-top">
            <div class="address-left">
              <q-radio
                :model-value="selectedAddressId"
                :val="address.id"
                color="teal"
                @update:model-value="selectAddress(address)"
              />

              <div class="address-content">
                <div class="address-name-row">
                  <h3 class="address-name">{{ address.full_name }}</h3>
                  <span v-if="address.is_default" class="default-badge">DEFAULT</span>
                </div>

                <p class="address-line">
                  {{ address.address_line1 }}
                  <span v-if="address.address_line2">, {{ address.address_line2 }}</span>
                  <span v-if="address.landmark">, {{ address.landmark }}</span>,
                  {{ address.city }}, {{ address.state }}, {{ address.country }},
                  {{ address.postal_code }}
                </p>

                <p class="address-phone">{{ address.phone }}</p>
                <p v-if="address.email" class="address-email">{{ address.email }}</p>
              </div>
            </div>

            <div class="address-actions">
              <button class="edit-btn" @click="openEditAddress(address)">
                EDIT
              </button>
              <button class="delete-btn" @click="deleteAddress(address)">
                DELETE
              </button>
            </div>
          </div>

          <button
            v-if="selectedAddressId === address.id"
            class="deliver-btn"
            @click="deliverToThisAddress"
          >
            Deliver to this Address
          </button>
        </div>

        <div v-if="!addresses.length && !loading" class="empty-address-box">
          <p>No saved address found.</p>
          <button class="deliver-btn" @click="openAddAddress">
            Add New Address
          </button>
        </div>
      </div>

      <!-- RIGHT -->
      <div class="price-section">
        <div class="price-card">
          <h2 class="price-title">Price Details ({{ totalItems }} Items)</h2>

          <div class="price-row">
            <span>Subtotal</span>
            <span>₹ {{ subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="price-row">
            <span>Delivery Charges</span>
            <span>
              ₹ {{ deliveryCharges.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
            </span>
          </div>

          <div class="price-row">
            <span>{{ gstLabel }}</span>
            <span>₹ {{ tax.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="divider"></div>

          <div class="price-row total-row">
            <span>Total</span>
            <span>₹ {{ grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
          </div>

          <div class="coupon-section">
            <label class="coupon-label">Apply Coupon</label>
            <div class="coupon-row">
              <input
                v-model.trim="couponCode"
                type="text"
                class="coupon-input"
                placeholder="Enter coupon code"
              />
              <button class="apply-btn" @click="applyCoupon">
                Apply
              </button>
            </div>
          </div>

          <button class="proceed-btn" type="button" @click="placeOrder">
           Place Order
          </button>
        </div>
      </div>
    </div>

    <!-- ADD / EDIT ADDRESS POPUP -->
    <q-dialog
      v-model="showAddressDialog"
      persistent
      transition-show="scale"
      transition-hide="scale"
    >
      <q-card class="address-dialog-card">
        <q-card-section class="dialog-header">
          <div>
            <h3 class="dialog-title">
              {{ isEditMode ? 'Edit Address' : 'Add New Address' }}
            </h3>
            <p class="dialog-subtitle">
              Fill the delivery details to continue checkout.
            </p>
          </div>

          <q-btn flat round dense icon="close" @click="closeDialog" />
        </q-card-section>

        <q-separator />

        <q-card-section class="dialog-body">
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <q-input
                v-model.trim="form.full_name"
                label="Full Name *"
                outlined
                dense
                :error="!!errors.full_name"
                :error-message="errors.full_name"
              />
            </div>

            <div class="col-12 col-md-6">
              <q-input
                v-model.trim="form.phone"
                label="Phone Number *"
                outlined
                dense
                maxlength="10"
                :error="!!errors.phone"
                :error-message="errors.phone"
              />
            </div>

            <div class="col-12">
              <q-input
                v-model.trim="form.email"
                label="Email *"
                outlined
                dense
                :error="!!errors.email"
                :error-message="errors.email"
              />
            </div>

            <div class="col-12">
              <q-input
                v-model.trim="form.address_line1"
                label="Address Line 1 *"
                outlined
                dense
                :error="!!errors.address_line1"
                :error-message="errors.address_line1"
              />
            </div>

            <div class="col-12">
              <q-input
                v-model.trim="form.address_line2"
                label="Address Line 2"
                outlined
                dense
              />
            </div>

            <div class="col-12">
              <q-input
                v-model.trim="form.landmark"
                label="Landmark"
                outlined
                dense
              />
            </div>

            <div class="col-12 col-md-4">
              <q-input
                v-model.trim="form.city"
                label="City *"
                outlined
                dense
                :error="!!errors.city"
                :error-message="errors.city"
              />
            </div>

            <div class="col-12 col-md-4">
              <q-input
                v-model.trim="form.state"
                label="State *"
                outlined
                dense
                :error="!!errors.state"
                :error-message="errors.state"
              />
            </div>

            <div class="col-12 col-md-4">
              <q-input
                v-model.trim="form.postal_code"
                label="Pincode *"
                outlined
                dense
                maxlength="6"
                :error="!!errors.postal_code"
                :error-message="errors.postal_code"
              />
            </div>

            <div class="col-12 col-md-6">
              <q-input
                v-model.trim="form.country"
                label="Country *"
                outlined
                dense
                :error="!!errors.country"
                :error-message="errors.country"
              />
            </div>

            <div class="col-12 col-md-6">
              <q-select
                v-model="form.address_type"
                :options="['HOME', 'WORK', 'OTHER']"
                label="Address Type *"
                outlined
                dense
                :error="!!errors.address_type"
                :error-message="errors.address_type"
              />
            </div>

            <div class="col-12">
              <q-checkbox
                v-model="form.is_default"
                label="Set as default address"
                color="teal"
              />
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="dialog-actions">
          <q-btn flat label="Cancel" @click="closeDialog" />
          <q-btn
            color="teal"
            label="Save Address"
            @click="saveAddress"
            :loading="saving"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { cart } from 'src/stores/shop'
import {
  getCheckoutProfile,
  saveCheckoutProfile,
  getUserId,
  getSelectedAddressId,
  saveSelectedAddressId,
  clearSelectedAddressId
} from 'src/utils/CheckoutStorage'
import {
  fetchAddresses,
  createAddress,
  updateAddress,
  removeAddress
} from 'src/service/addressService.js'
import {
  createRazorpayOrder,
  verifyRazorpayPayment
} from 'src/service/checkoutService'

const router = useRouter()

const addresses = ref([])
const selectedAddressId = ref(null)
const showAddressDialog = ref(false)
const isEditMode = ref(false)
const editingAddressId = ref(null)
const loading = ref(false)
const saving = ref(false)
const couponCode = ref('')

const WAREHOUSE_PINCODE = '413005'

const form = reactive({
  full_name: '',
  phone: '',
  email: '',
  address_line1: '',
  address_line2: '',
  landmark: '',
  city: '',
  state: '',
  country: 'India',
  postal_code: '',
  address_type: 'HOME',
  is_default: true
})

const errors = reactive({
  full_name: '',
  phone: '',
  email: '',
  address_line1: '',
  city: '',
  state: '',
  country: '',
  postal_code: '',
  address_type: ''
})

onMounted(() => {
  loadAddresses()
})

async function loadAddresses() {
  const userId = getUserId()

  if (!userId) {
    router.push('/login?redirect=/checkout/address')
    return
  }

  try {
    loading.value = true

    const data = await fetchAddresses(userId)
    addresses.value = Array.isArray(data) ? data : (data?.data || data?.items || [])

    const savedId = getSelectedAddressId()

    if (savedId && addresses.value.some(addr => Number(addr.id) === Number(savedId))) {
      selectedAddressId.value = Number(savedId)
    } else if (addresses.value.length > 0) {
      const defaultAddress = addresses.value.find(addr => addr.is_default) || addresses.value[0]
      selectedAddressId.value = Number(defaultAddress.id)
      saveSelectedAddressId(defaultAddress.id)
    } else {
      selectedAddressId.value = null
      clearSelectedAddressId()
    }
  } catch (error) {
    console.error('Failed to load addresses:', error)
    addresses.value = []
  } finally {
    loading.value = false
  }
}

function selectAddress(address) {
  selectedAddressId.value = Number(address.id)
  saveSelectedAddressId(address.id)
}

function deliverToThisAddress() {
  if (!selectedAddressId.value) {
    alert('Please select an address')
    return
  }

  saveSelectedAddressId(selectedAddressId.value)
  router.push('/checkout/payment')
}

async function placeOrder() {
  try {
    const userId = Number(getUserId())
    const addressId = Number(selectedAddressId.value)

    if (!userId) {
      alert('Login required')
      return
    }

    if (!addressId) {
      alert('Select address')
      return
    }

    if (!cart.value.length) {
      alert('Cart empty')
      return
    }

    const sdkLoaded = await loadRazorpayScript()
    if (!sdkLoaded) {
      alert('Razorpay load failed')
      return
    }

    // ✅ CREATE ORDER
    const orderData = await createRazorpayOrder({
      amount: Number(grandTotal.value),
      currency: 'INR',
      receipt: `receipt_${Date.now()}`,
      user_id: userId
    })

    console.log('ORDER DATA =', orderData)

    if (!orderData?.razorpay_order_id) {
      alert('Order creation failed')
      return
    }

    const options = {
      key: orderData.key_id,
      amount: orderData.amount,
      currency: orderData.currency,
      name: 'Parallel',
      order_id: orderData.razorpay_order_id,

      handler: async function (response) {
        try {
          // ✅ VERIFY PAYMENT
          const verifyRes = await verifyRazorpayPayment({
            order_id: orderData.order_id || orderData.id || null,
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
            user_id: userId,
            address_id: addressId
          })

          console.log('VERIFY =', verifyRes)

          // ✅ SAFE SUCCESS CHECK
          const isVerified =
            verifyRes?.success === true ||
            verifyRes?.status === 'success' ||
            String(verifyRes?.message || '').toLowerCase().includes('verified')

          if (isVerified) {
            alert('Payment Success')

            // 🔥 CLEAR CART (FRONTEND)
            cart.value = []

            // 🔥 CLEAR LOCAL STORAGE
            localStorage.removeItem('cart')
            localStorage.removeItem('guest_id')

            // ✅ REDIRECT
            router.push('/order-confirmed')

          } else {
            alert('Verification failed')
          }

        } catch (err) {
          console.error('VERIFY ERROR =', err)
          console.error('VERIFY ERROR DATA =', err?.response?.data)

          const detail = err?.response?.data?.detail

          if (Array.isArray(detail)) {
            alert(detail.map(d => d.msg).join('\n'))
          } else {
            alert(detail || err?.response?.data?.message || 'Verify error')
          }
        }
      }
    }

    const rzp = new window.Razorpay(options)

    rzp.on('payment.failed', function (res) {
      console.error(res)
      alert(res?.error?.description || 'Payment failed')
    })

    rzp.open()

  } catch (error) {
    console.error('ERROR =', error)
    console.log('FULL ERROR =', error?.response?.data)

    const detail = error?.response?.data?.detail

    if (Array.isArray(detail)) {
      alert(detail.map(d => d.msg).join('\n'))
    } else {
      alert(detail || 'Something went wrong')
    }
  }
}

function applyCoupon() {
  if (!couponCode.value) {
    alert('Please enter coupon code')
    return
  }

  alert(`Coupon "${couponCode.value}" applied`)
}

function openAddAddress() {
  resetForm()
  prefillFromProfile()
  isEditMode.value = false
  editingAddressId.value = null
  showAddressDialog.value = true
}

function openEditAddress(address) {
  resetForm()

  form.full_name = address.full_name || ''
  form.phone = address.phone || ''
  form.email = address.email || ''
  form.address_line1 = address.address_line1 || ''
  form.address_line2 = address.address_line2 || ''
  form.landmark = address.landmark || ''
  form.city = address.city || ''
  form.state = address.state || ''
  form.country = address.country || 'India'
  form.postal_code = address.postal_code || ''
  form.address_type = address.address_type || 'HOME'
  form.is_default = !!address.is_default

  isEditMode.value = true
  editingAddressId.value = address.id
  showAddressDialog.value = true
}

async function deleteAddress(address) {
  const userId = getUserId()

  if (!userId) {
    router.push('/login?redirect=/checkout/address')
    return
  }

  const confirmDelete = window.confirm(`Delete address for ${address.full_name}?`)
  if (!confirmDelete) return

  try {
    await removeAddress(address.id, userId)

    if (Number(selectedAddressId.value) === Number(address.id)) {
      clearSelectedAddressId()
      selectedAddressId.value = null
    }

    await loadAddresses()
  } catch (error) {
    console.error('Failed to delete address:', error)
    alert('Failed to delete address')
  }
}

function closeDialog() {
  showAddressDialog.value = false
}

function resetForm() {
  form.full_name = ''
  form.phone = ''
  form.email = ''
  form.address_line1 = ''
  form.address_line2 = ''
  form.landmark = ''
  form.city = ''
  form.state = ''
  form.country = 'India'
  form.postal_code = ''
  form.address_type = 'HOME'
  form.is_default = true

  clearErrors()
}

function prefillFromProfile() {
  const profile = getCheckoutProfile()

  if (profile) {
    form.full_name = profile.name || ''
    form.phone = profile.phone || ''
    form.email = profile.email || ''
  }
}

function clearErrors() {
  errors.full_name = ''
  errors.phone = ''
  errors.email = ''
  errors.address_line1 = ''
  errors.city = ''
  errors.state = ''
  errors.country = ''
  errors.postal_code = ''
  errors.address_type = ''
}

function validateForm() {
  clearErrors()
  let isValid = true

  if (!form.full_name || form.full_name.length < 3) {
    errors.full_name = 'Enter valid full name'
    isValid = false
  }

  if (!/^[6-9]\d{9}$/.test(form.phone)) {
    errors.phone = 'Enter valid 10-digit phone number'
    isValid = false
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Enter valid email address'
    isValid = false
  }

  if (!form.address_line1 || form.address_line1.length < 5) {
    errors.address_line1 = 'Enter valid address line 1'
    isValid = false
  }

  if (!form.city) {
    errors.city = 'City is required'
    isValid = false
  }

  if (!form.state) {
    errors.state = 'State is required'
    isValid = false
  }

  if (!form.country) {
    errors.country = 'Country is required'
    isValid = false
  }

  if (!/^\d{6}$/.test(form.postal_code)) {
    errors.postal_code = 'Enter valid 6-digit pincode'
    isValid = false
  }

  if (!form.address_type) {
    errors.address_type = 'Select address type'
    isValid = false
  }

  return isValid
}

async function saveAddress() {
  const userId = getUserId()

  if (!userId) {
    router.push('/login?redirect=/checkout/address')
    return
  }

  if (!validateForm()) return

  const payload = {
    user_id: userId,
    full_name: form.full_name,
    phone: form.phone,
    email: form.email,
    address_line1: form.address_line1,
    address_line2: form.address_line2,
    landmark: form.landmark,
    city: form.city,
    state: form.state,
    country: form.country,
    postal_code: form.postal_code,
    address_type: form.address_type,
    is_default: form.is_default
  }

  try {
    saving.value = true

    let savedAddress

    if (isEditMode.value) {
      savedAddress = await updateAddress(editingAddressId.value, payload)
    } else {
      savedAddress = await createAddress(payload)
    }

    saveCheckoutProfile({
      name: form.full_name,
      email: form.email,
      phone: form.phone
    })

    const finalAddressId =
      savedAddress?.id ||
      savedAddress?.data?.id ||
      editingAddressId.value

    if (finalAddressId) {
      selectedAddressId.value = Number(finalAddressId)
      saveSelectedAddressId(finalAddressId)
    }

    showAddressDialog.value = false
    await loadAddresses()
  } catch (error) {
    console.error('Failed to save address:', error)
    alert(error?.response?.data?.detail || 'Failed to save address')
  } finally {
    saving.value = false
  }
}

const selectedAddress = computed(() => {
  return addresses.value.find(addr => Number(addr.id) === Number(selectedAddressId.value)) || null
})

const totalItems = computed(() => {
  return cart.value.reduce((sum, item) => sum + Number(item.qty || 0), 0)
})

const subtotal = computed(() => {
  return cart.value.reduce((sum, item) => {
    return sum + Number(item.price || 0) * Number(item.qty || 0)
  }, 0)
})

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(true)
      return
    }

    const existingScript = document.querySelector('script[src="https://checkout.razorpay.com/v1/checkout.js"]')
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(true))
      existingScript.addEventListener('error', () => resolve(false))
      return
    }

    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.body.appendChild(script)
  })
}

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

const gstRate = computed(() => {
  return subtotal.value <= 2500 ? 0.05 : 0.18
})

const gstLabel = computed(() => {
  return subtotal.value <= 2500 ? 'Tax (GST 5%)' : 'Tax (GST 18%)'
})

const tax = computed(() => {
  return subtotal.value * gstRate.value
})

const grandTotal = computed(() => {
  return subtotal.value + deliveryCharges.value + tax.value
})
</script>

<style scoped>
.checkout-page {
  background: #f5f7f8;
  min-height: 100vh;
  padding: 32px 24px;
  font-family: 'DM Sans', sans-serif;
}

.checkout-wrapper {
  max-width: 1140px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
  align-items: start;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
  gap: 16px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #143b3f;
  margin: 0;
}

.add-address-link {
  border: none;
  background: transparent;
  color: #0f6c73;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.address-card {
  background: #eef8f8;
  border: 1px solid transparent;
  border-radius: 14px;
  padding: 22px;
  margin-bottom: 18px;
}

.address-card--active {
  border-color: #0f6c73;
  box-shadow: 0 0 0 1px rgba(15, 108, 115, 0.08);
}

.address-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.address-left {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  flex: 1;
}

.address-content {
  flex: 1;
}

.address-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.address-name {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #143b3f;
}

.default-badge {
  background: #d7f1ef;
  color: #0f6c73;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 999px;
}

.address-line {
  margin: 0 0 14px;
  font-size: 15px;
  line-height: 1.55;
  color: #48656a;
}

.address-phone,
.address-email {
  margin: 0 0 10px;
  font-size: 15px;
  color: #48656a;
}

.address-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.edit-btn,
.delete-btn {
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.edit-btn {
  color: #0f6c73;
}

.delete-btn {
  color: #b54747;
}

.deliver-btn {
  width: 100%;
  border: none;
  border-radius: 8px;
  background: linear-gradient(90deg, #0f6c73 0%, #16697a 100%);
  color: white;
  font-size: 17px;
  font-weight: 700;
  padding: 16px;
  cursor: pointer;
}

.empty-address-box {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e0e0e0;
}

.price-card {
  background: #f8f9f9;
  border-radius: 18px;
  padding: 26px 24px;
}

.price-title {
  font-size: 22px;
  font-weight: 700;
  color: #243746;
  margin: 0 0 24px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 18px;
  color: #4f5d73;
}

.divider {
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
  margin-top: 8px;
  margin-bottom: 18px;
}

.coupon-label {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: #101828;
  margin-bottom: 10px;
}

.coupon-row {
  display: flex;
  gap: 10px;
}

.coupon-input {
  flex: 1;
  height: 48px;
  border: 1px solid #d0d5dd;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 15px;
  outline: none;
  background: #fff;
}

.apply-btn {
  border: none;
  border-radius: 10px;
  background: #0f6c73;
  color: white;
  font-size: 16px;
  font-weight: 700;
  padding: 0 22px;
  cursor: pointer;
}

.proceed-btn {
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

.address-dialog-card {
  width: 100%;
  max-width: 760px;
  border-radius: 18px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.dialog-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #143b3f;
}

.dialog-subtitle {
  margin: 6px 0 0;
  color: #666;
  font-size: 14px;
}

.dialog-body {
  max-height: 70vh;
  overflow-y: auto;
}

.dialog-actions {
  padding: 16px 24px;
}

@media (max-width: 900px) {
  .checkout-wrapper {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .address-top {
    flex-direction: column;
  }

  .address-actions {
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
  }

  .coupon-row {
    flex-direction: column;
  }

  .apply-btn {
    height: 48px;
  }
}
</style>
