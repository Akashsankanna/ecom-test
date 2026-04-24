<template>
  <div class="men-page">
    <div class="main-container">

      <!-- Filters — COMPONENT (desktop sidebar) -->
      <FilterSidebar
        :filterCategories="filterCategories"
        :fabrics="fabrics"
        :sleeves="sleeves"
        :colors="colors"
        v-model:selectedCategories="selectedCategories"
        v-model:selectedFabrics="selectedFabrics"
        v-model:selectedSleeves="selectedSleeves"
        v-model:selectedColors="selectedColors"
      >
        <!-- Sort button slot for mobile bottom bar -->
        <template #sort-btn>
          <SortDropdown v-model="selectedSort" />
        </template>
      </FilterSidebar>

      <!-- Products -->
      <section class="products">
        <div class="top-bar">
  <span>{{ filteredProducts.length }} items</span>

  <div class="desktop-sort-only">
    <SortDropdown v-model="selectedSort" />
  </div>
</div>
        <div class="grid">
          <div
            v-for="product in filteredProducts"
            :key="product.id"
            class="card"
          >
            <!-- Image Section -->
            <div
              class="img-wrapper"
              @mouseenter="hoveredProduct = product.id"
              @mouseleave="hoveredProduct = null"
            >
              <img
                :src="hoveredProduct === product.id ? product.images?.[1] || product.image : product.image"
                class="product-img"
                @click="goToMenProduct(product)"
              />

              <span v-if="product.isBestSeller" class="badge">Bestseller</span>

              <!-- Wishlist -->
              <div class="card-icons" @click.stop="handleWishlist(product)">
                <q-icon
                  :name="isInWishlist(product.id) ? 'favorite' : 'favorite_border'"
                  size="22px"
                  :class="{ 'active-heart': isInWishlist(product.id) }"
                />
                <span class="fly-heart h1" :class="{ show: flyingHeartId === product.id }">❤</span>
                <span class="fly-heart h2" :class="{ show: flyingHeartId === product.id }">❤</span>
                <span class="fly-heart h3" :class="{ show: flyingHeartId === product.id }">❤</span>
                <span class="fly-heart h4" :class="{ show: flyingHeartId === product.id }">❤</span>
                <span class="fly-heart h5" :class="{ show: flyingHeartId === product.id }">❤</span>
              </div>

              <!-- Hover button -->
              <div class="hover-actions" v-if="hoveredProduct === product.id">
                <button class="quick-btn" @click="goToMenProduct(product)">
                  Quick View
                </button>
              </div>
            </div>

            <!-- Content -->
            <div class="card-content">
              <div class="fabric-wrap">
                <span class="fabric-link">{{ product.fabric }}</span>
                <div class="fabric-tooltip">
                  {{ getFabricDescription(product.fabric) }}
                </div>
              </div>

              <p class="title">{{ product.title }}</p>

              <div class="rating-row">
                <span class="stars">★★★★★</span>
                <span class="rating-text">{{ product.rating || 4.8 }}</span>
              </div>

              <div class="price-row">
                <p class="price">₹ {{ Number(product.price).toFixed(2) }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Mobile bottom spacing so products aren't hidden behind sticky bar -->
    <div class="mobile-bottom-spacer" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue'
import { api } from 'boot/axios'
import { toggleWishlist, isInWishlist } from 'src/stores/shop'
import SortDropdown from 'src/components/SortDropdown.vue'
import FilterSidebar from 'src/components/FilterSidebar.vue'

const selectedSort = ref('')
const router = useRouter()

const hoveredProduct = ref(null)
const flyingHeartId = ref(null)
const loading = ref(false)

const selectedCategories = ref([])
const selectedFabrics = ref([])
const selectedColors = ref([])
const selectedSleeves = ref([])

const filterCategories = ['Scrubs', 'Aprons']
const fabrics = ['Classic', 'Ecoflex Lite', 'Ecoflex']
const sleeves = ['Full Sleeve Aprons', '3-4 Sleeve Aprons', 'Half Sleeve Aprons']
const colors = ['Brown', 'Green', 'Grey', 'Mint Green', 'Maroon', 'White']

const allMenProducts = ref([])

onMounted(() => {
  loadMenProducts()
})

async function loadMenProducts() {
  try {
    loading.value = true

    const res = await api.get('/products/')
    const rawProducts = Array.isArray(res.data)
      ? res.data
      : res.data?.products || res.data?.data || res.data?.items || []

   allMenProducts.value = rawProducts
  .filter(p => String(p.gender || '').toLowerCase() === 'men')
  .map(p => {
    const productId = Number(p.id || p.product_id || p.db_product_id)

    return {
      id: productId,
      product_id: productId,
      db_product_id: productId,

      title: p.name || p.title || 'Product',
      name: p.name || p.title || 'Product',

      price: Number(p.price || 0),

      image: p.image_url || p.image || p.thumbnail || p.product_image || '/favicon.ico',

      images: [
        p.image_url || p.image || p.thumbnail || p.product_image || '/favicon.ico'
      ],

      category: p.category_name || p.category || 'Scrubs',
      fabric: p.fabric || 'Classic',
      sleeve: p.sleeve || '',
      color: p.color || '',

      type: String(p.category_name || p.category || '').toLowerCase().includes('apron')
        ? 'aprons'
        : 'men',

      rating: p.rating || 4.8,
      isBestSeller: !!p.isBestSeller || !!p.is_bestseller
    }
  })

    console.log('MEN PRODUCTS FROM BACKEND:', allMenProducts.value)
  } catch (err) {
    console.error('MEN PRODUCTS LOAD ERROR:', err)
    allMenProducts.value = []
  } finally {
    loading.value = false
  }
}

const goToMenProduct = (product) => {
  const productId = product.product_id || product.db_product_id || product.id

  if (product.type === 'aprons') {
    router.push(`/aprons-product/${productId}`)
  } else {
    router.push(`/men-product/${productId}`)
  }
}

const handleWishlist = (product) => {
  toggleWishlist(product)
  flyingHeartId.value = product.id
  setTimeout(() => {
    flyingHeartId.value = null
  }, 900)
}

const getFabricDescription = (fabric) => {
  if (fabric === 'Classic') return 'Classic fit • Soft feel • Everyday comfort'
  if (fabric === 'Ecoflex') return 'Ecoflex stretch • Breathable • Premium movement'
  return 'Premium scrub fabric'
}

const filteredProducts = computed(() => {
  let products = allMenProducts.value.filter(product => {
    const matchCategory =
      selectedCategories.value.length === 0 ||
      selectedCategories.value.includes(product.category)

    const matchFabric =
      selectedFabrics.value.length === 0 ||
      selectedFabrics.value.includes(product.fabric)

    const matchSleeve =
      selectedSleeves.value.length === 0 ||
      selectedSleeves.value.includes(product.sleeve)

    const matchColor =
      selectedColors.value.length === 0 ||
      selectedColors.value.includes(product.color)

    return matchCategory && matchFabric && matchSleeve && matchColor
  })

  if (selectedSort.value === 'low') {
    products.sort((a, b) => a.price - b.price)
  } else if (selectedSort.value === 'high') {
    products.sort((a, b) => b.price - a.price)
  } else if (selectedSort.value === 'bestseller') {
    products = products.filter(product => product.isBestSeller)
  }

  return products
})
</script>
<style scoped lang="scss">
@import 'src/css/men.scss';

/* Mobile bottom padding so grid isn't hidden behind sticky bar */
.mobile-bottom-spacer {
  display: none;
}

@media (max-width:1000px){
  .mobile-bottom-spacer{
    display:block;
    height:72px;
  }
}
</style>
