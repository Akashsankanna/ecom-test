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
        <p class="tag">Premium Women Collection</p>
        <h1>{{ product.title }}</h1>

        <div class="rating-row">
          <span class="stars">★★★★★</span>
          <span class="rating">{{ product.rating }}</span>
        </div>

        <div class="price-row">
          <h2>
            ₹ {{ Number(product.price).toLocaleString('en-IN', { minimumFractionDigits: 2 }) }}
          </h2>

          <span v-if="product.oldPrice" class="old-price">
            ₹ {{ Number(product.oldPrice).toLocaleString('en-IN') }}
          </span>

          <span v-if="product.oldPrice" class="discount">
            {{ discountPercent }}% OFF
          </span>
        </div>

           <!-- COLOUR -->
            <div class="variant-section">
                <p class="variant-label">Colour: <strong>{{ selectedColor }}</strong></p>
                  <div class="color-swatches">
                  <button
                    v-for="c in colorOptions" :key="c.name"
                    class="color-dot"
                    :class="{ active: selectedColor === c.name }"
                    :style="{ background: c.hex }"
                    :title="c.name"
                    @click="changeColor(c.name)"
                  > </button>
                  </div>
              </div>

                  <!-- Size -->
                  <div class="variant-section">
                    <div class="section-head">
                        <p class="variant-label">
                          Size: <strong>{{ selectedSize }}</strong>
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

                <!-- Delivery features (Knya style) -->
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

  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { womenProducts } from 'src/data/womenProducts'
import { addToCart } from 'src/stores/shop'
import sizeChartImg from 'src/assets/size_chart/size-chart.png'
import measureImg from 'src/assets/size_chart/measure.png'
//import ProductCustomization from 'components/ProductCustomization.vue'

//customization
const customizationData = ref(null)

const onCustomizationUpdated = (payload) => {
  customizationData.value = payload
  console.log('Customization:', payload)
}

// description
const activeAccordion = ref(null)

const route  = useRoute()
const router = useRouter()

// PRODUCT
const product = computed(() =>
  womenProducts.find(p => p.id === Number(route.params.id))
)

// IMAGES
const selectedImage = ref('')
const displayImages = ref([])
const imageDialog   = ref(false)

watch(product, (val) => {
  if (val && val.images?.length) {
    displayImages.value = [...val.images]
    selectedImage.value = val.images[0]
  }
}, { immediate: true })

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

// COLORS
const colorOptions = computed(() => product.value?.colors || [])
const selectedColor = ref('')

watch(product, (val) => {
  if (val?.colors?.length) {
    selectedColor.value = val.colors[0].name
  }
}, { immediate: true })

const changeColor = (colorName) => {
  selectedColor.value = colorName

  const colorObj = product.value?.colors?.find(
    c => String(c.name || '').toLowerCase().trim() === String(colorName || '').toLowerCase().trim()
  )

  if (colorObj?.images?.length) {
    displayImages.value = [...colorObj.images]
    selectedImage.value = colorObj.images[0]
  }
}

// PRICE
const oldPrice = computed(() => product.value?.oldPrice)
const discountPercent = computed(() => {
  const p = product.value
  if (!p?.oldPrice || !p?.price) return 0

  return Math.round(((p.oldPrice - p.price) / p.oldPrice) * 100)
})

// SIZE
const sizes = ['XS','S','M','L','XL','2XL','3XL']
const selectedSize = ref('')
const sizeError = ref(false)

// Qty
const quantity = ref(1)

const increaseQty = () => {
  quantity.value++
}

const decreaseQty = () => {
  if (quantity.value > 1) quantity.value--
}

// SIZE CHART POPUP
const sizeChartDialog = ref(false)
const activeTab = ref('size')

// PINCODE
const pincode = ref('')
const deliveryStatus = ref(null)
const pincodeError = ref('')
const isChecking = ref(false)

const onPincodeInput = () => {
  if (pincode.value.length > 6) {
    pincode.value = pincode.value.slice(0, 6)
  }

  deliveryStatus.value = null
  pincodeError.value = ''
}

const solapurPincodes = [
  '413001','413002','413003','413004','413005',
  '413006','413007','413101','413109','413112',
  '413203','413212','413214','413215','413216',
  '413219','413221','413222','413228','413253',
  '413301','413303','413304','413305','413306',
  '413307','413309','413310','413311','413314',
  '413401','413402','413403','413406','413409',
  '413410','413411'
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

// FLYING CART ANIMATION
const cartBtnRef = ref(null)
const flyingImgRef = ref(null)
const flyingVisible = ref(false)
const flyingActive = ref(false)
const flyingStyle = ref({})

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

// ONLY OLD BACKEND CONNECTION LOGIC
const handleAddToCart = async () => {
  try {
    if (!product.value) return

    if (!selectedSize.value) {
      sizeError.value = true
      return
    }

    sizeError.value = false

    const selectedColorObj = product.value.colors?.find(
      c => String(c.name || '').toLowerCase().trim() === String(selectedColor.value || '').toLowerCase().trim()
    )

    let variantId = selectedColorObj?.variant_id || product.value.variant_id

    if (!variantId && product.value?.variants?.length) {
      const matchedVariant = product.value.variants.find((variant) => {
        const variantName = String(variant.variant_name || '').toLowerCase()
        return (
          variantName.includes(String(selectedSize.value).toLowerCase()) &&
          variantName.includes(String(selectedColor.value).toLowerCase())
        )
      })

      variantId = matchedVariant?.variant_id || matchedVariant?.id
    }

    if (!variantId) {
      console.error('variant_id missing in womenProducts item:', {
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
  if (!selectedSize.value) {
    sizeError.value = true
    return
  }

  await handleAddToCart()
  router.push('/cart')
}
</script>

<style scoped lang="scss">
@import 'src/css/women-product-details.scss';
</style>
