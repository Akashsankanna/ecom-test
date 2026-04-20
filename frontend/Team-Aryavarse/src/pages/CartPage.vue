<template>
  <q-page class="cart-page">
    <div class="cart-container">
      <h1 class="cart-heading">Shopping Cart</h1>

      <div class="cart-layout">
        <!-- LEFT SIDE -->
        <div class="cart-left">
          <div v-if="hasItems">
            <div
              v-for="item in cart"
              :key="item.id"
              class="cart-card"
            >
              <!-- image -->
              <img
                :src="item.image || item.image_url"
                :alt="item.title || item.product_name"
                class="cart-img"
              />

              <!-- details -->
              <div class="cart-info">
                <h3 class="product-title">
                  {{ item.title || item.product_name }}
                </h3>

                <p class="product-meta">
                  <template v-if="item.variant_name">
                    Variant: {{ item.variant_name }}
                  </template>
                  <template v-else>
                    Size: {{ item.size || 'M' }}
                    <span class="dot">•</span>
                    Color: {{ item.color || 'Default' }}
                  </template>
                </p>

                <p v-if="item.price" class="product-price">
                  ₹ {{ Number(item.price).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
                </p>

                <!-- qty -->
                <div class="qty-box">
                  <button class="qty-btn" @click="updateQty(item.id, 'dec')">−</button>
                  <span class="qty-value">{{ item.qty }}</span>
                  <button class="qty-btn" @click="updateQty(item.id, 'inc')">+</button>
                </div>
              </div>

              <!-- price -->
              <div class="price-box">
                ₹ {{ (Number(item.price) * Number(item.qty)).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
              </div>

              <!-- delete -->
              <button class="delete-btn" @click="removeFromCart(item.id)">
                <q-icon name="delete_outline" size="22px" />
              </button>
            </div>
          </div>

          <!-- empty cart -->
          <div v-else class="empty-cart">
            <h3>Your cart is empty</h3>
            <p>Add some products to continue shopping.</p>
            <button class="continue-btn" @click="$router.push('/')">
              Continue Shopping
            </button>
          </div>
        </div>

        <!-- RIGHT SIDE -->
        <div v-if="hasItems" class="cart-right">
          <div class="summary-card">
            <h2>Order Summary</h2>

            <div class="summary-row">
              <span>Subtotal</span>
              <span>₹ {{ subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
            </div>

            <div class="summary-row">
              <span>Shipping</span>
              <span>
                {{ shipping === 0
                  ? 'FREE'
                  : '₹ ' + Number(shipping).toLocaleString('en-IN', { minimumFractionDigits: 2 })
                }}
              </span>
            </div>

            <div class="summary-row">
              <span>Tax (GST 18%)</span>
              <span>₹ {{ tax.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
            </div>

            <p class="shipping-msg">🎉 You've qualified for free shipping!</p>

            <hr />

            <div class="summary-row total-row">
              <span>Total</span>
              <span>₹ {{ total.toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}</span>
            </div>

            <button class="checkout-btn" @click="goToCheckout">
              Proceed to Checkout
            </button>

            <button class="shopping-link" @click="$router.push('/')">
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { cart, removeFromCart, updateQty, loadCart } from 'src/stores/shop'

const router = useRouter()

onMounted(() => {
  loadCart()
})

const goToCheckout = () => {
  const userId = localStorage.getItem('user_id')

  if (userId) {
    router.push('/checkout/address')
  } else {
    router.push('/login?redirect=/checkout/address')
  }
}

const hasItems = computed(() => cart.value.length > 0)

const subtotal = computed(() => {
  return cart.value.reduce((sum, item) => {
    return sum + Number(item.price || 0) * Number(item.qty || 0)
  }, 0)
})

const shipping = computed(() => {
  return subtotal.value > 0 ? 0 : 0
})

const tax = computed(() => {
  return subtotal.value * 0.18
})

const total = computed(() => {
  return subtotal.value + shipping.value + tax.value
})
</script>

<style lang="scss">
@import 'src/css/cart.scss';
</style>
