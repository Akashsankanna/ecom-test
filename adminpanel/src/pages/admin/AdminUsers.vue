<template>
  <q-page class="admin-page">
    <!-- Header -->
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">User & Role Management</div>
          <div class="text-caption text-blue-7">
            Manage users, roles, permissions and audit logs
          </div>
        </div>
        <q-badge color="blue-6" class="q-pa-sm">
          <q-icon name="admin_panel_settings" size="14px" class="q-mr-xs" /> Admin
        </q-badge>
      </div>
    </div>

    <!-- Tabs -->
    <div class="q-px-lg q-pt-md">
      <q-tabs
        v-model="activeTab"
        dense
        active-color="blue-7"
        indicator-color="blue-6"
        align="left"
        class="text-grey-6"
      >
        <q-tab name="users" icon="group" label="Users" no-caps />
        <q-tab name="roles" icon="badge" label="Roles" no-caps />
        <q-tab name="permissions" icon="lock_open" label="Permissions" no-caps />
        <q-tab name="audit" icon="history" label="Audit Logs" no-caps />
      </q-tabs>
      <q-separator color="blue-1" />
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <q-tab-panels v-model="activeTab" animated keep-alive>
        <!-- ═══════════════════════════════════════════════════════
             TAB 1 — USERS
        ═══════════════════════════════════════════════════════ -->
        <q-tab-panel name="users" class="q-pa-none">
          <!-- Filters -->
          <div class="row q-gutter-md q-mb-md items-center">
            <div class="col-12 col-sm">
              <q-input
                v-model="userSearch"
                placeholder="Search by name, email, phone..."
                dense
                standout="bg-blue-1"
                clearable
              >
                <template #prepend><q-icon name="search" color="blue-4" /></template>
              </q-input>
            </div>
            <div class="col-auto">
              <q-btn-toggle
                v-model="userStatusFilter"
                :options="[
                  { label: 'All', value: 'all' },
                  { label: 'Active', value: 'active' },
                  { label: 'Inactive', value: 'inactive' },
                ]"
                toggle-color="blue-6"
                color="grey-2"
                text-color="blue-8"
                dense
                no-caps
                rounded
              />
            </div>
          </div>

          <q-card class="data-card" flat>
            <q-table
              :rows="filteredUsers"
              :columns="userColumns"
              row-key="user_id"
              flat
              :loading="loadingUsers"
              :rows-per-page-options="[10, 25, 50]"
              rows-per-page-label="Rows:"
              class="users-table"
              wrap-cells
            >
              <template #body-cell-name="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm no-wrap">
                    <q-avatar
                      size="32px"
                      :color="avatarColor(props.row.user_id)"
                      text-color="white"
                      font-size="13px"
                    >
                      {{ initials(props.value) }}
                    </q-avatar>
                    <span class="text-grey-9 text-weight-medium">{{ props.value }}</span>
                  </div>
                </q-td>
              </template>

              <template #body-cell-status="props">
                <q-td :props="props">
                  <q-chip
                    :color="
                      props.value === 'active' || props.value === true ? 'positive' : 'negative'
                    "
                    text-color="white"
                    dense
                    size="sm"
                    :icon="
                      props.value === 'active' || props.value === true ? 'check_circle' : 'cancel'
                    "
                  >
                    {{ props.value === 'active' || props.value === true ? 'Active' : 'Inactive' }}
                  </q-chip>
                </q-td>
              </template>

              <template #body-cell-user_type="props">
                <q-td :props="props">
                  <q-badge :color="roleColor(props.value)" outline>{{ props.value }}</q-badge>
                </q-td>
              </template>

              <template #body-cell-actions="props">
                <q-td :props="props">
                  <div class="row q-gutter-xs no-wrap">
                    <q-btn
                      round
                      flat
                      size="sm"
                      icon="visibility"
                      color="blue-4"
                      @click="viewUser(props.row)"
                    >
                      <q-tooltip>View Details</q-tooltip>
                    </q-btn>
                    <q-btn
                      round
                      flat
                      size="sm"
                      icon="edit"
                      color="amber-7"
                      @click="openEditUser(props.row)"
                    >
                      <q-tooltip>Edit User</q-tooltip>
                    </q-btn>
                    <q-btn
                      round
                      flat
                      size="sm"
                      icon="delete"
                      color="negative"
                      @click="confirmDeleteUser(props.row)"
                    >
                      <q-tooltip>Delete User</q-tooltip>
                    </q-btn>
                  </div>
                </q-td>
              </template>

              <template #no-data>
                <div class="full-width column flex-center q-pa-xl text-blue-7">
                  <q-icon name="person_off" size="48px" class="q-mb-sm" />
                  <div>No users found</div>
                </div>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ═══════════════════════════════════════════════════════
             TAB 2 — ROLES
        ═══════════════════════════════════════════════════════ -->
        <q-tab-panel name="roles" class="q-pa-none">
          <q-card class="data-card" flat>
            <q-table
              :rows="roles"
              :columns="roleColumns"
              row-key="role_id"
              flat
              :loading="loadingRoles"
              :rows-per-page-options="[10, 25]"
              rows-per-page-label="Rows:"
              class="users-table"
            >
              <template #body-cell-role_name="props">
                <q-td :props="props">
                  <q-badge :color="roleColor(props.value)" outline>{{ props.value }}</q-badge>
                </q-td>
              </template>

              <template #body-cell-actions="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    dense
                    no-caps
                    size="sm"
                    icon="manage_accounts"
                    color="blue-6"
                    label="Manage Assignments"
                    @click="openRoleAssign(props.row)"
                  />
                </q-td>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ═══════════════════════════════════════════════════════
             TAB 3 — PERMISSIONS
        ═══════════════════════════════════════════════════════ -->
        <q-tab-panel name="permissions" class="q-pa-none">
          <div class="row q-gutter-md q-mb-md">
            <q-btn-toggle
              v-model="permView"
              :options="[
                { label: 'Access View', value: 'access' },
                { label: 'Full Access', value: 'full' },
              ]"
              toggle-color="blue-6"
              color="grey-2"
              text-color="blue-8"
              dense
              no-caps
              rounded
            />
          </div>
          <q-card class="data-card" flat>
            <q-table
              :rows="permView === 'access' ? permissionsAccess : permissionsFull"
              :columns="permissionColumns"
              row-key="role"
              flat
              :loading="loadingPermissions"
              :rows-per-page-options="[10, 25]"
              rows-per-page-label="Rows:"
              class="users-table"
            >
              <template #body-cell-can_read="props">
                <q-td :props="props" class="text-center">
                  <q-icon
                    :name="props.value ? 'check_circle' : 'cancel'"
                    :color="props.value ? 'positive' : 'grey-4'"
                    size="18px"
                  />
                </q-td>
              </template>
              <template #body-cell-can_write="props">
                <q-td :props="props" class="text-center">
                  <q-icon
                    :name="props.value ? 'check_circle' : 'cancel'"
                    :color="props.value ? 'positive' : 'grey-4'"
                    size="18px"
                  />
                </q-td>
              </template>
              <template #body-cell-can_delete="props">
                <q-td :props="props" class="text-center">
                  <q-icon
                    :name="props.value ? 'check_circle' : 'cancel'"
                    :color="props.value ? 'positive' : 'grey-4'"
                    size="18px"
                  />
                </q-td>
              </template>
              <template #body-cell-full_access="props">
                <q-td :props="props" class="text-center">
                  <q-icon
                    :name="props.value ? 'check_circle' : 'cancel'"
                    :color="props.value ? 'amber-7' : 'grey-4'"
                    size="18px"
                  />
                </q-td>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>

        <!-- ═══════════════════════════════════════════════════════
             TAB 4 — AUDIT LOGS
        ═══════════════════════════════════════════════════════ -->
        <q-tab-panel name="audit" class="q-pa-none">
          <q-card class="data-card" flat>
            <q-table
              :rows="auditLogs"
              :columns="auditColumns"
              row-key="id"
              flat
              :loading="loadingAudit"
              :rows-per-page-options="[10, 25, 50]"
              rows-per-page-label="Rows:"
              class="users-table"
            >
              <template #body-cell-action="props">
                <q-td :props="props">
                  <q-badge :color="auditActionColor(props.value)" :label="props.value" />
                </q-td>
              </template>
              <template #body-cell-old_data="props">
                <q-td :props="props">
                  <q-btn
                    v-if="props.value"
                    flat
                    dense
                    size="xs"
                    icon="visibility"
                    color="grey-6"
                    @click="showDataDiff(props.row)"
                  >
                    <q-tooltip>View Changes</q-tooltip>
                  </q-btn>
                  <span v-else class="text-grey-4">—</span>
                </q-td>
              </template>
              <template #body-cell-new_data="props">
                <q-td :props="props">
                  <span
                    v-if="props.value"
                    class="text-caption text-grey-7 ellipsis-2-lines"
                    style="max-width: 180px; display: block"
                  >
                    {{ JSON.stringify(props.value).slice(0, 60) }}…
                  </span>
                  <span v-else class="text-grey-4">—</span>
                </q-td>
              </template>
            </q-table>
          </q-card>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         MODAL — View User Details
    ══════════════════════════════════════════════════════════ -->
    <q-dialog v-model="showViewModal">
      <q-card class="modal-card" style="min-width: 340px; max-width: 520px; width: 100%">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">User Details</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section v-if="selectedUser">
          <div class="column items-center q-mb-lg">
            <q-avatar
              size="72px"
              :color="avatarColor(selectedUser.user_id)"
              text-color="white"
              font-size="28px"
              class="q-mb-sm"
            >
              {{ initials(selectedUser.name) }}
            </q-avatar>
            <div class="text-h6 text-grey-9">{{ selectedUser.name }}</div>
            <q-badge
              :color="selectedUser.status === 'active' ? 'positive' : 'negative'"
              class="q-mt-xs"
            >
              {{ selectedUser.status === 'active' ? 'Active' : 'Inactive' }}
            </q-badge>
          </div>
          <div class="detail-grid">
            <div v-for="field in userDetailFields" :key="field.key" class="detail-row">
              <div class="detail-label">
                <q-icon :name="field.icon" size="14px" color="blue-4" class="q-mr-xs" />{{
                  field.label
                }}
              </div>
              <div class="detail-value">{{ selectedUser[field.key] }}</div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════════════
         MODAL — Edit User
    ══════════════════════════════════════════════════════════ -->
    <q-dialog v-model="showEditModal">
      <q-card class="modal-card" style="min-width: 360px; max-width: 520px; width: 100%">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Edit User</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section>
          <div class="column q-gutter-md">
            <q-input v-model="editForm.name" label="Name" dense outlined />
            <q-input v-model="editForm.email" label="Email" dense outlined type="email" />
            <q-input v-model="editForm.phone" label="Phone" dense outlined />
            <q-select
              v-model="editForm.status"
              :options="['active', 'inactive']"
              label="Status"
              dense
              outlined
            />
          </div>
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn flat no-caps label="Cancel" v-close-popup color="grey-6" />
          <q-btn
            unelevated
            no-caps
            label="Save Changes"
            color="blue-6"
            :loading="savingUser"
            @click="saveUser"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════════════
         MODAL — Role Assignment
    ══════════════════════════════════════════════════════════ -->
    <q-dialog v-model="showRoleModal">
      <q-card class="modal-card" style="min-width: 360px; max-width: 520px; width: 100%">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Manage Role Assignments</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section v-if="selectedRole">
          <div class="text-subtitle2 text-grey-7 q-mb-md">
            Role: <strong>{{ selectedRole.role_name }}</strong>
          </div>

          <!-- Assign to user -->
          <div class="text-caption text-blue-7 q-mb-xs">Assign to User</div>
          <div class="row q-gutter-sm items-center q-mb-lg">
            <div class="col">
              <q-select
                v-model="assignUserId"
                :options="userOptions"
                option-value="value"
                option-label="label"
                emit-value
                map-options
                label="Select user"
                dense
                outlined
              />
            </div>
            <q-btn
              unelevated
              no-caps
              color="blue-6"
              label="Assign"
              :loading="assigningRole"
              @click="assignRole"
            />
          </div>

          <!-- Assigned users list -->
          <div class="text-caption text-blue-7 q-mb-xs">Currently Assigned Users</div>
          <div class="row q-gutter-xs flex-wrap">
            <q-chip
              v-for="u in assignedUsers"
              :key="u.user_id"
              removable
              color="blue-1"
              text-color="blue-8"
              icon="person"
              @remove="removeRole(u)"
              >{{ u.name }}</q-chip
            >
            <div v-if="!assignedUsers.length" class="text-caption text-grey-5 q-pa-sm">
              No users assigned yet
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════════════
         DIALOG — Delete Confirmation
    ══════════════════════════════════════════════════════════ -->
    <q-dialog v-model="showDeleteDialog">
      <q-card style="min-width: 320px">
        <q-card-section class="row items-center q-pb-none">
          <q-icon name="warning" color="negative" size="28px" class="q-mr-sm" />
          <div class="text-h6 text-grey-9">Delete User</div>
        </q-card-section>
        <q-card-section>
          Are you sure you want to delete <strong>{{ userToDelete?.name }}</strong
          >? This action cannot be undone.
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat no-caps label="Cancel" v-close-popup color="grey-6" />
          <q-btn
            unelevated
            no-caps
            label="Delete"
            color="negative"
            :loading="deletingUser"
            @click="deleteUser"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ══════════════════════════════════════════════════════════
         DIALOG — Data Diff Viewer
    ══════════════════════════════════════════════════════════ -->
    <q-dialog v-model="showDiffDialog">
      <q-card style="min-width: 400px; max-width: 600px; width: 100%">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Change Details</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section v-if="diffLog">
          <div class="row q-gutter-md">
            <div class="col">
              <div class="text-caption text-negative q-mb-xs text-weight-bold">Old Data</div>
              <pre class="diff-pre diff-old">{{ JSON.stringify(diffLog.old_data, null, 2) }}</pre>
            </div>
            <div class="col">
              <div class="text-caption text-positive q-mb-xs text-weight-bold">New Data</div>
              <pre class="diff-pre diff-new">{{ JSON.stringify(diffLog.new_data, null, 2) }}</pre>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const activeTab = ref('users')

// ── Helpers ────────────────────────────────────────────────────
const avatarColors = ['blue-8', 'purple-8', 'teal-8', 'indigo-8', 'cyan-8', 'green-8', 'amber-8']
const avatarColor = (id) => avatarColors[(id ?? 0) % avatarColors.length]
const initials = (name) =>
  name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || '?'
const roleColor = (r) =>
  ({ Admin: 'blue-8', Manager: 'purple-8', Vendor: 'teal-8', Customer: 'grey-8' })[r] || 'grey-8'

const notify = (msg, type = 'positive') =>
  $q.notify({ message: msg, color: type, position: 'top-right', timeout: 2500 })

// ══════════════════════════════════════════════════════════════
// TAB 1 — USERS
// ══════════════════════════════════════════════════════════════
const loadingUsers = ref(false)
const userSearch = ref('')
const userStatusFilter = ref('all')
const users = ref([])

const userColumns = [
  {
    name: 'user_id',
    label: 'ID',
    field: 'user_id',
    align: 'left',
    sortable: true,
    style: 'width:60px',
  },
  { name: 'name', label: 'Name', field: 'name', align: 'left', sortable: true },
  { name: 'email', label: 'Email', field: 'email', align: 'left', sortable: true },
  { name: 'phone', label: 'Phone', field: 'phone', align: 'left' },
  { name: 'user_type', label: 'Type', field: 'user_type', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const filteredUsers = computed(() =>
  users.value.filter((u) => {
    const s = userSearch.value.toLowerCase()
    const matchSearch =
      !s ||
      u.name?.toLowerCase().includes(s) ||
      u.email?.toLowerCase().includes(s) ||
      u.phone?.includes(s)
    const matchStatus =
      userStatusFilter.value === 'all' ||
      (userStatusFilter.value === 'active' && (u.status === 'active' || u.status === true)) ||
      (userStatusFilter.value === 'inactive' && (u.status === 'inactive' || u.status === false))
    return matchSearch && matchStatus
  }),
)

const fetchUsers = async () => {
  loadingUsers.value = true
  try {
    // Using static fallback values
    users.value = [
      {
        user_id: 1,
        name: 'Rahul Sharma',
        email: 'rahul@example.com',
        phone: '9876543210',
        user_type: 'Admin',
        status: 'active',
      },
      {
        user_id: 2,
        name: 'Priya Mehta',
        email: 'priya@example.com',
        phone: '9123456780',
        user_type: 'Customer',
        status: 'active',
      },
      {
        user_id: 3,
        name: 'Ankit Patel',
        email: 'ankit@example.com',
        phone: '9988776655',
        user_type: 'Vendor',
        status: 'inactive',
      },
      {
        user_id: 4,
        name: 'Sneha Joshi',
        email: 'sneha@example.com',
        phone: '9765432100',
        user_type: 'Customer',
        status: 'active',
      },
      {
        user_id: 5,
        name: 'Vikram Singh',
        email: 'vikram@example.com',
        phone: '9654321098',
        user_type: 'Manager',
        status: 'active',
      },
      {
        user_id: 6,
        name: 'Divya Rao',
        email: 'divya@example.com',
        phone: '9543210987',
        user_type: 'Customer',
        status: 'inactive',
      },
    ]
  } catch {
    // fallback already set
  } finally {
    loadingUsers.value = false
  }
}

// View
const selectedUser = ref(null)
const showViewModal = ref(false)
const userDetailFields = [
  { key: 'user_id', label: 'User ID', icon: 'tag' },
  { key: 'email', label: 'Email', icon: 'email' },
  { key: 'phone', label: 'Phone', icon: 'phone' },
  { key: 'user_type', label: 'Type', icon: 'badge' },
  { key: 'status', label: 'Status', icon: 'circle' },
]
const viewUser = async (row) => {
  try {
    // Using static fallback values
    selectedUser.value = row
  } catch {
    selectedUser.value = row
  }
  showViewModal.value = true
}

// Edit
const showEditModal = ref(false)
const savingUser = ref(false)
const editForm = ref({ name: '', email: '', phone: '', status: 'active' })
const editingUserId = ref(null)

const openEditUser = (row) => {
  editingUserId.value = row.user_id
  editForm.value = { name: row.name, email: row.email, phone: row.phone, status: row.status }
  showEditModal.value = true
}

const saveUser = async () => {
  savingUser.value = true
  try {
    // Using static fallback values
    const idx = users.value.findIndex((u) => u.user_id === editingUserId.value)
    if (idx !== -1) Object.assign(users.value[idx], editForm.value)
    notify('User updated successfully')
    showEditModal.value = false
  } catch {
    notify('Failed to update user', 'negative')
  } finally {
    savingUser.value = false
  }
}

// Delete
const showDeleteDialog = ref(false)
const deletingUser = ref(false)
const userToDelete = ref(null)

const confirmDeleteUser = (row) => {
  userToDelete.value = row
  showDeleteDialog.value = true
}

const deleteUser = async () => {
  deletingUser.value = true
  try {
    // Using static fallback values
    users.value = users.value.filter((u) => u.user_id !== userToDelete.value.user_id)
    notify('User deleted successfully')
    showDeleteDialog.value = false
  } catch {
    notify('Failed to delete user', 'negative')
  } finally {
    deletingUser.value = false
  }
}

// ══════════════════════════════════════════════════════════════
// TAB 2 — ROLES
// ══════════════════════════════════════════════════════════════
const loadingRoles = ref(false)
const roles = ref([])
const roleColumns = [
  { name: 'role_id', label: 'Role ID', field: 'role_id', align: 'left', sortable: true },
  { name: 'role_name', label: 'Role Name', field: 'role_name', align: 'left', sortable: true },
  { name: 'description', label: 'Description', field: 'description', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const fetchRoles = async () => {
  loadingRoles.value = true
  try {
    // Using static fallback values
    roles.value = [
      { role_id: 1, role_name: 'Admin', description: 'Full system access' },
      { role_id: 2, role_name: 'Manager', description: 'Manage products and orders' },
      { role_id: 3, role_name: 'Vendor', description: 'Manage own listings' },
      { role_id: 4, role_name: 'Customer', description: 'Browse and purchase' },
    ]
  } catch {
    // fallback already set
  } finally {
    loadingRoles.value = false
  }
}

// Role assignment modal
const showRoleModal = ref(false)
const selectedRole = ref(null)
const assignUserId = ref(null)
const assigningRole = ref(false)
const assignedUsers = ref([])

const userOptions = computed(() => users.value.map((u) => ({ label: u.name, value: u.user_id })))

const openRoleAssign = (role) => {
  selectedRole.value = role
  assignedUsers.value = users.value.filter((u) => u.user_type === role.role_name)
  assignUserId.value = null
  showRoleModal.value = true
}

const assignRole = async () => {
  if (!assignUserId.value) return
  assigningRole.value = true
  try {
    // Using static fallback values
    const user = users.value.find((u) => u.user_id === assignUserId.value)
    if (user && !assignedUsers.value.find((u) => u.user_id === user.user_id)) {
      assignedUsers.value.push(user)
    }
    notify('Role assigned successfully')
  } catch {
    notify('Failed to assign role', 'negative')
  } finally {
    assigningRole.value = false
  }
}

const removeRole = async (user) => {
  try {
    // Using static fallback values
    assignedUsers.value = assignedUsers.value.filter((u) => u.user_id !== user.user_id)
    notify('Role removed successfully')
  } catch {
    notify('Failed to remove role', 'negative')
  }
}

// ══════════════════════════════════════════════════════════════
// TAB 3 — PERMISSIONS
// ══════════════════════════════════════════════════════════════
const loadingPermissions = ref(false)
const permView = ref('access')
const permissionsAccess = ref([])
const permissionsFull = ref([])

const permissionColumns = [
  { name: 'role', label: 'Role', field: 'role', align: 'left' },
  { name: 'resource', label: 'Resource', field: 'resource', align: 'left' },
  { name: 'can_read', label: 'Read', field: 'can_read', align: 'center' },
  { name: 'can_write', label: 'Write', field: 'can_write', align: 'center' },
  { name: 'can_delete', label: 'Delete', field: 'can_delete', align: 'center' },
  { name: 'full_access', label: 'Full Access', field: 'full_access', align: 'center' },
]

const fetchPermissions = async () => {
  loadingPermissions.value = true
  try {
    // Using static fallback values
    const fallback = [
      {
        role: 'Admin',
        resource: 'Users',
        can_read: true,
        can_write: true,
        can_delete: true,
        full_access: true,
      },
      {
        role: 'Admin',
        resource: 'Products',
        can_read: true,
        can_write: true,
        can_delete: true,
        full_access: true,
      },
      {
        role: 'Manager',
        resource: 'Products',
        can_read: true,
        can_write: true,
        can_delete: false,
        full_access: false,
      },
      {
        role: 'Manager',
        resource: 'Orders',
        can_read: true,
        can_write: true,
        can_delete: false,
        full_access: false,
      },
      {
        role: 'Vendor',
        resource: 'Products',
        can_read: true,
        can_write: true,
        can_delete: false,
        full_access: false,
      },
      {
        role: 'Customer',
        resource: 'Orders',
        can_read: true,
        can_write: false,
        can_delete: false,
        full_access: false,
      },
    ]
    permissionsAccess.value = fallback.filter((p) => !p.full_access)
    permissionsFull.value = fallback.filter((p) => p.full_access)
  } finally {
    loadingPermissions.value = false
  }
}

// ══════════════════════════════════════════════════════════════
// TAB 4 — AUDIT LOGS
// ══════════════════════════════════════════════════════════════
const loadingAudit = ref(false)
const auditLogs = ref([])

const auditColumns = [
  { name: 'action', label: 'Action', field: 'action', align: 'left' },
  { name: 'entity', label: 'Entity', field: 'entity', align: 'left' },
  { name: 'user', label: 'User', field: 'user', align: 'left' },
  { name: 'timestamp', label: 'Timestamp', field: 'timestamp', align: 'left', sortable: true },
  { name: 'old_data', label: 'Old Data', field: 'old_data', align: 'center' },
  { name: 'new_data', label: 'New Data', field: 'new_data', align: 'left' },
]

const auditActionColor = (a) =>
  ({ CREATE: 'positive', UPDATE: 'warning', DELETE: 'negative', LOGIN: 'info' })[
    a?.toUpperCase()
  ] || 'grey-6'

const fetchAuditLogs = async () => {
  loadingAudit.value = true
  try {
    // Using static fallback values
    auditLogs.value = [
      {
        id: 1,
        action: 'UPDATE',
        entity: 'User',
        user: 'Rahul Sharma',
        timestamp: '2024-01-15 10:32:00',
        old_data: { status: 'inactive' },
        new_data: { status: 'active' },
      },
      {
        id: 2,
        action: 'CREATE',
        entity: 'User',
        user: 'Priya Mehta',
        timestamp: '2024-01-14 09:15:00',
        old_data: null,
        new_data: { name: 'Ankit Patel', email: 'ankit@example.com' },
      },
      {
        id: 3,
        action: 'DELETE',
        entity: 'User',
        user: 'Admin',
        timestamp: '2024-01-13 16:44:00',
        old_data: { name: 'Old User' },
        new_data: null,
      },
      {
        id: 4,
        action: 'LOGIN',
        entity: 'Session',
        user: 'Vikram Singh',
        timestamp: '2024-01-12 08:00:00',
        old_data: null,
        new_data: null,
      },
    ]
  } catch {
    // fallback already set
  } finally {
    loadingAudit.value = false
  }
}

// Diff viewer
const showDiffDialog = ref(false)
const diffLog = ref(null)
const showDataDiff = (log) => {
  diffLog.value = log
  showDiffDialog.value = true
}

// ── Mount ──────────────────────────────────────────────────────
onMounted(() => {
  fetchUsers()
  fetchRoles()
  fetchPermissions()
  fetchAuditLogs()
})
</script>

<style scoped>
.admin-page {
  background: #f8fafc;
  min-height: 100vh;
}
.page-header {
  border-bottom: 1px solid #e2e8f0;
}

.data-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}
.users-table {
  background: transparent !important;
}
.users-table :deep(.q-table__container) {
  background: transparent !important;
}
.users-table :deep(th) {
  background: #eff6ff;
  color: #1e40af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #dbeafe;
}
.users-table :deep(td) {
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}
.users-table :deep(tr:hover td) {
  background: #eff6ff;
}
.users-table :deep(.q-table__bottom) {
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}

.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #eff6ff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.detail-label {
  color: #64748b;
  font-size: 13px;
  display: flex;
  align-items: center;
}
.detail-value {
  color: #1e293b;
  font-size: 13px;
  font-weight: 500;
}

.diff-pre {
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px;
  font-size: 11px;
  overflow: auto;
  max-height: 300px;
  white-space: pre-wrap;
  word-break: break-all;
}
.diff-old {
  border: 1px solid #fecaca;
  background: #fff5f5;
}
.diff-new {
  border: 1px solid #bbf7d0;
  background: #f0fdf4;
}
</style>
