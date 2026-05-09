<template>
  <q-page class="wishlist-page">
    <div class="wishlist-container">
      <h1 class="wishlist-heading">My Wishlist</h1>

      <div class="wishlist-layout">
        <div class="wishlist-left">
          <div v-if="wishlist.length > 0">
            <div
              v-for="item in wishlist"
              :key="item.variant_id"
              class="wishlist-card"
            >
              <img :src="item.image" :alt="item.title" class="wishlist-img" />

              <div class="wishlist-info">
                <h3 class="product-title">{{ item.title }}</h3>

                <p class="product-meta">
                  Size: {{ item.size || 'M' }}
                  <span class="dot">•</span>
                  Color: {{ item.color || 'Default' }}
                </p>

                <div class="wishlist-btns">
                  <button
                    class="cart-btn"
                    :disabled="loadingItem === item.variant_id"
                    @click="addToCart(item)"
                  >
                    {{ loadingItem === item.variant_id ? 'Adding...' : 'Add to Cart' }}
                  </button>

                  <button
                    class="remove-btn"
                    :disabled="loadingItem === item.variant_id"
                    @click="removeFromWishlist(item)"
                  >
                    Remove
                  </button>
                </div>
              </div>

              <div class="price-box">
                ₹{{ Number(item.price || 0).toLocaleString() }}
              </div>
            </div>
          </div>

          <div v-else class="empty-wishlist">
            <h3>Your wishlist is empty</h3>
            <p>Save your favorite products here.</p>

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
      id: Number(item.wishlist_item_id || item.id || 0),
      wishlist_item_id: Number(item.wishlist_item_id || item.id || 0),

      product_id: Number(item.product_id || item.db_product_id || 0),
      db_product_id: Number(item.product_id || item.db_product_id || 0),

      variant_id: Number(item.variant_id || 0),

      title: item.product_name || item.title || item.name || 'Product',
      name: item.product_name || item.title || item.name || 'Product',

      image: item.image_url || item.image || '/favicon.ico',
      image_url: item.image_url || item.image || '/favicon.ico',

      price: Number(item.price || 0),
      size: item.size || '',
      color: item.color || item.color_name || '',
      stock: Number(item.stock || 0)
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
      variant_id: Number(item.variant_id),
      quantity: 1,
      user_id: Number(userId)
    }

    console.log('ADD TO CART PAYLOAD:', payload)

    await api.post('/cart/add', payload)

    await removeFromWishlist(item, false)

    wishlist.value = wishlist.value.filter(
      (wishItem) => Number(wishItem.variant_id) !== Number(item.variant_id)
    )

    alert('Product added to cart')
  } catch (error) {
    console.error(
      'ADD TO CART FROM WISHLIST ERROR:',
      error.response?.data || error
    )

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

onMounted(() => {
  loadWishlist()
})
</script>

<style lang="scss">
@import 'src/css/wishlist.scss';
</style>