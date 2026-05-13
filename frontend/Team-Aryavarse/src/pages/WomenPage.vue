<template>
  <div class="women-page">
    <div class="main-container">

      <!-- Filters sidebar -->
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

      <!-- Products -->
      <section class="products">
        <div class="top-bar">
          <span>{{ filteredProducts.length }} items</span>
          <div class="desktop-sort-only">
            <SortDropdown v-model="selectedSort" />
          </div>
        </div>

        <!-- GRID — ProductCard component 
        <div class="grid">
          <ProductCard
            v-for="product in filteredProducts"
            :key="product.id"
            :product="product"
            @go-to-product="goToWomenProduct"
          />
        </div>-->

                <!-- GRID -->
  <ProductPagination :products="filteredProducts">

    <template #default="{ paginatedProducts }">
      <div class="grid">
        <ProductCard
          v-for="product in paginatedProducts"
          :key="product.id"
          :product="product"
           :wishlistIds="wishlistIds"
  @wishlist-updated="updateWishlist"
          @go-to-product="goToWomenProduct"
        />
      </div>
    </template>

  </ProductPagination>

      </section>

    </div>

    <!-- Mobile bottom spacing -->
    <div class="mobile-bottom-spacer" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue'
import { api } from 'boot/axios'
import SortDropdown from 'src/components/SortDropdown.vue'
import FilterSidebar from 'src/components/FilterSidebar.vue'
import ProductCard from 'src/components/ProductCard.vue'
import ProductPagination from 'src/components/ProductPagination.vue'

const router = useRouter()

const selectedSort = ref('')
//const hoveredProduct = ref(null)
//const flyingHeartId = ref(null)
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

const allWomenProducts = ref([])

const colors = computed(() => {
  const map = new Map()

  allWomenProducts.value.forEach((product) => {
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
      p.gender || 'women'
    ).toLowerCase(),

    fabric: p.fabric || 'Classic',

    sleeve: p.sleeve || '',

    stock: Number(
      defaultVariant?.stock ||
      p.stock ||
      0
    ),

    type: 'women',

    rating: p.rating || 4.8,

    isBestSeller: Boolean(
      p.isBestSeller ||
      p.is_bestseller
    )
  }
}

const loadWomenProducts = async () => {
  try {
    loading.value = true

    const res = await api.get('/products/', {
      params: {
        gender: 'women'
      }
    })

    const rawProducts = Array.isArray(res.data)
      ? res.data
      : res.data?.products ||
        res.data?.data ||
        res.data?.items ||
        []

    console.log(
      'RAW WOMEN PRODUCTS:',
      rawProducts
    )

    allWomenProducts.value = rawProducts
      .map(normalizeProduct)
      .filter(
        (p) =>
          p.product_id &&
          p.variant_id
      )

    console.log(
      'WOMEN PRODUCTS FINAL:',
      allWomenProducts.value
    )
  } catch (err) {
    console.error(
      'WOMEN PRODUCTS LOAD ERROR:',
      err.response?.data || err
    )

    allWomenProducts.value = []
  } finally {
    loading.value = false
  }
}

const updateWishlist = ({
  type,
  variantId
}) => {

  if (type === 'add') {

    if (
      !wishlistIds.value.includes(
        variantId
      )
    ) {
      wishlistIds.value.push(
        variantId
      )
    }

  } else {

    wishlistIds.value =
      wishlistIds.value.filter(
        (id) => id !== variantId
      )
  }
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


const goToWomenProduct = (product) => {
  const productId =
    product.product_id ||
    product.db_product_id ||
    product.id

  router.push(`/women-product/${productId}`)
}

const filteredProducts = computed(() => {
  let products = [...allWomenProducts.value]

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
  await loadWomenProducts()
  await loadWishlistIds()
})
</script>
<style scoped lang="scss">
@import 'src/css/women.scss';

/* Mobile bottom padding so grid isn't hidden behind sticky bar */
.mobile-bottom-spacer {
  display: none;
}

@media (max-width: 1000px) {
  .mobile-bottom-spacer {
    display: block;
    height: 72px;
  }

  /* Hide desktop SortDropdown in top-bar on mobile (shown in bottom bar instead) */
  .top-bar .q-select,
  .top-bar > :last-child {
    display: none;
  }
}
</style>