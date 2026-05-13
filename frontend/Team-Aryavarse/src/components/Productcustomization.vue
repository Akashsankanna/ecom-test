<template>
  <div class="customization-panel">

    <!-- ── Toggle Header ── -->
    <div class="custom-toggle-header" @click="isExpanded = !isExpanded">
      <div class="toggle-left">
        <span class="custom-icon"><i class="bi bi-layers"></i></span>
        <div>
          <p class="toggle-title">Customize This Product</p>
          <p class="toggle-sub">Embroidery · Logo Print & more</p>
        </div>
      </div>
      <div class="toggle-chevron" :class="{ 'is-open': isExpanded }">
        <q-icon name="keyboard_arrow_down" size="20px" color="teal" />
      </div>
    </div>

    <!-- ── Expandable Body ── -->
    <transition name="slide-down">
      <div v-if="isExpanded" class="custom-body">

        <!-- STEP 1: Customization Type -->
        <div class="custom-section">
          <p class="custom-label">
            Customization Type
            <span class="required-star">*</span>
          </p>
          <div class="custom-type-grid">
            <button
              v-for="type in finalTypes"
              :key="type.id"
              class="type-chip"
              :class="{ 'type-chip--active': selectedTypes.includes(type.id) }"
              @click="toggleType(type.id)"
            >
              <span class="chip-icon">{{ type.icon }}</span>
              <span class="chip-label">{{ type.name }}</span>
              <span v-if="type.price > 0" class="chip-price">+₹{{ type.price }}</span>
            </button>
          </div>

          
        </div>

        <!-- TEXT INPUT: shown only when Embroidery is selected -->
        <transition name="fade">
          <div v-if="requiresText" class="custom-section embroidery-block">

            <!-- Line 1 -->
            <div class="text-field-wrap">
              <p class="custom-label">
                 Name / Title
                <span class="required-star">*</span>
                <span class="char-count">{{ customText.length }}/{{ maxTextLength }}</span>
              </p>
              <q-input
                v-model="customText"
                outlined
                dense
                :maxlength="maxTextLength"
                placeholder="e.g. Dr. Aditi Sharma"
                class="custom-input"
                :error="showValidation && requiresText && !customText.trim()"
                error-message="Line 1 is required"
              />
            </div>

            <!-- Line 2 -->
            <div class="text-field-wrap" style="margin-top: 12px;">
              <p class="custom-label">
                 Department
                <span class="optional">(optional)</span>
                <span class="char-count">{{ customText2.length }}/{{ maxTextLength }}</span>
              </p>
              <q-input
                v-model="customText2"
                outlined
                dense
                :maxlength="maxTextLength"
                placeholder="e.g. MBBS · Department of Surgery"
                class="custom-input"
              />
              <p class="input-hint">ℹ️ Line 2 is optional — leave blank if not needed</p>
            </div>

            <!-- Font Style -->
            <div class="field-group mt-14">
              <label class="field-label">Font Style</label>
              <div class="font-grid">
                <button
                  v-for="f in fontOptions"
                  :key="f.value"
                  class="font-chip"
                  :class="{ 'font-chip--active': selectedFont === f.value }"
                  :style="{ fontFamily: f.css }"
                  @click="selectedFont = f.value"
                >
                  {{ f.label }}
                  <span class="font-preview" :style="{ fontFamily: f.css }">Aa</span>
                </button>
              </div>


            </div>

          </div>
        </transition>

        <!-- LOGO UPLOAD: shown only when Logo Print is selected -->
        <transition name="fade">
          <div v-if="requiresLogo" class="custom-section">
            <div class="custom-logo-upload">
              <p class="upload-sub-label">📁 Upload Your Logo</p>
              <div
                class="upload-zone"
                @click="$refs.logoInput.click()"
                @dragover.prevent
                @drop.prevent="handleDrop"
              >
                <div v-if="!logoFile" class="upload-placeholder">
                  <div class="upload-icon-wrap">
                    <q-icon name="cloud_upload" size="28px" color="teal" />
                  </div>
                  <p class="upload-text">Click or Drag to Upload</p>
                  <p class="upload-hint">PNG · JPG · SVG up to 5 MB</p>
                </div>
                <div v-else class="upload-preview">
                  <img :src="logoPreview" class="logo-preview-img" alt="Logo preview" />
                  <div>
                    <p class="logo-name">{{ logoFile.name }}</p>
                    <button class="remove-logo" @click.stop="removeLogo">✕ Remove</button>
                  </div>
                </div>
                <input
                  ref="logoInput"
                  type="file"
                  accept=".jpg,.jpeg,.png,.svg"
                  style="display:none"
                  @change="handleLogoUpload"
                />
              </div>
              <div class="upload-requirements">
                <p>Minimum resolution: 200 × 200 px</p>
                <p>Maximum file size: 5 MB</p>
                <p>Accepted formats: JPG / JPEG / PNG / SVG</p>
              </div>
              <p v-if="showValidation && requiresLogo && !logoFile" style="color:#e53935; font-size:12px; margin-top:6px; font-weight:600;">
                ⚠️ Please upload your logo to continue
              </p>
            </div>
          </div>
        </transition>

<!-- POSITIONS -->
<transition name="fade">
  <div v-if="selectedTypes.length > 0" class="custom-section">
    
    <p class="custom-label">
      Positions
      <span class="optional">(select multiple)</span>
    </p>

    <div class="mini-position-grid">

<button
  v-for="p in positionOptions"
  :key="p.id"
  type="button"
  class="mini-position-chip"
  :class="{
    'mini-position-chip--active':
    selectedPosition.includes(Number(p.id))
  }"
  @click="togglePosition(Number(p.id))"
>
  <span>{{ p.name }}</span>
</button>

    </div>
  </div>
</transition>


        <!-- SPECIAL INSTRUCTIONS -->
        <transition name="fade">
          <div v-if="selectedTypes.length > 0" class="custom-section">
            <p class="custom-label">
              Special Instructions
              <span class="optional">(optional)</span>
            </p>
            <q-input
  v-model="customNotes"
  outlined
  dense
  type="textarea"
  maxlength="50"
  rows="2"
  counter
  placeholder="Any specific font, color preference, logo size details..."
  class="custom-input notes-input"
/>
          </div>
        </transition>

        <!-- BOTTOM ROW: Reset + Apply (same size) -->
        <div class="bottom-row" v-if="selectedTypes.length > 0">
          <button class="reset-btn" @click="resetAll">↺ Reset</button>
          <button
            class="apply-btn"
            :disabled="showValidation && !isValid"
            @click="applyCustomization"
          >
            Apply Customization
          </button>
        </div>

        <!-- APPROVAL NOTICE -->
        <div class="approval-notice" v-if="selectedTypes.length > 0">
          <q-icon name="info_outline" color="orange-8" size="18px" />
          <p>
            Your customization will be reviewed by our team within <strong>24 hours</strong>.
            You will receive a confirmation before production begins.
          </p>
        </div>

      </div>
    </transition>
  </div>
</template>

<script>
import { api } from 'boot/axios'
export default {
  name: 'ProductCustomization',

  props: {
    productId: {
      type: Number,
      default: null
    },
    customizationTypes: {
      type: Array,
      default: () => []
    }
  },

  emits: ['customization-updated', 'customization-applied'],

  data() {
    return {
      isExpanded:     false,
      showValidation: false,

      // Only Embroidery + Logo Print — override via prop if needed
      customizationTypesData: [
        { id: 1, name: 'Embroidery', icon: '🪡', price: 150, requiresText: true,  requiresLogo: false },
        { id: 2, name: 'Logo Print', icon: '🖨️', price: 100, requiresText: false, requiresLogo: true  },
      ],

      fontOptions: [
        { value: 'arial-narrow', label: 'Classic', css: "'Arial Narrow', Arial, sans-serif"   },
        { value: 'times',        label: 'Serif',   css: "'Times New Roman', Times, serif"      },
        { value: 'courier',      label: 'Mono',    css: "'Courier New', Courier, monospace"    },
        { value: 'palatino',     label: 'Elegant', css: "Palatino, 'Palatino Linotype', serif" },
      ],

      //selectedFont:  'arial-narrow',

selectedPosition: [],

positionOptions: [
],

//logoFile:      null,

      // Form state
      selectedTypes: [],
      customText:    '',
      customText2:   '',
      selectedFont:  'arial-narrow',
      logoFile:      null,
      logoPreview:   null,
      customNotes:   '',
      maxTextLength: 22,
    }
  },

async mounted() {

  await this.getCustomizationTypes()

  await this.getPositions()
},

  computed: {
    finalTypes() {
      return this.customizationTypes.length
        ? this.customizationTypes
        : this.customizationTypesData
    },
    requiresText() {
      return this.selectedTypes.some(id => {
        const t = this.finalTypes.find(c => c.id === id)
        return t && t.requiresText
      })
    },
    requiresLogo() {
      return this.selectedTypes.some(id => {
        const t = this.finalTypes.find(c => c.id === id)
        return t && t.requiresLogo
      })
    },
    isValid() {
      if (!this.selectedTypes.length) return false
      if (this.requiresText && !this.customText.trim()) return false
      if (this.requiresLogo && !this.logoFile) return false
      return true
    },
    customizationPayload() {
      return {
        customization_type_ids: this.selectedTypes,
        text_value:             this.customText  || null,
        text_value_2:           this.customText2 || null,
        font:                   this.selectedFont,
        positions:              this.selectedPosition,
        image_name:             this.logoFile ? this.logoFile.name : null,
        image_file:             this.logoFile  || null,
        notes:                  this.customNotes || null,
        approval_status:        'PENDING',
        has_customization:      this.selectedTypes.length > 0
      }
    }
  },

  watch: {
    customizationPayload: {
      deep: true,
      handler(val) {
        this.$emit('customization-updated', val)
      }
    }
  },

  methods: {

    async getCustomizationTypes() {

  try {

    const res = await api.get(
      '/customization/types'
    )

    if (
      res.data &&
      res.data.length
    ) {

      this.customizationTypesData =
        res.data
    }

  } catch (err) {

    console.error(
      'TYPE FETCH ERROR',
      err
    )
  }
},
async getPositions() {

  try {

    const res = await api.get(
      '/customization/positions'
    )

    console.log(res.data)

    if (
      res.data &&
      res.data.length
    ) {

      this.positionOptions =
        res.data
    }

  } catch (err) {

    console.error(
      'POSITION FETCH ERROR',
      err
    )
  }
},
    toggleType(id) {
      const idx = this.selectedTypes.indexOf(id)
      if (idx === -1) this.selectedTypes.push(id)
      else            this.selectedTypes.splice(idx, 1)
      this.showValidation = false
    },
    getLabelForType(id) {
      const t = this.finalTypes.find(c => c.id === id)
      if (!t) return ''
      if (t.requiresText && t.requiresLogo) return `${t.name}: Text + Logo`
      if (t.requiresText)                   return `${t.name}: Text`
      if (t.requiresLogo)                   return `${t.name}: Logo`
      return t.name
    },
handleLogoUpload(e) {
  const file = e.target.files[0]
  if (!file) return

  // Extension check
  const allowedExtensions = [
  'jpg',
  'jpeg',
  'png',
  'svg'
]

  const extension = file.name
    .split('.')
    .pop()
    .toLowerCase()

  if (!allowedExtensions.includes(extension)) {

    this.logoFile = null
    this.logoPreview = null

    this.$q.notify({
      type: 'negative',
      message: 'Only JPG and SVG files are allowed'
    })

    e.target.value = ''
    return
  }

  // Size check (5MB)
  const maxSize = 5 * 1024 * 1024

  if (file.size >= maxSize) {

    this.logoFile = null
    this.logoPreview = null

    this.$q.notify({
      type: 'negative',
      message: 'File must be smaller than 5MB'
    })

    e.target.value = ''
    return
  }

  // Valid file
  this.logoFile = file
  this.logoPreview = URL.createObjectURL(file)
},

handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (!file) return

  const allowedExtensions = [
  'jpg',
  'jpeg',
  'png',
  'svg'
]

  const extension = file.name
    .split('.')
    .pop()
    .toLowerCase()

  if (!allowedExtensions.includes(extension)) {
    this.$q.notify({
      type: 'negative',
      message: 'Only JPG and SVG files are allowed'
    })
    return
  }

  const maxSize = 5 * 1024 * 1024

if (file.size >= maxSize) {
  this.$q.notify({
    type: 'negative',
    message: 'File must be smaller than 5MB'
  })
  return
}

  this.logoFile = file
  this.logoPreview = URL.createObjectURL(file)
},


    togglePosition(value) {
  const index = this.selectedPosition.indexOf(value)

  if (index === -1) {
    this.selectedPosition.push(value)
  } else {
    this.selectedPosition.splice(index, 1)
  }
},
    removeLogo() {
      this.logoFile    = null
      this.logoPreview = null
    },
async applyCustomization() {

  this.showValidation = true

  if (!this.isValid) return

  try {

    const formData = new FormData()

    // Product ID
formData.append('product_id', 1)

    // Customization Types
formData.append(
  'customization_type_ids',
  JSON.stringify(this.selectedTypes)
)

    // Text Fields
    formData.append(
      'text_value',
      this.customText
    )

    formData.append(
      'text_value_2',
      this.customText2
    )

    // Font
    formData.append(
      'font',
      this.selectedFont
    )

    // Positions
formData.append(
  'positions',
  JSON.stringify(this.selectedPosition)
)

    // Notes
    formData.append(
      'notes',
      this.customNotes
    )

    // Status
    formData.append(
      'approval_status',
      'PENDING'
    )

    // Logo Upload
    if (this.logoFile) {

      formData.append(
        'image_file',
        this.logoFile
      )
    }

    // API CALL
    const res = await api.post(
      '/customization/add',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    console.log(
      'CUSTOMIZATION SAVED:',
      res.data
    )

    this.$q.notify({
      type: 'positive',
      message: 'Customization Applied Successfully'
    })

    // Emit after success
    this.$emit(
      'customization-applied',
      res.data
    )

  } catch (err) {

    console.error(
      'CUSTOMIZATION ERROR:',
      err.response?.data || err
    )

    this.$q.notify({
      type: 'negative',
      message: 'Failed to save customization'
    })
  }
},
    resetAll() {
      this.selectedTypes  = []
      this.customText     = ''
      this.customText2    = ''
      this.selectedFont   = 'arial-narrow'
      this.showValidation = false
      this.customNotes    = ''
      this.removeLogo()
      this.selectedPosition = []
    }
  }
}
</script>

<style scoped lang="scss">
@import 'src/css/customization.scss';
</style>