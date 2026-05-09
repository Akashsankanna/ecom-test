<template>
  <div class="home-page">
    <div class="hero">
      <div class="hero-slider">
        <div
          class="hero-track"
          :style="{
            transform: `translateX(-${currentSlide * 100}%)`,
            transition: isTransitioning ? 'transform 0.6s ease-in-out' : 'none'
          }"
        >
          <div class="hero-slide" v-for="(slide, i) in banners" :key="i">
            <div class="hero-text">
              <h1>{{ slide.title }}</h1>

              <div class="features">
                <span v-for="f in slide.features" :key="f">{{ f }}</span>
              </div>

              <button class="shop-btn" @click="scrollToProducts">
                Shop Now
              </button>
            </div>

            <div class="hero-image-wrapper">
              <img :src="slide.image" class="hero-img" />
            </div>
          </div>

          <div class="hero-slide">
            <div class="hero-text">
              <h1>{{ banners[0].title }}</h1>
              <div class="features">
                <span v-for="f in banners[0].features" :key="f">{{ f }}</span>
              </div>
              <button class="shop-btn" @click="scrollToProducts">Shop Now</button>
            </div>

            <div class="hero-image-wrapper">
              <img :src="banners[0].image" class="hero-img" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="trusted-clients-section">
      <div class="section-header">
        <h3 class="clients-title">Our Trusted Clients</h3>
        <div class="title-underline"></div>
      </div>

      <div class="promo-strip">
        <div class="promo-track">
          <div class="promo-group">
            <div
              class="promo-item"
              v-for="(item, index) in promoItems"
              :key="'first-' + index"
            >
              <img :src="sliderImg(item.logo)" :alt="item.text" class="promo-logo" />
              <span class="promo-separator"></span>
            </div>
          </div>

          <div class="promo-group">
            <div
              class="promo-item"
              v-for="(item, index) in promoItems"
              :key="'second-' + index"
            >
              <img :src="sliderImg(item.logo)" :alt="item.text" class="promo-logo" />
              <span class="promo-separator"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="main-container">
      <FilterSidebar
        :filterCategories="filterCategories"
        :fabrics="fabrics"
        :sleeves="sleeves"
        :colors="colors"
        v-model:selectedCategories="selectedCategories"
        v-model:selectedFabrics="selectedFabrics"
        v-model:selectedSleeves="selectedSleeves"
        v-model:selectedColors="selectedColors"
        @openSort="showSortSheet = true"
      >
        <template #sort-btn>
          <SortDropdown v-model="selectedSort" />
        </template>
      </FilterSidebar>

      <section class="products" ref="productsSection">
        <div class="top-bar">
          <span>{{ filteredProducts.length }} items</span>

          <div class="desktop-sort-only">
            <SortDropdown v-model="selectedSort" />
          </div>
        </div>

        <div v-if="showSort" class="sort-dropdown">
          <div @click="setSort('popular')">MOST POPULAR</div>
          <div @click="setSort('bestseller')">BEST SELLING</div>
          <div @click="setSort('low')">LOW PRICE</div>
          <div @click="setSort('high')">HIGH PRICE</div>
        </div>

        <div class="grid">
          <div
            v-for="product in filteredProducts"
            :key="product.id + '-' + product.type"
            class="card"
          >
            <div
              class="img-wrapper"
              @mouseenter="hoveredProduct = product.id + '-' + product.type"
              @mouseleave="hoveredProduct = null"
            >
              <img
                :src="hoveredProduct === product.id + '-' + product.type
                  ? product.images?.[1] || product.images?.[0]
                  : product.images?.[0]"
                class="product-img"
                @click="goToProduct(product)"
                @error="handleImageError"
              />

              <span v-if="product.isBestSeller" class="badge">Bestseller</span>

              <div class="card-icons" @click.stop="handleWishlist(product)">
                <q-icon
                  :name="isInWishlist(product.id) ? 'favorite' : 'favorite_border'"
                  size="22px"
                  :class="{ 'active-heart': isInWishlist(product.id) }"
                />
                <span class="fly-heart h1" :class="{ show: flyingHeartId === product.id + '-' + product.type }">❤</span>
                <span class="fly-heart h2" :class="{ show: flyingHeartId === product.id + '-' + product.type }">❤</span>
                <span class="fly-heart h3" :class="{ show: flyingHeartId === product.id + '-' + product.type }">❤</span>
                <span class="fly-heart h4" :class="{ show: flyingHeartId === product.id + '-' + product.type }">❤</span>
                <span class="fly-heart h5" :class="{ show: flyingHeartId === product.id + '-' + product.type }">❤</span>
              </div>

              <div
                class="hover-actions"
                v-if="hoveredProduct === product.id + '-' + product.type"
              >
                <button class="quick-btn" @click="goToProduct(product)">
                  Quick View
                </button>
              </div>
            </div>

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

      <transition name="sort-sheet">
        <div v-if="showSortSheet" class="sort-sheet">
          <div class="sheet-overlay" @click="showSortSheet = false"></div>

          <div class="sheet-content">
            <h3>Sort By</h3>
            <div @click="setSort('bestseller')">Best Selling</div>
            <div @click="setSort('low')">Low Price</div>
            <div @click="setSort('high')">High Price</div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { api } from 'boot/axios'

import { bannerImg, sliderImg } from 'src/data/imageHelper'
import SortDropdown from 'src/components/SortDropdown.vue'
import FilterSidebar from 'src/components/FilterSidebar.vue'

const router = useRouter()

const homeProducts = ref([])
const loadingProducts = ref(false)

const selectedSort = ref('')
const showSort = ref(false)
const showSortSheet = ref(false)

const hoveredProduct = ref(null)
const flyingHeartId = ref(null)

const productsSection = ref(null)

const wishlistVariantIds = ref([])

const selectedCategories = ref([])
const selectedFabrics = ref([])
const selectedColors = ref([])
const selectedSleeves = ref([])

const filterCategories = ['Scrubs', 'Aprons']

const fabrics = [
  'Classic',
  'Ecoflex',
  'Ecoflex Lite'
]

const sleeves = [
  'Full Sleeve Aprons',
  '3-4 Sleeve Aprons',
  'Half Sleeve Aprons'
]

const colors = [
  'Maroon',
  'Black',
  'Green',
  'Dark Green',
  'Grey'
]

const banners = [
  {
    title: 'So comfortable, I Can Go Long Shifts Without Breaking a Sweat!',
    features: [
      '☁ Super-soft',
      '💧 Breathable',
      '🪶 Featherlite'
    ],
    image: bannerImg('doctor1.png')
  },
  {
    title: 'Premium Scrubs Built for Long Duty Hours',
    features: [
      '🧵 Durable',
      '🌬 Airflow fabric',
      '💪 Stretch fit'
    ],
    image: bannerImg('bg_img2.png')
  },
  {
    title: 'Where Comfort Meets Style Confidence Follows All Day',
    features: [
      '✨ Stylish',
      '🩺 Medical fit',
      '🪶 Lightweight'
    ],
    image: bannerImg('bg_img.png')
  }
]

const promoItems = [
  { logo: 'myntra.png', text: 'Myntra' },
  { text: 'Akasa Air', logo: 'akasa_air.png' },
  { text: 'Maruti Suzuki', logo: 'maruti_suguki.png' },
  { text: 'IndiGo', logo: 'indigo.png' },
  { text: 'MGM Healthcare', logo: 'mgm.png' },
  { text: 'RSS', logo: 'rss.png' },
  { text: 'Rucha', logo: 'rucha.png' },
  { text: 'Spicejet', logo: 'spicejet.png' },
  { text: 'Yashoda Hospital', logo: 'yashoda.png' }
]

const currentSlide = ref(0)
const isTransitioning = ref(true)

let interval = null

const nextSlide = () => {
  currentSlide.value += 1

  if (currentSlide.value === banners.length) {
    setTimeout(() => {
      isTransitioning.value = false
      currentSlide.value = 0

      setTimeout(() => {
        isTransitioning.value = true
      }, 50)
    }, 600)
  }
}

const setSort = (val) => {
  selectedSort.value = val
  showSort.value = false
  showSortSheet.value = false
}

const getApiBaseUrl = () => {
  return String(
    api.defaults.baseURL || 'http://127.0.0.1:8000'
  ).replace(/\/$/, '')
}

const normalizeImageUrl = (url) => {
  const cleanUrl = String(url || '').trim()

  if (!cleanUrl) {
    return '/no-image.png'
  }

  if (
    cleanUrl.startsWith('http://') ||
    cleanUrl.startsWith('https://')
  ) {
    return cleanUrl
  }

  if (cleanUrl.startsWith('/uploads/')) {
    return `${getApiBaseUrl()}${cleanUrl}`
  }

  if (cleanUrl.startsWith('uploads/')) {
    return `${getApiBaseUrl()}/${cleanUrl}`
  }

  if (cleanUrl.startsWith('/static/')) {
    return `${getApiBaseUrl()}${cleanUrl}`
  }

  if (cleanUrl.startsWith('static/')) {
    return `${getApiBaseUrl()}/${cleanUrl}`
  }

  if (cleanUrl.startsWith('/src/assets/')) {
    return cleanUrl
  }

  if (cleanUrl.startsWith('src/assets/')) {
    return '/' + cleanUrl
  }

  if (cleanUrl.startsWith('/')) {
    return cleanUrl
  }

  return `${getApiBaseUrl()}/uploads/products/${cleanUrl}`
}

const handleImageError = (event) => {
  if (
    event.target.src.includes('/no-image.png')
  ) return

  event.target.src = '/no-image.png'
}

const getProductType = (item) => {
  const category = String(
    item.category_name ||
    item.category ||
    ''
  ).toLowerCase()

  const gender = String(
    item.gender || ''
  ).toLowerCase()

  const name = String(
    item.name ||
    item.title ||
    ''
  ).toLowerCase()

  if (
    category.includes('apron') ||
    name.includes('apron')
  ) {
    return 'aprons'
  }

  if (
    gender === 'women' ||
    gender === 'female'
  ) {
    return 'women'
  }

  return 'men'
}

const buildProductImages = (item) => {
  const images = []

  if (item.image_url) {
    images.push(
      normalizeImageUrl(item.image_url)
    )
  }

  if (item.image) {
    images.push(
      normalizeImageUrl(item.image)
    )
  }

  if (Array.isArray(item.images)) {
    item.images.forEach((img) => {
      if (typeof img === 'string') {
        images.push(
          normalizeImageUrl(img)
        )
      } else if (img?.image_url) {
        images.push(
          normalizeImageUrl(img.image_url)
        )
      } else if (img?.image) {
        images.push(
          normalizeImageUrl(img.image)
        )
      }
    })
  }

  if (Array.isArray(item.variants)) {
    item.variants.forEach((v) => {
      if (v?.image_url) {
        images.push(
          normalizeImageUrl(v.image_url)
        )
      }

      if (v?.image) {
        images.push(
          normalizeImageUrl(v.image)
        )
      }
    })
  }

  const uniqueImages = [
    ...new Set(images.filter(Boolean))
  ]

  return uniqueImages.length
    ? uniqueImages
    : ['/no-image.png']
}

const mapBackendProduct = (item) => {
  const productImages =
    buildProductImages(item)

  return {
    id: Number(
      item.product_id || item.id
    ),

    product_id: Number(
      item.product_id || item.id
    ),

    db_product_id: Number(
      item.db_product_id ||
      item.product_id ||
      item.id
    ),

    variant_id: Number(
      item.variant_id ||
      item.default_variant_id ||
      item.variants?.[0]?.variant_id ||
      item.variants?.[0]?.id ||
      0
    ),

    default_variant_id: Number(
      item.default_variant_id ||
      item.variant_id ||
      item.variants?.[0]?.variant_id ||
      item.variants?.[0]?.id ||
      0
    ),

    type: getProductType(item),

    title:
      item.title ||
      item.name ||
      'Product',

    name:
      item.name ||
      item.title ||
      'Product',

    price: Number(
      item.price ||
      item.variants?.[0]?.price ||
      0
    ),

    category:
      item.category_name ||
      item.category ||
      'Scrubs',

    category_name:
      item.category_name ||
      item.category ||
      'Scrubs',

    gender:
      item.gender || 'unisex',

    fabric:
      item.fabric || 'Classic',

    color:
      item.color ||
      item.color_name ||
      item.variants?.[0]?.color ||
      '',

    color_name:
      item.color_name ||
      item.color ||
      item.variants?.[0]?.color_name ||
      '',

    color_id:
      item.color_id ||
      item.variants?.[0]?.color_id ||
      null,

    size:
      item.size ||
      item.variants?.[0]?.size ||
      '',

    sleeve:
      item.sleeve || '',

    images: productImages,

    image_url: productImages[0],

    image: productImages[0],

    rating:
      item.rating || 4.8,

    isBestSeller:
      item.is_bestseller ||
      item.isBestSeller ||
      false,

    sizes:
      item.sizes || [],

    colors:
      item.colors || [],

    variants:
      item.variants || []
  }
}

const loadHomeProducts = async () => {
  try {
    loadingProducts.value = true

    const res = await api.get('/products/')

    const data = Array.isArray(res.data)
      ? res.data
      : Array.isArray(
            res.data?.products
          )
        ? res.data.products
        : []

    homeProducts.value = data
      .map(mapBackendProduct)
      .filter(
        (product) =>
          product.id &&
          product.variant_id
      )

    console.log(
      'HOME PRODUCTS:',
      homeProducts.value
    )
  } catch (err) {
    console.error(
      'Home products fetch error:',
      err
    )

    homeProducts.value = []
  } finally {
    loadingProducts.value = false
  }
}

const filteredProducts = computed(() => {
  let products =
    homeProducts.value.filter(
      (product) => {
        const matchCategory =
          selectedCategories.value.length === 0 ||
          selectedCategories.value.includes(
            product.category
          )

        const matchFabric =
          selectedFabrics.value.length === 0 ||
          selectedFabrics.value.includes(
            product.fabric
          )

        const matchSleeve =
          selectedSleeves.value.length === 0 ||
          selectedSleeves.value.includes(
            product.sleeve
          )

        const matchColor =
          selectedColors.value.length === 0 ||
          selectedColors.value.includes(
            product.color
          )

        return (
          matchCategory &&
          matchFabric &&
          matchSleeve &&
          matchColor
        )
      }
    )

  if (selectedSort.value === 'low') {
    products = [...products].sort(
      (a, b) =>
        Number(a.price) -
        Number(b.price)
    )
  } else if (
    selectedSort.value === 'high'
  ) {
    products = [...products].sort(
      (a, b) =>
        Number(b.price) -
        Number(a.price)
    )
  } else if (
    selectedSort.value === 'bestseller'
  ) {
    products = products.filter(
      (product) =>
        product.isBestSeller
    )
  }

  return products
})

const scrollToProducts = async () => {
  await nextTick()

  if (productsSection.value) {
    const top =
      productsSection.value.getBoundingClientRect()
        .top +
      window.pageYOffset -
      100

    window.scrollTo({
      top,
      behavior: 'smooth'
    })
  }
}

const goToProduct = (product) => {
  if (product.type === 'men') {
    router.push(
      `/men-product/${product.id}`
    )
  } else if (
    product.type === 'women'
  ) {
    router.push(
      `/women-product/${product.id}`
    )
  } else if (
    product.type === 'aprons'
  ) {
    router.push(
      `/aprons-product/${product.id}`
    )
  }
}

const getUserId = () => {
  const user = JSON.parse(
    localStorage.getItem('user') || '{}'
  )

  return (
    user?.id ||
    localStorage.getItem('user_id')
  )
}

const getGuestUuid = () => {
  return localStorage.getItem(
    'guest_uuid'
  )
}

const getVariantId = (product) => {
  return Number(
    product.variant_id ||
    product.db_variant_id ||
    product.default_variant_id
  )
}

const isInWishlist = (product) => {
  const variantId =
    getVariantId(product)

  if (!variantId) return false

  return wishlistVariantIds.value.includes(
    variantId
  )
}

const loadWishlist = async () => {
  try {
    const userId = getUserId()

    const guestUuid =
      getGuestUuid()

    if (!userId && !guestUuid) {
      wishlistVariantIds.value = []
      return
    }

    const res = await api.get(
      '/wishlist/',
      {
        params: userId
          ? { user_id: userId }
          : {},

        headers: guestUuid
          ? {
              'guest-uuid':
                guestUuid
            }
          : {}
      }
    )

    const list = Array.isArray(
      res.data
    )
      ? res.data
      : res.data?.items ||
        res.data?.wishlist ||
        []

    wishlistVariantIds.value =
      list
        .map((item) =>
          Number(item.variant_id)
        )
        .filter(Boolean)

    console.log(
      'WISHLIST VARIANT IDS:',
      wishlistVariantIds.value
    )
  } catch (err) {
    console.error(
      'Wishlist load error:',
      err
    )
  }
}

const handleWishlist = async (
  product
) => {
  try {
    const userId = getUserId()

    const guestUuid =
      getGuestUuid()

    if (!userId && !guestUuid) {
      router.push('/login')
      return
    }

    const variantId =
      getVariantId(product)

    if (!variantId) {
      console.error(
        'variant_id missing for wishlist product:',
        product
      )
      return
    }

    const config = {
      params: userId
        ? { user_id: userId }
        : {},

      headers: guestUuid
        ? {
            'guest-uuid':
              guestUuid
          }
        : {}
    }

    if (isInWishlist(product)) {
      await api.delete(
        '/wishlist/remove',
        {
          ...config,

          data: {
            variant_id: variantId
          }
        }
      )

      wishlistVariantIds.value =
        wishlistVariantIds.value.filter(
          (id) =>
            id !== variantId
        )
    } else {
      await api.post(
        '/wishlist/add',
        {
          variant_id: variantId
        },
        config
      )

      if (
        !wishlistVariantIds.value.includes(
          variantId
        )
      ) {
        wishlistVariantIds.value.push(
          variantId
        )
      }
    }

    flyingHeartId.value =
      product.id +
      '-' +
      product.type

    setTimeout(() => {
      flyingHeartId.value = null
    }, 900)
  } catch (err) {
    console.error(
      'Wishlist add/remove error:',
      err
    )
  }
}

const getFabricDescription = (
  fabric
) => {
  if (fabric === 'Classic') {
    return 'Classic fit • Soft feel • Everyday comfort'
  }

  if (fabric === 'Ecoflex') {
    return 'Ecoflex stretch • Breathable • Premium movement'
  }

  if (fabric === 'Ecoflex Lite') {
    return 'Ecoflex Lite • Ultra light • Max comfort'
  }

  return 'Premium scrub fabric'
}

onMounted(() => {
  interval = setInterval(
    nextSlide,
    3000
  )

  loadHomeProducts()
  loadWishlist()
})

onBeforeUnmount(() => {
  clearInterval(interval)
})
</script>

<style scoped lang="scss">
@import 'src/css/home.scss';
</style>