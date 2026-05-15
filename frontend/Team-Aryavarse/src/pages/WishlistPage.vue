<template>
  <q-page class="wishlist-page">
    <div class="wishlist-container">

      <!-- Header -->
      <div class="wishlist-header-row">
        <div class="heading-left">
          <span class="heading-icon">
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="#0f7b6c"
              stroke="#0f7b6c"
              stroke-width="1.5"
            >
              <path
                d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
              />
            </svg>
          </span>

          <h1 class="wishlist-heading">My Wishlist</h1>

          <span v-if="wishlist.length > 0" class="item-pill">
            {{ wishlist.length }} items
          </span>
        </div>
      </div>

      <div class="wishlist-layout">
        <div class="wishlist-left">

          <!-- Wishlist items -->
          <div v-if="wishlist.length > 0">
            <div
              v-for="item in wishlist"
              :key="item.variant_id"
              class="wishlist-card"
            >
              <!-- Image -->
              <div class="img-container" @click="$router.push(getRoute(item))">
                <img
                  :src="item.image"
                  :alt="item.title"
                  class="wishlist-img"
                />

                <div class="img-shine"></div>

                <div class="img-overlay-btn">
                  <svg
                    width="13"
                    height="13"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  View
                </div>
              </div>

              <!-- Details -->
              <div class="wishlist-info">
                <div class="info-top">
                  <h3
                    class="product-title"
                    @click="$router.push(getRoute(item))"
                  >
                    {{ item.title }}
                  </h3>

                  <p class="product-meta">
                    Size: {{ item.size || 'M' }}
                    <span class="dot">•</span>
                    Color: {{ item.color || 'Default' }}
                  </p>
                </div>

                <!-- Footer -->
                <div class="card-footer">
                  <div class="price-box">
                    <span class="price-main">
                      {{ formatPrice(item.price) }}
                    </span>

                    <span
                      v-if="item.originalPrice && item.originalPrice > item.price"
                      class="price-old"
                    >
                      {{ formatPrice(item.originalPrice) }}
                    </span>
                  </div>

                  <div class="wishlist-btns">
                    <button
                      class="cart-btn"
                      :disabled="loadingItem === item.variant_id"
                      @click="addToCart(item)"
                    >
                      <svg
                        v-if="loadingItem !== item.variant_id"
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.5"
                      >
                        <circle cx="9" cy="21" r="1" />
                        <circle cx="20" cy="21" r="1" />
                        <path
                          d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
                        />
                      </svg>

                      {{ loadingItem === item.variant_id ? 'Adding...' : 'Add to Cart' }}
                    </button>

                    <button
                      class="remove-btn"
                      :disabled="loadingItem === item.variant_id"
                      @click="removeFromWishlist(item)"
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.5"
                      >
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                        <path d="M10 11v6M14 11v6" />
                      </svg>

                      Remove
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty wishlist -->
          <div v-else class="empty-wishlist">
            <div class="empty-heart">
              <svg
                width="58"
                height="58"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#0f7b6c"
                stroke-width="1.2"
              >
                <path
                  d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                />
              </svg>
            </div>

            <h3 class="empty-title">Your wishlist is empty</h3>
            <p class="empty-sub">Save your favorite scrubs &amp; aprons here.</p>

            <button class="continue-btn" @click="$router.push('/')">
              <svg
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              </svg>
              Continue Shopping
            </button>
          </div>

        </div>
      </div>

    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'

const wishlist = ref([])
const loadingItem = ref(null)

/* ---------------- GET USER ---------------- */

const getUserId = () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')

    return (
      localStorage.getItem('user_id') ||
      user?.id ||
      user?.user_id ||
      user?.user?.id ||
      user?.data?.id ||
      null
    )
  } catch {
    return localStorage.getItem('user_id') || null
  }
}

/* ---------------- FORMAT PRICE ---------------- */

const formatPrice = (price) => {
  const amount = Number(price || 0)

  return amount.toLocaleString('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

/* ---------------- LOAD WISHLIST ---------------- */

const loadWishlist = async () => {
  try {
    const userId = getUserId()

    if (!userId) {
      wishlist.value = []
      console.warn('USER ID MISSING: Please login to view wishlist')
      return
    }

    const res = await api.get('/wishlist/', {
      params: {
        user_id: Number(userId)
      }
    })

    console.log('WISHLIST RESPONSE:', res.data)

    const data = Array.isArray(res.data)
      ? res.data
      : Array.isArray(res.data?.items)
        ? res.data.items
        : Array.isArray(res.data?.wishlist)
          ? res.data.wishlist
          : Array.isArray(res.data?.data)
            ? res.data.data
            : []

    wishlist.value = data.map((item) => ({
      id: Number(item.wishlist_item_id || item.id || item.product_id || 0),
      wishlist_item_id: Number(item.wishlist_item_id || item.id || 0),

      product_id: Number(item.product_id || item.db_product_id || 0),
      db_product_id: Number(item.product_id || item.db_product_id || 0),

      variant_id: Number(item.variant_id || 0),

      title: item.product_name || item.title || item.name || 'Product',
      name: item.product_name || item.title || item.name || 'Product',

      image: item.image_url || item.image || '/favicon.ico',
      image_url: item.image_url || item.image || '/favicon.ico',

      price: Number(item.price || item.min_price || item.selling_price || 0),
      originalPrice: Number(item.original_price || item.originalPrice || 0),

      size: item.size || '',
      color: item.color || item.color_name || '',
      stock: Number(item.stock || item.available_stock || 0),

      type: String(item.type || item.gender || item.category_name || '').toLowerCase()
    }))
  } catch (error) {
    console.error('WISHLIST LOAD ERROR:', error.response?.data || error)
    wishlist.value = []
  }
}

/* ---------------- ADD TO CART + REMOVE FROM WISHLIST ---------------- */

const addToCart = async (item) => {
  try {
    const userId = getUserId()

    if (!userId) {
      alert('Please login to add product to cart')
      return
    }

    if (!item?.variant_id) {
      console.error('VARIANT ID MISSING IN WISHLIST ITEM:', item)
      alert('Product variant missing. Cannot add to cart.')
      return
    }

    loadingItem.value = item.variant_id

    const payload = {
      user_id: Number(userId),
      variant_id: Number(item.variant_id),
      quantity: 1
    }

    console.log('ADD TO CART PAYLOAD:', payload)

    await api.post('/cart/add', payload)

    await removeFromWishlist(item, false)

    wishlist.value = wishlist.value.filter(
      (wishItem) => Number(wishItem.variant_id) !== Number(item.variant_id)
    )

    alert('Product added to cart')
  } catch (error) {
    console.error('ADD TO CART FROM WISHLIST ERROR:', error.response?.data || error)
    alert(error.response?.data?.detail || 'Failed to add product to cart')
  } finally {
    loadingItem.value = null
  }
}

/* ---------------- REMOVE FROM WISHLIST ---------------- */

const removeFromWishlist = async (item, showAlert = true) => {
  try {
    const userId = getUserId()

    if (!userId) {
      alert('Please login to remove wishlist item')
      return
    }

    if (!item?.variant_id) {
      console.error('VARIANT ID MISSING FOR REMOVE:', item)
      alert('Product variant missing. Cannot remove.')
      return
    }

    await api.delete('/wishlist/remove', {
      params: {
        user_id: Number(userId)
      },
      data: {
        variant_id: Number(item.variant_id)
      }
    })

    wishlist.value = wishlist.value.filter(
      (wishItem) => Number(wishItem.variant_id) !== Number(item.variant_id)
    )

    if (showAlert) {
      alert('Product removed from wishlist')
    }
  } catch (error) {
    console.error('REMOVE WISHLIST ERROR:', error.response?.data || error)
    alert(error.response?.data?.detail || 'Failed to remove product from wishlist')
  }
}

/* ---------------- PRODUCT ROUTE ---------------- */

const getRoute = (item) => {
  const type = String(item?.type || '').toLowerCase()
  const productId = item?.db_product_id || item?.product_id || item?.id

  if (!productId) return '/'

  if (type.includes('women')) return `/women-product/${productId}`
  if (type.includes('men')) return `/men-product/${productId}`
  if (type.includes('apron')) return `/aprons-product/${productId}`

  return `/product/${productId}`
}

/* ---------------- MOUNT ---------------- */

onMounted(() => {
  loadWishlist()
})
</script>

<style lang="scss">
@import 'src/css/wishlist.scss';
</style>
