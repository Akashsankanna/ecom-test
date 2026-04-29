<template>
  <q-page class="admin-page">

    <!-- ── Header ── -->
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="page-title">Product &amp; Catalogue Management</div>
          <div class="page-subtitle">Manage products, variants, categories &amp; colors</div>
        </div>
        <q-btn
          v-if="activeTab === 'products'" label="Add Product" color="blue-6"
          unelevated no-caps icon="add" class="action-btn" @click="openProductModal(null)"
        />
        <q-btn
          v-else-if="activeTab === 'variants'" label="Add Variant" color="teal-6"
          unelevated no-caps icon="add" class="action-btn" @click="openVariantModal(null, null)"
        />
        <q-btn
          v-else-if="activeTab === 'categories'" label="Add Category" color="purple-6"
          unelevated no-caps icon="add" class="action-btn" @click="openCatModal(null)"
        />
        <q-btn
          v-else-if="activeTab === 'colors'" label="Add Color" color="pink-6"
          unelevated no-caps icon="add" class="action-btn" @click="openColorModal(null)"
        />
      </div>
    </div>

    <!-- ── Tabs ── -->
    <div class="q-px-lg q-pt-sm">
      <q-tabs
        v-model="activeTab" dense align="left"
        active-color="blue-7" indicator-color="blue-6"
        class="product-tabs"
        @update:model-value="onTabChange"
      >
        <q-tab name="products"    icon="inventory_2"  label="Products"    no-caps />
        <q-tab name="variants"    icon="category"     label="Variants"    no-caps />
        <q-tab name="categories"  icon="folder"       label="Categories"  no-caps />
        <q-tab name="colors"      icon="palette"      label="Colors"      no-caps />
      </q-tabs>
      <q-separator color="blue-2" />
    </div>

    <!-- ── Tab Panels ── -->
    <div class="q-px-lg q-pb-xl q-pt-md">
      <q-tab-panels v-model="activeTab" animated keep-alive style="background:transparent">

        <!-- ══════════════ TAB: PRODUCTS ══════════════ -->
        <q-tab-panel name="products" class="q-pa-none">
          <div class="row q-gutter-sm q-mb-md items-center">
            <div class="col">
              <q-input
                v-model="search" placeholder="Search by name, SKU…" dense outlined
                clearable bg-color="white" @update:model-value="onSearchChange"
              >
                <template #prepend><q-icon name="search" color="blue-4" /></template>
              </q-input>
            </div>
            <div class="col-auto">
              <q-select
                v-model="catFilter"
                :options="[{ label: 'All Categories', value: null }, ...categories.map(c=>({ label: c.name, value: c.id }))]"
                option-value="value" option-label="label" emit-value map-options
                label="Category" dense outlined bg-color="white" style="min-width:160px"
                @update:model-value="fetchProducts"
              />
            </div>
            <div class="col-auto">
              <q-btn-toggle
                v-model="activeFilter"
                :options="[
                  { label:'All',      value:'all'      },
                  { label:'Active',   value:'active'   },
                  { label:'Inactive', value:'inactive' }
                ]"
                toggle-color="blue-6" color="white" text-color="grey-7"
                dense no-caps unelevated
                style="border:1px solid #dbeafe;border-radius:10px"
                @update:model-value="fetchProducts"
              />
            </div>
            <div class="col-auto">
              <q-btn
                label="Low Stock" flat no-caps dense icon="warning"
                color="amber-8" @click="fetchLowStock"
                style="border:1px solid #fef3c7;border-radius:10px;background:#fffbeb"
              />
            </div>
          </div>

          <q-card class="tbl-card" flat bordered>
            <q-table
              :rows="products" :columns="productColumns" row-key="id"
              flat :rows-per-page-options="[10,25,50]"
              class="product-table" wrap-cells :loading="loadingProducts"
            >
              <template #body="props">
                <!-- Product Row -->
                <q-tr :props="props" class="product-row" @click="toggleExpand(props.row.id)">

                  <!-- Expand -->
                  <q-td auto-width>
                    <q-btn
                      round flat dense size="xs"
                      :icon="expanded.includes(props.row.id) ? 'expand_less' : 'expand_more'"
                      color="blue-4" @click.stop="toggleExpand(props.row.id)"
                    />
                  </q-td>

                  <!-- Images -->
                  <q-td style="width:130px">
                    <div class="row items-center q-gutter-xs no-wrap">
                      <template v-if="props.row.images && props.row.images.length">
                        <div
                          v-for="(img,i) in props.row.images.slice(0,2)" :key="i"
                          class="tbl-thumb" @click.stop="previewImage(img.image_url)"
                        >
                          <img :src="img.image_url" class="tbl-thumb-img" />
                          <q-badge
                            v-if="img.is_primary" color="blue-6" floating
                            style="font-size:8px;padding:1px 4px"
                          >★</q-badge>
                        </div>
                        <div v-if="props.row.images.length > 2" class="tbl-thumb-more">
                          +{{ props.row.images.length - 2 }}
                        </div>
                      </template>
                      <div v-else class="tbl-thumb-empty">
                        <q-icon name="image" color="grey-5" size="16px" />
                      </div>
                    </div>
                  </q-td>

                  <!-- Name -->
                  <q-td>
                    <div class="prod-name">{{ props.row.name }}</div>
                    <div class="prod-desc">{{ props.row.description?.slice(0,50) }}</div>
                    <div class="prod-slug">{{ props.row.slug }}</div>
                  </q-td>

                  <!-- SKU -->
                  <q-td><code class="sku-pill">{{ props.row.sku }}</code></q-td>

                  <!-- Category -->
                  <q-td>
                    <q-chip dense size="sm" color="blue-1" text-color="blue-8" style="font-weight:600">
                      {{ getCatName(props.row.category_id) }}
                    </q-chip>
                  </q-td>

                  <!--
                    ══════════════════════════════════════════
                    BUG FIX #2 — TAX DISPLAY
                    ══════════════════════════════════════════
                    Before: getTaxName(props.row.tax_rate_id) only worked after
                    taxRates was loaded (which only happened on modal open).

                    Fix: taxRates is now fetched in onMounted so the lookup
                    is always populated when the table renders. getTaxName()
                    itself is also hardened (see script section).
                  -->
                  <q-td>
                    <span v-if="props.row.tax_rate_id" class="tax-label">
                      {{ getTaxName(props.row.tax_rate_id) }}
                    </span>
                    <span v-else class="text-grey-4 text-caption">—</span>
                  </q-td>

                  <!-- Bestseller -->
                  <q-td @click.stop class="text-center">
                    <q-toggle
                      :model-value="props.row.is_bestseller"
                      color="blue-6"
                      dense
                      @update:model-value="toggleBestseller(props.row)"
                    >
                      <q-tooltip>Toggle Bestseller</q-tooltip>
                    </q-toggle>
                  </q-td>

                  <!-- Status -->
                  <q-td>
                    <q-chip
                      dense size="sm" :label="props.row.is_active ? 'Active' : 'Inactive'"
                      :color="props.row.is_active ? 'positive' : 'red-2'"
                      :text-color="props.row.is_active ? 'white' : 'red-8'"
                      style="font-weight:700"
                    />
                  </q-td>

                  <!-- Actions -->
                  <q-td @click.stop>
                    <div class="row q-gutter-xs no-wrap items-center">
                      <q-btn round flat size="xs" icon="edit" color="blue-5" @click="openProductModal(props.row)">
                        <q-tooltip>Edit Product</q-tooltip>
                      </q-btn>
                      <q-btn round flat size="xs" icon="add_circle" color="teal-5" @click="openVariantModal(props.row.id, null)">
                        <q-tooltip>Add Variant</q-tooltip>
                      </q-btn>
                      <q-btn round flat size="xs" icon="add_photo_alternate" color="indigo-5" @click="openImageModal(props.row.id)">
                        <q-tooltip>Manage Images</q-tooltip>
                      </q-btn>
                      <q-btn round flat size="xs" icon="delete" color="red-5" @click="confirmDeleteProduct(props.row)">
                        <q-tooltip>Delete</q-tooltip>
                      </q-btn>
                    </div>
                  </q-td>
                </q-tr>

                <!-- ── Expanded Variants ── -->
                <q-tr v-if="expanded.includes(props.row.id)" :props="props" class="expand-row">
                  <q-td colspan="100%" class="expand-td">
                    <div class="expand-inner">
                      <div class="row items-center justify-between q-mb-sm">
                        <span class="var-section-label">
                          <q-icon name="category" size="13px" class="q-mr-xs" />Variants
                        </span>
                        <q-btn
                          label="Add Variant" flat dense no-caps size="xs"
                          color="teal-6" icon="add"
                          @click="openVariantModal(props.row.id, null)"
                        />
                      </div>

                      <div v-if="loadingVariants[props.row.id]" class="text-center q-py-md">
                        <q-spinner color="teal-5" size="24px" />
                      </div>

                      <template v-else-if="getVariants(props.row.id).length">
                        <div class="var-grid-header">
                          <span>Variant</span><span>Price</span><span>Stock</span>
                          <span>Reserved</span><span>Color</span><span>Size</span>
                          <span>SKU</span><span>Actions</span>
                        </div>
                        <div
                          v-for="v in getVariants(props.row.id)" :key="v.id"
                          class="var-grid-row"
                        >
                          <span>
                            <q-chip size="sm" color="indigo-1" text-color="indigo-8" dense>
                              {{ v.variant_name }}
                            </q-chip>
                          </span>
                          <span class="price-text">₹{{ Number(v.price).toLocaleString() }}</span>
                          <span>
                            <q-chip
                              dense size="sm" text-color="white"
                              :color="v.stock > (v.low_stock_threshold||5) ? 'positive' : v.stock > 0 ? 'orange-6' : 'negative'"
                            >{{ v.stock }}</q-chip>
                          </span>
                          <span class="text-caption text-grey-6">{{ v.reserved_stock ?? 0 }}</span>
                          <span>
                            <div v-if="v.color_id || v.color" class="row items-center q-gutter-xs">
                              <div
                                class="color-dot"
                                :style="{ background: getColorHex(v.color_id) || v.color }"
                              />
                              <span class="text-caption text-grey-7">{{ v.color }}</span>
                            </div>
                            <span v-else class="text-grey-4 text-caption">—</span>
                          </span>
                          <span>
                            <q-badge v-if="v.size" color="blue-1" text-color="blue-8">{{ v.size }}</q-badge>
                            <span v-else class="text-grey-4 text-caption">—</span>
                          </span>
                          <span class="text-caption text-blue-5 mono">{{ v.sku || '—' }}</span>
                          <span class="row q-gutter-xs">
                            <q-btn round flat size="xs" icon="edit" color="blue-5" @click="openVariantModal(props.row.id, v)" />
                            <q-btn round flat size="xs" icon="delete" color="red-5" @click="confirmDeleteVariant(v)" />
                          </span>
                        </div>
                      </template>

                      <div v-else class="text-caption text-grey-5 text-center q-py-md">
                        No variants yet — click "Add Variant"
                      </div>
                    </div>
                  </q-td>
                </q-tr>
              </template>

              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-grey-5">
                  <q-icon name="inventory_2" size="48px" class="q-mb-sm" />
                  <div>No products found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ══════════════ TAB: VARIANTS ══════════════ -->
        <q-tab-panel name="variants" class="q-pa-none">
          <div class="row q-gutter-sm q-mb-md items-center">
            <div class="col">
              <q-input v-model="varSearch" placeholder="Search variant, product, size…" dense outlined clearable bg-color="white">
                <template #prepend><q-icon name="search" color="blue-4" /></template>
              </q-input>
            </div>
            <div class="col-auto">
              <q-select
                v-model="varProductFilter"
                :options="[{ label:'All Products', value: null }, ...products.map(p=>({ label: p.name, value: p.id }))]"
                option-value="value" option-label="label" emit-value map-options
                label="Filter by Product" dense outlined bg-color="white" style="min-width:200px"
              />
            </div>
          </div>
          <q-card class="tbl-card" flat bordered>
            <q-table
              :rows="filteredVariantsAll" :columns="variantColumns" row-key="id"
              flat :rows-per-page-options="[10,25]" class="product-table"
              wrap-cells :loading="loadingAllVariants"
            >
              <template #body-cell-product_name="props">
                <q-td :props="props"><span class="prod-name">{{ props.value }}</span></q-td>
              </template>
              <template #body-cell-variant_name="props">
                <q-td :props="props">
                  <q-chip size="sm" color="indigo-1" text-color="indigo-8" dense>{{ props.value }}</q-chip>
                </q-td>
              </template>
              <template #body-cell-size="props">
                <q-td :props="props">
                  <q-badge v-if="props.value" color="blue-1" text-color="blue-8">{{ props.value }}</q-badge>
                  <span v-else class="text-grey-4">—</span>
                </q-td>
              </template>
              <template #body-cell-color="props">
                <q-td :props="props">
                  <div v-if="props.row.color" class="row items-center q-gutter-xs">
                    <div class="color-dot" :style="{ background: getColorHex(props.row.color_id) || props.row.color }" />
                    <span class="text-caption">{{ props.row.color }}</span>
                  </div>
                  <span v-else class="text-grey-4">—</span>
                </q-td>
              </template>
              <template #body-cell-price="props">
                <q-td :props="props"><span class="price-text">₹{{ Number(props.value).toLocaleString() }}</span></q-td>
              </template>
              <template #body-cell-stock="props">
                <q-td :props="props">
                  <q-chip
                    dense size="sm" text-color="white"
                    :color="props.value > 10 ? 'positive' : props.value > 0 ? 'orange-6' : 'negative'"
                  >{{ props.value }} units</q-chip>
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props">
                  <div class="row q-gutter-xs">
                    <q-btn round flat size="xs" icon="edit" color="blue-5" @click="openVariantModal(props.row.product_id, props.row)" />
                    <q-btn round flat size="xs" icon="delete" color="red-5" @click="confirmDeleteVariant(props.row)" />
                  </div>
                </q-td>
              </template>
              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-grey-5">
                  <q-icon name="category" size="48px" class="q-mb-sm" /><div>No variants found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ══════════════ TAB: CATEGORIES ══════════════ -->
        <q-tab-panel name="categories" class="q-pa-none">
          <div class="row q-mb-md">
            <div class="col-12 col-sm-5">
              <q-input v-model="catSearch" placeholder="Search category…" dense outlined clearable bg-color="white">
                <template #prepend><q-icon name="search" color="blue-4" /></template>
              </q-input>
            </div>
          </div>
          <q-card class="tbl-card" flat bordered>
            <q-table
              :rows="filteredCategories" :columns="categoryColumns" row-key="id"
              flat :rows-per-page-options="[10,25]" class="product-table"
              wrap-cells :loading="loadingCategories"
            >
              <template #body-cell-id="props">
                <q-td :props="props"><code class="id-pill">#{{ props.value }}</code></q-td>
              </template>
              <template #body-cell-name="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <div class="cat-icon"><q-icon name="folder" color="purple-5" size="15px" /></div>
                    <span class="prod-name">{{ props.value }}</span>
                  </div>
                </q-td>
              </template>
              <template #body-cell-is_active="props">
                <q-td :props="props">
                  <q-chip dense size="sm" :color="props.value ? 'positive' : 'red-2'" :text-color="props.value ? 'white' : 'red-8'" style="font-weight:700">
                    {{ props.value ? 'Active' : 'Inactive' }}
                  </q-chip>
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props">
                  <div class="row q-gutter-xs">
                    <q-btn round flat size="xs" icon="edit" color="purple-5" @click="openCatModal(props.row)" />
                    <q-btn round flat size="xs" icon="delete" color="red-5" @click="confirmDeleteCat(props.row)" />
                  </div>
                </q-td>
              </template>
              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-grey-5">
                  <q-icon name="folder_open" size="48px" class="q-mb-sm" /><div>No categories found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ══════════════ TAB: COLORS ══════════════ -->
        <q-tab-panel name="colors" class="q-pa-none">
          <div class="row q-mb-md">
            <div class="col-12 col-sm-5">
              <q-input v-model="colorSearch" placeholder="Search color name or hex…" dense outlined clearable bg-color="white">
                <template #prepend><q-icon name="search" color="blue-4" /></template>
              </q-input>
            </div>
          </div>
          <q-card class="tbl-card" flat bordered>
            <q-table
              :rows="filteredColors" :columns="colorColumns" row-key="id"
              flat :rows-per-page-options="[10,25,50]" class="product-table"
              wrap-cells :loading="loadingColors"
            >
              <template #body-cell-id="props">
                <q-td :props="props"><code class="id-pill">#{{ props.value }}</code></q-td>
              </template>
              <template #body-cell-hex_code="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <div class="color-swatch-preview" :style="{ background: props.value }" />
                    <code class="hex-pill">{{ props.value }}</code>
                  </div>
                </q-td>
              </template>
              <template #body-cell-name="props">
                <q-td :props="props"><span class="prod-name">{{ props.value }}</span></q-td>
              </template>
              <template #body-cell-is_active="props">
                <q-td :props="props">
                  <q-chip dense size="sm" :color="props.value ? 'positive' : 'red-2'" :text-color="props.value ? 'white' : 'red-8'" style="font-weight:700">
                    {{ props.value ? 'Active' : 'Inactive' }}
                  </q-chip>
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props">
                  <div class="row q-gutter-xs">
                    <q-btn round flat size="xs" icon="edit" color="pink-5" @click="openColorModal(props.row)" />
                    <q-btn round flat size="xs" icon="delete" color="red-5" @click="confirmDeleteColor(props.row)" />
                  </div>
                </q-td>
              </template>
              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-grey-5">
                  <q-icon name="palette" size="48px" class="q-mb-sm" /><div>No colors found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- ══════════════════════════════════════════════════
         PRODUCT MODAL
    ══════════════════════════════════════════════════ -->
    <q-dialog v-model="productModal" persistent maximized transition-show="slide-up" transition-hide="slide-down">
      <q-card class="dialog-fullcard">
        <q-card-section class="dialog-header row items-center">
          <div>
            <div class="dialog-title">{{ editingProduct ? 'Edit Product' : 'Add New Product' }}</div>
            <div class="dialog-subtitle">{{ editingProduct ? 'Update product details below' : 'Fill in the details to create a new product' }}</div>
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-6" />
        </q-card-section>

        <q-separator />

        <q-card-section class="dialog-body">
          <div class="row q-col-gutter-lg">

            <!-- LEFT: Form fields -->
            <div class="col-12 col-md-7">
              <div class="form-section-title">Basic Information</div>
<div class="row q-col-gutter-md">

  <div class="col-12">
    <q-input
      v-model="pForm.name"
      label="Product Name *"
      outlined dense
      input-class="full-input"
      :rules="[v=>!!v||'Required']"
    />
  </div>

  <div class="col-6">
    <q-input
      v-model="pForm.sku"
      label="SKU *"
      outlined dense
      input-class="full-input"
    />
  </div>

  <div class="col-6">
    <q-select
      v-model="pForm.category_id"
      :options="categories"
      option-value="id"
      option-label="name"
      emit-value map-options
      label="Category"
      outlined dense clearable
      popup-content-class="select-popup"
    />
  </div>

  <!-- ✅ ADDED THIS (Gender / Section) -->
  <div class="col-6">
    <q-select
      v-model="pForm.gender"
      :options="[
        { label: 'Men', value: 'men' },
        { label: 'Women', value: 'women' },
        { label: 'Unisex / Homepage', value: 'all' }
      ]"
      option-value="value"
      option-label="label"
      emit-value
      map-options
      label="Section (Gender) *"
      outlined dense
    />
  </div>

  <div class="col-12">
    <q-input
      v-model="pForm.description"
      label="Description"
      outlined dense
      type="textarea"
      rows="2"
      input-class="full-input"
    />
  </div>

</div>
              </div>

              <div class="form-section-title q-mt-lg">Additional Details</div>
              <div class="row q-col-gutter-md">
                <div class="col-12">
                  <q-input
                    v-model="pForm.details_and_fit"
                    label="Details &amp; Fit"
                    outlined dense
                    type="textarea" rows="2"
                    input-class="full-input"
                    placeholder="e.g. Relaxed fit, round neck, drop shoulders"
                  />
                </div>
                <div class="col-12">
                  <q-input
                    v-model="pForm.fabric_and_care"
                    label="Fabric &amp; Care"
                    outlined dense
                    type="textarea" rows="2"
                    input-class="full-input"
                    placeholder="e.g. 100% Cotton, machine wash cold"
                  />
                </div>
                <div class="col-12">
                  <q-input
                    v-model="pForm.return_and_exchange"
                    label="Return &amp; Exchange Policy"
                    outlined dense
                    type="textarea" rows="2"
                    input-class="full-input"
                    placeholder="e.g. 7-day return available"
                  />
                </div>
                <div class="col-6">
                  <!--
                    ══════════════════════════════════════════
                    BUG FIX #2 — TAX RATE SELECT DISPLAY
                    ══════════════════════════════════════════
                    taxRates is now pre-loaded in onMounted so this
                    select always has options. The #selected-item slot
                    ensures the chosen name is always visible in the field.
                  -->
                  <q-select
                    v-model="pForm.tax_rate_id"
                    :options="taxRates"
                    option-value="id"
                    option-label="name"
                    emit-value map-options
                    label="Tax Rate"
                    outlined dense clearable
                    popup-content-class="select-popup"
                    :loading="loadingTaxRates"
                    :hint="!loadingTaxRates && taxRates.length === 0 ? 'No tax rates found' : ''"
                  >
                    <template #selected-item="scope">
                      <span class="select-selected-text">{{ scope.opt.name }}</span>
                    </template>
                    <template #prepend>
                      <q-icon name="receipt_long" color="blue-3" size="18px" />
                    </template>
                  </q-select>
                </div>
                <div class="col-6 column justify-center">
                  <div class="row items-center q-gutter-md q-pt-sm">
                    <q-toggle v-model="pForm.is_active" label="Active" color="blue-6" dense />
                    <q-toggle v-model="pForm.is_bestseller" label="Bestseller" color="blue-6" dense />
                  </div>
                </div>
              </div>
            </div>

            <!-- RIGHT: Images -->
            <div class="col-12 col-md-5">
              <div class="img-panel">
                <div class="form-section-title q-mb-sm">Product Images</div>

                <div v-if="!editingProduct" class="new-product-img-info">
                  <q-icon name="info_outline" size="16px" color="blue-5" />
                  <span>Create the product first, then add images using the image button in the table.</span>
                </div>

                <template v-if="editingProduct">
                  <div v-if="editingProduct.images && editingProduct.images.length" class="q-mb-md">
                    <div class="img-gallery">
                      <div
                        v-for="img in editingProduct.images" :key="img.id"
                        class="img-thumb-wrap"
                        :class="{ 'is-primary': img.is_primary }"
                        @click="previewImage(img.image_url)"
                      >
                        <img :src="img.image_url" class="img-thumb" />
                        <div v-if="img.is_primary" class="primary-badge">Primary</div>
                        <button class="img-remove-btn" @click.stop="deleteProductImage(img.id)">
                          <q-icon name="close" size="10px" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div v-else class="img-empty-state q-mb-md">
                    <q-icon name="image_not_supported" size="32px" color="grey-4" />
                    <div class="text-caption text-grey-5 q-mt-xs">No images yet</div>
                  </div>

                  <q-separator class="q-mb-md" />
                  <div class="form-section-title q-mb-sm" style="font-size:11px">Add New Image</div>

                  <div
                    class="img-drop-zone q-mb-sm"
                    :class="{ 'drop-active': isDraggingOverProduct }"
                    @dragover.prevent="isDraggingOverProduct = true"
                    @dragleave.prevent="isDraggingOverProduct = false"
                    @drop.prevent="onProductImageDrop"
                  >
                    <q-icon name="add_photo_alternate" size="28px" color="blue-4" />
                    <div class="text-caption text-grey-6 q-mt-xs">Drag &amp; drop image URL here</div>
                    <div class="text-caption text-grey-4" style="font-size:10px">or fill the fields below</div>
                  </div>

                  <div class="column q-gutter-sm">
                    <q-input v-model="newImageUrl" label="Image URL *" outlined dense input-class="full-input" placeholder="https://example.com/image.jpg" />
                    <q-input v-model="newImageName" label="Image Name (optional)" outlined dense input-class="full-input" />
                    <div class="row items-center justify-between">
                      <q-toggle v-model="newImagePrimary" label="Set as Primary" color="blue-6" dense />
                      <q-btn
                        label="Add Image" color="blue-6" unelevated no-caps dense
                        icon="add_photo_alternate" @click="addProductImage" :loading="savingImage"
                        style="border-radius:10px"
                      />
                    </div>
                  </div>
                </template>
              </div>
            </div>
          
        </q-card-section>

        <q-separator />
        <q-card-actions align="right" class="dialog-footer">
          <q-btn label="Cancel" flat no-caps v-close-popup color="grey-6" style="min-width:90px" />
          <q-btn
            :label="editingProduct ? 'Update Product' : 'Create Product'"
            color="blue-6" unelevated no-caps icon="check"
            @click="saveProduct" :loading="savingProduct"
            style="min-width:160px;border-radius:12px"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════
         IMAGE MODAL
    ══════════════════════════════════════════════════ -->
    <q-dialog v-model="imageModal" persistent>
      <q-card class="modal-card" style="width:520px;max-width:96vw">
        <q-card-section class="modal-header row items-center">
          <div>
            <div class="modal-title">Manage Images</div>
            <div class="modal-subtitle" v-if="imageModalProduct">{{ imageModalProduct.name }}</div>
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-6" />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-lg">
          <div class="form-section-title q-mb-sm">Current Images</div>
          <div v-if="imageModalProduct?.images?.length" class="img-gallery q-mb-md">
            <div
              v-for="img in imageModalProduct.images" :key="img.id"
              class="img-thumb-wrap" :class="{ 'is-primary': img.is_primary }"
              @click="previewImage(img.image_url)"
            >
              <img :src="img.image_url" class="img-thumb" />
              <div v-if="img.is_primary" class="primary-badge">Primary</div>
              <button class="img-remove-btn" @click.stop="deleteProductImageFromModal(img.id)">
                <q-icon name="close" size="10px" />
              </button>
            </div>
          </div>
          <div v-else class="img-empty-state q-mb-md">
            <q-icon name="image_not_supported" size="32px" color="grey-4" />
            <div class="text-caption text-grey-5 q-mt-xs">No images yet</div>
          </div>
          <q-separator class="q-mb-md" />
          <div class="form-section-title q-mb-sm">Add New Image</div>
          <div
            class="img-drop-zone q-mb-sm"
            :class="{ 'drop-active': isDraggingOverModal }"
            @dragover.prevent="isDraggingOverModal = true"
            @dragleave.prevent="isDraggingOverModal = false"
            @drop.prevent="onModalImageDrop"
          >
            <q-icon name="add_photo_alternate" size="28px" color="blue-4" />
            <div class="text-caption text-grey-6 q-mt-xs">Drag &amp; drop image URL here</div>
            <div class="text-caption text-grey-4" style="font-size:10px">or fill the fields below</div>
          </div>
          <div class="column q-gutter-sm">
            <q-input v-model="newImageUrl" label="Image URL *" outlined dense input-class="full-input" placeholder="https://example.com/image.jpg" />
            <q-input v-model="newImageName" label="Image Name (optional)" outlined dense input-class="full-input" />
            <div class="row items-center justify-between">
              <q-toggle v-model="newImagePrimary" label="Set as Primary" color="blue-6" dense />
              <q-btn
                label="Add Image" color="blue-6" unelevated no-caps dense
                icon="add_photo_alternate" @click="addProductImageFromModal" :loading="savingImage"
                style="border-radius:10px"
              />
            </div>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn label="Done" color="blue-6" unelevated no-caps v-close-popup style="min-width:80px;border-radius:10px" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════
         VARIANT MODAL
    ══════════════════════════════════════════════════ -->
    <q-dialog v-model="variantModal" persistent>
      <q-card class="modal-card" style="width:680px;max-width:96vw">
        <q-card-section class="modal-header row items-center">
          <div>
            <div class="modal-title">{{ editingVariant ? 'Edit Variant' : 'Add Variant' }}</div>
            <div class="modal-subtitle">{{ getProductName(currentProductId) }}</div>
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-6" />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-lg">
          <div class="row q-col-gutter-md">
            <div class="col-12" v-if="!currentProductId || variantTabMode">
              <q-select
                v-model="vForm.product_id"
                :options="products" option-value="id" option-label="name"
                emit-value map-options label="Product *" outlined dense
                popup-content-class="select-popup"
              />
            </div>
            <div class="col-12" v-else>
              <q-input :model-value="getProductName(currentProductId)" label="Product" outlined dense readonly input-class="full-input" />
            </div>
            <div class="col-12">
              <q-input v-model="vForm.variant_name" label="Variant Name *" outlined dense input-class="full-input" placeholder="e.g. Black XL" />
            </div>
            <div class="col-6">
              <q-input v-model.number="vForm.price" label="Price (₹) *" type="number" outlined dense prefix="₹" input-class="full-input" />
            </div>
            <div class="col-6">
              <q-input v-model.number="vForm.stock" label="Stock *" type="number" outlined dense input-class="full-input" />
            </div>
            <div class="col-6">
              <q-input v-model.number="vForm.low_stock_threshold" label="Low Stock Threshold" type="number" outlined dense input-class="full-input" />
            </div>
            <div class="col-6">
              <q-input v-model="vForm.size" label="Size" outlined dense input-class="full-input" placeholder="S, M, L, XL, 2XL…" />
            </div>
            <div class="col-6">
              <q-select
                v-model="vForm.color_id"
                :options="colors" option-value="id" option-label="name"
                emit-value map-options label="Color" outlined dense clearable
                popup-content-class="select-popup"
                @update:model-value="onColorSelect"
              />
            </div>
            <div class="col-6">
              <q-input v-model="vForm.color" label="Color Name" outlined dense input-class="full-input" placeholder="e.g. Black" />
            </div>
            <div class="col-12">
              <q-input v-model="vForm.sku" label="Variant SKU" outlined dense input-class="full-input" placeholder="e.g. TSHIRT001-BLK-XL" />
            </div>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="grey-6" style="min-width:90px" />
          <q-btn
            :label="editingVariant ? 'Update Variant' : 'Add Variant'"
            color="teal-6" unelevated no-caps icon="check"
            @click="saveVariant" :loading="savingVariant"
            style="min-width:150px;border-radius:12px"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════
         CATEGORY MODAL
    ══════════════════════════════════════════════════ -->
    <q-dialog v-model="catModal" persistent>
      <q-card class="modal-card" style="width:440px;max-width:96vw">
        <q-card-section class="modal-header row items-center">
          <div class="modal-title">{{ editingCat ? 'Edit Category' : 'Add Category' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-6" />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-lg">
          <div class="column q-gutter-md">
            <q-input v-model="catForm.name" label="Category Name *" outlined dense autofocus input-class="full-input" :rules="[v=>!!v||'Required']" />
            <q-input v-model="catForm.description" label="Description" outlined dense type="textarea" rows="2" input-class="full-input" />
            <q-toggle v-model="catForm.is_active" label="Active" color="blue-6" dense />
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="grey-6" />
          <q-btn
            :label="editingCat ? 'Update' : 'Create'"
            color="purple-6" unelevated no-caps icon="check"
            @click="saveCat" :loading="savingCat" :disable="!catForm.name?.trim()"
            style="min-width:120px;border-radius:12px"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════
         COLOR MODAL
    ══════════════════════════════════════════════════ -->
    <q-dialog v-model="colorModal" persistent>
      <q-card class="modal-card" style="width:420px;max-width:96vw">
        <q-card-section class="modal-header row items-center">
          <div class="modal-title">{{ editingColor ? 'Edit Color' : 'Add Color' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-6" />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-lg">
          <div class="column q-gutter-md">
            <q-input v-model="colorForm.name" label="Color Name *" outlined dense autofocus input-class="full-input" placeholder="e.g. Ocean Blue" />
            <div>
              <div class="field-lbl q-mb-sm">Hex Code *</div>
              <div class="row items-center q-gutter-md">
                <div class="color-picker-preview" :style="{ background: colorForm.hex_code }" />
                <q-input
                  v-model="colorForm.hex_code" label="Hex Code" outlined dense class="col"
                  input-class="full-input"
                  placeholder="#3b82f6"
                  :rules="[v=>!!v||'Required', v=>/^#[0-9A-Fa-f]{6}$/.test(v)||'Invalid hex']"
                >
                  <template #append>
                    <label style="cursor:pointer;position:relative">
                      <q-icon name="colorize" color="blue-4" size="18px" />
                      <input type="color" v-model="colorForm.hex_code" class="hidden-color-input" />
                    </label>
                  </template>
                </q-input>
              </div>
            </div>
            <q-toggle v-model="colorForm.is_active" label="Active" color="blue-6" dense />
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="grey-6" />
          <q-btn
            :label="editingColor ? 'Update' : 'Add Color'"
            color="pink-6" unelevated no-caps icon="palette"
            @click="saveColor" :loading="savingColor"
            :disable="!colorForm.name || !colorForm.hex_code"
            style="min-width:130px;border-radius:12px"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════
         CONFIRM DELETE DIALOG
    ══════════════════════════════════════════════════ -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card class="modal-card" style="width:380px;max-width:96vw">
        <q-card-section class="column items-center q-pa-xl">
          <div class="delete-icon-wrap q-mb-md">
            <q-icon name="delete_forever" color="red-5" size="36px" />
          </div>
          <div class="modal-title q-mb-xs">Delete {{ deleteConfig.type }}?</div>
          <div class="text-caption text-grey-6 text-center">
            You are about to delete
            <strong class="text-grey-9">"{{ deleteConfig.name }}"</strong>.
            This action cannot be undone.
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="center" class="q-pa-md q-gutter-sm">
          <q-btn label="Cancel" flat no-caps v-close-popup color="grey-6" style="min-width:100px" />
          <q-btn
            label="Delete" color="red-6" unelevated no-caps icon="delete"
            :loading="deleteLoading" @click="executeDelete"
            style="min-width:120px;border-radius:12px"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Lightbox -->
    <q-dialog v-model="lightboxOpen">
      <div class="lightbox-bg" @click="lightboxOpen = false">
        <img :src="lightboxSrc" class="lightbox-img" @click.stop />
        <q-btn round flat icon="close" color="white" class="lightbox-close" @click="lightboxOpen = false" />
      </div>
    </q-dialog>

  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'src/boot/axios'

const $q = useQuasar()

// ── Tab ───────────────────────────────────────────────
const activeTab = ref('products')

// ── UI ────────────────────────────────────────────────
const lightboxOpen          = ref(false)
const lightboxSrc           = ref('')
const expanded              = ref([])
const loadingVariants       = ref({})
const isDraggingOverProduct = ref(false)
const isDraggingOverModal   = ref(false)

// ── Loading ───────────────────────────────────────────
const loadingProducts    = ref(false)
const loadingCategories  = ref(false)
const loadingColors      = ref(false)
const loadingAllVariants = ref(false)
const loadingTaxRates    = ref(false)   // ← NEW: show spinner in tax select

// ── Saving ────────────────────────────────────────────
const savingProduct = ref(false)
const savingVariant = ref(false)
const savingCat     = ref(false)
const savingColor   = ref(false)
const savingImage   = ref(false)

// ── Modals ────────────────────────────────────────────
const productModal    = ref(false)
const variantModal    = ref(false)
const catModal        = ref(false)
const colorModal      = ref(false)
const imageModal      = ref(false)
const deleteDialog    = ref(false)
const deleteLoading   = ref(false)

const editingProduct    = ref(null)
const editingVariant    = ref(null)
const editingCat        = ref(null)
const editingColor      = ref(null)
const currentProductId  = ref(null)
const variantTabMode    = ref(false)
const imageModalProduct = ref(null)
const editingProductId  = ref(null)   // ← for modal↔table bestseller sync

const deleteConfig = ref({ type: '', name: '', fn: async () => {} })

// ── Image form ────────────────────────────────────────
const newImageUrl     = ref('')
const newImageName    = ref('')
const newImagePrimary = ref(false)

// ── Filters ───────────────────────────────────────────
const search           = ref('')
const catFilter        = ref(null)
const activeFilter     = ref('all')
const varSearch        = ref('')
const varProductFilter = ref(null)
const catSearch        = ref('')
const colorSearch      = ref('')

// ── Data ──────────────────────────────────────────────
const products    = ref([])
const variants    = ref({})
const allVariants = ref([])
const categories  = ref([])
const colors      = ref([])
const taxRates    = ref([])

// ── Forms ─────────────────────────────────────────────
const defaultPForm = () => ({
  name: '',
  sku: '',
  category_id: null,
  description: '',
  details_and_fit: '',
  fabric_and_care: '',
  return_and_exchange: '',
  tax_rate_id: null,
  is_active: true,
  is_bestseller: false,
  gender: 'men' // ✅ NEW (default safe)
})
const defaultVForm = () => ({
  product_id: null, variant_name: '', price: 0, stock: 0,
  sku: '', color: '', color_id: null, size: '', low_stock_threshold: 5
})
const defaultCatForm   = () => ({ name: '', description: '', is_active: true })
const defaultColorForm = () => ({ name: '', hex_code: '#3b82f6', is_active: true })

const pForm     = ref(defaultPForm())
const vForm     = ref(defaultVForm())
const catForm   = ref(defaultCatForm())
const colorForm = ref(defaultColorForm())

// ── Columns ───────────────────────────────────────────
const productColumns = [
  { name: 'expand',     label: '',           field: 'id',           align: 'left', style: 'width:48px' },
  { name: 'images',     label: 'Images',     field: 'images',       align: 'left', style: 'width:130px' },
  { name: 'name',       label: 'Product',    field: 'name',         align: 'left', sortable: true },
  { name: 'sku',        label: 'SKU',        field: 'sku',          align: 'left' },
  { name: 'category',   label: 'Category',   field: 'category_id',  align: 'left' },
  { name: 'tax',        label: 'Tax',        field: 'tax_rate_id',  align: 'left' },
  { name: 'bestseller', label: 'Bestseller', field: 'is_bestseller',align: 'center', style: 'width:100px' },
  { name: 'status',     label: 'Status',     field: 'is_active',    align: 'left', style: 'width:100px' },
  { name: 'actions',    label: 'Actions',    field: 'id',           align: 'left', style: 'width:160px' }
]

const variantColumns = [
  { name: 'product_name', label: 'Product',  field: r => getProductName(r.product_id), align: 'left', sortable: true },
  { name: 'variant_name', label: 'Variant',  field: 'variant_name', align: 'left' },
  { name: 'size',         label: 'Size',     field: 'size',         align: 'left' },
  { name: 'color',        label: 'Color',    field: 'color',        align: 'left' },
  { name: 'price',        label: 'Price',    field: 'price',        align: 'left', sortable: true },
  { name: 'stock',        label: 'Stock',    field: 'stock',        align: 'left', sortable: true },
  { name: 'sku',          label: 'SKU',      field: 'sku',          align: 'left' },
  { name: 'actions',      label: 'Actions',  field: 'id',           align: 'left' }
]

const categoryColumns = [
  { name: 'id',          label: 'ID',          field: 'id',          align: 'left', style: 'width:70px' },
  { name: 'name',        label: 'Name',        field: 'name',        align: 'left', sortable: true },
  { name: 'description', label: 'Description', field: 'description', align: 'left' },
  { name: 'is_active',   label: 'Status',      field: 'is_active',   align: 'left', style: 'width:110px' },
  { name: 'actions',     label: 'Actions',     field: 'id',          align: 'left', style: 'width:100px' }
]

const colorColumns = [
  { name: 'id',        label: 'ID',       field: 'id',       align: 'left', style: 'width:70px' },
  { name: 'name',      label: 'Name',     field: 'name',     align: 'left', sortable: true },
  { name: 'hex_code',  label: 'Hex Code', field: 'hex_code', align: 'left' },
  { name: 'is_active', label: 'Status',   field: 'is_active',align: 'left', style: 'width:110px' },
  { name: 'actions',   label: 'Actions',  field: 'id',       align: 'left', style: 'width:100px' }
]

// ── Computed ──────────────────────────────────────────
const filteredVariantsAll = computed(() =>
  allVariants.value.filter(v => {
    const pName = getProductName(v.product_id)
    const q = varSearch.value?.toLowerCase() || ''
    const ms = !q ||
      v.variant_name?.toLowerCase().includes(q) ||
      pName.toLowerCase().includes(q) ||
      (v.size || '').toLowerCase().includes(q)
    const mp = !varProductFilter.value || v.product_id === varProductFilter.value
    return ms && mp
  })
)

const filteredCategories = computed(() =>
  categories.value.filter(c =>
    !catSearch.value || c.name.toLowerCase().includes(catSearch.value.toLowerCase())
  )
)

const filteredColors = computed(() =>
  colors.value.filter(c =>
    !colorSearch.value ||
    c.name.toLowerCase().includes(colorSearch.value.toLowerCase()) ||
    (c.hex_code || '').toLowerCase().includes(colorSearch.value.toLowerCase())
  )
)

// ── Helpers ───────────────────────────────────────────
const getCatName     = id => categories.value.find(c => c.id === id)?.name || '—'
const getProductName = id => products.value.find(p => p.id === id)?.name || '—'
const getVariants    = pid => variants.value[pid] || []

/**
 * BUG FIX #2 — Tax name resolution
 * Before: taxRates was only populated when the modal was opened (fetchTaxRates
 * was called inside openProductModal). So when the table rendered, taxRates
 * was empty and every cell showed "—" or "Tax #N".
 *
 * Fix: fetchTaxRates() is now called in onMounted() so the lookup table is
 * ready before the product list renders.
 */
const getTaxName = id => {
  if (!id) return null                               // null → template shows "—"
  const t = taxRates.value.find(t => t.id === id)
  return t ? t.name : `Tax #${id}`                  // fallback shows raw id if rates not yet loaded
}

const getColorHex = id => colors.value.find(c => c.id === id)?.hex_code || null

let searchTimer = null
const onSearchChange = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchProducts, 400)
}

const toggleExpand = async id => {
  const i = expanded.value.indexOf(id)
  if (i >= 0) {
    expanded.value.splice(i, 1)
  } else {
    expanded.value.push(id)
    await fetchVariants(id)
  }
}

const previewImage = src => { lightboxSrc.value = src; lightboxOpen.value = true }

const onColorSelect = colorId => {
  const c = colors.value.find(x => x.id === colorId)
  if (c) vForm.value.color = c.name
}

const extractUrlFromDrop = e => {
  const text = e.dataTransfer?.getData('text/plain') || ''
  return text.startsWith('http') ? text : ''
}

const onProductImageDrop = e => {
  isDraggingOverProduct.value = false
  const url = extractUrlFromDrop(e)
  if (url) newImageUrl.value = url
}

const onModalImageDrop = e => {
  isDraggingOverModal.value = false
  const url = extractUrlFromDrop(e)
  if (url) newImageUrl.value = url
}

const notify = (message, type = 'positive') => {
  $q.notify({ message, type, position: 'top-right', timeout: 3000 })
}

// ═══════════════════════════════════════════════════════
// TAX RATES
// ═══════════════════════════════════════════════════════
/**
 * BUG FIX #2 — called in onMounted() so taxRates is populated
 * before any table row tries to resolve getTaxName().
 */
const fetchTaxRates = async () => {
  loadingTaxRates.value = true
  try {
    const endpoints = [
      '/admin/tax-rates/',
      '/admin/tax-rates',
      '/tax-rates',
      '/admin/products/tax-rates'
    ]

    for (const url of endpoints) {
      try {
        const res = await api.get(url)
        const rows = Array.isArray(res.data)
          ? res.data
          : Array.isArray(res.data?.data)
            ? res.data.data
            : []

        if (rows.length > 0) {
          taxRates.value = rows
            .filter(t => t.is_active !== false)
            .map(t => ({
              id:   t.id,
              name: t.name || t.tax_name || `GST ${t.rate ?? 0}%`
            }))
          return
        }
      } catch {
        continue
      }
    }

    taxRates.value = []
  } catch {
    taxRates.value = []
    notify('Failed to load tax rates', 'negative')
  } finally {
    loadingTaxRates.value = false
  }
}

// ═══════════════════════════════════════════════════════
// PRODUCTS
// ═══════════════════════════════════════════════════════
const fetchProducts = async () => {
  loadingProducts.value = true
  try {
    const params = {}
    if (catFilter.value !== null)        params.category_id = catFilter.value
    if (activeFilter.value === 'active') params.is_active   = true
    if (activeFilter.value === 'inactive') params.is_active = false

    const res = await api.get('/admin/products/', { params })
    let rows = Array.isArray(res.data) ? res.data
      : Array.isArray(res.data?.data) ? res.data.data : []

    if (search.value?.trim()) {
      const q = search.value.toLowerCase()
      rows = rows.filter(p =>
        p.name?.toLowerCase().includes(q) ||
        p.sku?.toLowerCase().includes(q)
      )
    }

    products.value = rows.filter(p => !p.is_deleted)

    // keep modal in sync if open
    if (productModal.value && editingProductId.value) {
      const fresh = products.value.find(p => p.id === editingProductId.value)
      if (fresh) editingProduct.value = JSON.parse(JSON.stringify(fresh))
    }
  } catch {
    notify('Failed to load products', 'negative')
  } finally {
    loadingProducts.value = false
  }
}

const fetchLowStock = async () => {
  loadingProducts.value = true
  try {
    const res = await api.get('/admin/products/low-stock')
    const rows = Array.isArray(res.data) ? res.data
      : Array.isArray(res.data?.data) ? res.data.data : []
    products.value = rows
    notify(`Showing ${rows.length} low stock items`, 'info')
  } catch {
    notify('Failed to load low stock', 'negative')
  } finally {
    loadingProducts.value = false
  }
}

const openProductModal = async (p) => {
  // taxRates is already loaded from onMounted; only re-fetch if empty (e.g. first load failed)
  if (taxRates.value.length === 0) await fetchTaxRates()

  if (p) {
    editingProductId.value = p.id
    editingProduct.value   = JSON.parse(JSON.stringify(p))
    pForm.value = {
      name:               p.name,
      sku:                p.sku,
      category_id:        p.category_id,
      description:        p.description || '',
      details_and_fit:    p.details_and_fit || '',
      fabric_and_care:    p.fabric_and_care || '',
      return_and_exchange:p.return_and_exchange || '',
      tax_rate_id:        p.tax_rate_id   ?? null,   // ← always carry existing value
      is_active:          p.is_active,
      is_bestseller:      p.is_bestseller  || false,
      gender: p.gender || 'men' // ✅ NEW

    }
  } else {
    editingProductId.value = null
    editingProduct.value   = null
    pForm.value            = defaultPForm()
  }

  newImageUrl.value     = ''
  newImageName.value    = ''
  newImagePrimary.value = false
  productModal.value    = true
}

/**
 * BUG FIX #1 — POST not saving tax_rate_id / is_bestseller
 * ══════════════════════════════════════════════════════════
 * Root causes found by reading the SQL dump:
 *
 * (A) sp_add_product does NOT accept is_bestseller.
 *     Bestseller must be set via a SEPARATE call to
 *     POST /admin/products/{id}/bestseller after creation.
 *     Previously this extra call was only made during UPDATE,
 *     so new products never got bestseller saved.
 *
 * (B) tax_rate_id was included in the payload but could silently
 *     be dropped when pForm.tax_rate_id was null (falsy) because
 *     the old code used `|| null` which turns 0 into null.
 *     Using `?? null` (nullish coalescing) is safer, but more
 *     importantly we must always include the key, even as null,
 *     so the backend schema validator doesn't reject the body.
 *
 * (C) The previous code did the bestseller call only in the
 *     editingProduct branch (PUT). The POST branch skipped it.
 *     Fix: move the bestseller call AFTER both POST and PUT,
 *     guarding with the resolved product id.
 */
const saveProduct = async () => {
  if (!pForm.value.name?.trim() || !pForm.value.sku?.trim()) {
    notify('Product name and SKU are required', 'warning')
    return
  }

  savingProduct.value = true

  try {
    // ─── Build payload ───────────────────────────────
    // Always include tax_rate_id key (null is valid).
    // Do NOT include is_bestseller here — sp_add_product
    // doesn't accept it; it must go via the bestseller endpoint.
    const payload = {
      name:               pForm.value.name.trim(),
      description:        pForm.value.description        || '',
      sku:                pForm.value.sku.trim(),
      category_id:        pForm.value.category_id        ?? null,
      is_active:          pForm.value.is_active,
      details_and_fit:    pForm.value.details_and_fit    || '',
      fabric_and_care:    pForm.value.fabric_and_care    || '',
      return_and_exchange:pForm.value.return_and_exchange|| '',
      tax_rate_id:        pForm.value.tax_rate_id        ?? null ,  // ← always sent, even when null
      gender: pForm.value.gender || 'men'

    }

    let savedId   // id of the product we just created / updated

    if (editingProduct.value) {
      // ── UPDATE (PUT) ─────────────────────────────
      await api.put(`/admin/products/${editingProduct.value.id}`, payload)
      savedId = editingProduct.value.id

      // Optimistic local update so the table row refreshes immediately
      const idx = products.value.findIndex(p => p.id === savedId)
      if (idx >= 0) {
        products.value[idx] = {
          ...products.value[idx],
          ...payload,
          is_bestseller: pForm.value.is_bestseller
        }
      }

      notify('Product updated successfully!', 'positive')
    } else {
      // ── CREATE (POST) ────────────────────────────
      const res = await api.post('/admin/products/', payload)

      // Extract the new product id from the response.
      // Backends commonly return the created object or { id, ... } or { data: { id } }
      savedId =
        res.data?.id          ??
        res.data?.data?.id    ??
        res.data?.product_id  ??
        null

      notify('Product created successfully!', 'positive')
    }

    // ── Bestseller — always call after POST *and* PUT ──────────────────
    // sp_mark_bestseller is a separate DB procedure; the product CRUD
    // endpoints do not handle this flag.  We call it for both create and
    // update so the value is always persisted.
    if (savedId) {
      try {
        await api.post(
          `/admin/products/${savedId}/bestseller?is_bestseller=${pForm.value.is_bestseller}`
        )
      } catch (bsErr) {
        // Non-fatal — log and continue. Product is already saved.
        console.warn('Bestseller endpoint skipped:', bsErr?.response?.status)
      }
    } else {
      // savedId is null — likely the POST response didn't return an id.
      // Refresh the product list to find it.
      console.warn('Could not determine new product id from POST response; bestseller not set on create.')
    }

    // ── Close modal & refresh ─────────────────────────────────────────
    productModal.value     = false
    editingProduct.value   = null
    editingProductId.value = null

    await fetchProducts()

  } catch (e) {
    notify(
      e.response?.data?.detail  ||
      e.response?.data?.message ||
      'Failed to save product',
      'negative'
    )
  } finally {
    savingProduct.value = false
  }
}

const confirmDeleteProduct = row => {
  deleteConfig.value = {
    type: 'Product',
    name: row.name,
    fn: async () => {
      await api.delete(`/admin/products/${row.id}`)
      products.value = products.value.filter(p => p.id !== row.id)
      notify('Product deleted', 'positive')
    }
  }
  deleteDialog.value = true
}

/**
 * Bestseller toggle (from table row)
 * Also syncs the modal form if it's currently open for this product.
 */
const toggleBestseller = async row => {
  const newVal = !row.is_bestseller
  try {
    await api.post(`/admin/products/${row.id}/bestseller?is_bestseller=${newVal}`)

    // Update local table row
    const i = products.value.findIndex(p => p.id === row.id)
    if (i >= 0) products.value[i] = { ...products.value[i], is_bestseller: newVal }

    // Sync modal form if open for this product
    if (productModal.value && editingProductId.value === row.id) {
      pForm.value.is_bestseller = newVal
      if (editingProduct.value) {
        editingProduct.value = { ...editingProduct.value, is_bestseller: newVal }
      }
    }

    notify(
      newVal
        ? `"${row.name}" marked as Bestseller`
        : `"${row.name}" removed from Bestsellers`,
      'positive'
    )
  } catch (e) {
    notify(e.response?.data?.detail || 'Failed to update bestseller', 'negative')
  }
}

// ═══════════════════════════════════════════════════════
// VARIANTS
// ═══════════════════════════════════════════════════════
const fetchVariants = async productId => {
  loadingVariants.value = { ...loadingVariants.value, [productId]: true }
  try {
    const res  = await api.get(`/admin/products/${productId}/variants`)
    const rows = (Array.isArray(res.data) ? res.data : res.data?.data || [])
      .filter(v => !v.is_deleted)

    variants.value = { ...variants.value, [productId]: rows }

    const existing = allVariants.value.filter(v => v.product_id !== productId)
    allVariants.value = [...existing, ...rows.map(v => ({ ...v, product_id: productId }))]
  } catch (e) {
    notify(e.response?.data?.detail || 'Failed to load variants', 'negative')
  } finally {
    loadingVariants.value = { ...loadingVariants.value, [productId]: false }
  }
}

const fetchAllVariants = async () => {
  if (!products.value.length) return
  loadingAllVariants.value = true
  try {
    const results = await Promise.all(
      products.value.map(p =>
        api.get(`/admin/products/${p.id}/variants`)
          .then(r => (Array.isArray(r.data) ? r.data : r.data?.data || [])
            .filter(v => !v.is_deleted)
            .map(v => ({ ...v, product_id: p.id })))
          .catch(() => [])
      )
    )
    allVariants.value = results.flat()
    products.value.forEach((p, i) => { variants.value[p.id] = results[i] || [] })
  } catch {
    notify('Failed to load variants', 'negative')
  } finally {
    loadingAllVariants.value = false
  }
}

const openVariantModal = (pid, v) => {
  currentProductId.value = pid
  variantTabMode.value   = !pid
  editingVariant.value   = v
  vForm.value = v ? {
    product_id:          v.product_id || pid,
    variant_name:        v.variant_name,
    price:               Number(v.price),
    stock:               v.stock,
    sku:                 v.sku              || '',
    color:               v.color            || '',
    color_id:            v.color_id         || null,
    size:                v.size             || '',
    low_stock_threshold: v.low_stock_threshold || 5
  } : { ...defaultVForm(), product_id: pid }
  variantModal.value = true
}

const saveVariant = async () => {
  const pid = vForm.value.product_id || currentProductId.value
  if (!pid)                      { notify('Please select a product', 'warning'); return }
  if (!vForm.value.variant_name) { notify('Variant name is required', 'warning'); return }
  if (!vForm.value.price)        { notify('Price is required', 'warning'); return }
  savingVariant.value = true
  try {
    const payload = {
      variant_name:        vForm.value.variant_name,
      price:               vForm.value.price,
      stock:               vForm.value.stock,
      sku:                 vForm.value.sku   || undefined,
      color:               vForm.value.color || undefined,
      color_id:            vForm.value.color_id || undefined,
      size:                vForm.value.size  || undefined,
      low_stock_threshold: vForm.value.low_stock_threshold
    }
    if (editingVariant.value) {
      await api.put(`/admin/products/variants/${editingVariant.value.id}`, payload)
      notify('Variant updated!', 'positive')
    } else {
      await api.post(`/admin/products/${pid}/variants`, payload)
      notify('Variant added!', 'positive')
    }
    variantModal.value = false
    await fetchVariants(pid)
    if (variantTabMode.value) await fetchAllVariants()
  } catch (e) {
    notify(e.response?.data?.detail || e.response?.data?.message || 'Failed to save variant', 'negative')
  } finally {
    savingVariant.value = false
  }
}

const confirmDeleteVariant = v => {
  deleteConfig.value = {
    type: 'Variant',
    name: v.variant_name,
    fn: async () => {
      await api.delete(`/admin/products/variants/${v.id}`)
      const pid = v.product_id || currentProductId.value
      if (pid) variants.value[pid] = (variants.value[pid] || []).filter(x => x.id !== v.id)
      allVariants.value = allVariants.value.filter(x => x.id !== v.id)
      notify('Variant deleted', 'positive')
    }
  }
  deleteDialog.value = true
}

// ═══════════════════════════════════════════════════════
// IMAGES
// ═══════════════════════════════════════════════════════
const openImageModal = productId => {
  imageModalProduct.value = products.value.find(p => p.id === productId) || null
  newImageUrl.value       = ''
  newImageName.value      = ''
  newImagePrimary.value   = false
  imageModal.value        = true
}

const _uploadImage = async pid => {
  if (!newImageUrl.value?.trim()) { notify('Image URL is required', 'warning'); return false }
  await api.post(`/admin/products/${pid}/images`, {
    image_url:  newImageUrl.value.trim(),
    image_name: newImageName.value || undefined,
    is_primary: newImagePrimary.value
  })
  newImageUrl.value = ''; newImageName.value = ''; newImagePrimary.value = false
  return true
}

const addProductImage = async () => {
  savingImage.value = true
  try {
    const pid = editingProduct.value?.id
    if (await _uploadImage(pid)) {
      notify('Image added!', 'positive')
      await fetchProducts()
      editingProduct.value = products.value.find(p => p.id === pid) || editingProduct.value
    }
  } catch (e) {
    notify(e.response?.data?.detail || 'Failed to add image', 'negative')
  } finally { savingImage.value = false }
}

const addProductImageFromModal = async () => {
  savingImage.value = true
  try {
    const pid = imageModalProduct.value?.id
    if (await _uploadImage(pid)) {
      notify('Image added!', 'positive')
      await fetchProducts()
      imageModalProduct.value = products.value.find(p => p.id === pid) || null
    }
  } catch (e) {
    notify(e.response?.data?.detail || 'Failed to add image', 'negative')
  } finally { savingImage.value = false }
}

const deleteProductImage = async imageId => {
  try {
    await api.delete(`/admin/products/images/${imageId}`)
    notify('Image removed', 'positive')
    await fetchProducts()
    const pid = editingProduct.value?.id
    editingProduct.value = products.value.find(p => p.id === pid) || editingProduct.value
  } catch (e) {
    notify(e.response?.data?.detail || 'Failed to delete image', 'negative')
  }
}

const deleteProductImageFromModal = async imageId => {
  try {
    await api.delete(`/admin/products/images/${imageId}`)
    notify('Image removed', 'positive')
    await fetchProducts()
    const pid = imageModalProduct.value?.id
    imageModalProduct.value = products.value.find(p => p.id === pid) || null
  } catch (e) {
    notify(e.response?.data?.detail || 'Failed to delete image', 'negative')
  }
}

// ═══════════════════════════════════════════════════════
// CATEGORIES
// ═══════════════════════════════════════════════════════
const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const res  = await api.get('/admin/products/categories')
    const rows = Array.isArray(res.data) ? res.data : res.data?.data || []
    categories.value = rows.filter(c => !c.is_deleted)
  } catch {
    notify('Failed to load categories', 'negative')
  } finally {
    loadingCategories.value = false
  }
}

const openCatModal = c => {
  editingCat.value = c
  catForm.value    = c
    ? { name: c.name, description: c.description || '', is_active: c.is_active }
    : defaultCatForm()
  catModal.value = true
}

const saveCat = async () => {
  if (!catForm.value.name?.trim()) { notify('Category name is required', 'warning'); return }
  savingCat.value = true
  try {
    const payload = {
      name:        catForm.value.name.trim(),
      description: catForm.value.description || '',
      is_active:   catForm.value.is_active
    }
    if (editingCat.value) {
      await api.put(`/admin/products/categories/${editingCat.value.id}`, payload)
      notify('Category updated!', 'positive')
    } else {
      await api.post('/admin/products/categories', payload)
      notify('Category created!', 'positive')
    }
    catModal.value = false
    await fetchCategories()
  } catch (e) {
    notify(e.response?.data?.detail || e.response?.data?.message || 'Failed to save category', 'negative')
  } finally {
    savingCat.value = false
  }
}

const confirmDeleteCat = row => {
  deleteConfig.value = {
    type: 'Category',
    name: row.name,
    fn: async () => {
      await api.delete(`/admin/products/categories/${row.id}`)
      categories.value = categories.value.filter(c => c.id !== row.id)
      notify('Category deleted', 'positive')
    }
  }
  deleteDialog.value = true
}

// ═══════════════════════════════════════════════════════
// COLORS
// ═══════════════════════════════════════════════════════
const fetchColors = async () => {
  loadingColors.value = true
  try {
    const res  = await api.get('/admin/products/colors')
    const rows = Array.isArray(res.data) ? res.data : res.data?.data || []
    colors.value = rows.filter(c => !c.is_deleted)
  } catch {
    notify('Failed to load colors', 'negative')
  } finally {
    loadingColors.value = false
  }
}

const openColorModal = c => {
  editingColor.value = c
  colorForm.value    = c
    ? { name: c.name, hex_code: c.hex_code, is_active: c.is_active }
    : defaultColorForm()
  colorModal.value = true
}

const saveColor = async () => {
  if (!colorForm.value.name || !colorForm.value.hex_code) return
  savingColor.value = true
  try {
    const payload = {
      name:      colorForm.value.name,
      hex_code:  colorForm.value.hex_code,
      is_active: colorForm.value.is_active
    }
    if (editingColor.value) {
      await api.put(`/admin/products/colors/${editingColor.value.id}`, payload)
      notify('Color updated!', 'positive')
    } else {
      await api.post('/admin/products/colors', payload)
      notify('Color added!', 'positive')
    }
    colorModal.value = false
    await fetchColors()
  } catch (e) {
    notify(e.response?.data?.detail || 'Failed to save color', 'negative')
  } finally {
    savingColor.value = false
  }
}

const confirmDeleteColor = row => {
  deleteConfig.value = {
    type: 'Color',
    name: row.name,
    fn: async () => {
      await api.delete(`/admin/products/colors/${row.id}`)
      colors.value = colors.value.filter(c => c.id !== row.id)
      notify('Color deleted', 'positive')
    }
  }
  deleteDialog.value = true
}

// ── Shared delete executor ────────────────────────────
const executeDelete = async () => {
  deleteLoading.value = true
  try {
    await deleteConfig.value.fn()
  } catch (e) {
    notify(e.response?.data?.detail || e.response?.data?.message || 'Delete failed', 'negative')
  } finally {
    deleteLoading.value = false
    deleteDialog.value  = false
  }
}

// ── Tab change ────────────────────────────────────────
const onTabChange = async tab => {
  if (tab === 'variants'   && allVariants.value.length === 0) await fetchAllVariants()
  if (tab === 'categories') await fetchCategories()
  if (tab === 'colors')     await fetchColors()
}

// ── Init ──────────────────────────────────────────────
/**
 * BUG FIX #2 — fetchTaxRates() is now part of the initial load sequence.
 * This populates taxRates before products render so getTaxName() resolves
 * correctly in every table row from the first render.
 */
onMounted(async () => {
  await Promise.all([
    fetchCategories(),
    fetchColors(),
    fetchTaxRates()     // ← was missing; this is why tax names were blank in the table
  ])
  await fetchProducts() // fetch products after lookup tables are ready
})
</script>

<style scoped>
/* ══════════════════════════════════════════════════════
   PAGE
══════════════════════════════════════════════════════ */
.admin-page {
  background: #f4f7fb;
  min-height: 100vh;
}

.page-header {
  background: #fff;
  border-bottom: 1px solid #e8edf5;
}

.page-title {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 13px;
  color: #3b82f6;
  font-weight: 600;
  margin-top: 2px;
}

.action-btn {
  border-radius: 12px !important;
  font-weight: 700 !important;
  min-height: 40px !important;
  padding: 0 18px !important;
}

/* ══════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════ */
.product-tabs { background: #fff; }

.product-tabs :deep(.q-tab) {
  font-weight: 700;
  font-size: 13px;
  min-height: 48px;
  padding: 0 20px;
  color: #64748b;
  border-radius: 0;
}

.product-tabs :deep(.q-tab--active)    { color: #1d4ed8; }
.product-tabs :deep(.q-tab__indicator) { height: 3px; border-radius: 3px 3px 0 0; }

/* ══════════════════════════════════════════════════════
   TABLE
══════════════════════════════════════════════════════ */
.tbl-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0 !important;
  overflow: hidden;
  background: #fff;
}

.product-table { background: transparent !important; }
.product-table :deep(.q-table__container) { background: transparent !important; }

.product-table :deep(thead th) {
  background: #f8fafd;
  color: #475569;
  font-size: 11.5px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  border-bottom: 1.5px solid #e2e8f0;
  padding: 12px 14px;
}

.product-table :deep(tbody td) {
  border-bottom: 1px solid #f1f5f9;
  padding: 10px 14px;
  vertical-align: middle;
  color: #1e293b;
  font-size: 13.5px;
}

.product-table :deep(tbody tr:hover td) { background: #f8fbff; }

.product-table :deep(.q-table__bottom) {
  border-top: 1px solid #e8edf5;
  background: #fafbfc;
  color: #64748b;
  font-size: 13px;
}

.product-row { cursor: pointer; }

/* ── Cell text ── */
.prod-name  { font-weight: 700; font-size: 14px; color: #0f172a; }
.prod-desc  { font-size: 12px; color: #64748b; margin-top: 1px; }
.prod-slug  { font-size: 11px; color: #94a3b8; margin-top: 1px; font-family: monospace; }
.price-text { font-weight: 800; color: #16a34a; font-size: 14px; }
.tax-label  { font-size: 12.5px; color: #3b82f6; font-weight: 600; }
.mono       { font-family: monospace; }

/* ── Pills ── */
.sku-pill {
  display: inline-block;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 8px;
  font-family: monospace;
}

.id-pill {
  display: inline-block;
  background: #f1f5f9;
  color: #475569;
  font-size: 11.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 7px;
  font-family: monospace;
}

.hex-pill {
  display: inline-block;
  background: #f1f5f9;
  color: #334155;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 7px;
  font-family: monospace;
}

/* ── Image thumbs ── */
.tbl-thumb {
  width: 42px; height: 42px;
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid #e2e8f0;
  cursor: pointer;
  flex-shrink: 0;
  position: relative;
  transition: border-color 0.15s;
}
.tbl-thumb:hover { border-color: #3b82f6; }
.tbl-thumb-img   { width: 100%; height: 100%; object-fit: cover; display: block; }

.tbl-thumb-more {
  width: 42px; height: 42px;
  border-radius: 10px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 11px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.tbl-thumb-empty {
  width: 42px; height: 42px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1.5px dashed #cbd5e1;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.color-dot {
  width: 16px; height: 16px;
  border-radius: 50%;
  border: 1.5px solid rgba(0,0,0,0.12);
  flex-shrink: 0;
  display: inline-block;
}

.color-swatch-preview {
  width: 26px; height: 26px;
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.1);
  flex-shrink: 0;
}

.cat-icon {
  width: 26px; height: 26px;
  border-radius: 7px;
  background: #f3e8ff;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* ══════════════════════════════════════════════════════
   EXPANDED VARIANTS
══════════════════════════════════════════════════════ */
.expand-row :deep(td) { padding: 0 !important; }
.expand-td { background: #f8fafd !important; }

.expand-inner {
  padding: 14px 18px;
  border-left: 3px solid #3b82f6;
  margin: 6px 16px;
  background: #ffffff;
  border-radius: 0 12px 12px 0;
  box-shadow: 0 2px 8px rgba(15,23,42,0.06);
}

.var-section-label {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #3b82f6;
}

.var-grid-header,
.var-grid-row {
  display: grid;
  grid-template-columns: 160px 90px 80px 80px 120px 70px 140px 90px;
  gap: 8px;
  align-items: center;
  padding: 6px 8px;
}

.var-grid-header {
  font-size: 10.5px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #64748b;
  background: #f1f5f9;
  border-radius: 8px;
  margin-bottom: 4px;
}

.var-grid-row { border-bottom: 1px solid #f1f5f9; font-size: 13px; }
.var-grid-row:last-child { border-bottom: none; }
.var-grid-row:hover { background: #f8fbff; border-radius: 8px; }

/* ══════════════════════════════════════════════════════
   DIALOGS & MODALS
══════════════════════════════════════════════════════ */
.dialog-fullcard {
  background: #fff;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.dialog-header   { padding: 20px 28px; background: #fff; flex-shrink: 0; }
.dialog-title    { font-size: 20px; font-weight: 800; color: #0f172a; }
.dialog-subtitle { font-size: 12.5px; color: #64748b; margin-top: 2px; }

.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
}

.dialog-footer { padding: 16px 28px; background: #fafbfc; flex-shrink: 0; }

.modal-card {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(15,23,42,0.15);
}

.modal-header   { padding: 18px 22px; }
.modal-title    { font-size: 18px; font-weight: 800; color: #0f172a; }
.modal-subtitle { font-size: 12px; color: #64748b; margin-top: 2px; }

/* ── Form sections ── */
.form-section-title {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #3b82f6;
  margin-bottom: 14px;
  padding-bottom: 6px;
  border-bottom: 1.5px solid #dbeafe;
}

.field-lbl { font-size: 12px; font-weight: 700; color: #475569; }

/* ── Input text clipping fix ── */
:deep(.q-field--outlined .q-field__control) {
  border-radius: 10px !important;
  overflow: visible !important;
}

:deep(.q-field__native),
:deep(.q-field__input) {
  overflow: visible !important;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  width: 100%;
}

:deep(textarea.q-field__native) {
  white-space: pre-wrap !important;
  overflow-y: auto !important;
  resize: vertical;
}

:deep(.full-input) {
  overflow: visible !important;
  text-overflow: ellipsis;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

:deep(.q-field--outlined .q-field__control:before)       { border-color: #e2e8f0 !important; }
:deep(.q-field--outlined.q-field--focused .q-field__control:after) {
  border-color: #3b82f6 !important;
  border-width: 1.5px !important;
}

:deep(.q-field__label) {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #64748b !important;
}

/* ── Select selected value visibility ── */
:deep(.q-field__control-container) { overflow: hidden; min-width: 0; flex: 1; }

:deep(.q-select .q-field__native) {
  display: flex !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: #0f172a !important;
  font-weight: 500;
  font-size: 13.5px;
}

.select-selected-text {
  color: #0f172a;
  font-weight: 600;
  font-size: 13.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
  max-width: 100%;
}

:global(.select-popup) {
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(15,23,42,0.12) !important;
  border: 1px solid #e2e8f0 !important;
}
:global(.select-popup .q-item) {
  font-size: 13.5px;
  color: #1e293b;
  border-radius: 8px;
  margin: 2px 6px;
}
:global(.select-popup .q-item--active) {
  background: #eff6ff !important;
  color: #1d4ed8 !important;
  font-weight: 700;
}
:global(.select-popup .q-item:hover) { background: #f0f9ff; }

/* ── Image panel ── */
.img-panel {
  background: #f8fafd;
  border: 1.5px dashed #bfdbfe;
  border-radius: 14px;
  padding: 18px;
  height: 100%;
}

.new-product-img-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 13px;
  color: #1d4ed8;
  font-weight: 500;
}

.img-gallery { display: flex; flex-wrap: wrap; gap: 10px; }

.img-thumb-wrap {
  position: relative;
  width: 72px; height: 72px;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid #e2e8f0;
  cursor: pointer;
  flex-shrink: 0;
  transition: border-color 0.15s, transform 0.15s;
}
.img-thumb-wrap:hover      { border-color: #3b82f6; transform: translateY(-2px); }
.img-thumb-wrap.is-primary { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.2); }
.img-thumb                 { width: 100%; height: 100%; object-fit: cover; display: block; }

.primary-badge {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: rgba(37,99,235,0.88);
  color: #fff; font-size: 9px; font-weight: 700;
  text-align: center; padding: 2px 0;
}

.img-remove-btn {
  position: absolute; top: 3px; right: 3px;
  width: 18px; height: 18px;
  border-radius: 50%;
  background: rgba(239,68,68,0.9);
  border: none; cursor: pointer; color: #fff;
  display: none; align-items: center; justify-content: center; padding: 0;
}
.img-thumb-wrap:hover .img-remove-btn { display: flex; }

.img-empty-state {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 24px;
  background: #f1f5f9;
  border-radius: 10px;
  border: 1.5px dashed #cbd5e1;
}

.img-drop-zone {
  border: 2px dashed #93c5fd;
  border-radius: 12px;
  background: #f0f9ff;
  padding: 18px;
  text-align: center;
  cursor: default;
  transition: border-color 0.2s, background 0.2s;
  display: flex; flex-direction: column; align-items: center;
}
.img-drop-zone.drop-active { border-color: #3b82f6; background: #dbeafe; }

/* ── Color picker ── */
.color-picker-preview {
  width: 42px; height: 42px;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
  flex-shrink: 0;
}

.hidden-color-input { position: absolute; width: 0; height: 0; opacity: 0; left: 0; top: 0; }

/* ── Delete dialog ── */
.delete-icon-wrap {
  width: 68px; height: 68px;
  border-radius: 50%;
  background: #fef2f2;
  display: flex; align-items: center; justify-content: center;
}

/* ── Lightbox ── */
.lightbox-bg {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.93);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; cursor: pointer;
}
.lightbox-img {
  max-width: 92vw; max-height: 90vh;
  border-radius: 14px;
  object-fit: contain;
  cursor: default;
  box-shadow: 0 0 60px rgba(0,0,0,0.5);
}
.lightbox-close { position: absolute; top: 20px; right: 20px; }

/* ── Toggle colour (all blue) ── */
:deep(.q-toggle__inner--truthy) { color: #3b82f6 !important; }

/* ══════════════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .page-title { font-size: 18px; }
  .var-grid-header, .var-grid-row { grid-template-columns: repeat(4, 1fr); font-size: 11px; }
  .dialog-body   { padding: 16px; }
  .dialog-header { padding: 16px 18px; }
  .dialog-footer { padding: 12px 16px; }
}
</style>