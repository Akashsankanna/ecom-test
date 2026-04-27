<template>
  <q-page class="inv-page">

    <!-- ══════════════════════════ HEADER ══════════════════════════ -->
    <div class="inv-header">
      <div class="inv-header__left">
        <div class="inv-header__eyebrow">ADMIN · INVENTORY</div>
        <h1 class="inv-header__title">Stock Control</h1>
      </div>

      <div class="inv-header__stats">
        <div class="stat-chip stat-chip--warn">
          <q-icon name="warning_amber" size="13px" />
          {{ stats.lowStock }} Low Stock
        </div>
        <div class="stat-chip stat-chip--blue">
          <q-icon name="inventory_2" size="13px" />
          {{ stats.totalVariants }} Variants
        </div>
        <div class="stat-chip stat-chip--green">
          <q-icon name="check_circle_outline" size="13px" />
          {{ stats.inStock }} In Stock
        </div>
      </div>

      <div class="inv-header__actions">
        <q-btn flat no-caps class="hdr-btn hdr-btn--ghost" icon="lock_outline" label="Reserve"
          @click="openQuickModal('reserve')" />
        <q-btn unelevated no-caps class="hdr-btn hdr-btn--red" icon="remove" label="Remove Stock"
          @click="openQuickModal('remove')" />
        <q-btn unelevated no-caps class="hdr-btn hdr-btn--blue" icon="add" label="Add Stock"
          @click="openQuickModal('add')" />
      </div>
    </div>

    <!-- ══════════════════════════ TABS ══════════════════════════ -->
    <div class="inv-tabs-bar">
      <button v-for="t in tabs" :key="t.key" class="inv-tab"
        :class="{ 'inv-tab--active': activeTab === t.key }" @click="switchTab(t.key)">
        <q-icon :name="t.icon" size="14px" />
        {{ t.label }}
        <span v-if="t.key === 'lowstock' && stats.lowStock > 0" class="tab-badge">
          {{ stats.lowStock }}
        </span>
      </button>
    </div>

    <div class="inv-body">

      <!-- ════════════════════ TAB: ALL VARIANTS ════════════════════ -->
      <div v-show="activeTab === 'variants'">
        <!-- toolbar -->
        <div class="toolbar">
          <div class="toolbar__search">
            <q-icon name="search" size="15px" color="grey-5" />
            <input v-model="variantSearch" class="toolbar__input"
              placeholder="Search product or variant…"
              @input="onSearchInput" />
            <q-icon v-if="variantSearch" name="close" size="14px" color="grey-5"
              class="cursor-pointer" @click="clearSearch" />
          </div>

          <label class="toggle-wrap">
            <input v-model="lowStockOnly" type="checkbox" @change="fetchVariants" />
            <span class="toggle-track" />
            <span class="toggle-label">Low stock only</span>
          </label>

          <q-btn flat round dense icon="refresh" color="grey-6" size="sm"
            :loading="variantsLoading" @click="fetchVariants" />
        </div>

        <!-- table -->
        <div class="tbl-wrap">
          <table class="dtbl">
            <thead>
              <tr>
                <th>Product / Variant</th>
                <th>SKU</th>
                <th>Color · Size</th>
                <th class="tc">Stock</th>
                <th class="tc">Reserved</th>
                <th class="tc">Available</th>
                <th class="tc">Threshold</th>
                <th class="tc">Status</th>
                <th class="tr">Actions</th>
              </tr>
            </thead>

            <tbody v-if="variantsLoading">
              <tr><td colspan="9" class="empty-cell">
                <q-spinner-dots color="blue-5" size="32px" />
              </td></tr>
            </tbody>

            <tbody v-else-if="variants.length === 0">
              <tr><td colspan="9" class="empty-cell">
                <q-icon name="inventory_2" size="36px" color="grey-4" />
                <div class="empty-msg">No variants found</div>
              </td></tr>
            </tbody>

            <tbody v-else>
              <tr v-for="v in variants" :key="v.id"
                class="dtbl__row" :class="{ 'dtbl__row--warn': v.stock <= v.low_stock_threshold }">

                <td>
                  <div class="cell-title">{{ v.product_name || v.name }}</div>
                  <div class="cell-sub">{{ v.variant_name }}</div>
                </td>

                <td><code class="sku-tag">{{ v.sku || '—' }}</code></td>

                <td>
                  <div class="color-size">
                    <span v-if="v.hex_code" class="color-dot"
                      :style="{ background: v.hex_code }" />
                    <span>{{ v.color_name || v.color || '—' }}</span>
                    <span v-if="v.size" class="size-pill">{{ v.size }}</span>
                  </div>
                </td>

                <td class="tc num-bold">{{ v.stock }}</td>
                <td class="tc num-warn">{{ v.reserved_stock ?? 0 }}</td>
                <td class="tc">
                  <span class="num-avail"
                    :class="{ 'num-avail--low': (v.stock - (v.reserved_stock ?? 0)) <= v.low_stock_threshold }">
                    {{ v.stock - (v.reserved_stock ?? 0) }}
                  </span>
                </td>
                <td class="tc num-mute">{{ v.low_stock_threshold }}</td>

                <td class="tc">
                  <span class="status-pill" :class="statusClass(v)">{{ statusLabel(v) }}</span>
                </td>

                <td class="tr">
                  <div class="row-acts">
                    <q-btn flat round size="xs" icon="add_circle_outline" color="positive"
                      title="Add stock" @click="openRowModal('add', v)" />
                    <q-btn flat round size="xs" icon="remove_circle_outline" color="negative"
                      title="Remove stock" @click="openRowModal('remove', v)" />
                    <q-btn flat round size="xs" icon="lock_outline" color="warning"
                      title="Reserve" @click="openRowModal('reserve', v)" />
                    <q-btn flat round size="xs" icon="settings" color="blue-grey"
                      title="Settings" @click="openSettings(v)" />
                    <q-btn flat round size="xs" icon="history" color="indigo-5"
                      title="Logs" @click="openDrawer(v)" />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═════════════════════ TAB: LOW STOCK ═════════════════════ -->
      <div v-show="activeTab === 'lowstock'">
        <div class="alert-banner">
          <q-icon name="warning_amber" color="amber-7" size="18px" />
          Variants at or below their reorder threshold.
          <q-btn flat no-caps size="sm" label="Refresh" icon="refresh" color="amber-8"
            class="q-ml-auto" :loading="lowStockLoading" @click="fetchLowStock" />
        </div>

        <div class="tbl-wrap">
          <table class="dtbl">
            <thead>
              <tr>
                <th>Product / Variant</th>
                <th>Category</th>
                <th class="tc">Stock</th>
                <th class="tc">Threshold</th>
                <th class="tc">Gap</th>
                <th class="tr">Restock</th>
              </tr>
            </thead>
            <tbody v-if="lowStockLoading">
              <tr><td colspan="6" class="empty-cell"><q-spinner-dots color="amber-6" size="32px" /></td></tr>
            </tbody>
            <tbody v-else-if="lowStockVariants.length === 0">
              <tr><td colspan="6" class="empty-cell good-cell">
                <q-icon name="check_circle" size="36px" color="positive" />
                <div class="empty-msg" style="color:#15803d">All variants are well-stocked!</div>
              </td></tr>
            </tbody>
            <tbody v-else>
              <tr v-for="v in lowStockVariants" :key="v.variant_id"
                class="dtbl__row dtbl__row--warn">
                <td>
                  <div class="cell-title">{{ v.product_name }}</div>
                  <div class="cell-sub">{{ v.variant_name }}</div>
                </td>
                <td><span class="cat-tag">{{ v.category_name || '—' }}</span></td>
                <td class="tc"><span class="num-bold" style="color:#dc2626">{{ v.stock }}</span></td>
                <td class="tc"><span class="num-mute">{{ v.low_stock_threshold }}</span></td>
                <td class="tc">
                  <span class="gap-chip">−{{ v.low_stock_threshold - v.stock }}</span>
                </td>
                <td class="tr">
                  <q-btn unelevated no-caps size="sm" label="Restock" icon="add"
                    color="primary" style="font-size:11px;padding:4px 10px"
                    @click="openRowModal('add', { id: v.variant_id, product_name: v.product_name, variant_name: v.variant_name, stock: v.stock })" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ════════════════════════ TAB: LOGS ════════════════════════ -->
      <div v-show="activeTab === 'logs'">
        <div class="toolbar">
          <div class="toolbar__search">
            <q-icon name="search" size="15px" color="grey-5" />
            <input v-model="logSearch" class="toolbar__input" placeholder="Filter logs…" />
          </div>
          <select v-model="logChangeType" class="sel" @change="fetchLogs">
            <option value="">All Types</option>
            <option v-for="ct in changeTypes" :key="ct" :value="ct">{{ ct }}</option>
          </select>
          <select v-model="logLimit" class="sel sel--sm" @change="fetchLogs">
            <option :value="50">50</option>
            <option :value="100">100</option>
            <option :value="200">200</option>
            <option :value="500">500</option>
          </select>
          <q-btn flat round dense icon="refresh" size="sm" color="grey-6"
            :loading="logsLoading" @click="fetchLogs" />
        </div>

        <div class="tbl-wrap">
          <table class="dtbl">
            <thead>
              <tr>
                <th>#</th>
                <th>Variant</th>
                <th>Type</th>
                <th class="tc">Qty</th>
                <th>Ref</th>
                <th>Notes</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody v-if="logsLoading">
              <tr><td colspan="7" class="empty-cell"><q-spinner-dots color="blue-5" size="32px" /></td></tr>
            </tbody>
            <tbody v-else-if="filteredLogs.length === 0">
              <tr><td colspan="7" class="empty-cell">
                <q-icon name="history" size="36px" color="grey-4" />
                <div class="empty-msg">No logs found</div>
              </td></tr>
            </tbody>
            <tbody v-else>
              <tr v-for="log in filteredLogs" :key="log.id" class="dtbl__row">
                <td><code class="id-tag">#{{ log.id }}</code></td>
                <td>
                  <div class="cell-title" style="font-size:12px">
                    {{ log.product_name || `Variant #${log.variant_id}` }}
                  </div>
                  <div class="cell-sub">{{ log.variant_name }}</div>
                </td>
                <td>
                  <span class="log-type-pill" :class="`ltp--${(log.change_type||'').toLowerCase()}`">
                    <q-icon :name="logIcon(log.change_type)" size="10px" />
                    {{ log.change_type }}
                  </span>
                </td>
                <td class="tc">
                  <span class="log-qty"
                    :class="isDeduction(log.change_type) ? 'log-qty--neg' : 'log-qty--pos'">
                    {{ isDeduction(log.change_type) ? '−' : '+' }}{{ log.quantity }}
                  </span>
                </td>
                <td>
                  <code v-if="log.reference_id" class="sku-tag">#{{ log.reference_id }}</code>
                  <span v-else class="text-grey-4">—</span>
                </td>
                <td><span class="note-text">{{ log.notes || '—' }}</span></td>
                <td><span class="date-text">{{ fmtDate(log.created_at) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══════════════════ TAB: ADJUSTMENTS ═════════════════════ -->
      <div v-show="activeTab === 'adjustments'">
        <div class="adj-grid">

          <!-- ADD -->
          <div class="adj-card adj-card--add">
            <div class="adj-card__hdr">
              <div class="adj-icon adj-icon--add"><q-icon name="add_circle" size="20px" /></div>
              <div>
                <div class="adj-card__title">Add Stock</div>
                <div class="adj-card__sub">Restock · New shipment · Return</div>
              </div>
            </div>
            <div class="adj-form">
              <div class="fld fld--full">
                <label>Variant <span class="req">*</span></label>
                <select v-model="addForm.variant_id" class="sel sel--full">
                  <option value="" disabled>Select variant…</option>
                  <option v-for="v in variantOptions" :key="v.id" :value="v.id">{{ v.label }}</option>
                </select>
              </div>
              <div class="fld">
                <label>Quantity <span class="req">*</span></label>
                <input v-model.number="addForm.quantity" type="number" min="1" class="inp" placeholder="50" />
              </div>
              <div class="fld">
                <label>Change Type <span class="req">*</span></label>
                <select v-model="addForm.change_type" class="sel sel--full">
                  <option value="RESTOCK">RESTOCK</option>
                  <option value="ADJUSTMENT">ADJUSTMENT</option>
                  <option value="RETURN">RETURN</option>
                </select>
              </div>
              <div class="fld">
                <label>Reference ID <span class="opt">(optional)</span></label>
                <input v-model.number="addForm.reference_id" type="number" class="inp" placeholder="e.g. order ID" />
              </div>
              <div class="fld fld--full">
                <label>Notes <span class="opt">(optional)</span></label>
                <input v-model="addForm.notes" class="inp" placeholder="e.g. April shipment batch" />
              </div>
              <q-btn unelevated no-caps class="adj-submit adj-submit--add"
                icon="add" label="Add Stock"
                :loading="addLoading"
                :disable="!addForm.variant_id || addForm.quantity < 1"
                @click="submitAdd" />
            </div>
          </div>

          <!-- REMOVE -->
          <div class="adj-card adj-card--remove">
            <div class="adj-card__hdr">
              <div class="adj-icon adj-icon--remove"><q-icon name="remove_circle" size="20px" /></div>
              <div>
                <div class="adj-card__title">Remove Stock</div>
                <div class="adj-card__sub">Damage · Shrinkage · Correction</div>
              </div>
            </div>
            <div class="adj-form">
              <div class="fld fld--full">
                <label>Variant <span class="req">*</span></label>
                <select v-model="removeForm.variant_id" class="sel sel--full">
                  <option value="" disabled>Select variant…</option>
                  <option v-for="v in variantOptions" :key="v.id" :value="v.id">{{ v.label }}</option>
                </select>
              </div>
              <div class="fld">
                <label>Quantity <span class="req">*</span></label>
                <input v-model.number="removeForm.quantity" type="number" min="1" class="inp" placeholder="5" />
              </div>
              <div class="fld">
                <label>Change Type <span class="req">*</span></label>
                <select v-model="removeForm.change_type" class="sel sel--full">
                  <option value="ADJUSTMENT">ADJUSTMENT</option>
                  <option value="ORDER">ORDER</option>
                  <option value="EXCHANGE">EXCHANGE</option>
                </select>
              </div>
              <div class="fld">
                <label>Reference ID <span class="opt">(optional)</span></label>
                <input v-model.number="removeForm.reference_id" type="number" class="inp" placeholder="e.g. order ID" />
              </div>
              <div class="fld fld--full">
                <label>Reason / Notes <span class="req">*</span></label>
                <input v-model="removeForm.notes" class="inp" placeholder="e.g. Damaged goods found in warehouse" />
              </div>
              <q-btn unelevated no-caps class="adj-submit adj-submit--remove"
                icon="remove" label="Remove Stock"
                :loading="removeLoading"
                :disable="!removeForm.variant_id || removeForm.quantity < 1 || !removeForm.notes"
                @click="submitRemove" />
            </div>
          </div>

          <!-- RESERVE -->
          <div class="adj-card adj-card--reserve">
            <div class="adj-card__hdr">
              <div class="adj-icon adj-icon--reserve"><q-icon name="lock_outline" size="20px" /></div>
              <div>
                <div class="adj-card__title">Reserve Stock</div>
                <div class="adj-card__sub">Hold units pending fulfillment</div>
              </div>
            </div>
            <div class="adj-form">
              <div class="fld fld--full">
                <label>Variant <span class="req">*</span></label>
                <select v-model="reserveForm.variant_id" class="sel sel--full">
                  <option value="" disabled>Select variant…</option>
                  <option v-for="v in variantOptions" :key="v.id" :value="v.id">{{ v.label }}</option>
                </select>
              </div>
              <div class="fld">
                <label>Quantity <span class="req">*</span></label>
                <input v-model.number="reserveForm.quantity" type="number" min="1" class="inp" placeholder="10" />
              </div>
              <div class="fld">
                <label>Reference ID <span class="opt">(optional)</span></label>
                <input v-model.number="reserveForm.reference_id" type="number" class="inp" placeholder="bulk order ID" />
              </div>
              <div class="fld fld--full">
                <label>Notes <span class="opt">(optional)</span></label>
                <input v-model="reserveForm.notes" class="inp" placeholder="e.g. Bulk order #BO-001" />
              </div>
              <q-btn unelevated no-caps class="adj-submit adj-submit--reserve"
                icon="lock_outline" label="Reserve Stock"
                :loading="reserveLoading"
                :disable="!reserveForm.variant_id || reserveForm.quantity < 1"
                @click="submitReserve" />
            </div>
          </div>

          <!-- RELEASE -->
          <div class="adj-card adj-card--release">
            <div class="adj-card__hdr">
              <div class="adj-icon adj-icon--release"><q-icon name="lock_open" size="20px" /></div>
              <div>
                <div class="adj-card__title">Release Reserved</div>
                <div class="adj-card__sub">Free held units back to available</div>
              </div>
            </div>
            <div class="adj-form">
              <div class="fld fld--full">
                <label>Variant <span class="req">*</span></label>
                <select v-model="releaseForm.variant_id" class="sel sel--full">
                  <option value="" disabled>Select variant…</option>
                  <option v-for="v in variantOptions" :key="v.id" :value="v.id">{{ v.label }}</option>
                </select>
              </div>
              <div class="fld">
                <label>Quantity <span class="req">*</span></label>
                <input v-model.number="releaseForm.quantity" type="number" min="1" class="inp" placeholder="5" />
              </div>
              <div class="fld">
                <label>Reference ID <span class="opt">(optional)</span></label>
                <input v-model.number="releaseForm.reference_id" type="number" class="inp" placeholder="order ID" />
              </div>
              <div class="fld fld--full">
                <label>Notes <span class="opt">(optional)</span></label>
                <input v-model="releaseForm.notes" class="inp" placeholder="e.g. Order cancelled — releasing hold" />
              </div>
              <q-btn unelevated no-caps class="adj-submit adj-submit--release"
                icon="lock_open" label="Release Stock"
                :loading="releaseLoading"
                :disable="!releaseForm.variant_id || releaseForm.quantity < 1"
                @click="submitRelease" />
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ═══════════════════════ VARIANT DRAWER ═══════════════════════ -->
    <q-dialog v-model="drawerOpen" position="right" full-height>
      <q-card style="width:420px;max-width:95vw;height:100%;border-radius:0;display:flex;flex-direction:column">
        <div class="drawer-hdr">
          <div>
            <div style="font-weight:700;font-size:15px;color:#0f1520">{{ drawerVariant?.product_name }}</div>
            <div style="font-size:12px;color:#9ca3af;margin-top:2px">
              {{ drawerVariant?.variant_name }} · {{ drawerVariant?.sku }}
            </div>
          </div>
          <q-btn flat round dense icon="close" color="grey-5" v-close-popup />
        </div>

        <div style="flex:1;overflow-y:auto;padding:18px" v-if="drawerVariant">
          <!-- stats row -->
          <div class="drawer-stats">
            <div class="dstat"><div class="dstat__val">{{ drawerVariant.stock }}</div><div class="dstat__lbl">Total</div></div>
            <div class="dstat"><div class="dstat__val" style="color:#d97706">{{ drawerVariant.reserved_stock ?? 0 }}</div><div class="dstat__lbl">Reserved</div></div>
            <div class="dstat"><div class="dstat__val" style="color:#15803d">{{ (drawerVariant.stock||0) - (drawerVariant.reserved_stock||0) }}</div><div class="dstat__lbl">Available</div></div>
            <div class="dstat"><div class="dstat__val" style="color:#1d4ed8">{{ drawerVariant.low_stock_threshold }}</div><div class="dstat__lbl">Threshold</div></div>
          </div>

          <div class="drawer-section-title">Recent Activity</div>
          <div v-if="drawerLogsLoading" style="text-align:center;padding:20px"><q-spinner-dots color="blue-5" size="28px" /></div>
          <div v-else-if="drawerLogs.length === 0" style="color:#9ca3af;font-size:13px;padding:12px 0">No activity logged yet.</div>
          <div v-else class="drawer-logs">
            <div v-for="log in drawerLogs" :key="log.id" class="drawer-log-row">
              <span class="log-type-pill" :class="`ltp--${(log.change_type||'').toLowerCase()}`" style="font-size:10px">
                <q-icon :name="logIcon(log.change_type)" size="10px" />
                {{ log.change_type }}
              </span>
              <span class="log-qty" :class="isDeduction(log.change_type) ? 'log-qty--neg' : 'log-qty--pos'">
                {{ isDeduction(log.change_type) ? '−' : '+' }}{{ log.quantity }}
              </span>
              <span class="note-text" style="flex:1">{{ log.notes || '—' }}</span>
              <span class="date-text">{{ fmtDate(log.created_at) }}</span>
            </div>
          </div>

          <div class="drawer-section-title" style="margin-top:20px">Quick Actions</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <q-btn unelevated no-caps size="sm" color="positive" icon="add" label="Add"
              @click="openRowModal('add', drawerVariant)" />
            <q-btn unelevated no-caps size="sm" color="negative" icon="remove" label="Remove"
              @click="openRowModal('remove', drawerVariant)" />
            <q-btn unelevated no-caps size="sm" color="warning" icon="lock_outline" label="Reserve"
              @click="openRowModal('reserve', drawerVariant)" />
          </div>
        </div>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════ SETTINGS MODAL ══════════════════════ -->
    <q-dialog v-model="settingsOpen" persistent>
      <q-card class="modal-card">
        <div class="modal-hdr">
          <div class="modal-title">Update Stock Settings</div>
          <div class="modal-sub">{{ settingsForm._label }}</div>
          <q-btn flat round dense icon="close" color="grey-5" v-close-popup />
        </div>
        <div style="padding:18px 20px">
          <div class="fld" style="margin-bottom:14px">
            <label>Stock Override</label>
            <input v-model.number="settingsForm.stock" type="number" min="0" class="inp" placeholder="Current stock" />
            <span class="fld-hint">Set exact stock (use carefully)</span>
          </div>
          <div class="fld">
            <label>Low Stock Threshold</label>
            <input v-model.number="settingsForm.low_stock_threshold" type="number" min="0" class="inp" placeholder="e.g. 10" />
            <span class="fld-hint">Alert trigger level</span>
          </div>
        </div>
        <div class="modal-footer">
          <q-btn flat no-caps label="Cancel" color="grey-6" v-close-popup />
          <q-btn unelevated no-caps label="Save Settings" color="primary"
            :loading="settingsLoading" @click="submitSettings" />
        </div>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════ QUICK / ROW MODAL ══════════════════ -->
    <q-dialog v-model="quickOpen" persistent>
      <q-card class="modal-card">
        <div class="modal-hdr">
          <div class="modal-title">{{ quickConfig.title }}</div>
          <div v-if="quickForm._label" class="modal-sub">{{ quickForm._label }}</div>
          <q-btn flat round dense icon="close" color="grey-5" v-close-popup />
        </div>
        <div style="padding:18px 20px">
          <!-- variant select only shown when no pre-selected variant -->
          <div v-if="!quickForm._preSelected" class="fld" style="margin-bottom:14px">
            <label>Variant <span class="req">*</span></label>
            <select v-model="quickForm.variant_id" class="sel sel--full">
              <option value="" disabled>Select variant…</option>
              <option v-for="v in variantOptions" :key="v.id" :value="v.id">{{ v.label }}</option>
            </select>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
            <div class="fld">
              <label>Quantity <span class="req">*</span></label>
              <input v-model.number="quickForm.quantity" type="number" min="1" class="inp" />
            </div>
            <div class="fld" v-if="quickConfig.showChangeType">
              <label>Change Type</label>
              <select v-model="quickForm.change_type" class="sel sel--full">
                <option v-for="ct in quickConfig.changeTypes" :key="ct" :value="ct">{{ ct }}</option>
              </select>
            </div>
            <div class="fld">
              <label>Ref ID <span class="opt">(opt)</span></label>
              <input v-model.number="quickForm.reference_id" type="number" class="inp" placeholder="e.g. 42" />
            </div>
          </div>
          <div class="fld">
            <label>{{ quickConfig.notesLabel }}
              <span :class="quickConfig.notesRequired ? 'req' : 'opt'">
                {{ quickConfig.notesRequired ? '*' : '(optional)' }}
              </span>
            </label>
            <input v-model="quickForm.notes" class="inp" :placeholder="quickConfig.notesPlaceholder" />
          </div>
        </div>
        <div class="modal-footer">
          <q-btn flat no-caps label="Cancel" color="grey-6" v-close-popup />
          <q-btn unelevated no-caps :label="quickConfig.btnLabel" :color="quickConfig.btnColor"
            :loading="quickLoading"
            :disable="!quickForm.variant_id || quickForm.quantity < 1"
            @click="submitQuick" />
        </div>
      </q-card>
    </q-dialog>

    <!-- ═══════════════════════════ TOAST ═══════════════════════════ -->
    <transition name="tslide">
      <div v-if="toast.show" class="toast" :class="`toast--${toast.type}`">
        <q-icon :name="toast.type === 'ok' ? 'check_circle' : 'error'" size="16px" />
        {{ toast.msg }}
        <button class="toast-x" @click="toast.show = false">×</button>
      </div>
    </transition>

  </q-page>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from 'boot/axios'

/* =========================================================
   AXIOS HELPER
========================================================= */
async function inv(path, opts = {}) {
  try {
    const res = await api({
      url: `/admin/inventory${path}`,
      method: (opts.method || 'GET').toLowerCase(),
      params: opts.params || {},
      data: opts.data || {}
    })
    return res.data
  } catch (err) {
    const detail = err?.response?.data?.detail
    let msg = 'Network error'

    if (typeof detail === 'string') msg = detail
    else if (Array.isArray(detail)) msg = detail.map(x => x.msg).join(', ')
    else if (err?.response?.status) msg = `Request failed (${err.response.status})`

    throw new Error(msg)
  }
}

/* =========================================================
   CONSTANTS
========================================================= */
const changeTypes = [
  'ORDER',
  'ORDER_CANCELLED',
  'RETURN',
  'RESTOCK',
  'EXCHANGE',
  'ADJUSTMENT',
  'DAMAGED'
]

const DEDUCTION_SET = new Set([
  'ORDER',
  'EXCHANGE',
  'ADJUSTMENT',
  'DAMAGED'
])

const tabs = [
  { key: 'variants', label: 'All Variants', icon: 'inventory_2' },
  { key: 'lowstock', label: 'Low Stock', icon: 'warning_amber' },
  { key: 'logs', label: 'Logs', icon: 'history' },
  { key: 'adjustments', label: 'Adjustments', icon: 'tune' }
]

/* =========================================================
   STATE
========================================================= */
const activeTab = ref('variants')

const variants = ref([])
const variantsLoading = ref(false)
const variantSearch = ref('')
const lowStockOnly = ref(false)

const lowStockVariants = ref([])
const lowStockLoading = ref(false)

const logs = ref([])
const logsLoading = ref(false)
const logSearch = ref('')
const logChangeType = ref('')
const logLimit = ref(100)

const drawerOpen = ref(false)
const drawerVariant = ref(null)
const drawerLogs = ref([])
const drawerLogsLoading = ref(false)

const stats = ref({
  lowStock: 0,
  totalVariants: 0,
  inStock: 0
})

let searchTimer = null

/* =========================================================
   FORMS
========================================================= */
const addForm = ref({
  variant_id: '',
  quantity: 1,
  change_type: 'RESTOCK',
  reference_id: '',
  notes: ''
})

const removeForm = ref({
  variant_id: '',
  quantity: 1,
  change_type: 'ADJUSTMENT',
  reference_id: '',
  notes: ''
})

const reserveForm = ref({
  variant_id: '',
  quantity: 1,
  reference_id: '',
  notes: ''
})

const releaseForm = ref({
  variant_id: '',
  quantity: 1,
  reference_id: '',
  notes: ''
})

const addLoading = ref(false)
const removeLoading = ref(false)
const reserveLoading = ref(false)
const releaseLoading = ref(false)

/* SETTINGS */
const settingsOpen = ref(false)
const settingsLoading = ref(false)

const settingsForm = ref({
  stock: 0,
  reserved_stock: 0,
  low_stock_threshold: 0,
  _id: null,
  _label: ''
})

/* QUICK MODAL */
const quickOpen = ref(false)
const quickLoading = ref(false)
const quickType = ref('add')

const quickForm = ref({
  variant_id: '',
  quantity: 1,
  change_type: 'RESTOCK',
  reference_id: '',
  notes: '',
  _label: '',
  _preSelected: false
})

/* TOAST */
const toast = ref({
  show: false,
  type: 'ok',
  msg: ''
})

/* =========================================================
   COMPUTED
========================================================= */
const variantOptions = computed(() =>
  variants.value.map(v => ({
    id: v.id,
    label: `${v.product_name || v.name || 'Product'} — ${v.variant_name || 'Variant'}`
  }))
)

const filteredLogs = computed(() => {
  const q = logSearch.value.toLowerCase().trim()
  if (!q) return logs.value
  return logs.value.filter(l =>
    (l.product_name || '').toLowerCase().includes(q) ||
    (l.variant_name || '').toLowerCase().includes(q) ||
    (l.notes || '').toLowerCase().includes(q) ||
    (l.reference_type || '').toLowerCase().includes(q) ||
    String(l.id).includes(q)
  )
})

const quickConfig = computed(() => ({
  add: {
    title: 'Add Stock',
    btnLabel: 'Add Stock',
    btnColor: 'positive',
    showChangeType: true,
    changeTypes: ['RESTOCK', 'RETURN'],
    notesLabel: 'Notes',
    notesRequired: false,
    notesPlaceholder: 'shipment / supplier notes'
  },
  remove: {
    title: 'Remove Stock',
    btnLabel: 'Remove Stock',
    btnColor: 'negative',
    showChangeType: true,
    changeTypes: ['ADJUSTMENT', 'EXCHANGE'],
    notesLabel: 'Reason',
    notesRequired: true,
    notesPlaceholder: 'damaged / shrinkage'
  },
  reserve: {
    title: 'Reserve Stock',
    btnLabel: 'Reserve',
    btnColor: 'warning',
    showChangeType: false,
    notesLabel: 'Notes',
    notesRequired: false,
    notesPlaceholder: 'bulk order hold'
  },
  release: {
    title: 'Release Reserved',
    btnLabel: 'Release',
    btnColor: 'info',
    showChangeType: false,
    notesLabel: 'Notes',
    notesRequired: false,
    notesPlaceholder: 'cancelled order'
  }
}[quickType.value]))

/* =========================================================
   FETCHERS
========================================================= */
async function fetchVariants() {
  variantsLoading.value = true
  try {
    const params = {}
    if (variantSearch.value.trim()) params.search = variantSearch.value.trim()
    if (lowStockOnly.value) params.low_stock_only = true

    const data = await inv('/', { method: 'GET', params })

    variants.value = Array.isArray(data)
      ? data
      : Array.isArray(data.items)
      ? data.items
      : []

    recalcStats()
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    variantsLoading.value = false
  }
}

async function fetchLowStock() {
  lowStockLoading.value = true
  try {
    const data = await inv('/low-stock')

    lowStockVariants.value = Array.isArray(data)
      ? data
      : Array.isArray(data.items)
      ? data.items
      : []

    stats.value.lowStock = lowStockVariants.value.length
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    lowStockLoading.value = false
  }
}

async function fetchLogs() {
  logsLoading.value = true
  try {
    const params = { limit: logLimit.value }
    if (logChangeType.value) params.change_type = logChangeType.value

    const data = await inv('/logs/all', { method: 'GET', params })

    logs.value = Array.isArray(data)
      ? data
      : Array.isArray(data.items)
      ? data.items
      : []
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    logsLoading.value = false
  }
}

async function fetchDrawerLogs(id) {
  drawerLogsLoading.value = true
  try {
    const data = await inv(`/logs/${id}`)
    drawerLogs.value = Array.isArray(data)
      ? data
      : Array.isArray(data.items)
      ? data.items
      : []
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    drawerLogsLoading.value = false
  }
}

/* =========================================================
   STATS
========================================================= */
function recalcStats() {
  stats.value.totalVariants = variants.value.length
  stats.value.inStock = variants.value.filter(v => Number(v.stock) > 0).length
  stats.value.lowStock = variants.value.filter(
    v => Number(v.stock) <= Number(v.low_stock_threshold)
  ).length
}

/* =========================================================
   PAYLOAD BUILDER — FIXED
========================================================= */
function buildPayload(form, mode = '') {
  // Determine change_type based on mode
  let type = form.change_type

  if (mode === 'reserve') type = 'ORDER'
  if (mode === 'release') type = 'ORDER_CANCELLED'

  // CRITICAL FIX: Remove stock must NEVER send DAMAGED
  // Always map remove operations to ADJUSTMENT if DAMAGED slips through
  if (mode === 'remove' && (!type || type === 'DAMAGED')) {
    type = 'ADJUSTMENT'
  }

  // Resolve variant_id with fallbacks
  const variantId = Number(form.variant_id ?? form.id ?? form.variant?.id ?? 0)

  const payload = {
    variant_id: variantId,
    quantity: Number(form.quantity) || 1,
    change_type: type,
    reference_id: form.reference_id ? Number(form.reference_id) : null,
    notes: form.notes?.trim() || ''
  }

  return payload
}

/* =========================================================
   REFRESH ALL
========================================================= */
async function refresh() {
  await Promise.all([
    fetchVariants(),
    fetchLowStock(),
    fetchLogs()
  ])
}

/* =========================================================
   RESET QUICK FORM
========================================================= */
function resetQuick() {
  quickForm.value = {
    variant_id: '',
    quantity: 1,
    change_type: 'RESTOCK',
    reference_id: '',
    notes: '',
    _label: '',
    _preSelected: false
  }
}

/* =========================================================
   SUBMITS — ADJUSTMENTS TAB
========================================================= */
async function submitAdd() {
  addLoading.value = true
  try {
    const payload = buildPayload(addForm.value, 'add')
    await inv('/add-stock', { method: 'POST', data: payload })
    showToast('Stock added')
    await refresh()
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    addLoading.value = false
  }
}

async function submitRemove() {
  removeLoading.value = true
  try {
    // Force ADJUSTMENT — never send DAMAGED
    const safeForm = {
      ...removeForm.value,
      change_type: ['ADJUSTMENT', 'EXCHANGE'].includes(removeForm.value.change_type)
        ? removeForm.value.change_type
        : 'ADJUSTMENT'
    }
    const payload = buildPayload(safeForm, 'remove')
    await inv('/remove-stock', { method: 'POST', data: payload })
    showToast('Stock removed')
    await refresh()
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    removeLoading.value = false
  }
}

async function submitReserve() {
  reserveLoading.value = true
  try {
    const payload = buildPayload(reserveForm.value, 'reserve')
    await inv('/reserve-stock', { method: 'POST', data: payload })
    showToast('Reserved successfully')
    await refresh()
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    reserveLoading.value = false
  }
}

async function submitRelease() {
  releaseLoading.value = true
  try {
    const payload = buildPayload(releaseForm.value, 'release')
    await inv('/release-stock', { method: 'POST', data: payload })
    showToast('Released successfully')
    await refresh()
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    releaseLoading.value = false
  }
}

async function submitSettings() {
  settingsLoading.value = true
  try {
    await inv(`/${settingsForm.value._id}`, {
      method: 'PUT',
      data: {
        stock: Number(settingsForm.value.stock),
        reserved_stock: Number(settingsForm.value.reserved_stock),
        low_stock_threshold: Number(settingsForm.value.low_stock_threshold)
      }
    })
    showToast('Settings updated')
    settingsOpen.value = false
    await refresh()
  } catch (e) {
    showToast(e.message, 'err')
  } finally {
    settingsLoading.value = false
  }
}

/* =========================================================
   SUBMIT QUICK MODAL — FULLY FIXED
========================================================= */
async function submitQuick() {
  quickLoading.value = true

  // Debug logs
  console.log('quickType =>', quickType.value)
  console.log('quickForm =>', { ...quickForm.value })

  const endpointMap = {
    add: '/add-stock',
    remove: '/remove-stock',
    reserve: '/reserve-stock',
    release: '/release-stock'
  }

  const endpoint = endpointMap[quickType.value]

  if (!endpoint) {
    showToast('Unknown action type', 'err')
    quickLoading.value = false
    return
  }

  try {
    // For remove: sanitize change_type — never allow DAMAGED
    if (quickType.value === 'remove') {
      if (!quickForm.value.change_type || quickForm.value.change_type === 'DAMAGED') {
        quickForm.value.change_type = 'ADJUSTMENT'
      }
    }

    const payload = buildPayload(quickForm.value, quickType.value)

    console.log('payload =>', payload)

    // Validate variant_id
    if (!payload.variant_id || payload.variant_id <= 0) {
      showToast('Invalid variant selected', 'err')
      return
    }

    await inv(endpoint, { method: 'POST', data: payload })

    showToast('Success')
    quickOpen.value = false
    drawerOpen.value = false
    resetQuick()

    await refresh()
  } catch (e) {
    console.error('submitQuick error =>', e)
    showToast(e.message, 'err')
  } finally {
    quickLoading.value = false
  }
}

/* =========================================================
   UI HANDLERS
========================================================= */
function switchTab(key) {
  activeTab.value = key
  if (key === 'lowstock') fetchLowStock()
  if (key === 'logs') fetchLogs()
}

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchVariants, 400)
}

function clearSearch() {
  variantSearch.value = ''
  fetchVariants()
}

function openQuickModal(type) {
  quickType.value = type
  resetQuick()
  // Pre-set safe change_type defaults per action
  if (type === 'remove') quickForm.value.change_type = 'ADJUSTMENT'
  if (type === 'add') quickForm.value.change_type = 'RESTOCK'
  quickOpen.value = true
}

/* FIXED: openRowModal — resolves variant id correctly */
function openRowModal(type, v) {
  quickType.value = type

  // Resolve id with all possible fallbacks
  const resolvedId = v.id ?? v.variant_id ?? v.variant?.id ?? ''

  // Safe change_type per action
  let defaultChangeType = 'RESTOCK'
  if (type === 'remove') defaultChangeType = 'ADJUSTMENT'
  if (type === 'reserve') defaultChangeType = 'ORDER'
  if (type === 'release') defaultChangeType = 'ORDER_CANCELLED'

  quickForm.value = {
    variant_id: resolvedId,
    quantity: 1,
    change_type: defaultChangeType,
    reference_id: '',
    notes: '',
    _label: `${v.product_name || v.name || ''} — ${v.variant_name || ''}`.trim(),
    _preSelected: true
  }

  console.log('openRowModal => variant_id resolved:', resolvedId, 'for type:', type)

  quickOpen.value = true
}

function openSettings(v) {
  settingsForm.value = {
    stock: v.stock,
    reserved_stock: v.reserved_stock || 0,
    low_stock_threshold: v.low_stock_threshold,
    _id: v.id,
    _label: `${v.product_name} — ${v.variant_name}`
  }
  settingsOpen.value = true
}

async function openDrawer(v) {
  drawerVariant.value = v
  drawerOpen.value = true
  await fetchDrawerLogs(v.id)
}

/* =========================================================
   HELPERS
========================================================= */
function statusLabel(v) {
  const available = Number(v.stock) - Number(v.reserved_stock || 0)
  if (available <= 0) return 'Out of Stock'
  if (available <= Number(v.low_stock_threshold)) return 'Low Stock'
  return 'In Stock'
}

function statusClass(v) {
  const available = Number(v.stock) - Number(v.reserved_stock || 0)
  if (available <= 0) return 'sp--out'
  if (available <= Number(v.low_stock_threshold)) return 'sp--low'
  return 'sp--in'
}

function isDeduction(t) {
  return DEDUCTION_SET.has(t)
}

function logIcon(t) {
  return {
    ORDER: 'shopping_cart',
    ORDER_CANCELLED: 'cancel',
    RETURN: 'assignment_return',
    RESTOCK: 'add_circle',
    EXCHANGE: 'swap_horiz',
    ADJUSTMENT: 'tune',
    DAMAGED: 'warning'
  }[t] || 'help'
}

function fmtDate(v) {
  if (!v) return '—'
  return new Date(v).toLocaleString('en-IN')
}

function showToast(msg, type = 'ok') {
  toast.value = { show: true, type, msg }
  setTimeout(() => { toast.value.show = false }, 3500)
}

/* =========================================================
   MOUNT
========================================================= */
onMounted(async () => {
  await refresh()
})
</script>

<style scoped>
/* ── PAGE ── */
.inv-page { font-family:'IBM Plex Sans','Segoe UI',sans-serif; background:#f4f5f7; min-height:100vh; color:#1a1d23; }

/* ── HEADER ── */
.inv-header {
  background:#fff; border-bottom:1px solid #e0e4ea;
  display:flex; align-items:center; gap:20px; flex-wrap:wrap;
  padding:14px 24px; position:sticky; top:0; z-index:50;
}
.inv-header__eyebrow { font-size:10px; font-weight:700; letter-spacing:.1em; color:#9ca3af; margin-bottom:2px; }
.inv-header__title   { font-family:'IBM Plex Mono','Courier New',monospace; font-size:20px; font-weight:700; color:#0f1520; margin:0; line-height:1; }
.inv-header__stats   { display:flex; gap:6px; flex-wrap:wrap; margin-left:auto; }
.inv-header__actions { display:flex; gap:8px; }

.stat-chip { display:inline-flex; align-items:center; gap:5px; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:700; border:1px solid; }
.stat-chip--warn  { background:#fff7ed; color:#c2410c; border-color:#fed7aa; }
.stat-chip--blue  { background:#eff6ff; color:#1d4ed8; border-color:#bfdbfe; }
.stat-chip--green { background:#f0fdf4; color:#15803d; border-color:#bbf7d0; }

.hdr-btn { font-size:12px !important; font-weight:600 !important; border-radius:8px !important; padding:6px 13px !important; }
.hdr-btn--ghost { border:1px solid #d1d5db !important; color:#374151 !important; }
.hdr-btn--red   { background:#dc2626 !important; color:#fff !important; }
.hdr-btn--red:hover { background:#b91c1c !important; }
.hdr-btn--blue  { background:#1d4ed8 !important; color:#fff !important; }
.hdr-btn--blue:hover { background:#1e40af !important; }

/* ── TABS ── */
.inv-tabs-bar { display:flex; gap:0; border-bottom:2px solid #e0e4ea; background:#fff; overflow-x:auto; padding:0 24px; }
.inv-tab {
  display:inline-flex; align-items:center; gap:5px; padding:10px 14px;
  font-size:12px; font-weight:600; color:#6b7a94;
  background:transparent; border:none; border-bottom:2px solid transparent;
  margin-bottom:-2px; cursor:pointer; border-radius:6px 6px 0 0;
  transition:all .15s; white-space:nowrap;
}
.inv-tab:hover { color:#1d4ed8; background:#f8fbff; }
.inv-tab--active { color:#1d4ed8; border-bottom-color:#1d4ed8; background:#f8fbff; }
.tab-badge { background:#dc2626; color:#fff; font-size:10px; font-weight:700; padding:1px 5px; border-radius:99px; }

/* ── BODY ── */
.inv-body { max-width:1440px; margin:0 auto; padding:20px 24px; }

/* ── TOOLBAR ── */
.toolbar { display:flex; align-items:center; gap:10px; margin-bottom:14px; flex-wrap:wrap; }
.toolbar__search {
  display:flex; align-items:center; gap:7px; flex:1; min-width:200px;
  background:#f8fafc; border:1px solid #e0e4ea; border-radius:8px; padding:6px 11px;
}
.toolbar__input { flex:1; border:none; outline:none; background:transparent; font-family:inherit; font-size:13px; color:#1a1d23; }
.toolbar__input::placeholder { color:#9ca3af; }

.toggle-wrap { display:inline-flex; align-items:center; gap:7px; cursor:pointer; }
.toggle-wrap input { display:none; }
.toggle-track { width:32px; height:17px; background:#d1d5db; border-radius:99px; position:relative; transition:background .2s; flex-shrink:0; }
.toggle-track::after { content:''; position:absolute; top:2px; left:2px; width:13px; height:13px; background:#fff; border-radius:50%; transition:transform .2s; }
.toggle-wrap input:checked + .toggle-track { background:#1d4ed8; }
.toggle-wrap input:checked + .toggle-track::after { transform:translateX(15px); }
.toggle-label { font-size:12px; font-weight:600; color:#4b5563; white-space:nowrap; }

.sel { background:#f8fafc; border:1px solid #e0e4ea; border-radius:7px; padding:6px 9px; font-family:inherit; font-size:12px; color:#1a1d23; outline:none; cursor:pointer; }
.sel:focus { border-color:#93c5fd; }
.sel--full { width:100%; }
.sel--sm   { min-width:70px; }

/* ── TABLE ── */
.tbl-wrap { overflow-x:auto; background:#fff; border:1px solid #e0e4ea; border-radius:10px; }
.dtbl { width:100%; border-collapse:collapse; font-size:13px; }
.dtbl thead tr { background:#f8fafc; border-bottom:1px solid #e0e4ea; }
.dtbl th { padding:9px 13px; text-align:left; font-size:11px; font-weight:700; color:#6b7a94; letter-spacing:.05em; text-transform:uppercase; white-space:nowrap; }
.dtbl td { padding:10px 13px; border-bottom:1px solid #f0f2f5; vertical-align:middle; }
.dtbl__row:last-child td { border-bottom:none; }
.dtbl__row:hover td { background:#fafbff; }
.dtbl__row--warn td { background:#fffbeb; }
.dtbl__row--warn:hover td { background:#fef9c3; }
.tc { text-align:center; }
.tr { text-align:right; }

.empty-cell { text-align:center; padding:52px 20px; color:#9ca3af; }
.empty-msg  { margin-top:8px; font-size:13px; }
.good-cell  { color:#15803d; }

.cell-title  { font-weight:600; color:#0f1520; }
.cell-sub    { font-size:11px; color:#9ca3af; margin-top:1px; }
.sku-tag     { font-family:'IBM Plex Mono',monospace; font-size:11px; background:#f3f4f6; padding:2px 5px; border-radius:4px; color:#4b5563; }
.id-tag      { font-family:'IBM Plex Mono',monospace; font-size:11px; color:#9ca3af; }
.cat-tag     { background:#f3f4f6; color:#4b5563; font-size:11px; padding:2px 7px; border-radius:4px; }
.color-size  { display:flex; align-items:center; gap:5px; }
.color-dot   { width:9px; height:9px; border-radius:50%; border:1px solid rgba(0,0,0,.1); flex-shrink:0; }
.size-pill   { background:#e0e7ff; color:#3730a3; font-size:10px; font-weight:700; padding:1px 5px; border-radius:4px; }
.num-bold    { font-weight:700; font-size:14px; color:#1a1d23; }
.num-warn    { font-weight:600; color:#d97706; }
.num-avail   { font-weight:700; color:#15803d; }
.num-avail--low { color:#dc2626; }
.num-mute    { color:#9ca3af; font-size:12px; }
.gap-chip    { font-family:'IBM Plex Mono',monospace; font-weight:700; color:#dc2626; }
.note-text   { font-size:12px; color:#6b7a94; }
.date-text   { font-size:11px; color:#9ca3af; white-space:nowrap; }

.status-pill { display:inline-block; font-size:10px; font-weight:700; padding:2px 8px; border-radius:99px; }
.sp--in  { background:#dcfce7; color:#15803d; }
.sp--low { background:#fef9c3; color:#a16207; }
.sp--out { background:#fee2e2; color:#dc2626; }

.log-type-pill { display:inline-flex; align-items:center; gap:3px; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; text-transform:uppercase; letter-spacing:.03em; }
.ltp--order          { background:#dbeafe; color:#1e40af; }
.ltp--order_cancelled{ background:#fee2e2; color:#991b1b; }
.ltp--return         { background:#f3e8ff; color:#6b21a8; }
.ltp--restock        { background:#dcfce7; color:#166534; }
.ltp--exchange       { background:#e0f2fe; color:#0369a1; }
.ltp--adjustment     { background:#fff7ed; color:#9a3412; }

.log-qty     { font-family:'IBM Plex Mono',monospace; font-size:13px; font-weight:700; }
.log-qty--pos{ color:#15803d; }
.log-qty--neg{ color:#dc2626; }

.row-acts { display:flex; gap:2px; justify-content:flex-end; }

/* ── ALERT BANNER ── */
.alert-banner { display:flex; align-items:center; gap:8px; padding:10px 16px; background:#fffbeb; border:1px solid #fde68a; border-radius:8px; margin-bottom:12px; font-size:12px; color:#92400e; font-weight:500; }

/* ── ADJUSTMENTS ── */
.adj-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:18px; }
.adj-card { background:#fff; border:1px solid #e0e4ea; border-radius:10px; overflow:hidden; }
.adj-card--add    { border-top:3px solid #22c55e; }
.adj-card--remove { border-top:3px solid #ef4444; }
.adj-card--reserve{ border-top:3px solid #f59e0b; }
.adj-card--release{ border-top:3px solid #06b6d4; }
.adj-card__hdr { display:flex; align-items:center; gap:12px; padding:14px 16px; border-bottom:1px solid #f0f2f5; }
.adj-icon { width:38px; height:38px; border-radius:9px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.adj-icon--add     { background:#dcfce7; color:#15803d; }
.adj-icon--remove  { background:#fee2e2; color:#dc2626; }
.adj-icon--reserve { background:#fef9c3; color:#a16207; }
.adj-icon--release { background:#e0f2fe; color:#0369a1; }
.adj-card__title { font-size:13px; font-weight:700; color:#0f1520; }
.adj-card__sub   { font-size:11px; color:#9ca3af; margin-top:1px; }

.adj-form { padding:14px 16px; display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.fld { display:flex; flex-direction:column; gap:4px; }
.fld--full { grid-column:1 / -1; }
.fld label { font-size:10px; font-weight:700; color:#4b5563; text-transform:uppercase; letter-spacing:.06em; }
.req { color:#dc2626; }
.opt { color:#9ca3af; font-weight:400; text-transform:none; letter-spacing:0; font-size:10px; }
.inp { background:#f8fafc; border:1px solid #e0e4ea; border-radius:6px; padding:6px 9px; font-family:inherit; font-size:12px; color:#1a1d23; outline:none; }
.inp:focus { border-color:#93c5fd; background:#fff; }
.inp::placeholder { color:#9ca3af; }
.fld-hint { font-size:10px; color:#9ca3af; }

.adj-submit { width:100%; grid-column:1 / -1; justify-content:center; font-size:12px !important; font-weight:700 !important; border-radius:7px !important; padding:8px !important; }
.adj-submit--add     { background:#22c55e !important; color:#fff !important; }
.adj-submit--remove  { background:#ef4444 !important; color:#fff !important; }
.adj-submit--reserve { background:#f59e0b !important; color:#fff !important; }
.adj-submit--release { background:#06b6d4 !important; color:#fff !important; }

/* ── DRAWER ── */
.drawer-hdr { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; padding:16px 18px; border-bottom:1px solid #e0e4ea; }
.drawer-stats { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:18px; }
.dstat { background:#f8fafc; border:1px solid #e0e4ea; border-radius:7px; padding:9px 6px; text-align:center; }
.dstat__val { font-family:'IBM Plex Mono',monospace; font-size:18px; font-weight:700; color:#0f1520; }
.dstat__lbl { font-size:9px; color:#9ca3af; text-transform:uppercase; letter-spacing:.05em; margin-top:2px; }
.drawer-section-title { font-size:10px; font-weight:700; color:#6b7a94; text-transform:uppercase; letter-spacing:.08em; margin-bottom:8px; }
.drawer-logs { display:flex; flex-direction:column; gap:7px; }
.drawer-log-row { display:flex; align-items:center; gap:7px; padding:7px 9px; background:#f8fafc; border-radius:6px; font-size:12px; flex-wrap:wrap; }

/* ── MODAL ── */
.modal-card { width:440px; max-width:95vw; border-radius:12px; background:#fff; border:1px solid #e0e4ea; }
.modal-hdr  { display:flex; align-items:flex-start; gap:10px; padding:16px 18px; border-bottom:1px solid #f0f2f5; }
.modal-title { font-size:14px; font-weight:700; color:#0f1520; flex:1; }
.modal-sub   { font-size:11px; color:#9ca3af; margin-top:2px; }
.modal-footer { display:flex; justify-content:flex-end; gap:8px; padding:12px 18px; border-top:1px solid #f0f2f5; }

/* ── TOAST ── */
.toast {
  position:fixed; bottom:22px; right:22px; z-index:9999;
  display:flex; align-items:center; gap:9px; padding:11px 16px;
  border-radius:9px; font-size:13px; font-weight:600; min-width:240px;
  box-shadow:0 8px 24px rgba(0,0,0,.13);
}
.toast--ok  { background:#052e16; color:#86efac; border:1px solid #166534; }
.toast--err { background:#450a0a; color:#fca5a5; border:1px solid #991b1b; }
.toast-x    { margin-left:auto; background:none; border:none; cursor:pointer; font-size:17px; line-height:1; color:inherit; opacity:.7; }
.toast-x:hover { opacity:1; }
.tslide-enter-active,.tslide-leave-active { transition:all .22s ease; }
.tslide-enter-from,.tslide-leave-to       { transform:translateY(14px); opacity:0; }

/* ── RESPONSIVE ── */
@media (max-width:720px) {
  .inv-header { padding:12px 14px; }
  .inv-header__stats { display:none; }
  .inv-body { padding:14px; }
  .adj-grid { grid-template-columns:1fr; }
  .adj-form { grid-template-columns:1fr; }
  .drawer-stats { grid-template-columns:repeat(2,1fr); }
}
</style>