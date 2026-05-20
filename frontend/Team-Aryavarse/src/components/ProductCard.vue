<template>
  <!-- PRODUCT CARD COMPONENT — men/women/home screenshot sarkhi exact structure -->
  <div class="card">

    <!-- ===== IMAGE WRAPPER ===== -->
    <div
      class="img-wrapper"
      @mouseenter="hoveredLocal = true"
      @mouseleave="hoveredLocal = false"
    >
      <!-- Product Image — hover var 2nd image -->
      <img
        :src="hoveredLocal ? getProductImage(product, 1) : getProductImage(product, 0)"
        class="product-img"
        @click="$emit('go-to-product', product)"
      />

      <!-- Bestseller Badge — top-left
      <span v-if="product.isBestSeller" class="badge">Bestseller</span>--->

      <!-- Wishlist Heart — top-right -->
      <div class="card-icons" @click.stop="handleWishlist">
        <q-icon
  :name="isInWishlist ? 'favorite' : 'favorite_border'"
  size="22px"
  :class="{ 'active-heart': isInWishlist }"
/>
        <!-- Flying hearts animation -->
        <span class="fly-heart h1" :class="{ show: showFlyHeart }">❤</span>
        <span class="fly-heart h2" :class="{ show: showFlyHeart }">❤</span>
        <span class="fly-heart h3" :class="{ show: showFlyHeart }">❤</span>
        <span class="fly-heart h4" :class="{ show: showFlyHeart }">❤</span>
        <span class="fly-heart h5" :class="{ show: showFlyHeart }">❤</span>
      </div>

      <!-- Quick View hover button -->
      <div class="hover-actions" v-if="hoveredLocal">
        <button class="quick-btn" @click="$emit('go-to-product', product)">
          Quick View
        </button>
      </div>
    </div>

    <!-- ===== CARD CONTENT — screenshot madhe exact jas aahe ===== -->
    <div class="card-content">

      <!-- Fabric label + tooltip -->
      <div class="fabric-wrap">
        <span class="fabric-link">{{ product.fabric }}</span>
        <div class="fabric-tooltip">
          {{ getFabricDescription(product.fabric) }}
        </div>
      </div>

      <!-- Product title -->
      <p class="title" @click="$emit('go-to-product', product)">{{ product.title }}</p>

      <!-- Rating stars + number -->
      <div class="rating-row" @click="$emit('go-to-product', product)">
        <span class="stars">★★★★★</span>
        <span class="rating-text">{{ product.rating || 4.5 }}</span>
      </div>

      <!-- Price -->
      <div class="price-row"  @click="$emit('go-to-product', product)">
      <!---dynamic--->
        <p class="price">₹ {{ formatPrice(product.price) }}</p>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

// Props
const props = defineProps({
  product: {
    type: Object,
    required: true
  },

  wishlistIds: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits([
  'go-to-product',
  'wishlist-updated'
])

const router = useRouter()

// Local hover state
const hoveredLocal = ref(false)
const showFlyHeart = ref(false)

// =========================
// PRODUCT IMAGES
// =========================
const getProductImage = (product, index = 0) => {
  if (product.images && product.images.length > 0) {
    return (
      product.images[index] ||
      product.images[0]
    )
  }

  return product.image
}


// =========================
// PRICE FORMAT
// =========================
const formatPrice = (price) => {
  return new Intl.NumberFormat(
    'en-IN',
    {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }
  ).format(price || 0)
}


// =========================
// USER ID
// =========================
const getUserId = () => {
  try {
    const user = JSON.parse(
      localStorage.getItem('user') || '{}'
    )

    return (
      localStorage.getItem('user_id') ||
      user?.id ||
      null
    )
  } catch {
    return (
      localStorage.getItem('user_id') ||
      null
    )
  }
}

// =========================
// WISHLIST CHECK
// =========================
const isInWishlist = computed(() => {
  return props.wishlistIds.includes(
    Number(props.product.variant_id)
  )
})

// =========================
// HANDLE WISHLIST
// =========================
const handleWishlist = async () => {
  try {
    const userId = getUserId()

    // Login check
    if (!userId) {
      router.push('/login')
      return
    }

    const variantId = Number(
      props.product.variant_id
    )

    if (
      !variantId ||
      Number.isNaN(variantId)
    ) {
      console.error(
        'VARIANT ID MISSING:',
        props.product
      )

      return
    }

    // REMOVE
    if (isInWishlist.value) {
      await api.delete(
        '/wishlist/remove',
        {
          params: {
            user_id: userId
          },

          data: {
            variant_id: variantId
          }
        }
      )

      emit(
        'wishlist-updated',
        {
          type: 'remove',
          variantId
        }
      )
    }

    // ADD
    else {
      await api.post(
        '/wishlist/add',
        {
          variant_id: variantId
        },
        {
          params: {
            user_id: userId
          }
        }
      )

      emit(
        'wishlist-updated',
        {
          type: 'add',
          variantId
        }
      )
    }

    // Flying hearts
    showFlyHeart.value = true

    setTimeout(() => {
      showFlyHeart.value = false
    }, 900)
  } catch (err) {
    console.error(
      'WISHLIST ERROR:',
      err.response?.data || err
    )
  }
}

// =========================
// FABRIC TOOLTIP
// =========================
const fabricMap = {
  Classic:
    'Classic fit • Soft feel • Everyday comfort',

  Ecoflex:
    'Ecoflex stretch • Breathable • Premium movement',

  'Ecoflex Lite':
    'Ecoflex Lite • Ultra light • Max comfort',

  'Cotton Aprons':
    'Cotton apron • Breathable • Daily use',

  'Raymond Aprons':
    'Raymond fabric • Premium quality • Durable',

  'Polycotton Aprons':
    'PolyCotton blend • Strong • Easy maintenance'
}

const getFabricDescription = (
  fabric
) => {
  return (
    fabricMap[fabric] ||
    'Premium scrub fabric'
  )
}

</script>

<style scoped lang="scss">
@use 'src/css/Product-card.scss' as *;
</style>
