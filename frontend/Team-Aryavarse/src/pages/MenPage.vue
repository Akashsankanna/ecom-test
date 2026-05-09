<template>
  <div class="men-page">
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
      >
        <template #sort-btn>
          <SortDropdown v-model="selectedSort" />
        </template>
      </FilterSidebar>

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

              <!-- ❤️ FIXED -->
              <div class="card-icons" @click.stop="handleWishlist(product)">
                <q-icon
                  :name="isProductInWishlist(product) ? 'favorite' : 'favorite_border'"
                  size="22px"
                  :class="{ 'active-heart': isProductInWishlist(product) }"
                />
              </div>

              <div class="hover-actions" v-if="hoveredProduct === product.id">
                <button class="quick-btn" @click="goToMenProduct(product)">
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
    </div>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue'
import { api } from 'boot/axios'
import SortDropdown from 'src/components/SortDropdown.vue'
import FilterSidebar from 'src/components/FilterSidebar.vue'

const router = useRouter()

const selectedSort = ref('')
const hoveredProduct = ref(null)
const flyingHeartId = ref(null)
const loading = ref(false)

const wishlistIds = ref([])

const selectedCategories = ref([])
const selectedFabrics = ref([])
const selectedColors = ref([])
const selectedSleeves = ref([])

const filterCategories = ['Scrubs', 'Aprons']

const fabrics = [
  'Classic',
  'Ecoflex Lite',
  'Ecoflex'
]

const sleeves = [
  'Full Sleeve Aprons',
  '3-4 Sleeve Aprons',
  'Half Sleeve Aprons'
]

const allMenProducts = ref([])

const colors = computed(() => {
  const map = new Map()

  allMenProducts.value.forEach((product) => {
    ;(product.colors || []).forEach((color) => {
      if (color.color_id) {
        map.set(
          color.color_id,
          color.color_name || color.color
        )
      }
    })
  })

  return [...map.values()]
})

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
    return localStorage.getItem('user_id') || null
  }
}

const normalizeProduct = (p) => {
  const productId = Number(
    p.product_id ||
    p.db_product_id ||
    p.id
  )

  const variants = Array.isArray(p.variants)
    ? p.variants.map((v) => ({
        id: Number(v.id || v.variant_id),

        variant_id: Number(
          v.variant_id || v.id
        ),

        product_id: Number(
          v.product_id || productId
        ),

        size: v.size || '',

        color_id: v.color_id
          ? Number(v.color_id)
          : null,

        color: v.color || v.color_name || '',

        color_name:
          v.color_name || v.color || '',

        hex_code: v.hex_code || '',

        price: Number(v.price || 0),

        stock: Number(v.stock || 0),

        image:
          v.image ||
          v.image_url ||
          p.image ||
          p.image_url ||
          '/favicon.ico',

        image_url:
          v.image_url ||
          v.image ||
          p.image_url ||
          p.image ||
          '/favicon.ico'
      }))
    : []

  const defaultVariant =
    variants.find((v) => v.stock > 0) ||
    variants[0] ||
    null

  const image =
    defaultVariant?.image_url ||
    p.image_url ||
    p.image ||
    '/favicon.ico'

  const productColors = Array.isArray(p.colors)
    ? p.colors.map((c) => ({
        color_id: c.color_id
          ? Number(c.color_id)
          : null,

        color: c.color || c.color_name || '',

        color_name:
          c.color_name || c.color || '',

        hex_code: c.hex_code || ''
      }))
    : [
        ...new Map(
          variants
            .filter((v) => v.color_id)
            .map((v) => [
              v.color_id,
              {
                color_id: v.color_id,
                color: v.color,
                color_name: v.color_name,
                hex_code: v.hex_code
              }
            ])
        ).values()
      ]

  const productSizes = Array.isArray(p.sizes)
    ? p.sizes
    : [
        ...new Set(
          variants
            .map((v) => v.size)
            .filter(Boolean)
        )
      ]

  return {
    id: productId,

    product_id: productId,

    db_product_id: productId,

    variant_id:
      defaultVariant?.variant_id ||
      Number(
        p.variant_id ||
        p.default_variant_id ||
        0
      ),

    default_variant_id:
      defaultVariant?.variant_id ||
      Number(
        p.default_variant_id ||
        p.variant_id ||
        0
      ),

    color_id:
      defaultVariant?.color_id ||
      p.color_id ||
      null,

    color:
      defaultVariant?.color ||
      p.color ||
      p.color_name ||
      '',

    color_name:
      defaultVariant?.color_name ||
      p.color_name ||
      p.color ||
      '',

    hex_code:
      defaultVariant?.hex_code ||
      p.hex_code ||
      '',

    size:
      defaultVariant?.size ||
      p.size ||
      '',

    sizes: productSizes,

    colors: productColors,

    variants,

    title: p.name || p.title || 'Product',

    name: p.name || p.title || 'Product',

    description: p.description || '',

    price: Number(
      defaultVariant?.price ||
      p.price ||
      0
    ),

    image,

    image_url: image,

    images: [
      image,

      p.images?.[1]?.image_url ||
      p.images?.[1]?.image ||
      p.second_image ||
      p.hover_image ||
      image
    ],

    category:
      p.category_name ||
      p.category ||
      'Scrubs',

    category_name:
      p.category_name ||
      p.category ||
      'Scrubs',

    gender: String(
      p.gender || 'men'
    ).toLowerCase(),

    fabric: p.fabric || 'Classic',

    sleeve: p.sleeve || '',

    stock: Number(
      defaultVariant?.stock ||
      p.stock ||
      0
    ),

    type: 'men',

    rating: p.rating || 4.8,

    isBestSeller: Boolean(
      p.isBestSeller ||
      p.is_bestseller
    )
  }
}

const loadMenProducts = async () => {
  try {
    loading.value = true

    const res = await api.get('/products/', {
      params: {
        gender: 'men'
      }
    })

    const rawProducts = Array.isArray(res.data)
      ? res.data
      : res.data?.products ||
        res.data?.data ||
        res.data?.items ||
        []

    console.log(
      'RAW MEN PRODUCTS:',
      rawProducts
    )

    allMenProducts.value = rawProducts
      .map(normalizeProduct)
      .filter(
        (p) =>
          p.product_id &&
          p.variant_id &&
          p.gender === 'men'
      )

    console.log(
      'MEN PRODUCTS FINAL:',
      allMenProducts.value
    )
  } catch (err) {
    console.error(
      'MEN PRODUCTS LOAD ERROR:',
      err.response?.data || err
    )

    allMenProducts.value = []
  } finally {
    loading.value = false
  }
}

const isProductInWishlist = (product) => {
  return wishlistIds.value.includes(
    Number(product.variant_id)
  )
}

const loadWishlistIds = async () => {
  try {
    const userId = getUserId()

    if (!userId) {
      wishlistIds.value = []
      return
    }

    const res = await api.get('/wishlist/', {
      params: {
        user_id: userId
      }
    })

    wishlistIds.value = Array.isArray(res.data)
      ? res.data
          .map((item) =>
            Number(item.variant_id)
          )
          .filter(Boolean)
      : []

    console.log(
      'WISHLIST IDS:',
      wishlistIds.value
    )
  } catch (err) {
    console.error(
      'LOAD WISHLIST ERROR:',
      err.response?.data || err
    )
  }
}

const handleWishlist = async (product) => {
  try {
    const userId = getUserId()

    if (!userId) {
      router.push('/login')
      return
    }

    const variantId = Number(
      product.variant_id
    )

    if (
      !variantId ||
      Number.isNaN(variantId)
    ) {
      console.error(
        'VARIANT ID MISSING:',
        product
      )
      return
    }

    if (isProductInWishlist(product)) {
      await api.delete('/wishlist/remove', {
        params: {
          user_id: userId
        },

        data: {
          variant_id: variantId
        }
      })

      wishlistIds.value =
        wishlistIds.value.filter(
          (id) => id !== variantId
        )
    } else {
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

      if (
        !wishlistIds.value.includes(
          variantId
        )
      ) {
        wishlistIds.value.push(
          variantId
        )
      }
    }

    flyingHeartId.value = product.id

    setTimeout(() => {
      flyingHeartId.value = null
    }, 900)
  } catch (err) {
    console.error(
      'WISHLIST ERROR:',
      err.response?.data || err
    )
  }
}

const goToMenProduct = (product) => {
  const productId =
    product.product_id ||
    product.db_product_id ||
    product.id

  router.push(`/men-product/${productId}`)
}

const getFabricDescription = (fabric) => {
  if (fabric === 'Classic') {
    return 'Classic fit • Soft feel • Everyday comfort'
  }

  if (fabric === 'Ecoflex') {
    return 'Ecoflex stretch • Breathable • Premium movement'
  }

  if (fabric === 'Ecoflex Lite') {
    return 'Lightweight • Flexible • Comfortable'
  }

  return 'Premium scrub fabric'
}

const filteredProducts = computed(() => {
  let products = [...allMenProducts.value]

  products = products.filter((product) => {
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
      product.variants.some(
        (v) =>
          selectedColors.value.includes(
            v.color
          ) ||
          selectedColors.value.includes(
            v.color_name
          )
      )

    return (
      matchCategory &&
      matchFabric &&
      matchSleeve &&
      matchColor
    )
  })

  if (selectedSort.value === 'low') {
    products.sort((a, b) => a.price - b.price)
  } else if (
    selectedSort.value === 'high'
  ) {
    products.sort((a, b) => b.price - a.price)
  } else if (
    selectedSort.value === 'bestseller'
  ) {
    products = products.filter(
      (product) => product.isBestSeller
    )
  }

  return products
})

onMounted(async () => {
  await loadMenProducts()
  await loadWishlistIds()
})
</script>
<style scoped lang="scss">
@import 'src/css/men.scss';
</style>