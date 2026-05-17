<template>
  <div v-if="product" class="women-product-page">
    <div class="product-page">

    <!-- LEFT: thumbs + main image -->
    <div class="left-wrap">
      <div class="left">
        <div class="thumbs">
          <img
            v-for="img in displayImages"
            :key="img"
            :src="img"
            :class="{ active: selectedImage === img }"
            @click="selectedImage = img"
          />
        </div>

        <div class="main-image-box" @click="openImageDialog">
          <img :src="selectedImage" class="main-image" />
        </div>
      </div>
    </div>

      <!------------right--------------->
      <div class="right">
      <p class="tag">{{ productTag }}</p>
        <!---<p class="tag">Premium Women Collection</p>--->
       <h1>{{ product.title || product.name || 'Product' }}</h1>

        <div
  class="rating-row"
  @click="scrollToReviews"
  style="cursor:pointer;"
>
  <span class="stars">{{ ratingStars }}</span>
  <span class="rating">{{ displayRating }}</span>
</div>

        <div class="price-row">
          <h2>
            ₹ {{ Number(currentPrice).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
          </h2>

          <span v-if="oldPrice" class="old-price">
            ₹ {{ Number(oldPrice).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
          </span>

          <span v-if="oldPrice && discountPercent > 0" class="discount">
            {{ discountPercent }}% OFF
          </span>
        </div>

                  <!-- COLOUR -->
        <div class="variant-section" v-if="colorOptions.length">
          <p class="variant-label">Colour: <strong>{{ selectedColor || 'Select Colour' }}</strong></p>
          <div class="color-swatches">
            <button
              v-for="c in colorOptions"
              :key="c.name"
              class="color-dot"
              :class="{ active: selectedColor === c.name }"
              :style="{ background: c.hex || c.color_code || '#ccc' }"
              :title="c.name"
              @click="changeColor(c.name)"
            ></button>
          </div>
        </div>

        <!-- SIZE SECTION -->
        <div class="variant-section" v-if="sizes.length">
          <div class="section-head">
            <p class="variant-label">
              Size: <strong>{{ selectedSize || 'Select Size' }}</strong>
            </p>
            <button class="size-chart-link" @click="sizeChartDialog = true">
              Size Chart
            </button>
          </div>

                    <div class="size-options">
                      <button
                        v-for="s in sizes" :key="s"
                        class="size-btn"
                        :class="{ active: selectedSize === s }"
                        @click="selectedSize = s; sizeError = false;"
                      >
                      {{ s }}
                      </button>
                    </div>

                    <p v-if="sizeError" class="size-error">
                      Please select size
                    </p>
                  </div>

      <ProductCustomization
        @customization-updated="onCustomizationUpdated"
      />

        <!-- BUTTONS -->
        <div class="btns">

          <!-- QTY BOX -->
          <div class="detail-qty-box">
            <button class="detail-qty-btn" @click="decreaseQty">−</button>
            <span class="detail-qty-value">{{ quantity }}</span>
            <button class="detail-qty-btn" @click="increaseQty">+</button>
          </div>

          <button class="cart-btn" ref="cartBtnRef" @click="handleAddToCart">
            Add to Cart
          </button>

          <button class="buy-btn" @click="handleBuyNow">
            Buy Now
          </button>

        </div>

        <!-- ✅ FLYING IMAGE ELEMENT -->
        <img
          v-if="flyingVisible"
          :src="selectedImage"
          class="flying-img"
          :class="{ flying: flyingActive }"
          :style="flyingStyle"
          ref="flyingImgRef"
        />

                <!-- Delivery features (Knya style)
                      <div class="delivery-cols">

                        <div class="delivery-col">
                            <i class="bi bi-truck-flatbed"></i>
                            <p class="delivery-title">1–3 Day<br />Express Shipping</p>
                         </div>

                          <div class="delivery-col">
                            <i class="bi bi-box-seam"></i>
                              <p class="delivery-title">Easy Exchange<br />& Returns</p>
                          </div>

                            <div class="delivery-col">
                              <i class="bi bi-truck"></i>
                                <p class="delivery-title">Cash on Delivery<br />Available</p>
                            </div>
                      </div>--->
        <!-- Delivery features -->
        <div class="delivery-cols">
          <div
            class="delivery-col"
            v-for="(item, index) in deliveryFeatures"
            :key="index"
          >
            <i :class="item.icon"></i>
            <p class="delivery-title">{{ item.title }}</p>
          </div>
        </div>

            <!--pin code section---->
              <div class="section delivery-details">
                <h3>Delivery Details</h3>

            <div class="pincode-checker">
            <div class="input-btn-group">
              <q-input
                v-model="pincode"
                type="text"
                maxlength="6"
                dense
                class="pincode-input"
                placeholder="Enter 6-digit pincode"
                :hide-bottom-space="true"
                @keyup.enter="checkPincode"
                @input="onPincodeInput"
              />
              <q-btn
                class="check-btn"
                :loading="isChecking"
                :disable="isChecking || pincode.length !== 6"
                label="Check"
                @click="checkPincode"
              />
            </div>

            <div v-if="pincode.length > 0 && pincode.length < 6" class="error-msg">
              Pincode must be 6 digits
            </div>

            <div v-if="pincodeError" class="error-msg">
              {{ pincodeError }}
            </div>

            <div v-if="deliveryStatus" class="delivery-messages">
              <div class="delivery-date">
                <i class="bi bi-truck"></i>
                {{ deliveryStatus.deliveryDate }}
              </div>

              <div class="delivery-cod" v-if="deliveryStatus.cod">
                <i class="bi bi-cash-stack"></i>
                {{ deliveryStatus.cod }}
              </div>
            </div>
          </div>
        </div>

<!----details---->
<div class="product-info-right">

  <!-- Details & Fit -->
  <div class="section accordion">
    <div class="accordion-header" @click="activeAccordion = activeAccordion === 0 ? null : 0">
      <span>Details & Fit</span>
      <q-icon :name="activeAccordion === 0 ? 'remove' : 'add'" />
    </div>

    <div v-show="activeAccordion === 0" class="accordion-content">
      <p>{{ product.description }}</p>

      <ul>
        <li v-for="(detail,index) in product.details" :key="index">
          {{ detail }}
        </li>
      </ul>
    </div>
  </div>

  <!-- Fabric & Care -->
  <div class="section accordion">
    <div class="accordion-header" @click="activeAccordion = activeAccordion === 1 ? null : 1">
      <span>Fabric & Care</span>
      <q-icon :name="activeAccordion === 1 ? 'remove' : 'add'" />
    </div>

    <div v-show="activeAccordion === 1" class="accordion-content">
      <p>{{ product.fabricDescription }}</p>

      <ul>
        <li v-for="(care,index) in product.fabricCare" :key="index">
          {{ care }}
        </li>
      </ul>
    </div>
  </div>

  <!-- Return & Exchange -->
  <div class="section accordion">
    <div class="accordion-header" @click="activeAccordion = activeAccordion === 2 ? null : 2">
      <span>Return & Exchange</span>
      <q-icon :name="activeAccordion === 2 ? 'remove' : 'add'" />
    </div>

    <div v-show="activeAccordion === 2" class="accordion-content">
      <p>{{ product.returnDescription }}</p>

      <ul>
        <li v-for="(point,index) in product.returnPoints" :key="index">
          {{ point }}
        </li>
      </ul>
    </div>
  </div>

</div>

      </div>
    </div>

      <!-- IMAGE DIALOG -->
      <div v-if="imageDialog" class="image-popup" @click.self="imageDialog = false">
        <button class="full-close-btn" @click="imageDialog = false">✕</button>
        <img :src="selectedImage" class="popup-image" />
      </div>

<!-- SIZE CHART POPUP -->
    <q-dialog v-model="sizeChartDialog">
      <div class="size-chart-popup">
        <div class="size-chart-header">
          <h3>Size Chart</h3>
          <button class="size-chart-close" @click="sizeChartDialog = false">✕</button>
        </div>

        <div class="size-chart-tabs">
          <button
            class="tab"
            :class="{ active: activeTab === 'size' }"
            @click="activeTab = 'size'"
          >
            Size
          </button>

          <button
            class="tab"
            :class="{ active: activeTab === 'measure' }"
            @click="activeTab = 'measure'"
          >
            How to Measure
          </button>
        </div>

        <div class="size-chart-content">
          <img
            v-if="activeTab === 'size'"
            :src="sizeChartImg"
            class="size-chart-img"
          />

          <img
            v-else
            :src="measureImg"
            class="size-chart-img"
          />
        </div>
      </div>
    </q-dialog>
 <!-- REVIEWS SECTION -->
    <div class="reviews-section-wrapper">

      <ProductReviews
        ref="reviewsRef"
        :reviews="product?.reviews || []"
        :productId="product?.id"
        @updateReviews="addReview"
      />

    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from 'boot/axios'
import { addToCart } from 'src/stores/shop'
import sizeChartImg from 'src/assets/size_chart/size-chart.png'
import measureImg from 'src/assets/size_chart/measure.png'
import ProductCustomization from 'components/Productcustomization.vue'
import ProductReviews from 'components/ProductReviews.vue'

const route = useRoute()
const router = useRouter()

const product = ref(null)
const loading = ref(false)

const selectedImage = ref('')
const displayImages = ref([])
const imageDialog = ref(false)

const selectedColorId = ref(null)
const selectedColor = ref('')
const selectedSize = ref('')
const sizeError = ref(false)

const quantity = ref(1)
const customizationData = ref(null)
const activeAccordion = ref(null)

const sizeChartDialog = ref(false)
const activeTab = ref('size')

const pincode = ref('')
const deliveryStatus = ref(null)
const pincodeError = ref('')
const isChecking = ref(false)

const cartBtnRef = ref(null)
const flyingImgRef = ref(null)
const flyingVisible = ref(false)
const flyingActive = ref(false)
const flyingStyle = ref({})

// REVIEW SECTION
const reviewsRef = ref(null)

const scrollToReviews = () => {
  const el = reviewsRef.value?.$el

  if (!el) return

  el.scrollIntoView({
    behavior: 'smooth'
  })

  el.classList.add('highlight')

  setTimeout(() => {
    el.classList.remove('highlight')
  }, 1000)
}

const addReview = (newReview) => {
  if (!product.value.reviews) {
    product.value.reviews = []
  }

  product.value.reviews.push(newReview)
}

const normalizeProduct = (p) => {
  const productId = Number(p.product_id || p.db_product_id || p.id)

  const variants = Array.isArray(p.variants)
    ? p.variants.map((v) => ({
        id: Number(v.id || v.variant_id),
        variant_id: Number(v.variant_id || v.id),
        product_id: Number(v.product_id || productId),

        size: v.size || '',
        color_id: v.color_id ? Number(v.color_id) : null,
        color: v.color || v.color_name || '',
        color_name: v.color_name || v.color || '',
        hex_code: v.hex_code || '',

        price: Number(v.price || 0),
        stock: Number(v.stock || 0),

        image: v.image || v.image_url || p.image || p.image_url || '/favicon.ico',
        image_url: v.image_url || v.image || p.image_url || p.image || '/favicon.ico'
      }))
    : []

  const images = Array.isArray(p.images)
    ? p.images
        .map((img) => img.image_url || img.image)
        .filter(Boolean)
    : []

  const colors = Array.isArray(p.colors)
    ? p.colors.map((c) => ({
        color_id: c.color_id ? Number(c.color_id) : null,
        name: c.color_name || c.color || '',
        color: c.color || c.color_name || '',
        color_name: c.color_name || c.color || '',
        hex: c.hex_code || '#cccccc',
        hex_code: c.hex_code || '#cccccc'
      }))
    : [
        ...new Map(
          variants
            .filter((v) => v.color_id)
            .map((v) => [
              v.color_id,
              {
                color_id: v.color_id,
                name: v.color_name || v.color,
                color: v.color,
                color_name: v.color_name,
                hex: v.hex_code || '#cccccc',
                hex_code: v.hex_code || '#cccccc'
              }
            ])
        ).values()
      ]

  const sizes = Array.isArray(p.sizes)
    ? p.sizes
    : [...new Set(variants.map((v) => v.size).filter(Boolean))]

  const defaultVariant =
    variants.find((v) => v.stock > 0) ||
    variants[0] ||
    null

  const image =
    defaultVariant?.image_url ||
    images[0] ||
    p.image_url ||
    p.image ||
    '/favicon.ico'

  return {
    id: productId,
    product_id: productId,
    db_product_id: productId,

    title: p.title || p.name || 'Product',
    name: p.name || p.title || 'Product',
    description: p.description || '',

    gender: String(p.gender || 'women').toLowerCase(),
    category: p.category_name || p.category || 'Scrubs',
    category_name: p.category_name || p.category || 'Scrubs',

    fabric: p.fabric || 'Classic',
    rating: p.rating || 4.8,

    price: Number(defaultVariant?.price || p.price || 0),
    oldPrice: p.oldPrice || p.old_price || null,

    variant_id: defaultVariant?.variant_id || Number(p.variant_id || p.default_variant_id || 0),
    color_id: defaultVariant?.color_id || p.color_id || null,
    color: defaultVariant?.color || p.color || p.color_name || '',
    color_name: defaultVariant?.color_name || p.color_name || p.color || '',
    size: defaultVariant?.size || p.size || '',

    stock: Number(defaultVariant?.stock || p.stock || 0),

    image,
    image_url: image,
    images: images.length ? images : [image],

    colors,
    sizes,
    variants,
  reviews: p.reviews || [],
    details_and_fit: p.details_and_fit || '',
    fabric_and_care: p.fabric_and_care || '',
    return_and_exchange: p.return_and_exchange || '',

    details: p.details_and_fit
      ? String(p.details_and_fit).split('\n').filter(Boolean)
      : [],

    fabricDescription: p.fabric_and_care || 'Premium comfortable fabric.',
    fabricCare: p.fabric_and_care
      ? String(p.fabric_and_care).split('\n').filter(Boolean)
      : [],

    returnDescription: p.return_and_exchange || 'Easy return and exchange available.',
    returnPoints: p.return_and_exchange
      ? String(p.return_and_exchange).split('\n').filter(Boolean)
      : []
  }
}

const loadProductDetails = async () => {
  try {
    loading.value = true

    const productId = Number(route.params.id)

    const res = await api.get(`/products/${productId}`)

    console.log('RAW WOMEN PRODUCT DETAILS:', res.data)

    product.value = normalizeProduct(res.data)

    if (product.value.images?.length) {
      displayImages.value = [...product.value.images]
      selectedImage.value = product.value.images[0]
    }

    if (product.value.colors?.length) {
      selectedColorId.value = product.value.colors[0].color_id
      selectedColor.value = product.value.colors[0].name
    }

    if (product.value.sizes?.length) {
      selectedSize.value = product.value.sizes[0]
    }

    updateSelectedVariant()
  } catch (err) {
    console.error('WOMEN PRODUCT DETAILS LOAD ERROR:', err.response?.data || err)
    product.value = null
  } finally {
    loading.value = false
  }
}

const colorOptions = computed(() => {
  return product.value?.colors || []
})

const sizes = computed(() => {
  if (!product.value?.variants?.length) return []

  if (!selectedColorId.value) {
    return product.value.sizes || []
  }

  return [
    ...new Set(
      product.value.variants
        .filter((v) => Number(v.color_id) === Number(selectedColorId.value))
        .map((v) => v.size)
        .filter(Boolean)
    )
  ]
})

const selectedVariant = computed(() => {
  if (!product.value?.variants?.length) return null

  return product.value.variants.find((v) =>
    Number(v.color_id) === Number(selectedColorId.value) &&
    String(v.size).toLowerCase() === String(selectedSize.value).toLowerCase()
  ) || null
})

const updateSelectedVariant = () => {
  const variant = selectedVariant.value
  if (!variant || !product.value) return

  product.value.variant_id = variant.variant_id
  product.value.color_id = variant.color_id
  product.value.color = variant.color
  product.value.color_name = variant.color_name
  product.value.size = variant.size
  product.value.price = variant.price
  product.value.stock = variant.stock

  if (variant.image_url) {
    selectedImage.value = variant.image_url
  }
}

watch(selectedSize, () => {
  sizeError.value = false
  updateSelectedVariant()
})

watch(selectedColorId, () => {
  const availableSizes = sizes.value

  if (availableSizes.length && !availableSizes.includes(selectedSize.value)) {
    selectedSize.value = availableSizes[0]
  }

  const colorImages = product.value?.variants
    ?.filter((v) => Number(v.color_id) === Number(selectedColorId.value))
    ?.map((v) => v.image_url)
    ?.filter(Boolean)

  if (colorImages?.length) {
    displayImages.value = [...new Set(colorImages)]
    selectedImage.value = displayImages.value[0]
  }

  updateSelectedVariant()
})

const changeColor = (colorName) => {
  const colorObj = colorOptions.value.find(
    (c) => String(c.name || c.color_name || c.color).toLowerCase().trim() ===
      String(colorName).toLowerCase().trim()
  )

  if (!colorObj) return

  selectedColorId.value = colorObj.color_id
  selectedColor.value = colorObj.name || colorObj.color_name || colorObj.color
}
const displayRating = computed(() => {
  return Number(
    product.value?.rating ||
    product.value?.avg_rating ||
    4.8
  ).toFixed(1)
})

const ratingStars = computed(() => {
  const rating = Math.round(
    Number(
      product.value?.rating ||
      product.value?.avg_rating ||
      4.8
    )
  )

  return '★'.repeat(
    Math.max(0, Math.min(5, rating))
  ) +
  '☆'.repeat(
    Math.max(0, 5 - rating)
  )
})
const discountPercent = computed(() => {
  const p = product.value
  if (!p?.oldPrice || !p?.price) return 0
  return Math.round(((p.oldPrice - p.price) / p.oldPrice) * 100)
})

//me added
const productTag = computed(() => {
  return product.value?.tag ||
    product.value?.category_name ||
    product.value?.collection_name ||
    'Premium Collection'
})

const deliveryFeatures = computed(() => {
  return product.value?.delivery_features?.length
    ? product.value.delivery_features
    : [
        { icon: 'bi bi-truck-flatbed', title: '1–3 Day<br />Express Shipping' },
        { icon: 'bi bi-box-seam', title: 'Easy Exchange<br />& Returns' },
        { icon: 'bi bi-truck', title: 'Cash on Delivery<br />Available' }
      ]
})

const onCustomizationUpdated = (payload) => {
  customizationData.value = payload
  console.log('Customization:', payload)
}

const openImageDialog = () => {
  imageDialog.value = true
}

const prevImage = () => {
  const imgs = displayImages.value || []
  if (!imgs.length) return

  selectedImage.value =
    imgs[(imgs.indexOf(selectedImage.value) - 1 + imgs.length) % imgs.length]
}

const nextImage = () => {
  const imgs = displayImages.value || []
  if (!imgs.length) return

  selectedImage.value =
    imgs[(imgs.indexOf(selectedImage.value) + 1) % imgs.length]
}

const increaseQty = () => {
  quantity.value++
}

const decreaseQty = () => {
  if (quantity.value > 1) quantity.value--
}

const onPincodeInput = () => {
  if (pincode.value.length > 6) {
    pincode.value = pincode.value.slice(0, 6)
  }

  deliveryStatus.value = null
  pincodeError.value = ''
}

const solapurPincodes = [
  '413001', '413002', '413003', '413004', '413005',
  '413006', '413007', '413101', '413109', '413112',
  '413203', '413212', '413214', '413215', '413216',
  '413219', '413221', '413222', '413228', '413253',
  '413301', '413303', '413304', '413305', '413306',
  '413307', '413309', '413310', '413311', '413314',
  '413401', '413402', '413403', '413406', '413409',
  '413410', '413411'
]

const checkPincode = () => {
  const pin = String(pincode.value).trim()

  if (pin.length !== 6) {
    pincodeError.value = 'Please enter a valid 6-digit pincode'
    return
  }

  deliveryStatus.value = null
  pincodeError.value = ''
  isChecking.value = true

  const today = new Date()
  const startDate = today.getDate() + 2
  const endDate = today.getDate() + 3

  setTimeout(() => {
    if (solapurPincodes.includes(pin)) {
      deliveryStatus.value = {
        deliveryDate: `Delivery between ${startDate}th and ${endDate}th`,
        cod: 'Cash on delivery available'
      }
    } else {
      pincodeError.value = 'Sorry, delivery not available for this pincode'
    }

    isChecking.value = false
  }, 1200)
}

const triggerFlyAnimation = async () => {
  if (!cartBtnRef.value) return

  const btnRect = cartBtnRef.value.getBoundingClientRect()
  const cartIcon = document.querySelector('#cartIcon')

  const targetRect = cartIcon
    ? cartIcon.getBoundingClientRect()
    : { left: window.innerWidth - 40, top: 20, width: 0, height: 0 }

  const startX = btnRect.left + btnRect.width / 2 - 25
  const startY = btnRect.top + btnRect.height / 2 - 25

  const targetX = targetRect.left + targetRect.width / 2 - 25
  const targetY = targetRect.top + targetRect.height / 2 - 25

  flyingStyle.value = {
    left: startX + 'px',
    top: startY + 'px',
    transform: 'scale(1)',
    opacity: '1',
    transition: 'none'
  }

  flyingVisible.value = true
  flyingActive.value = false

  await nextTick()

  setTimeout(() => {
    flyingStyle.value = {
      left: targetX + 'px',
      top: targetY + 'px',
      transform: 'scale(0.4)',
      opacity: '0',
      transition: 'all 1.2s cubic-bezier(0.22, 1, 0.36, 1)'
    }

    setTimeout(() => {
      flyingVisible.value = false
    }, 1200)
  }, 50)
}

const handleAddToCart = async () => {
  try {
    if (!product.value) return

    if (!selectedSize.value) {
      sizeError.value = true
      return
    }

    const variant = selectedVariant.value

    if (!variant?.variant_id) {
      console.error('VARIANT NOT FOUND:', {
        selectedColorId: selectedColorId.value,
        selectedColor: selectedColor.value,
        selectedSize: selectedSize.value,
        variants: product.value.variants
      })
      return
    }

    await addToCart(Number(variant.variant_id), quantity.value)
    await triggerFlyAnimation()
  } catch (error) {
    console.error('HANDLE ADD TO CART ERROR:', error)
  }
}

const handleBuyNow = async () => {
  if (!selectedSize.value) {
    sizeError.value = true
    return
  }

  await handleAddToCart()
  router.push('/cart')
}

onMounted(() => {
  loadProductDetails()
})
</script>

<style scoped lang="scss">
@import 'src/css/women-product-details.scss';
.reviews-section-wrapper {
  margin-top: 50px;
}

.highlight {
  animation: reviewHighlight 1s ease;
}

@keyframes reviewHighlight {

  0% {
    background: rgba(255, 192, 203, 0.25);
  }

  100% {
    background: transparent;
  }

}
</style>
