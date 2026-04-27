<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Roles & Permissions</div>
          <div class="text-caption text-blue-7">Manage access control across the system</div>
        </div>
        <q-btn
          label="Add Role"
          color="blue-6"
          unelevated
          no-caps
          icon="add"
          @click="openModal(null)"
        />
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- Roles Table -->
      <q-card class="data-card" flat>
        <q-table
          :rows="roles"
          :columns="columns"
          row-key="id"
          flat
          :rows-per-page-options="[10, 25]"
          class="roles-table"
          wrap-cells
        >
          <!-- ID -->
          <template #body-cell-id="props">
            <q-td :props="props">
              <code class="id-badge">#{{ props.value }}</code>
            </q-td>
          </template>

          <!-- Role icon + name -->
          <template #body-cell-name="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-sm">
                <div class="role-icon-wrap" :style="{ background: iconBg(props.row.color) }">
                  <q-icon :name="props.row.icon" :color="props.row.color" size="18px" />
                </div>
                <span class="text-grey-9 text-weight-medium">{{ props.value }}</span>
              </div>
            </q-td>
          </template>

          <!-- Role name (slug) -->
          <template #body-cell-role_name="props">
            <q-td :props="props">
              <code class="role-slug">{{ props.value }}</code>
            </q-td>
          </template>

          <!-- Permissions chips -->
          <template #body-cell-permissions="props">
            <q-td :props="props">
              <div class="row q-gutter-xs flex-wrap">
                <q-badge
                  v-for="pId in rolePermissions[props.row.id]?.slice(0, 4)"
                  :key="pId"
                  color="grey-2"
                  text-color="blue-8"
                  outline
                  class="perm-chip"
                >
                  {{ permLabel(pId) }}
                </q-badge>
                <q-badge
                  v-if="(rolePermissions[props.row.id]?.length || 0) > 4"
                  color="blue-6"
                  class="perm-chip"
                >
                  +{{ rolePermissions[props.row.id].length - 4 }} more
                </q-badge>
                <span v-if="!rolePermissions[props.row.id]?.length" class="text-caption text-grey-6"
                  >No permissions</span
                >
              </div>
            </q-td>
          </template>

          <!-- Permission count -->
          <template #body-cell-count="props">
            <q-td :props="props">
              <q-chip color="blue-6" text-color="blue-8" dense size="sm" icon="lock">
                {{ rolePermissions[props.row.id]?.length || 0 }} / {{ allPermissions.length }}
              </q-chip>
            </q-td>
          </template>

          <!-- Actions -->
          <template #body-cell-actions="props">
            <q-td :props="props">
              <div class="row q-gutter-xs no-wrap">
                <q-btn
                  round
                  flat
                  size="sm"
                  icon="edit"
                  color="blue-4"
                  @click="openModal(props.row)"
                >
                  <q-tooltip>Edit Role</q-tooltip>
                </q-btn>
                <q-btn
                  round
                  flat
                  size="sm"
                  icon="delete"
                  color="negative"
                  @click="confirmDelete(props.row)"
                >
                  <q-tooltip>Delete Role</q-tooltip>
                </q-btn>
              </div>
            </q-td>
          </template>

          <template #no-data>
            <div class="full-width column flex-center q-pa-xl text-blue-7">
              <q-icon name="admin_panel_settings" size="48px" class="q-mb-sm" />
              <div>No roles found</div>
            </div>
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- ════════════════════════════════════════ -->
    <!-- ADD / EDIT ROLE MODAL                   -->
    <!-- ════════════════════════════════════════ -->
    <q-dialog v-model="modal" persistent>
      <q-card class="modal-card" style="width: 680px; max-width: 96vw">
        <q-card-section class="modal-header row items-center">
          <div class="text-h6 text-grey-9 text-weight-bold">
            {{ editing ? 'Edit Role' : 'Add New Role' }}
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>

        <q-card-section style="max-height: 72vh; overflow-y: auto">
          <div class="column q-gutter-lg">
            <!-- Basic info row -->
            <div class="row q-gutter-md">
              <q-input
                v-model="form.name"
                label="Display Name *"
                standout="bg-blue-1"
                dense
                class="col"
                placeholder="e.g. Manager"
                :rules="[(v) => !!v || 'Required']"
              />
              <q-input
                v-model="form.role_name"
                label="Role Name (slug) *"
                standout="bg-blue-1"
                dense
                class="col"
                placeholder="e.g. manager"
                hint="Lowercase, no spaces"
                :rules="[(v) => !!v || 'Required']"
              />
            </div>

            <!-- Icon + Color -->
            <div class="row q-gutter-md items-center">
              <q-select
                v-model="form.icon"
                :options="iconOptions"
                label="Icon"
                standout="bg-blue-1"
                dense
                class="col"
                emit-value
                map-options
              >
                <template #selected-item="scope">
                  <div class="row items-center q-gutter-sm">
                    <q-icon :name="scope.opt.value || scope.opt" size="18px" color="blue-4" />
                    <span>{{ scope.opt.label || scope.opt }}</span>
                  </div>
                </template>
                <template #option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section avatar>
                      <q-icon :name="scope.opt.value" size="18px" color="blue-4" />
                    </q-item-section>
                    <q-item-section>{{ scope.opt.label }}</q-item-section>
                  </q-item>
                </template>
              </q-select>

              <div class="col">
                <div class="field-label q-mb-xs">Badge Color</div>
                <div class="row q-gutter-sm">
                  <div
                    v-for="c in colorChoices"
                    :key="c.val"
                    class="color-choice"
                    :class="{ 'color-choice-active': form.color === c.val }"
                    :style="{ background: c.hex }"
                    @click="form.color = c.val"
                  >
                    <q-icon v-if="form.color === c.val" name="check" size="12px" color="white" />
                    <q-tooltip>{{ c.label }}</q-tooltip>
                  </div>
                </div>
              </div>

              <!-- Preview -->
              <div class="col-auto column items-center q-gutter-xs">
                <div class="field-label">Preview</div>
                <div class="role-preview-wrap" :style="{ background: iconBg(form.color) }">
                  <q-icon
                    :name="form.icon || 'shield'"
                    :color="form.color || 'blue-4'"
                    size="22px"
                  />
                </div>
                <div class="text-caption text-grey-9 text-weight-medium">
                  {{ form.name || 'Role' }}
                </div>
              </div>
            </div>

            <!-- Permissions section -->
            <div>
              <div class="section-label q-mb-md">
                <q-icon name="lock" size="15px" color="blue-4" class="q-mr-xs" />
                Assign Permissions
                <q-badge color="blue-8" class="q-ml-sm">
                  {{ selectedPerms.length }} / {{ allPermissions.length }} selected
                </q-badge>
              </div>

              <!-- Select All / Clear All -->
              <div class="row items-center q-gutter-sm q-mb-md">
                <q-btn
                  flat
                  dense
                  no-caps
                  size="sm"
                  label="Select All"
                  color="blue-4"
                  icon="check_box"
                  @click="selectAllPerms"
                />
                <q-btn
                  flat
                  dense
                  no-caps
                  size="sm"
                  label="Clear All"
                  color="grey-5"
                  icon="check_box_outline_blank"
                  @click="clearAllPerms"
                />
                <q-linear-progress
                  :value="selectedPerms.length / allPermissions.length"
                  color="blue-5"
                  track-color="grey-2"
                  rounded
                  style="height: 5px; flex: 1"
                />
              </div>

              <!-- Permission groups with checkboxes -->
              <div v-for="group in permissionGroups" :key="group.name" class="q-mb-md">
                <div class="row items-center q-mb-xs q-gutter-xs">
                  <q-icon :name="group.icon" color="blue-4" size="15px" />
                  <span class="group-label">{{ group.name }}</span>
                  <q-separator class="col q-ml-xs" style="opacity: 0.2" />
                  <!-- Group toggle -->
                  <q-btn
                    flat
                    dense
                    no-caps
                    size="xs"
                    :label="isGroupAllSelected(group) ? 'Deselect all' : 'Select all'"
                    :color="isGroupAllSelected(group) ? 'blue-4' : 'grey-5'"
                    @click="toggleGroup(group)"
                  />
                </div>
                <div class="perm-grid">
                  <div
                    v-for="perm in group.permissions"
                    :key="perm.id"
                    class="perm-checkbox-item"
                    :class="{ 'perm-checkbox-active': selectedPerms.includes(perm.id) }"
                    @click="togglePerm(perm.id)"
                  >
                    <q-checkbox
                      :model-value="selectedPerms.includes(perm.id)"
                      @update:model-value="togglePerm(perm.id)"
                      :label="perm.name"
                      color="blue-5"
                      dense
                      @click.stop
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-px-lg q-pb-lg q-pt-sm">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            :label="editing ? 'Update Role' : 'Create Role'"
            color="blue-6"
            unelevated
            no-caps
            icon="save"
            @click="saveRole"
            :disable="!form.name || !form.role_name"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete confirm dialog -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card class="modal-card" style="width: 360px">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="warning" color="negative" size="48px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold text-subtitle1">Delete Role?</div>
          <div class="text-caption text-blue-7 text-center q-mt-xs">
            Are you sure you want to delete
            <strong class="text-grey-9">{{ deleteTarget?.name }}</strong
            >? This cannot be undone.
          </div>
        </q-card-section>
        <q-card-actions align="center" class="q-pb-md q-gutter-sm">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Delete"
            color="negative"
            unelevated
            no-caps
            icon="delete"
            @click="doDelete"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Save success snack -->
    <q-dialog v-model="savedDialog">
      <q-card class="modal-card" style="width: 300px">
        <q-card-section class="column items-center q-pa-lg">
          <q-icon name="check_circle" color="positive" size="48px" class="q-mb-sm" />
          <div class="text-grey-9 text-weight-bold">{{ savedMsg }}</div>
        </q-card-section>
        <q-card-actions align="center">
          <q-btn label="OK" color="blue-6" unelevated no-caps v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'

// ── Dialogs ────────────────────────────────────────────────────
const modal = ref(false)
const deleteDialog = ref(false)
const savedDialog = ref(false)
const savedMsg = ref('')
const editing = ref(null) // null = add, object = edit
const deleteTarget = ref(null)

// ── Roles data ─────────────────────────────────────────────────
const roles = ref([
  { id: 1, name: 'Admin', role_name: 'admin', icon: 'shield', color: 'red-4' },
  { id: 2, name: 'Manager', role_name: 'manager', icon: 'manage_accounts', color: 'purple-4' },
  { id: 3, name: 'Vendor', role_name: 'vendor', icon: 'storefront', color: 'teal-4' },
  { id: 4, name: 'Customer', role_name: 'customer', icon: 'person', color: 'blue-4' },
])

// ── Permission groups ──────────────────────────────────────────
const permissionGroups = [
  {
    name: 'Users',
    icon: 'group',
    permissions: [
      { id: 'users.view', name: 'View Users' },
      { id: 'users.create', name: 'Create Users' },
      { id: 'users.edit', name: 'Edit Users' },
      { id: 'users.delete', name: 'Delete Users' },
    ],
  },
  {
    name: 'Products',
    icon: 'inventory_2',
    permissions: [
      { id: 'products.view', name: 'View Products' },
      { id: 'products.create', name: 'Create Products' },
      { id: 'products.edit', name: 'Edit Products' },
      { id: 'products.delete', name: 'Delete Products' },
    ],
  },
  {
    name: 'Orders',
    icon: 'shopping_cart',
    permissions: [
      { id: 'orders.view', name: 'View Orders' },
      { id: 'orders.update', name: 'Update Orders' },
      { id: 'orders.cancel', name: 'Cancel Orders' },
      { id: 'orders.export', name: 'Export Orders' },
    ],
  },
  {
    name: 'Payments',
    icon: 'payments',
    permissions: [
      { id: 'payments.view', name: 'View Payments' },
      { id: 'payments.approve', name: 'Approve Payments' },
      { id: 'payments.reject', name: 'Reject Payments' },
      { id: 'payments.refund', name: 'Process Refunds' },
    ],
  },
  {
    name: 'Inventory',
    icon: 'inventory',
    permissions: [
      { id: 'inventory.view', name: 'View Inventory' },
      { id: 'inventory.adjust', name: 'Adjust Stock' },
    ],
  },
  {
    name: 'Reports',
    icon: 'analytics',
    permissions: [
      { id: 'reports.view', name: 'View Reports' },
      { id: 'reports.export', name: 'Export Reports' },
    ],
  },
]

const allPermissions = permissionGroups.flatMap((g) => g.permissions)

// ── Role → permissions map ─────────────────────────────────────
const rolePermissions = ref({
  1: allPermissions.map((p) => p.id),
  2: [
    'users.view',
    'products.view',
    'products.create',
    'products.edit',
    'orders.view',
    'orders.update',
    'payments.view',
    'inventory.view',
  ],
  3: ['products.view', 'products.create', 'products.edit', 'orders.view', 'inventory.view'],
  4: ['orders.view'],
})

// ── Table columns ──────────────────────────────────────────────
const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left', style: 'width:60px' },
  { name: 'name', label: 'Name', field: 'name', align: 'left', sortable: true },
  { name: 'role_name', label: 'Role Name', field: 'role_name', align: 'left' },
  { name: 'permissions', label: 'Permissions', field: 'id', align: 'left' },
  { name: 'count', label: 'Total', field: 'id', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'id', align: 'center' },
]

// ── Static option lists ────────────────────────────────────────
const iconOptions = [
  { label: 'Shield', value: 'shield' },
  { label: 'Manage Accounts', value: 'manage_accounts' },
  { label: 'Storefront', value: 'storefront' },
  { label: 'Person', value: 'person' },
  { label: 'Star', value: 'star' },
  { label: 'Build', value: 'build' },
  { label: 'Security', value: 'security' },
  { label: 'Support Agent', value: 'support_agent' },
  { label: 'Local Shipping', value: 'local_shipping' },
  { label: 'Supervisor', value: 'supervisor_account' },
]
const colorChoices = [
  { val: 'red-4', label: 'Red', hex: '#f87171' },
  { val: 'purple-4', label: 'Purple', hex: '#c084fc' },
  { val: 'teal-4', label: 'Teal', hex: '#2dd4bf' },
  { val: 'blue-4', label: 'Blue', hex: '#60a5fa' },
  { val: 'amber-4', label: 'Amber', hex: '#fbbf24' },
  { val: 'green-4', label: 'Green', hex: '#4ade80' },
  { val: 'cyan-4', label: 'Cyan', hex: '#22d3ee' },
  { val: 'pink-4', label: 'Pink', hex: '#f472b6' },
]

// ── Form state ─────────────────────────────────────────────────
const defaultForm = () => ({ name: '', role_name: '', icon: 'shield', color: 'blue-4' })
const form = ref(defaultForm())
const selectedPerms = ref([])

// ── Helpers ────────────────────────────────────────────────────
const permLabel = (id) => allPermissions.find((p) => p.id === id)?.name || id
const iconBg = (color) => {
  const map = {
    'red-4': 'rgba(248,113,113,0.15)',
    'purple-4': 'rgba(192,132,252,0.15)',
    'teal-4': 'rgba(45,212,191,0.15)',
    'blue-4': 'rgba(96,165,250,0.15)',
    'amber-4': 'rgba(251,191,36,0.15)',
    'green-4': 'rgba(74,222,128,0.15)',
    'cyan-4': 'rgba(34,211,238,0.15)',
    'pink-4': 'rgba(244,114,182,0.15)',
  }
  return map[color] || 'rgba(59,130,246,0.15)'
}

// ── Permission helpers ─────────────────────────────────────────
const togglePerm = (id) => {
  const i = selectedPerms.value.indexOf(id)
  i >= 0 ? selectedPerms.value.splice(i, 1) : selectedPerms.value.push(id)
}
const selectAllPerms = () => {
  selectedPerms.value = allPermissions.map((p) => p.id)
}
const clearAllPerms = () => {
  selectedPerms.value = []
}
const isGroupAllSelected = (group) =>
  group.permissions.every((p) => selectedPerms.value.includes(p.id))
const toggleGroup = (group) => {
  const allSel = isGroupAllSelected(group)
  group.permissions.forEach((p) => {
    const i = selectedPerms.value.indexOf(p.id)
    if (allSel && i >= 0) selectedPerms.value.splice(i, 1)
    else if (!allSel && i < 0) selectedPerms.value.push(p.id)
  })
}

// ── CRUD ───────────────────────────────────────────────────────
const openModal = (role) => {
  editing.value = role
  form.value = role
    ? { name: role.name, role_name: role.role_name, icon: role.icon, color: role.color }
    : defaultForm()
  selectedPerms.value = role ? [...(rolePermissions.value[role.id] || [])] : []
  modal.value = true
}

const saveRole = () => {
  if (editing.value) {
    const i = roles.value.findIndex((r) => r.id === editing.value.id)
    roles.value[i] = { ...roles.value[i], ...form.value }
    rolePermissions.value[editing.value.id] = [...selectedPerms.value]
    savedMsg.value = `"${form.value.name}" updated successfully!`
  } else {
    const newId = Date.now()
    roles.value.push({ id: newId, ...form.value })
    rolePermissions.value[newId] = [...selectedPerms.value]
    savedMsg.value = `"${form.value.name}" created successfully!`
  }
  modal.value = false
  savedDialog.value = true
}

const confirmDelete = (role) => {
  deleteTarget.value = role
  deleteDialog.value = true
}
const doDelete = () => {
  roles.value = roles.value.filter((r) => r.id !== deleteTarget.value.id)
  delete rolePermissions.value[deleteTarget.value.id]
  deleteDialog.value = false
}
</script>

<style scoped>
.admin-page {
  background: #f8fafc;
  min-height: 100vh;
}
.page-header {
  border-bottom: 1px solid #e2e8f0;
}

/* ── Table card ── */
.data-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
.roles-table {
  background: transparent !important;
}
.roles-table :deep(.q-table__container) {
  background: transparent !important;
}
.roles-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #dbeafe;
}
.roles-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}
.roles-table :deep(tr:hover td) {
  background: #eff6ff;
}
.roles-table :deep(.q-table__bottom) {
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}

/* ── Table cells ── */
.id-badge {
  font-family: monospace;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}
.role-slug {
  font-family: monospace;
  font-size: 12px;
  color: #1e40af;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
}
.role-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.perm-chip {
  font-size: 10px !important;
  padding: 2px 7px !important;
  border-radius: 20px !important;
  margin: 1px;
}

/* ── Modal ── */
.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
.modal-header {
  border-bottom: 1px solid #dbeafe;
}
.field-label {
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
}
.section-label {
  color: #1e40af;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
}
.group-label {
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ── Permission grid ── */
.perm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
}
.perm-checkbox-item {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #dbeafe;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.15s;
}
.perm-checkbox-item:hover {
  border-color: #1d4ed8;
  background: #eff6ff;
}
.perm-checkbox-active {
  border-color: #60a5fa !important;
  background: #dbeafe !important;
}

/* ── Color choices ── */
.color-choice {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    transform 0.15s,
    border-color 0.15s;
}
.color-choice:hover {
  transform: scale(1.15);
}
.color-choice-active {
  border-color: #1e40af !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

/* ── Role preview ── */
.role-preview-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
