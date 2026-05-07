<template>
  <div v-if="product" class="men-product-page">
    <div class="product-page">

      <!-- LEFT: thumbs + main image -->
      <div class="left-wrap">
        <div class="left">
          <!-- thumbnails -->
          <div class="thumbs">
            <img
              v-for="img in displayImages"
              :key="img"
              :src="img"
              :class="{ active: selectedImage === img }"
              @click="selectedImage = img"
            />
          </div>

          <!-- main image -->
          <div class="main-image-box" @click="openImageDialog">
            <img :src="selectedImage" class="main-image" />
          </div>
        </div>
      </div>

      <!-- RIGHT: details -->
      <div class="right">
        <p class="tag">{{ productTag }}</p>
        <h1>{{ product.title || product.name || 'Product' }}</h1>

        <div class="rating-row"  @click="scrollToReviews" style="cursor:pointer;">
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

        <!-- CUSTOMIZATION -->
      <ProductCustomization
        :product-id="product?.id"
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

          <!-- ref added for flying animation origin -->
          <button class="cart-btn" ref="cartBtnRef" @click="handleAddToCart">
            Add to Cart
          </button>

          <button class="buy-btn" @click="handleBuyNow">
            Buy Now
          </button>

        </div>

        <!-- FLYING IMAGE ELEMENT -->
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
    v-for="(item, index) in deliveryFeatures"
    :key="index"
  >
    <i :class="item.icon"></i>
    <p class="delivery-title" v-html="item.title"></p>
  </div>
</div>
        
        <!-- PIN CODE SECTION -->
        <div class="section delivery-details">
          <h3>Delivery Details</h3>

          <div class="pincode-checker">
            <div class="input-btn-group">
              <!--  maxlength 6, @keyup.enter support -->
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

            <!--  6-digit validation message -->
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

        <!-- DETAILS ACCORDION -->
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
                <li v-for="(item,index) in product.details" :key="index">{{ item }}</li>
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
                <li v-for="(item,index) in product.fabricCare" :key="index">{{ item }}</li>
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
                <li v-for="(item,index) in product.returnPoints" :key="index">{{ item }}</li>
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
          <button class="tab" :class="{ active: activeTab === 'size' }" @click="activeTab = 'size'">Size</button>
          <button class="tab" :class="{ active: activeTab === 'measure' }" @click="activeTab = 'measure'">How to Measure</button>
        </div>
        <div class="size-chart-content">
          <img v-if="activeTab === 'size'" :src="sizeChartImg" class="size-chart-img" />
          <img v-else :src="measureImg" class="size-chart-img" />
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
```


  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from 'boot/axios'
import { addToCart } from 'src/stores/shop'
import ProductCustomization from 'src/components/Productcustomization.vue'
import sizeChartFallback from 'src/assets/size_chart/size-chart.png'
import measureFallback from 'src/assets/size_chart/measure.png'
import ProductReviews from 'components/ProductReviews.vue'


//scroll
const reviewsRef = ref(null)

const scrollToReviews = () => {
  const el = reviewsRef.value?.$el
  if (!el) return

  el.scrollIntoView({ behavior: 'smooth' })

  el.classList.add('highlight')
  setTimeout(() => {
    el.classList.remove('highlight')
  }, 1000)
}

//add review

const addReview = (newReview) => {
  if (!product.value.reviews) {
    product.value.reviews = []
  }

  product.value.reviews.push(newReview)
}
const route = useRoute()
const router = useRouter()

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
const flyingVisible = ref(false)
const flyingActive = ref(false)
const flyingStyle = ref({})

const normalizeVariant = (v) => {
  return {
    ...v,
    id: Number(v.id || v.variant_id),
    variant_id: Number(v.variant_id || v.id),
    product_id: Number(v.product_id),
    color_id: v.color_id || null,
    color: v.color || v.color_name || extractColorFromVariantName(v.variant_name),
    color_name: v.color_name || v.color || extractColorFromVariantName(v.variant_name),
    hex_code: v.hex_code || v.color_code || '#cccccc',
    size: v.size || extractSizeFromVariantName(v.variant_name),
    price: Number(v.price || 0),
    stock: Number(v.stock || 0),
    image_url: v.image_url || v.image || ''
  }
}

const fetchProduct = async () => {
  try {
    loading.value = true
    const productId = Number(route.params.id)

    const response = await api.get(`/products/${productId}`)
    const data = response.data?.product || response.data?.data || response.data

    const variants = Array.isArray(data.variants || data.product_variants)
      ? (data.variants || data.product_variants).map(normalizeVariant)
      : []

    product.value = {
      ...data,
      id: Number(data.id || data.product_id || productId),
      product_id: Number(data.product_id || data.id || productId),
      db_product_id: Number(data.db_product_id || data.product_id || data.id || productId),
      title: data.title || data.name || 'Product',
      name: data.name || data.title || 'Product',
      image_url: data.image_url || data.image || '',
      image: data.image || data.image_url || '',
      variants
    }

    console.log('PRODUCT DETAILS:', product.value)
  } catch (error) {
    console.error('PRODUCT FETCH ERROR:', error.response?.data || error)
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
}

const openImageDialog = () => {
  imageDialog.value = true
}

const normalizedImages = computed(() => {
  if (!product.value) return []

  const imgs = []

  if (Array.isArray(product.value.images)) {
    product.value.images.forEach(img => {
      if (typeof img === 'string') imgs.push(img)
      else imgs.push(img.image_url || img.url || img.src || img.file_path || '')
    })
  }

  if (Array.isArray(product.value.product_images)) {
    product.value.product_images.forEach(img => {
      if (typeof img === 'string') imgs.push(img)
      else imgs.push(img.image_url || img.url || img.src || img.file_path || '')
    })
  }

  product.value.variants?.forEach(v => {
    if (v.image_url) imgs.push(v.image_url)
    if (v.image) imgs.push(v.image)
  })

  if (product.value.image_url) imgs.push(product.value.image_url)
  if (product.value.product_image) imgs.push(product.value.product_image)
  if (product.value.image) imgs.push(product.value.image)

  return [...new Set(imgs.filter(Boolean))]
})

const colorOptions = computed(() => {
  if (!product.value?.variants?.length) return []

  const unique = new Map()

  product.value.variants.forEach((variant) => {
    const colorName =
      variant.color ||
      variant.color_name ||
      extractColorFromVariantName(variant.variant_name)

    if (colorName && !unique.has(colorName.toLowerCase())) {
      const variantImages = []

      if (variant.image_url) variantImages.push(variant.image_url)
      if (variant.image) variantImages.push(variant.image)

      unique.set(colorName.toLowerCase(), {
        name: colorName,
        color_id: variant.color_id || null,
        hex: variant.hex_code || variant.color_code || '#cccccc',
        variant_id: Number(variant.variant_id || variant.id),
        images: variantImages.filter(Boolean)
      })
    }
  })

  return Array.from(unique.values())
})

const sizes = computed(() => {
  if (!product.value?.variants?.length) return []

  const extracted = product.value.variants
    .map(v => v.size || extractSizeFromVariantName(v.variant_name))
    .filter(Boolean)

  return [...new Set(extracted)]
})

const selectedVariant = computed(() => {
  if (!product.value?.variants?.length) return null

  const selectedColorText = String(selectedColor.value || '').toLowerCase().trim()
  const selectedSizeText = String(selectedSize.value || '').toLowerCase().trim()

  const found = product.value.variants.find((variant) => {
    const variantSize = String(
      variant.size || extractSizeFromVariantName(variant.variant_name)
    ).toLowerCase().trim()

    const variantColor = String(
      variant.color ||
      variant.color_name ||
      extractColorFromVariantName(variant.variant_name)
    ).toLowerCase().trim()

    const sizeMatch = !selectedSizeText || variantSize === selectedSizeText
    const colorMatch = !selectedColorText || variantColor === selectedColorText

    return sizeMatch && colorMatch
  })

  return found || product.value.variants[0]
})

const currentPrice = computed(() => {
  return Number(
    selectedVariant.value?.price ||
    product.value?.price ||
    product.value?.sale_price ||
    product.value?.final_price ||
    0
  )
})

const oldPrice = computed(() => {
  return product.value?.oldPrice ||
    product.value?.old_price ||
    product.value?.mrp ||
    product.value?.original_price ||
    null
})

const displayRating = computed(() => {
  return Number(product.value?.rating || product.value?.avg_rating || 4.8).toFixed(1)
})

const ratingStars = computed(() => {
  const rating = Math.round(Number(product.value?.rating || product.value?.avg_rating || 4.8))
  return '★'.repeat(Math.max(0, Math.min(5, rating))) + '☆'.repeat(Math.max(0, 5 - rating))
})

const discountPercent = computed(() => {
  if (!oldPrice.value || !currentPrice.value) return 0
  return Math.round(((oldPrice.value - currentPrice.value) / oldPrice.value) * 100)
})

const productTag = computed(() => {
  return product.value?.tag ||
    product.value?.category_name ||
    product.value?.collection_name ||
    'Premium Collection'
})

const sizeChartImage = computed(() => product.value?.size_chart_image || sizeChartFallback)
const measureImage = computed(() => product.value?.measure_image || measureFallback)

const accordionSections = computed(() => {
  if (!product.value) return []

  return [
    {
      title: 'Details & Fit',
      description: product.value.details_and_fit || product.value.description || '',
      points: product.value.details || []
    },
    {
      title: 'Fabric & Care',
      description: product.value.fabric_and_care || product.value.fabricDescription || product.value.fabric_description || '',
      points: product.value.fabricCare || product.value.fabric_care || []
    },
    {
      title: 'Return & Exchange',
      description: product.value.return_and_exchange || product.value.returnDescription || product.value.return_description || '',
      points: product.value.returnPoints || product.value.return_points || []
    }
  ].filter(section => section.description || section.points?.length)
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

watch(product, (val) => {
  if (!val) return

  displayImages.value = normalizedImages.value.length ? [...normalizedImages.value] : ['/favicon.ico']
  selectedImage.value = displayImages.value[0]

  if (colorOptions.value.length) {
    selectedColor.value = colorOptions.value[0].name
  }

  if (sizes.value.length === 1) {
    selectedSize.value = sizes.value[0]
  }
}, { immediate: true })

const changeColor = (colorName) => {
  selectedColor.value = colorName

  const colorObj = colorOptions.value.find(
    c => String(c.name).toLowerCase().trim() === String(colorName).toLowerCase().trim()
  )

  if (colorObj?.images?.length) {
    displayImages.value = [...colorObj.images]
    selectedImage.value = colorObj.images[0]
  } else {
    displayImages.value = normalizedImages.value.length ? [...normalizedImages.value] : ['/favicon.ico']
    selectedImage.value = displayImages.value[0]
  }
}

const increaseQty = () => {
  quantity.value++
}

const decreaseQty = () => {
  if (quantity.value > 1) quantity.value--
}

const onPincodeInput = () => {
  if (pincode.value.length > 6) pincode.value = pincode.value.slice(0, 6)
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
    console.error('PINCODE CHECK ERROR:', error.response?.data || error)
    pincodeError.value = 'Unable to check delivery right now'
  } finally {
    isChecking.value = false
  }
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

const handleAddToCart = async () => {
  try {
    if (!product.value) return

    if (sizes.value.length && !selectedSize.value) {
      sizeError.value = true
      return
    }

    sizeError.value = false

    const variantId = Number(
      selectedVariant.value?.variant_id ||
      selectedVariant.value?.id ||
      product.value?.default_variant_id
    )

    if (!variantId) {
      console.error('variant_id missing', {
        product: product.value,
        selectedVariant: selectedVariant.value,
        selectedColor: selectedColor.value,
        selectedSize: selectedSize.value
      })
      return
    }

    console.log('ADD TO CART PAYLOAD:', {
      product_id: product.value.id,
      variant_id: variantId,
      color_id: selectedVariant.value?.color_id,
      color: selectedVariant.value?.color || selectedVariant.value?.color_name,
      size: selectedVariant.value?.size,
      quantity: quantity.value
    })

    await addToCart({
      product_id: product.value.id,
      variant_id: variantId,
      quantity: Number(quantity.value || 1),
      color_id: selectedVariant.value?.color_id || null,
      color: selectedVariant.value?.color || selectedVariant.value?.color_name || '',
      size: selectedVariant.value?.size || '',
      customization: customizationData.value || null
    })

    await triggerFlyAnimation()
  } catch (error) {
    console.error('HANDLE ADD TO CART ERROR:', error.response?.data || error)
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

function extractSizeFromVariantName(name = '') {
  const text = String(name).toUpperCase()
  const sizeList = ['5XL', '4XL', '3XL', '2XL', 'XL', 'L', 'M', 'S', 'XS', '2XS', '3XS']
  return sizeList.find(size => text.includes(size)) || ''
}

function extractColorFromVariantName(name = '') {
  const knownColors = [
    'Soft Blue+Grey',
    'Navy Blue',
    'Dark Grey',
    'Mint Green',
    'Mustard Yellow',
    'Dark Green',
    'Dust Pink',
    'Black',
    'White',
    'Blue',
    'Navy',
    'Green',
    'Grey',
    'Maroon',
    'Brown',
    'Tan',
    'Yellow'
  ]

  const lowerName = String(name).toLowerCase()
  return knownColors.find(color => lowerName.includes(color.toLowerCase())) || ''
}
</script>

<style lang="scss">
@import 'src/css/men-product-details.scss';
</style>