<template>
  <div v-if="product" class="product-page">
    <div class="left">
      <div class="thumbs">
        <img
          v-for="img in product.images"
          :key="img"
          :src="img"
          :class="{ active: selectedImage === img }"
          @click="selectedImage = img"
        />
      </div>

      <div class="main-image-box" @click="dialog = true">
        <img :src="selectedImage" class="main-image" />
      </div>
    </div>

    <div class="right">
      <p class="tag">Premium Collection</p>
      <h1>{{ product.title }}</h1>

      <div class="rating-row">
        <span class="stars">★★★★★</span>
        <span class="rating">{{ product.rating }} Rating</span>
      </div>

      <h2>{{ product.price }}</h2>

      <p class="desc">{{ product.description }}</p>

      <div class="info-box">
        <p><strong>Fabric:</strong> {{ product.fabric }}</p>
        <p><strong>Color:</strong> {{ product.color }}</p>
        <p><strong>Category:</strong> Premium Wear</p>
      </div>

      <!-- Size -->
      <div class="size-section">
        <p class="size-label">Select Size</p>

        <div class="size-options">
          <button
            v-for="size in sizes"
            :key="size"
            class="size-btn"
            :class="{ active: selectedSize === size }"
            @click="selectedSize = size"
          >
            {{ size }}
          </button>
        </div>
      </div>

      <div class="btns">
        <button class="cart-btn" @click="handleAddToCart">Add to Cart</button>
        <button class="wish-btn" @click="toggleWishlist(product)">Wishlist</button>
      </div>
    </div>

    <q-dialog v-model="dialog" persistent>
      <div class="popup">
        <button class="close-btn" @click="dialog = false">✕</button>
        <img :src="selectedImage" class="popup-image" />
      </div>
    </q-dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
//import { products } from 'src/data/products'
import { addToCart, toggleWishlist } from 'src/stores/shop'

const route = useRoute()

const sizes = ['S', 'M', 'L', 'XL']
const selectedSize = ref('M')

const product = computed(() =>
  products.find(p => p.id === Number(route.params.id))
)

const selectedImage = ref('')
const dialog = ref(false)

watch(product, (val) => {
  if (val) selectedImage.value = val.images[0]
}, { immediate: true })

// add to cart with selected size
const handleAddToCart = () => {
  addToCart({
    ...product.value,
    size: selectedSize.value
  })
}
</script>

<style scoped lang="scss">
@import 'src/css/product-details.scss';
</style>
