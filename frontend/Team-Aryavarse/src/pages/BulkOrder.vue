<template>
  <q-page class="bulk-page">

    <!-- ─── HERO BANNER with AUTO SLIDER ──────────────────────── -->
    <div class="bulk-banner">

      <!-- Slider Track -->
      <div
        class="bulk-slider__track"
        :style="{
          transform: `translateX(-${currentBannerSlide * 100}%)`,
          transition: isBannerTransitioning ? 'transform 0.7s cubic-bezier(0.4, 0, 0.2, 1)' : 'none'
        }"
      >
        <!-- Original Slides -->
<div
  class="bulk-slider__slide"
  v-for="(slide, i) in bannerSlides"
  :key="i"
>
  <!-- ADD this bulk-inner wrapper like hero-inner -->
  <div class="bulk-inner">
    <div class="bulk-banner__content">
      <p class="bulk-banner__eyebrow">{{ slide.eyebrow }}</p>
      <h1 class="bulk-banner__title">{{ slide.title }}</h1>
      <p class="bulk-banner__sub">{{ slide.sub }}</p>
      <div class="bulk-banner__badges">
        <span class="badge" v-for="badge in slide.badges" :key="badge">{{ badge }}</span>
      </div>
    </div>
    <!-- Image now as flex sibling, not background -->
    <div class="bulk-image-wrapper">
      <img :src="slide.image" class="bulk-banner__img" :alt="slide.eyebrow" />
    </div>
  </div>
</div>

<!-- Clone slide — same structure -->
<div class="bulk-slider__slide">
  <div class="bulk-inner">
    <div class="bulk-banner__content">
      <p class="bulk-banner__eyebrow">{{ bannerSlides[0].eyebrow }}</p>
      <h1 class="bulk-banner__title">{{ bannerSlides[0].title }}</h1>
      <p class="bulk-banner__sub">{{ bannerSlides[0].sub }}</p>
      <div class="bulk-banner__badges">
        <span class="badge" v-for="badge in bannerSlides[0].badges" :key="badge">{{ badge }}</span>
      </div>
    </div>
    <div class="bulk-image-wrapper">
      <img :src="bannerSlides[0].image" class="bulk-banner__img" :alt="bannerSlides[0].eyebrow" />
    </div>
  </div>
</div>
            
          </div>
    

      <!-- CHANGE: Fade overlay — same as home page, flashes white on each slide change -->
      <div class="bulk-fade-overlay" :class="{ 'is-fading': isBannerFading }"></div>

      <!-- Dot Indicators -->
      <div class="bulk-slider__dots">
        <button
          v-for="(slide, i) in bannerSlides"
          :key="i"
          class="bulk-slider__dot"
          :class="{ 'bulk-slider__dot--active': activeDotIndex === i }"
          @click="goToBannerSlide(i)"
        />
      </div>

    </div>

    <!---- MAIN CONTENT----->
    <div class="bulk-container">
      <div class="bulk-grid">

        <!---- LEFT: Why Us ----->
        <div class="why-card">
          <h3 class="why-card__title">Why Choose Us?</h3>

          <div v-for="(f, i) in features" :key="i" class="feature-item">
            <div class="feature-item__icon-wrap">
              <q-icon :name="f.icon" color="teal" size="22px" />
            </div>
            <div>
              <p class="feature-item__title">{{ f.title }}</p>
              <p class="feature-item__desc">{{ f.desc }}</p>
            </div>
          </div>

          <div class="divider" />

          <div class="trust-badge">
            <q-icon name="verified" color="teal" size="32px" />
            <p class="trust-badge__title">Trusted by Hospitals Across India</p>
            <p class="trust-badge__sub">500+ Bulk Orders Delivered Successfully</p>
          </div>

          <!-- HOW IT WORKS -->
          <div class="divider" />
          <h4 class="steps-title">How It Works</h4>
          <div v-for="(s, i) in steps" :key="i" class="step-item">
            <div class="step-item__num">{{ i + 1 }}</div>
            <div>
              <p class="step-item__title">{{ s.title }}</p>
              <p class="step-item__desc">{{ s.desc }}</p>
            </div>
          </div>
        </div>

        <!-- ── RIGHT: Form ──────────────────────────────────── -->
        <div class="form-card">
          <div class="form-card__header">
            <h2 class="form-card__title">Bulk Order Request</h2>
            <p class="form-card__sub">
              Fill the form below — our team will contact you within 24 hours
            </p>
          </div>

          <q-form @submit.prevent="submitForm" class="bulk-form">

            <!-- ── SECTION 1: Organisation -->
            <div class="form-section">
              <div class="section-header">
                <span class="section-num">01</span>
                <p class="section-title">Organisation Details</p>
              </div>

              <div class="form-row">
                <div class="form-field">
                  <p class="field-label">Organisation / Hospital Name <span class="required">*</span></p>
                  <q-input
  v-model="form.orgName"
  outlined
  dense
  maxlength="50"
  placeholder="Enter organisation name"

  @update:model-value="val => form.orgName = val.replace(/[^A-Za-z\s]/g, '')"

  :rules="[
    v => !!v || 'Required',
    v => /^[A-Za-z\s]+$/.test(v) || 'Only letters allowed (no numbers)',
    v => v.length <= 50 || 'Max 50 characters allowed'
  ]"
/>
                </div>
              </div>

              <div class="form-row form-row--2">
                <div class="form-field">
                  <p class="field-label">Contact Person Name <span class="required">*</span></p>
<q-input
  v-model="form.contactName"
  outlined
  dense
  maxlength="30"
  placeholder="Enter name"

  @update:model-value="val => form.contactName = val.replace(/[^A-Za-z\s]/g, '')"

  :rules="[
    v => !!v || 'Required',
    v => v.length <= 30 || 'Max 30 characters allowed'
  ]"
/>
                </div>
                <div class="form-field">
                  <p class="field-label">Email Address <span class="required">*</span></p>
                 <q-input
  v-model="form.email"
  outlined
  dense
  type="email"
  maxlength="40"
  placeholder="Enter email"

  @update:model-value="val => {
    // remove unwanted special characters
    form.email = val.replace(/[^a-zA-Z0-9.@]/g, '')
  }"

  :rules="[
    v => !!v || 'Required',
    v => /^[a-zA-Z0-9.]+@gmail\.com$/.test(v) || 'Only valid @gmail.com allowed'
  ]"
/>
                </div>
              </div>

              <div class="form-row form-row--2">
                <div class="form-field">
                  <p class="field-label">Phone Number <span class="required">*</span></p>
                  <q-input
  v-model="form.phone"
  outlined
  dense
  maxlength="10"
  inputmode="numeric"
  placeholder="Enter 10 digit phone number"

  @update:model-value="val => form.phone = val.replace(/[^0-9]/g, '')"

  :rules="[
    v => !!v || 'Required',
    v => v.length === 10 || 'Must be exactly 10 digits'
  ]"
/>
                </div>
                <div class="form-field">
                  <p class="field-label">Country <span class="required">*</span></p>
                  <q-select v-model="form.country" :options="countryOptions" outlined dense placeholder="Select country" :rules="[v => !!v || 'Required']" />
                </div>
              </div>

              <div class="form-row form-row--2">
                <div class="form-field">
                  <p class="field-label">State <span class="required">*</span></p>
                  <q-select
  v-model="form.state"
  :options="stateOptions"
  outlined
  dense
  :display-value="form.state || 'Select state'"
  :rules="[v => !!v || 'Required']"
/>
                </div>
                <div class="form-field">
                  <p class="field-label">City <span class="required">*</span></p>
                  <q-input
  v-model="form.city"
  outlined
  dense
  maxlength="20"
  placeholder="Enter city"

  @update:model-value="val => form.city = val.replace(/[^A-Za-z\s]/g, '')"

  :rules="[
    v => !!v || 'Required',
    v => /^[A-Za-z\s]+$/.test(v) || 'Only letters allowed',
    v => v.length <= 30 || 'Max 30 characters allowed'
  ]"
/>
                </div>
              </div>

              <div class="form-row">
                <div class="form-field">
                  <p class="field-label">Address <span class="required">*</span></p>
                  <q-input
  v-model="form.address"
  type="textarea"
  outlined
  dense
  rows="2"
  autogrow
  maxlength="50"
  counter
  placeholder="Enter full address"
  :rules="[
    v => !!v || 'Required',
    v => v.length <= 50 || 'Max 50 characters allowed'
  ]"
/>
                </div>
              </div>

              <div class="form-row form-row--2">
                <div class="form-field">
                  <p class="field-label">GST Number</p>
                  <q-input
  v-model="form.gst"
  outlined
  dense
  maxlength="15"
  placeholder="Enter GST number"

  @update:model-value="val => form.gst = val.toUpperCase().replace(/[^0-9A-Z]/g, '')"

  :rules="[
    v => !v || v.length === 15 || 'GST must be 15 characters',
    v => !v || /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(v) || 'Invalid GST format'
  ]"
/>
</div>
                <div class="form-field">
                  <p class="field-label">Postal Code</p>
                  <q-input
  v-model="form.postalCode"
  outlined
  dense
  maxlength="6"
  inputmode="numeric"
  placeholder="Enter 6 digit PIN code"

  @update:model-value="val => form.postalCode = val.replace(/[^0-9]/g, '')"

  :rules="[
    v => !!v || 'Required',
    v => /^[1-9][0-9]{5}$/.test(v) || 'Enter valid 6-digit PIN code'
  ]"
/>
                </div>
              </div>
            </div>

            <!-- ── SECTION 2: Order Details ─────────────────── -->
            <div class="form-section">
              <div class="section-header">
                <span class="section-num">02</span>
                <p class="section-title">Order Details</p>
              </div>

              <div v-for="(product, index) in form.products" :key="index" class="product-row-card">
                <div class="product-row-header">
                  <span class="product-row-label">Order {{ index + 1 }}</span>
                  <button v-if="form.products.length > 1" type="button" class="remove-product-btn" @click="removeProduct(index)">
                    <q-icon name="close" size="16px" /> Remove
                  </button>
                </div>

                <div class="product-fields-row">
                  <div class="product-field">
                    <p class="field-label">Product Category <span class="required">*</span></p>
                    <q-select v-model="product.category" :options="categories" outlined dense placeholder="Select" :rules="[v => !!v || 'Required']" />
                  </div>
                  <div class="product-field product-field--qty">
                    <p class="field-label">Quantity <span class="required">*</span></p>
                   <q-input
  v-model.number="product.quantity"
  type="number"
  outlined
  dense
  min="1"
  placeholder="Qty"

  @update:model-value="val => {
    if (val < 1) product.quantity = null
  }"

  :rules="[
    v => !!v || 'Required',
    v => v > 0 || 'Must be greater than 0'
  ]"
/>
                  </div>
                  <div class="product-field">
                    <p class="field-label">Size <span class="required">*</span></p>
                    <q-select v-model="product.size" :options="['XS','S','M','L','XL','XXL','3XL']" outlined dense placeholder="Size" :rules="[v => !!v || 'Required']" />
                  </div>
                  <div class="product-field">
                    <p class="field-label">Gender <span class="required">*</span></p>
                    <q-select v-model="product.gender" :options="genderOptions" outlined dense placeholder="Gender" :rules="[v => !!v || 'Required']" />
                  </div>
                  <div class="product-field product-field--color">
                    <p class="field-label">Color</p>
                    <q-select v-model="product.colors" :options="colorOptions" outlined dense multiple use-chips placeholder="Select colors" />
                  </div>
                </div>
              </div>

              <div class="add-product-wrap">
                <q-btn flat icon="add_circle" label="Add Product" color="teal" no-caps class="add-product-btn" @click="addProduct" />
              </div>

              <div class="form-row form-row--2" style="margin-top: 18px;">
                <div class="form-field">
                  <p class="field-label">Expected Delivery Date <span class="required">*</span></p>
                  <q-input v-model="form.deliveryDate" outlined dense type="date" :rules="[v => !!v || 'Required']" />
                </div>
                <div class="form-field">
                  <p class="field-label">Fabric Preference</p>
                  <q-select v-model="form.fabric" :options="fabrics" outlined dense :display-value="form.fabric ? form.fabric : 'Select fabric'" />
                </div>
              </div>

              <div class="form-row">
                <div class="form-field">
                  <p class="field-label">Additional Requirements</p>
                  <q-input v-model="form.notes" outlined dense type="textarea" rows="3" placeholder="Any specific requirements, packaging notes, etc." />
                </div>
              </div>
            </div>

             <!-- ── SECTION 3: Branding & Customization ─────── -->
            <div class="form-section">
              <div class="section-header">
                <span class="section-num">03</span>
                <p class="section-title">Branding & Customization</p>
              </div>

              <q-toggle v-model="form.hasCustomization" label="Add Custom Branding to this Order" color="teal" class="custom-toggle" />

              <transition name="slide-down">
  <div v-if="form.hasCustomization">

    <ProductCustomization
      @customization-updated="handleCustomizationUpdate"
      @customization-applied="handleCustomizationApply"
    />

  </div>
</transition>
            </div>

            <!-- ── SECTION 4: Quote Summary ──────────────────── -->
            <div v-if="totalQuantity >= 20" class="quote-summary">
              <div class="quote-header">
                <q-icon name="receipt_long" color="teal" size="20px" />
                <span>Estimated Quote Summary</span>
              </div>
              <div class="quote-rows">
                <div class="quote-row"><span>Total Quantity</span><span>{{ totalQuantity }} pcs</span></div>
                <div class="quote-row"><span>Estimated Price / Piece</span><span>₹{{ estimatedPricePerPiece }}</span></div>
                <div v-if="form.hasCustomization && customizationCost > 0" class="quote-row">
                  <span>Customization / Piece</span><span>+₹{{ customizationCost }}</span>
                </div>
                <div class="quote-row quote-row--total">
                  <span>Estimated Total</span><span>₹{{ estimatedTotal.toLocaleString('en-IN') }}</span>
                </div>
              </div>
              <p class="quote-note">
                <span class="required">*</span> Final pricing will be confirmed by our team after reviewing your request.
                50% advance required to begin production.
              </p>
            </div>

            <!-- ── SUBMIT----- -->
            <div class="form-submit">
              <q-btn type="submit" label="Submit Bulk Request" color="teal" class="submit-btn" :loading="submitting" unelevated no-caps>
                <template #loading><q-spinner-dots size="20px" /></template>
              </q-btn>
              <p class="submit-note">Our team will reach out within 24 business hours</p>
            </div>

          </q-form>
        </div>

      </div>
    </div>

    <!-- ── SUCCESS DIALOG ──────────────────────────────────── -->
    <q-dialog v-model="successDialog">
      <div class="success-card">
        <div class="success-icon">✅</div>
        <h3>Request Submitted!</h3>
        <p>Your bulk order request has been received.<br />Request ID: <strong>{{ requestNumber }}</strong></p>
        <p class="success-sub">Our team will contact you at <strong>{{ form.email }}</strong> within 24 business hours with a quote.</p>
        <q-btn label="Done" color="teal" unelevated no-caps v-close-popup class="done-btn" />
      </div>
    </q-dialog>

  </q-page>
</template>

<script>
import { bannerImg } from 'src/data/imageHelper'
import { fetchBulkOrderOptions, submitBulkOrderRequest } from 'src/service/bulkorderservice'
import ProductCustomization from 'src/components/Productcustomization.vue'

export default {
  name: 'BulkOrderPage',

  components: {
    ProductCustomization
  },

  data() {
    return {
      // ── SLIDER STATE ────────────────────────────────────────
      currentBannerSlide: 0,
      isBannerTransitioning: true,
      bannerInterval: null,

      // ── BANNER SLIDES ───────────────────────────────────────
      bannerSlides: [
        {
          image: bannerImg('bulkorder2.png'),
          eyebrow: 'FOR HOSPITALS & CLINICS',
          title: 'Bulk Orders Made Simple',
          sub: 'Premium hospital scrubs with custom branding & guaranteed delivery',
          badges: ['✅ GST Invoice', '✅ Pan India Delivery']
        },
        {
          image: bannerImg('bulkorder.png'),
          eyebrow: 'CUSTOM BRANDING AVAILABLE',
          title: 'Your Logo, Your Identity On Every Scrub.',
          sub: 'Embroidery, logo print & name tags — fully customized for your hospital',
          badges: ['🪡 Embroidery', '🖨️ Logo Print', '🏷️ Name Tags']
        },
        {
          image: bannerImg('bulkorder1.png'),
          eyebrow: 'BEST BULK PRICING',
          title: 'Volume Discounts Starting',
          sub: '50% advance, 50% on delivery. GST invoice provided for all B2B orders',
          badges: ['💰 Best Pricing', '📦 7–10 Day Delivery', '🧾 GST Invoice']
        }
      ],

      submitting: false,
      successDialog: false,
      requestNumber: '',
      logoPreview: null,

      // backend loading
      loadingOptions: false,

      // keep raw category rows from backend
      categoryRows: [],

      form: {
        orgName: '',
        contactName: '',
        email: '',
        phone: '',
        gst: '',
        address: '',
        city: '',
        state: '',
        postalCode: '',
        country: 'India',
        fabric: null,
        deliveryDate: '',
        notes: '',
        products: [
          { category: null, quantity: null, size: null, gender: null, colors: [] }
        ],
        hasCustomization: false,
        customTypes: [],
        positions: [],
        customText: '',
        logoFile: null,
        customNotes: ''
      },

      countryOptions: [
        'India', 'United States', 'United Kingdom', 'Canada', 'Australia',
        'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Sweden',
        'Norway', 'Denmark', 'Finland', 'Russia', 'China', 'Japan',
        'South Korea', 'Singapore', 'UAE', 'Saudi Arabia', 'Qatar',
        'South Africa', 'Brazil', 'Mexico', 'Indonesia', 'Thailand',
        'Malaysia', 'Philippines', 'Nepal', 'Bangladesh', 'Sri Lanka'
      ],

      stateOptions: [],

      allStates: {
        India: [
          'Maharashtra', 'Gujarat', 'Karnataka', 'Tamil Nadu', 'Telangana',
          'Kerala', 'Madhya Pradesh', 'Rajasthan', 'Uttar Pradesh',
          'Bihar', 'Punjab', 'Haryana', 'West Bengal', 'Odisha', 'Assam'
        ],
        'United States': ['California', 'Texas', 'Florida', 'New York', 'Illinois'],
        'United Kingdom': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
        Canada: ['Ontario', 'Quebec', 'British Columbia', 'Alberta']
      },

      // these are shown in UI
      categories: ['Collar Scrub Suit', 'V-Neck Scrub Suit', 'Doctor Apron', 'Nurse Uniform', 'OT Gown', 'Mixed'],
      fabrics: ['Apollo', 'Aqua', 'Cottex', 'Avenue', 'Poly-Cotton'],
      genderOptions: ['Men', 'Women', 'Mixed (Men + Women)'],
      colorOptions: ['Black', 'Navy Blue', 'Royal Blue', 'Green', 'Dark Grey', 'Brown', 'Maroon', 'White'],
      sizeOptions: ['XS', 'S', 'M', 'L', 'XL', 'XXL'],

      customizationTypes: [
        { id: 1, name: 'Embroidery', icon: '🪡', price: 150, requiresText: true, requiresLogo: false },
        { id: 2, name: 'Logo Print', icon: '🖨️', price: 100, requiresText: false, requiresLogo: true },
        { id: 3, name: 'Name Tag', icon: '🏷️', price: 80, requiresText: true, requiresLogo: false },
        { id: 4, name: 'Dept. Print', icon: '🏥', price: 120, requiresText: true, requiresLogo: false },
        { id: 5, name: 'Custom Patch', icon: '🎖️', price: 200, requiresText: false, requiresLogo: true }
      ],

      positions: [
        { id: 1, name: 'Left Chest' },
        { id: 2, name: 'Right Chest' },
        { id: 3, name: 'Back' },
        { id: 4, name: 'Sleeve' },
        { id: 5, name: 'Collar' }
      ],

      features: [
        { icon: 'local_hospital', title: 'Hospital-Grade Quality', desc: 'Premium, durable medical fabrics' },
        { icon: 'payments', title: 'Best Bulk Pricing', desc: 'Discounts starting at 20 pieces' },
        { icon: 'support_agent', title: 'Dedicated Account Manager', desc: 'End-to-end support & follow-up' },
        { icon: 'palette', title: 'Custom Branding', desc: 'Logo, embroidery & name tags' },
        { icon: 'local_shipping', title: 'Flexible Payment', desc: '50% advance, 50% on delivery' },
        { icon: 'receipt_long', title: 'GST Invoice', desc: 'Proper B2B tax invoice provided' }
      ],

      steps: [
        { title: 'Submit Request', desc: 'Fill the form with your requirements' },
        { title: 'Get a Quote', desc: 'Our team sends pricing within 24 hours' },
        { title: 'Approve & Pay', desc: '50% advance to start production' },
        { title: 'Production', desc: 'Manufacturing + customization in 7–10 days' },
        { title: 'Delivery', desc: 'Pan-India shipping to your door' }
      ]
    }
  },

  watch: {
    'form.country'(val) {
      this.stateOptions = this.allStates[val] || []
      this.form.state = ''
    }
  },

  computed: {
    activeDotIndex() {
      if (this.currentBannerSlide >= this.bannerSlides.length) return 0
      return this.currentBannerSlide
    },

    totalQuantity() {
      return this.form.products.reduce((sum, p) => sum + (Number(p.quantity) || 0), 0)
    },

    requiresText() {
      return this.form.customTypes.some(id => {
        const t = this.customizationTypes.find(c => c.id === id)
        return t && t.requiresText
      })
    },

    requiresLogo() {
      return this.form.customTypes.some(id => {
        const t = this.customizationTypes.find(c => c.id === id)
        return t && t.requiresLogo
      })
    },

    customizationCost() {
      return this.form.customTypes.reduce((sum, id) => {
        const t = this.customizationTypes.find(c => c.id === id)
        return sum + (t ? t.price : 0)
      }, 0)
    },

    estimatedPricePerPiece() {
      const qty = this.totalQuantity
      if (qty >= 200) return 700
      if (qty >= 100) return 750
      if (qty >= 50) return 820
      return 900
    },

    estimatedTotal() {
      return this.totalQuantity * (this.estimatedPricePerPiece + this.customizationCost)
    }
  },

  mounted() {
    this.stateOptions = this.allStates[this.form.country] || []
    this.startBannerSlider()
    this.loadBulkOptions()
  },

  beforeUnmount() {
    this.stopBannerSlider()
  },

  methods: {
    // ── API LOAD ──────────────────────────────────────────────
    async loadBulkOptions() {
      try {
        this.loadingOptions = true

        const data = await fetchBulkOrderOptions()

        if (Array.isArray(data?.categories) && data.categories.length) {
          this.categoryRows = data.categories
          this.categories = data.categories.map(item => item.name)
        }

        if (Array.isArray(data?.sizes) && data.sizes.length) {
          this.sizeOptions = data.sizes
        }

        if (Array.isArray(data?.colors) && data.colors.length) {
          this.colorOptions = data.colors
        }

        if (Array.isArray(data?.genders) && data.genders.length) {
          this.genderOptions = data.genders
        }

        if (Array.isArray(data?.fabrics) && data.fabrics.length) {
          this.fabrics = data.fabrics
        }
      } catch (error) {
        console.error('LOAD BULK OPTIONS ERROR:', error)
      } finally {
        this.loadingOptions = false
      }
    },

    // ── SLIDER METHODS ────────────────────────────────────────
    startBannerSlider() {
      this.bannerInterval = setInterval(this.nextBannerSlide, 4000)
    },

    stopBannerSlider() {
      clearInterval(this.bannerInterval)
    },

    nextBannerSlide() {
      this.currentBannerSlide += 1

      if (this.currentBannerSlide === this.bannerSlides.length) {
        setTimeout(() => {
          this.isBannerTransitioning = false
          this.currentBannerSlide = 0
          setTimeout(() => {
            this.isBannerTransitioning = true
          }, 50)
        }, 700)
      }
    },

    goToBannerSlide(index) {
      this.stopBannerSlider()
      this.isBannerTransitioning = true
      this.currentBannerSlide = index
      this.startBannerSlider()
    },

    // ── FORM METHODS ──────────────────────────────────────────
    addProduct() {
      this.form.products.push({
        category: null,
        quantity: null,
        size: null,
        gender: null,
        colors: []
      })
    },

    removeProduct(index) {
      if (this.form.products.length === 1) return
      this.form.products.splice(index, 1)
    },

    toggleCustomType(id) {
      const idx = this.form.customTypes.indexOf(id)
      if (idx === -1) this.form.customTypes.push(id)
      else this.form.customTypes.splice(idx, 1)
    },

    togglePosition(id) {
      const idx = this.form.positions.indexOf(id)
      if (idx === -1) this.form.positions.push(id)
      else this.form.positions.splice(idx, 1)
    },

    handleLogoUpload(e) {
      const file = e.target.files[0]
      if (!file) return
      this.form.logoFile = file
      this.logoPreview = URL.createObjectURL(file)
    },

    removeLogo() {
      this.form.logoFile = null
      this.logoPreview = null
    },

    getCategoryIdByName(categoryName) {
      if (!categoryName) return null

      const match = this.categoryRows.find(
        item => String(item.name).toLowerCase() === String(categoryName).toLowerCase()
      )

      return match ? Number(match.id) : null
    },

    getPrimaryColor(colors) {
      if (Array.isArray(colors)) {
        return colors.length ? colors[0] : null
      }
      return colors || null
    },

    buildAdditionalRequirements() {
      const parts = []

      if (this.form.notes) {
        parts.push(`General Notes: ${this.form.notes}`)
      }

      if (this.form.hasCustomization) {
        const selectedTypes = this.customizationTypes
          .filter(t => this.form.customTypes.includes(t.id))
          .map(t => t.name)

        const selectedPositions = this.positions
          .filter(p => this.form.positions.includes(p.id))
          .map(p => p.name)

        parts.push('Branding Required: Yes')

        if (selectedTypes.length) {
          parts.push(`Customization Types: ${selectedTypes.join(', ')}`)
        }

        if (selectedPositions.length) {
          parts.push(`Customization Positions: ${selectedPositions.join(', ')}`)
        }

        if (this.form.customText) {
          parts.push(`Customization Text: ${this.form.customText}`)
        }

        if (this.form.logoFile?.name) {
          parts.push(`Logo File: ${this.form.logoFile.name}`)
        }

        if (this.form.customNotes) {
          parts.push(`Customization Notes: ${this.form.customNotes}`)
        }
      } else {
        parts.push('Branding Required: No')
      }

      return parts.join(' | ') || null
    },

    validateBeforeSubmit() {
      if (!this.form.orgName?.trim()) {
        alert('Organization name is required')
        return false
      }

      if (!this.form.contactName?.trim()) {
        alert('Contact person name is required')
        return false
      }

      if (!this.form.phone?.trim()) {
        alert('Phone number is required')
        return false
      }

      if (!this.form.state?.trim()) {
        alert('State is required')
        return false
      }

      if (!this.form.city?.trim()) {
        alert('City is required')
        return false
      }

      if (!this.form.address?.trim()) {
        alert('Address is required')
        return false
      }

      if (!this.form.postalCode?.trim()) {
        alert('Postal code is required')
        return false
      }

      if (!this.form.products.length) {
        alert('Add at least one product')
        return false
      }

      for (let i = 0; i < this.form.products.length; i += 1) {
        const product = this.form.products[i]

        if (!product.category) {
          alert(`Please select category for Order ${i + 1}`)
          return false
        }

        if (!product.quantity || Number(product.quantity) <= 0) {
          alert(`Please enter valid quantity for Order ${i + 1}`)
          return false
        }

        if (!product.size) {
          alert(`Please select size for Order ${i + 1}`)
          return false
        }
      }

      return true
    },

    resetForm() {
      this.form = {
        orgName: '',
        contactName: '',
        email: '',
        phone: '',
        gst: '',
        address: '',
        city: '',
        state: '',
        postalCode: '',
        country: 'India',
        fabric: null,
        deliveryDate: '',
        notes: '',
        products: [
          { category: null, quantity: null, size: null, gender: null, colors: [] }
        ],
        hasCustomization: false,
        customTypes: [],
        positions: [],
        customText: '',
        logoFile: null,
        customNotes: ''
      }

      this.logoPreview = null
      this.stateOptions = this.allStates[this.form.country] || []
    },

    async submitForm() {
      try {
        if (!this.validateBeforeSubmit()) return

        this.submitting = true

        const payload = {
          user_id: Number(localStorage.getItem('user_id')) || null,
          organization_name: this.form.orgName?.trim(),
          contact_person: this.form.contactName?.trim(),
          email: this.form.email?.trim() || null,
          phone: this.form.phone?.trim(),
          gst_number: this.form.gst?.trim() || null,
          state: this.form.state?.trim(),
          city: this.form.city?.trim(),
          address: this.form.address?.trim(),
          postal_code: this.form.postalCode?.trim(),
          expected_delivery_date: this.form.deliveryDate || null,
          fabric_preference: this.form.fabric || null,
          additional_requirements: this.buildAdditionalRequirements(),
          branding_required: !!this.form.hasCustomization,
          items: this.form.products.map((p, index) => {
            const categoryId = this.getCategoryIdByName(p.category)

            if (!categoryId) {
              throw new Error(`Category ID not found for Order ${index + 1}: ${p.category}`)
            }

            return {
              product_category_id: Number(categoryId),
              quantity: Number(p.quantity),
              size: p.size,
              gender: p.gender || null,
              color: this.getPrimaryColor(p.colors)
            }
          })
        }

        console.log('BULK ORDER BACKEND PAYLOAD =', payload)

        const response = await submitBulkOrderRequest(payload)

        this.requestNumber = response?.request_number || ''
        this.successDialog = true
        this.resetForm()
      } catch (error) {
        console.error('SUBMIT BULK REQUEST ERROR:', error)
        alert(
          error?.response?.data?.detail ||
          error?.message ||
          'Failed to submit bulk request'
        )
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style lang="scss">
@import 'src/css/bulkorder.scss';
</style>
