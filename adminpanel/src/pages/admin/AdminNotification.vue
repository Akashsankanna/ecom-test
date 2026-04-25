<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Notifications</div>
          <div class="text-caption text-blue-7">System alerts and broadcasts</div>
        </div>
        <div class="row q-gutter-sm">
          <q-btn
            label="Send Notification"
            color="blue-6"
            unelevated
            no-caps
            icon="send"
            @click="sendModal = true"
          />
          <q-btn
            label="Mark All Read"
            flat
            color="blue-4"
            no-caps
            icon="done_all"
            @click="markAllRead"
            v-if="unreadCount"
          />
        </div>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- Stats row -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md-3" v-for="s in statsCards" :key="s.label">
          <q-card class="stat-card" flat>
            <q-card-section class="q-pa-md">
              <div class="row items-center q-gutter-sm q-mb-xs">
                <div class="stat-icon" :style="{ background: s.bg }">
                  <q-icon :name="s.icon" :color="s.color" size="18px" />
                </div>
                <span class="text-caption text-blue-7">{{ s.label }}</span>
              </div>
              <div class="text-h5 text-grey-9 text-weight-bold">{{ s.value }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Filters -->
      <div class="row q-gutter-md q-mb-md items-center">
        <div class="col-12 col-sm">
          <q-input
            v-model="search"
            placeholder="Search notifications..."
            dense
            standout="bg-blue-1"
            clearable
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
        <div class="col-auto">
          <q-btn-toggle
            v-model="tab"
            :options="[
              { label: 'All', value: 'all' },
              { label: 'Unread', value: 'unread' },
              { label: 'Read', value: 'read' },
            ]"
            toggle-color="blue-6"
            color="grey-2"
            text-color="blue-8"
            dense
            no-caps
            rounded
          />
        </div>
        <div class="col-auto">
          <q-select
            v-model="typeFilter"
            :options="['All Types', 'system', 'order', 'user', 'payment', 'alert']"
            dense
            standout="bg-blue-1"
            style="min-width: 130px"
          />
        </div>
      </div>

      <!-- Notifications List -->
      <div class="column q-gutter-sm">
        <q-card
          v-for="n in filteredNotifs"
          :key="n.id"
          class="notif-card"
          :class="{ 'notif-unread': !n.read }"
          flat
          @click="markRead(n)"
        >
          <q-card-section class="q-pa-md">
            <div class="row items-start q-gutter-md no-wrap">
              <!-- Icon -->
              <div class="notif-icon" :style="{ background: typeConfig[n.type]?.bg }">
                <q-icon
                  :name="typeConfig[n.type]?.icon"
                  :color="typeConfig[n.type]?.color"
                  size="20px"
                />
              </div>

              <!-- Content -->
              <div class="col">
                <div class="row items-start justify-between">
                  <div>
                    <div class="row items-center q-gutter-xs q-mb-xs">
                      <span class="text-grey-9 text-weight-medium">{{ n.title }}</span>
                      <q-badge v-if="!n.read" color="blue-6" label="New" size="xs" />
                      <q-badge
                        :color="typeConfig[n.type]?.color"
                        :label="n.type"
                        outline
                        size="xs"
                      />
                    </div>
                    <div class="notif-body">{{ n.body }}</div>
                  </div>
                  <div class="text-caption text-blue-4 text-no-wrap q-ml-md">
                    {{ n.created_at }}
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="row q-gutter-xs no-wrap" @click.stop>
                <q-btn
                  round
                  flat
                  size="xs"
                  :icon="n.read ? 'mark_email_read' : 'mark_email_unread'"
                  :color="n.read ? 'blue-7' : 'blue-4'"
                  @click="markRead(n)"
                >
                  <q-tooltip>{{ n.read ? 'Unread' : 'Mark Read' }}</q-tooltip>
                </q-btn>
                <q-btn
                  round
                  flat
                  size="xs"
                  icon="delete"
                  color="negative"
                  @click="deleteNotif(n.id)"
                >
                  <q-tooltip>Delete</q-tooltip>
                </q-btn>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <div v-if="!filteredNotifs.length" class="column flex-center q-pa-xl text-blue-7">
          <q-icon name="notifications_none" size="56px" class="q-mb-sm" />
          <div>No notifications found</div>
        </div>
      </div>
    </div>

    <!-- Send Notification Modal -->
    <q-dialog v-model="sendModal" persistent>
      <q-card class="modal-card" style="width: 500px; max-width: 95vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-grey-9 text-weight-bold">Send Notification</div>
          <q-space /><q-btn icon="close" flat round dense v-close-popup color="blue-4" />
        </q-card-section>
        <q-card-section>
          <div class="column q-gutter-md">
            <q-input
              v-model="sendForm.title"
              label="Title"
              standout="bg-blue-1"
              dense
              :rules="[(v) => !!v || 'Required']"
            />
            <q-input
              v-model="sendForm.body"
              label="Message"
              standout="bg-blue-1"
              dense
              type="textarea"
              rows="3"
              :rules="[(v) => !!v || 'Required']"
            />
            <div class="row q-gutter-md">
              <q-select
                v-model="sendForm.type"
                :options="['system', 'order', 'user', 'payment', 'alert']"
                label="Type"
                standout="bg-blue-1"
                dense
                class="col"
              />
              <q-select
                v-model="sendForm.audience"
                :options="['All Users', 'Admins Only', 'Specific Role']"
                label="Audience"
                standout="bg-blue-1"
                dense
                class="col"
              />
            </div>
            <q-toggle v-model="sendForm.urgent" label="Mark as Urgent" color="red-5" />
          </div>
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn label="Cancel" flat no-caps v-close-popup color="blue-4" />
          <q-btn
            label="Send Now"
            color="blue-6"
            unelevated
            no-caps
            icon="send"
            @click="sendNotification"
            :disable="!sendForm.title || !sendForm.body"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
const search = ref('')
const tab = ref('all')
const typeFilter = ref('All Types')
const sendModal = ref(false)
const sendForm = ref({ title: '', body: '', type: 'system', audience: 'All Users', urgent: false })

const typeConfig = {
  system: { icon: 'settings', color: 'blue-4', bg: 'rgba(59,130,246,.15)' },
  order: { icon: 'shopping_cart', color: 'green-4', bg: 'rgba(34,197,94,.15)' },
  user: { icon: 'person', color: 'cyan-4', bg: 'rgba(6,182,212,.15)' },
  payment: { icon: 'payments', color: 'amber-4', bg: 'rgba(245,158,11,.15)' },
  alert: { icon: 'warning', color: 'red-4', bg: 'rgba(239,68,68,.15)' },
}

const notifications = ref([
  {
    id: 1,
    title: 'New Order Received',
    body: 'Order #ORD-1010 placed by Rahul Sharma for ₹3,200.',
    type: 'order',
    read: false,
    created_at: '2 mins ago',
  },
  {
    id: 2,
    title: 'Payment Approved',
    body: 'Transaction TXN-00190 of ₹1,850 has been approved successfully.',
    type: 'payment',
    read: false,
    created_at: '15 mins ago',
  },
  {
    id: 3,
    title: 'Low Stock Alert',
    body: 'Mechanical Keyboard (RGB Backlit) is running low — only 3 units left.',
    type: 'alert',
    read: false,
    created_at: '1 hr ago',
  },
  {
    id: 4,
    title: 'New User Registered',
    body: 'Karan Malhotra has signed up and completed profile setup.',
    type: 'user',
    read: true,
    created_at: '3 hrs ago',
  },
  {
    id: 5,
    title: 'System Maintenance Scheduled',
    body: 'Planned downtime on Jan 20, 2024 from 2:00 AM to 4:00 AM IST.',
    type: 'system',
    read: true,
    created_at: '1 day ago',
  },
  {
    id: 6,
    title: 'Return Request Submitted',
    body: 'RET-005 submitted for Order #ORD-1007 — pages missing in book.',
    type: 'order',
    read: true,
    created_at: '2 days ago',
  },
  {
    id: 7,
    title: 'Coupon Expiring Soon',
    body: 'Coupon WINTER15 expires in 3 days. Consider renewing.',
    type: 'alert',
    read: false,
    created_at: '2 days ago',
  },
  {
    id: 8,
    title: 'High Traffic Alert',
    body: 'Server load at 78%. Auto-scaling triggered successfully.',
    type: 'alert',
    read: true,
    created_at: '3 days ago',
  },
])

const filteredNotifs = computed(() =>
  notifications.value.filter((n) => {
    const ms =
      !search.value ||
      n.title.toLowerCase().includes(search.value.toLowerCase()) ||
      n.body.toLowerCase().includes(search.value.toLowerCase())
    const mt =
      tab.value === 'all' || (tab.value === 'unread' && !n.read) || (tab.value === 'read' && n.read)
    const mtype = typeFilter.value === 'All Types' || n.type === typeFilter.value
    return ms && mt && mtype
  }),
)

const unreadCount = computed(() => notifications.value.filter((n) => !n.read).length)
const statsCards = computed(() => [
  {
    label: 'Total',
    value: notifications.value.length,
    icon: 'notifications',
    color: 'blue-4',
    bg: 'rgba(59,130,246,.12)',
  },
  {
    label: 'Unread',
    value: unreadCount.value,
    icon: 'mark_email_unread',
    color: 'amber-4',
    bg: 'rgba(245,158,11,.12)',
  },
  {
    label: 'Alerts',
    value: notifications.value.filter((n) => n.type === 'alert').length,
    icon: 'warning',
    color: 'red-4',
    bg: 'rgba(239,68,68,.12)',
  },
  {
    label: 'System',
    value: notifications.value.filter((n) => n.type === 'system').length,
    icon: 'settings',
    color: 'cyan-4',
    bg: 'rgba(6,182,212,.12)',
  },
])

const markRead = (n) => {
  const i = notifications.value.findIndex((x) => x.id === n.id)
  notifications.value[i].read = !notifications.value[i].read
}
const markAllRead = () => notifications.value.forEach((n) => (n.read = true))
const deleteNotif = (id) => {
  notifications.value = notifications.value.filter((n) => n.id !== id)
}
const sendNotification = () => {
  notifications.value.unshift({
    id: Date.now(),
    title: sendForm.value.title,
    body: sendForm.value.body,
    type: sendForm.value.type,
    read: false,
    created_at: 'Just now',
  })
  sendForm.value = { title: '', body: '', type: 'system', audience: 'All Users', urgent: false }
  sendModal.value = false
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
.stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}
.stat-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.notif-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.notif-card:hover {
  border-color: rgba(59, 130, 246, 0.25);
  background: #f0f7ff;
}
.notif-unread {
  border-left: 3px solid #3b82f6 !important;
}
.notif-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.notif-body {
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
}
.modal-card {
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
}
</style>
