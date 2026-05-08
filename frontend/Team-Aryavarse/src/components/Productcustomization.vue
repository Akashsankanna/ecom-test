<template>
  <div class="customization-panel">
    <!-- Toggle Header -->
    <div class="custom-toggle-header" @click="isExpanded = !isExpanded">
      <div class="toggle-left">
        <span class="custom-icon">✂️</span>
        <div>
          <p class="toggle-title">Customize This Product</p>
          <p class="toggle-sub">Add embroidery, logo print, name tags & more</p>
        </div>
      </div>
      <q-icon
        :name="isExpanded ? 'expand_less' : 'expand_more'"
        size="24px"
        color="teal"
      />
    </div>
  
    <!-- Expandable Body -->
    <transition name="slide-down">
      <div v-if="isExpanded" class="custom-body">

        <!-- Customization Types (maps: customization_type table) -->
        <div class="custom-section">
          <p class="custom-label">
            Customization Type
            <span class="required-star">*</span>
          </p>
          <div class="custom-type-grid">
            <button
              v-for="type in customizationTypes"
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

        <!-- Text Value (maps: order_item_customization.text_value, max_text_length) -->
        <transition name="fade">
          <div
            v-if="requiresText"
            class="custom-section"
          >
            <p class="custom-label">
              Text to Print / Embroider
              <span class="char-count">{{ customText.length }}/{{ maxTextLength }}</span>
            </p>
            <q-input
              v-model="customText"
              outlined
              dense
              :maxlength="maxTextLength"
              placeholder="e.g. Dr. Sharma, Department of Surgery"
              class="custom-input"
              counter
            />
            <p class="input-hint">Name, designation or department name</p>
          </div>
        </transition>

        <!-- Position (maps: customization_position table) -->
        <transition name="fade">
          <div v-if="selectedTypes.length > 0" class="custom-section">
            <p class="custom-label">Placement Position</p>
            <div class="position-grid">
              <button
                v-for="pos in positions"
                :key="pos.id"
                class="pos-chip"
                :class="{ 'pos-chip--active': selectedPositions.includes(pos.id) }"
                @click="togglePosition(pos.id)"
              >
                <span class="pos-icon">{{ pos.icon }}</span>
                {{ pos.name }}
              </button>
            </div>
          </div>
        </transition>

        <!-- Logo Upload (maps: order_item_customization.image_url, allowed_file_types) -->
        <transition name="fade">
          <div v-if="requiresLogo" class="custom-section">
            <p class="custom-label">Upload Logo / Design File</p>
            <div class="upload-zone" @click="$refs.logoInput.click()" @dragover.prevent @drop.prevent="handleDrop">
              <div v-if="!logoFile" class="upload-placeholder">
                <q-icon name="cloud_upload" size="36px" color="teal" />
                <p class="upload-text">Click or drag & drop your logo here</p>
                <p class="upload-hint">PNG, JPG, SVG up to 5MB</p>
              </div>
              <div v-else class="upload-preview">
                <img :src="logoPreview" class="logo-preview-img" />
                <div class="logo-info">
                  <p class="logo-name">{{ logoFile.name }}</p>
                  <button class="remove-logo" @click.stop="removeLogo">✕ Remove</button>
                </div>
              </div>
              <input
                ref="logoInput"
                type="file"
                accept=".png,.jpg,.jpeg,.svg,.pdf"
                style="display:none"
                @change="handleLogoUpload"
              />
            </div>
          </div>
        </transition>

        <!-- Additional Notes -->
        <div v-if="selectedTypes.length > 0" class="custom-section">
          <p class="custom-label">Special Instructions <span class="optional">(optional)</span></p>
          <q-input
            v-model="customNotes"
            outlined
            dense
            type="textarea"
            rows="2"
            placeholder="Any specific color, font, size for the customization..."
            class="custom-input"
          />
        </div>

        <!-- Price Summary -->
        <div v-if="totalCustomizationPrice > 0" class="price-summary">
          <div class="price-row-inner">
            <span>Customization Charges</span>
            <span class="price-val">+₹{{ totalCustomizationPrice.toLocaleString('en-IN') }}</span>
          </div>
          <p class="price-note">
            ⏱ Customized items take 3–5 extra business days
          </p>
        </div>

        <!-- Approval Notice (maps: order_item_customization.approval_status = PENDING) -->
        <div class="approval-notice">
          <q-icon name="info" color="teal" size="18px" />
          <p>
            Your customization will be reviewed and approved within 24 hours.
            You'll receive a confirmation before production begins.
          </p>
        </div>

      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'ProductCustomization',

  props: {
    productId: {
      type: Number,
      default: null
    }
  },

  emits: ['customization-updated'],

  data() {
    return {
      isExpanded: false,

      // Maps customization_type table (id, name, is_active)
      customizationTypes: [
        { id: 1, name: 'Embroidery',      icon: '🪡', price: 150, requiresText: true,  requiresLogo: false },
        { id: 2, name: 'Logo Print',       icon: '🖨️', price: 100, requiresText: false, requiresLogo: true  },
        { id: 3, name: 'Name Tag',         icon: '🏷️', price: 80,  requiresText: true,  requiresLogo: false },
        { id: 4, name: 'Department Print', icon: '🏥', price: 120, requiresText: true,  requiresLogo: false },
        { id: 5, name: 'Custom Patch',     icon: '🎖️', price: 200, requiresText: false, requiresLogo: true  },
      ],

      // Maps customization_position table (id, name)
      positions: [
        { id: 1, name: 'Left Chest',  icon: '◀' },
        { id: 2, name: 'Right Chest', icon: '▶' },
        { id: 3, name: 'Back',        icon: '⬛' },
        { id: 4, name: 'Sleeve',      icon: '🔷' },
        { id: 5, name: 'Collar',      icon: '🔼' },
      ],

      // Form state — maps order_item_customization columns
      selectedTypes:     [],   // customization_type_id (multiple)
      selectedPositions: [],   // position_id (multiple)
      customText:        '',   // text_value
      logoFile:          null, // image_url (after upload)
      logoPreview:       null,
      customNotes:       '',   // stored in order notes

      maxTextLength: 50,       // maps product_customization.max_text_length
    }
  },

  computed: {
    requiresText() {
      return this.selectedTypes.some(id => {
        const t = this.customizationTypes.find(c => c.id === id)
        return t && t.requiresText
      })
    },
    requiresLogo() {
      return this.selectedTypes.some(id => {
        const t = this.customizationTypes.find(c => c.id === id)
        return t && t.requiresLogo
      })
    },
    totalCustomizationPrice() {
      return this.selectedTypes.reduce((sum, id) => {
        const t = this.customizationTypes.find(c => c.id === id)
        return sum + (t ? t.price : 0)
      }, 0)
    },
    // Emittable payload matching order_item_customization columns
    customizationPayload() {
      return {
        customization_type_ids: this.selectedTypes,
        position_ids:           this.selectedPositions,
        text_value:             this.customText || null,
        image_name:             this.logoFile ? this.logoFile.name : null,
        image_file:             this.logoFile || null,
        notes:                  this.customNotes || null,
        approval_status:        'PENDING',
        extra_price:            this.totalCustomizationPrice,
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
    toggleType(id) {
      const idx = this.selectedTypes.indexOf(id)
      if (idx === -1) {
        this.selectedTypes.push(id)
      } else {
        this.selectedTypes.splice(idx, 1)
      }
    },

    togglePosition(id) {
      const idx = this.selectedPositions.indexOf(id)
      if (idx === -1) {
        this.selectedPositions.push(id)
      } else {
        this.selectedPositions.splice(idx, 1)
      }
    },

    handleLogoUpload(e) {
      const file = e.target.files[0]
      if (!file) return
      this.logoFile = file
      this.logoPreview = URL.createObjectURL(file)
    },

    handleDrop(e) {
      const file = e.dataTransfer.files[0]
      if (!file) return
      this.logoFile = file
      this.logoPreview = URL.createObjectURL(file)
    },

    removeLogo() {
      this.logoFile = null
      this.logoPreview = null
    }
  }
}
</script>

<style scoped lang="scss">
@import 'src/css/customization.scss';
</style>