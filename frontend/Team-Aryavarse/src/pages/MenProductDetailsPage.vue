<template>
  <div v-if="product" class="men-product-page">
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

      <!-- RIGHT: details -->
      <div class="right">
        <p class="tag">{{ productTag }}</p>
        <h1>{{ product.title || product.name || 'Product' }}</h1>

        <div class="rating-row">
          <span class="stars">{{ ratingStars }}</span>
          <span class="rating-val">{{ displayRating }}</span>
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
              v-for="s in sizes"
              :key="s"
              class="size-btn"
              :class="{ active: selectedSize === s }"
              @click="selectedSize = s; sizeError = false"
            >
              {{ s }}
            </button>
          </div>

          <p v-if="sizeError" class="size-error">
            Please select size
          </p>
        </div>

        <!-- CUSTOMIZATION -->
        <ProductCustomization
          :product-id="product?.id"
          @customization-updated="onCustomizationUpdated"
        />

        <!-- BUTTONS -->
        <div class="btns">
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

        <!-- FLYING IMAGE -->
        <img
          v-if="flyingVisible"
          :src="selectedImage"
          class="flying-img"
          :class="{ flying: flyingActive }"
          :style="flyingStyle"
          ref="flyingImgRef"
        />

        <!-- Delivery features -->
        <div class="delivery-cols">
          <div
            class="delivery-col"
            v-for="(feature, index) in deliveryFeatures"
            :key="index"
          >
            <i :class="feature.icon"></i>
            <p class="delivery-title" v-html="feature.title"></p>
          </div>
        </div>

        <!-- PIN CODE SECTION -->
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
              <div class="delivery-date" v-if="deliveryStatus.deliveryDate">
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

        <!-- DETAILS ACCORDION -->
        <div class="product-info-right">
          <div
            v-for="(section, index) in accordionSections"
            :key="index"
            class="section accordion"
          >
            <div
              class="accordion-header"
              @click="activeAccordion = activeAccordion === index ? null : index"
            >
              <span>{{ section.title }}</span>
              <q-icon :name="activeAccordion === index ? 'remove' : 'add'" />
            </div>

            <div v-show="activeAccordion === index" class="accordion-content">
              <p v-if="section.description">{{ section.description }}</p>
              <ul v-if="section.points?.length">
                <li v-for="(item, idx) in section.points" :key="idx">{{ item }}</li>
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
          <button class="tab" :class="{ active: activeTab === 'size' }" @click="activeTab = 'size'">
            Size
          </button>
          <button class="tab" :class="{ active: activeTab === 'measure' }" @click="activeTab = 'measure'">
            How to Measure
          </button>
        </div>

        <div class="size-chart-content">
          <img v-if="activeTab === 'size'" :src="sizeChartImage" class="size-chart-img" />
          <img v-else :src="measureImage" class="size-chart-img" />
        </div>
      </div>
    </q-dialog>
  </div>

  <div v-else-if="loading" class="men-product-page">
    <div class="product-page">
      <div class="right">
        <h2>Loading product...</h2>
      </div>
    </div>
  </div>

  <div v-else class="men-product-page">
    <div class="product-page">
      <div class="right">
        <h2>Product not found</h2>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from 'boot/axios'
import { addToCart } from 'src/stores/shop'
import sizeChartFallback from 'src/assets/size_chart/size-chart.png'
import measureFallback from 'src/assets/size_chart/measure.png'
//import ProductCustomization from 'components/ProductCustomization.vue'

const route = useRoute()
const router = useRouter()

// ----------------------
// STATE
// ----------------------
const loading = ref(false)
const product = ref(null)

const selectedImage = ref('')
const displayImages = ref([])
const imageDialog = ref(false)

const selectedColor = ref('')
const selectedSize = ref('')
const sizeError = ref(false)

const quantity = ref(1)

const sizeChartDialog = ref(false)
const activeTab = ref('size')
const activeAccordion = ref(null)

const customizationData = ref(null)

const pincode = ref('')
const deliveryStatus = ref(null)
const pincodeError = ref('')
const isChecking = ref(false)

const cartBtnRef = ref(null)
const flyingImgRef = ref(null)
const flyingVisible = ref(false)
const flyingActive = ref(false)
const flyingStyle = ref({})

// ----------------------
// FETCH PRODUCT DYNAMICALLY
// ----------------------
const fetchProduct = async () => {
  try {
    loading.value = true
    const productId = Number(route.params.id)

    // change endpoint if your backend route is different
    const response = await api.get(`/products/${productId}`)
    product.value = response.data
  } catch (error) {
    console.error('PRODUCT FETCH ERROR:', error)
    product.value = null
  } finally {
    loading.value = false
  }
}

onMounted(fetchProduct)

watch(() => route.params.id, async () => {
  resetSelections()
  await fetchProduct()
})

// ----------------------
// HELPERS
// ----------------------
const resetSelections = () => {
  selectedImage.value = ''
  displayImages.value = []
  selectedColor.value = ''
  selectedSize.value = ''
  sizeError.value = false
  quantity.value = 1
  deliveryStatus.value = null
  pincodeError.value = ''
  pincode.value = ''
}

const onCustomizationUpdated = (payload) => {
  customizationData.value = payload
  console.log('Customization:', payload)
}

const openImageDialog = () => {
  imageDialog.value = true
}

// ----------------------
// DYNAMIC PRODUCT FIELD NORMALIZATION
// ----------------------
const normalizedImages = computed(() => {
  if (!product.value) return []

  if (Array.isArray(product.value.images) && product.value.images.length) {
    return product.value.images.map((img) => {
      if (typeof img === 'string') return img
      return img.image_url || img.url || img.src || ''
    }).filter(Boolean)
  }

  if (product.value.image_url) return [product.value.image_url]
  if (product.value.image) return [product.value.image]

  return []
})

const colorOptions = computed(() => {
  if (!product.value) return []

  if (Array.isArray(product.value.colors) && product.value.colors.length) {
    return product.value.colors
  }

  // fallback: build colors from variants if backend does not send colors separately
  if (Array.isArray(product.value.variants)) {
    const unique = new Map()

    product.value.variants.forEach((variant) => {
      const colorName =
        variant.color ||
        variant.color_name ||
        extractColorFromVariantName(variant.variant_name)

      if (colorName && !unique.has(colorName.toLowerCase())) {
        unique.set(colorName.toLowerCase(), {
          name: colorName,
          hex: variant.color_code || '#cccccc',
          variant_id: variant.variant_id || variant.id,
          images: variant.images || []
        })
      }
    })

    return Array.from(unique.values())
  }

  return []
})

const sizes = computed(() => {
  if (!product.value) return []

  if (Array.isArray(product.value.sizes) && product.value.sizes.length) {
    return product.value.sizes
  }

  if (Array.isArray(product.value.variants) && product.value.variants.length) {
    const extractedSizes = product.value.variants
      .map((variant) => variant.size || extractSizeFromVariantName(variant.variant_name))
      .filter(Boolean)

    return [...new Set(extractedSizes)]
  }

  return []
})

const currentPrice = computed(() => {
  if (!product.value) return 0
  return product.value.price || product.value.sale_price || product.value.final_price || 0
})

const oldPrice = computed(() => {
  if (!product.value) return null
  return product.value.oldPrice || product.value.old_price || product.value.mrp || product.value.original_price || null
})

const displayRating = computed(() => {
  if (!product.value) return '0.0'
  return Number(product.value.rating || product.value.avg_rating || 0).toFixed(1)
})

const ratingStars = computed(() => {
  const rating = Math.round(Number(product.value?.rating || product.value?.avg_rating || 0))
  return '★'.repeat(Math.max(0, Math.min(5, rating))) + '☆'.repeat(Math.max(0, 5 - Math.round(rating)))
})

const discountPercent = computed(() => {
  if (!oldPrice.value || !currentPrice.value) return 0
  return Math.round(((oldPrice.value - currentPrice.value) / oldPrice.value) * 100)
})

const productTag = computed(() => {
  return (
    product.value?.tag ||
    product.value?.category_name ||
    product.value?.collection_name ||
    'Premium Collection'
  )
})

const sizeChartImage = computed(() => {
  return product.value?.size_chart_image || sizeChartFallback
})

const measureImage = computed(() => {
  return product.value?.measure_image || measureFallback
})

const accordionSections = computed(() => {
  if (!product.value) return []

  if (Array.isArray(product.value.accordion_sections) && product.value.accordion_sections.length) {
    return product.value.accordion_sections
  }

  return [
    {
      title: 'Details & Fit',
      description: product.value.description || '',
      points: product.value.details || []
    },
    {
      title: 'Fabric & Care',
      description: product.value.fabricDescription || product.value.fabric_description || '',
      points: product.value.fabricCare || product.value.fabric_care || []
    },
    {
      title: 'Return & Exchange',
      description: product.value.returnDescription || product.value.return_description || '',
      points: product.value.returnPoints || product.value.return_points || []
    }
  ].filter(section => section.description || (section.points && section.points.length))
})

const deliveryFeatures = computed(() => {
  if (Array.isArray(product.value?.delivery_features) && product.value.delivery_features.length) {
    return product.value.delivery_features
  }

  return [
    { icon: 'bi bi-truck-flatbed', title: '1–3 Day<br />Express Shipping' },
    { icon: 'bi bi-box-seam', title: 'Easy Exchange<br />& Returns' },
    { icon: 'bi bi-truck', title: 'Cash on Delivery<br />Available' }
  ]
})

// ----------------------
// WATCH PRODUCT
// ----------------------
watch(product, (val) => {
  if (!val) return

  displayImages.value = [...normalizedImages.value]
  selectedImage.value = normalizedImages.value[0] || ''

  if (colorOptions.value.length) {
    selectedColor.value = colorOptions.value[0]?.name || ''
    const firstColorImages = colorOptions.value[0]?.images || []
    if (firstColorImages.length) {
      displayImages.value = [...firstColorImages]
      selectedImage.value = firstColorImages[0]
    }
  }

  if (sizes.value.length === 1) {
    selectedSize.value = sizes.value[0]
  }
}, { immediate: true })

// ----------------------
// COLOR CHANGE
// ----------------------
const changeColor = (colorName) => {
  selectedColor.value = colorName

  const colorObj = colorOptions.value.find(
    c => String(c.name || '').toLowerCase().trim() === String(colorName || '').toLowerCase().trim()
  )

  if (colorObj?.images?.length) {
    displayImages.value = [...colorObj.images]
    selectedImage.value = colorObj.images[0]
    return
  }

  if (normalizedImages.value.length) {
    displayImages.value = [...normalizedImages.value]
    selectedImage.value = normalizedImages.value[0]
  }
}

// ----------------------
// QTY
// ----------------------
const increaseQty = () => {
  quantity.value++
}

const decreaseQty = () => {
  if (quantity.value > 1) quantity.value--
}

// ----------------------
// PINCODE - NOW DYNAMIC BACKEND CHECK
// ----------------------
const onPincodeInput = () => {
  if (pincode.value.length > 6) {
    pincode.value = pincode.value.slice(0, 6)
  }

  deliveryStatus.value = null
  pincodeError.value = ''
}

const checkPincode = async () => {
  const pin = String(pincode.value).trim()

  if (pin.length !== 6) {
    pincodeError.value = 'Please enter a valid 6-digit pincode'
    return
  }

  deliveryStatus.value = null
  pincodeError.value = ''
  isChecking.value = true

  try {
    // change endpoint if your backend route is different
    const response = await api.get('/delivery/check-pincode', {
      params: {
        pincode: pin,
        product_id: product.value?.id
      }
    })

    const data = response.data || {}

    if (data.available) {
      deliveryStatus.value = {
        deliveryDate: data.deliveryDate || data.delivery_date || 'Delivery available',
        cod: data.cod ? 'Cash on delivery available' : ''
      }
    } else {
      pincodeError.value = data.message || 'Sorry, delivery not available for this pincode'
    }
  } catch (error) {
    console.error('PINCODE CHECK ERROR:', error)
    pincodeError.value = 'Unable to check delivery right now'
  } finally {
    isChecking.value = false
  }
}

// ----------------------
// FLYING CART ANIMATION
// ----------------------
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
    left: `${startX}px`,
    top: `${startY}px`,
    transform: 'scale(1)',
    opacity: '1',
    transition: 'none'
  }

  flyingVisible.value = true
  flyingActive.value = false

  await nextTick()

  setTimeout(() => {
    flyingStyle.value = {
      left: `${targetX}px`,
      top: `${targetY}px`,
      transform: 'scale(0.4)',
      opacity: '0',
      transition: 'all 1.2s cubic-bezier(0.22, 1, 0.36, 1)'
    }

    setTimeout(() => {
      flyingVisible.value = false
    }, 1200)
  }, 50)
}

// ----------------------
// KEEP SAME ADD TO CART LOGIC STYLE
// ----------------------
const handleAddToCart = async () => {
  try {
    if (!product.value) return

    if (sizes.value.length && !selectedSize.value) {
      sizeError.value = true
      return
    }

    sizeError.value = false

    const selectedColorObj = colorOptions.value.find(
      c => String(c.name || '').toLowerCase().trim() === String(selectedColor.value || '').toLowerCase().trim()
    )

    let variantId = selectedColorObj?.variant_id

    if (!variantId && product.value?.variants?.length) {
      const matchedVariant = product.value.variants.find((variant) => {
        const variantName = String(variant.variant_name || '').toLowerCase()
        return (
          (!selectedSize.value || variantName.includes(String(selectedSize.value).toLowerCase())) &&
          (!selectedColor.value || variantName.includes(String(selectedColor.value).toLowerCase()))
        )
      })

      variantId = matchedVariant?.variant_id || matchedVariant?.id
    }

    if (!variantId && product.value?.variants?.length && selectedSize.value) {
      const matchedBySize = product.value.variants.find((variant) => {
        const variantName = String(variant.variant_name || '').toLowerCase()
        return variantName.includes(String(selectedSize.value).toLowerCase())
      })

      variantId = matchedBySize?.variant_id || matchedBySize?.id
    }

    if (!variantId && product.value?.default_variant_id) {
      variantId = product.value.default_variant_id
    }

    if (!variantId) {
      console.error('variant_id missing for selected product', {
        product: product.value,
        selectedColor: selectedColor.value,
        selectedSize: selectedSize.value
      })
      return
    }

    await addToCart(Number(variantId), quantity.value)
    await triggerFlyAnimation()
  } catch (error) {
    console.error('HANDLE ADD TO CART ERROR:', error)
  }
}

const handleBuyNow = async () => {
  if (sizes.value.length && !selectedSize.value) {
    sizeError.value = true
    return
  }

  await handleAddToCart()
  router.push('/cart')
}

// ----------------------
// UTILS
// ----------------------
function extractSizeFromVariantName(name = '') {
  const text = String(name).toUpperCase()
  const sizeList = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']
  return sizeList.find(size => text.includes(size)) || ''
}

function extractColorFromVariantName(name = '') {
  const knownColors = [
    'Black', 'White', 'Blue', 'Navy', 'Green', 'Olive', 'Grey', 'Gray',
    'Maroon', 'Wine', 'Red', 'Brown', 'Beige', 'Pink', 'Purple', 'Teal',
    'Mint', 'Sky Blue', 'Royal Blue'
  ]

  const lowerName = String(name).toLowerCase()

  const found = knownColors.find(color =>
    lowerName.includes(color.toLowerCase())
  )

  return found || ''
}
</script>

<style lang="scss">
@import 'src/css/men-product-details.scss';
</style>
