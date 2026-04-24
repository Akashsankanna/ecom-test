<template>
  <q-page class="cart-page">
    <div class="cart-container">
      <h1 class="cart-heading">Shopping Cart</h1>

      <div class="cart-layout">
        <div class="cart-left">
          <div v-if="hasItems">
            <div
              v-for="item in cart"
              :key="item.id || item.cart_item_id"
              class="cart-card"
            >
              <img
                :src="item.image || item.image_url || item.product_image || '/favicon.ico'"
                :alt="item.title || item.product_name || item.name || 'Product'"
                class="cart-img"
              />

              <div class="cart-info">
                <h3 class="product-title">
                  {{ item.title || item.product_name || item.name || 'Product' }}
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

                <p class="product-price">
                  ₹ {{ Number(item.price || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
                </p>

                <div class="qty-box">
                  <button class="qty-btn" @click="updateQty(item.id || item.cart_item_id, 'dec')">−</button>
                  <span class="qty-value">{{ item.qty || item.quantity || 1 }}</span>
                  <button class="qty-btn" @click="updateQty(item.id || item.cart_item_id, 'inc')">+</button>
                </div>
              </div>

              <div class="price-box">
                ₹ {{ (Number(item.price || 0) * Number(item.qty || item.quantity || 1)).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
              </div>

              <button class="delete-btn" @click="removeFromCart(item.id || item.cart_item_id)">
                <q-icon name="delete_outline" size="22px" />
              </button>
            </div>

            <div class="cart-actions">
              <button class="checkout-btn" @click="goToCheckout">
                Proceed to Checkout
              </button>

              <button class="shopping-link" @click="$router.push('/')">
                Continue Shopping
              </button>
            </div>
          </div>

          <div v-else class="empty-cart">
            <h3>Your cart is empty</h3>
            <p>Add some products to continue shopping.</p>
            <button class="continue-btn" @click="$router.push('/')">
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
</script>

<style lang="scss">
@import 'src/css/cart.scss';
</style>
