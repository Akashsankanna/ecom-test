<template>
  <q-page class="admin-page">
    <div class="page-header q-px-lg q-pt-lg q-pb-md">
      <div class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold text-grey-9">Reviews</div>
          <div class="text-caption text-blue-7">Moderate customer product reviews</div>
        </div>
        <div class="row q-gutter-sm">
          <q-chip color="warning" text-color="white" icon="pending" size="sm"
            >Pending: {{ pendingCount }}</q-chip
          >
        </div>
      </div>
    </div>

    <div class="q-px-lg q-pb-lg q-pt-md">
      <!-- Tabs -->
      <q-tabs
        v-model="tab"
        dense
        align="left"
        active-color="blue-4"
        indicator-color="blue-5"
        class="q-mb-md"
      >
        <q-tab name="all" label="All Reviews" />
        <q-tab name="pending" label="Pending" />
        <q-tab name="approved" label="Approved" />
        <q-tab name="rejected" label="Rejected" />
      </q-tabs>

      <!-- Filters -->
      <div class="row q-gutter-md q-mb-md">
        <div class="col-12 col-sm">
          <q-input
            v-model="search"
            placeholder="Search by product or reviewer..."
            dense
            standout="bg-blue-1"
            clearable
          >
            <template #prepend><q-icon name="search" color="blue-4" /></template>
          </q-input>
        </div>
        <div class="col-auto">
          <q-select
            v-model="ratingFilter"
            :options="['All Ratings', '5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star']"
            dense
            standout="bg-blue-1"
            style="min-width: 140px"
          />
        </div>
      </div>

      <!-- Reviews Grid -->
      <div class="row q-gutter-md">
        <div class="col-12 col-md-6 col-lg-4" v-for="review in filteredReviews" :key="review.id">
          <q-card class="review-card" flat>
            <q-card-section class="q-pb-xs">
              <div class="row items-start justify-between">
                <div class="row items-center q-gutter-sm">
                  <q-avatar
                    size="36px"
                    :color="avatarColor(review.id)"
                    text-color="white"
                    font-size="13px"
                  >
                    {{ review.reviewer[0] }}
                  </q-avatar>
                  <div>
                    <div class="text-grey-9 text-weight-medium text-subtitle2">
                      {{ review.reviewer }}
                    </div>
                    <div class="text-caption text-blue-7">{{ review.created_at }}</div>
                  </div>
                </div>
                <q-badge :color="statusColor(review.status)" :label="review.status" size="sm" />
              </div>
            </q-card-section>

            <q-card-section class="q-pt-xs q-pb-xs">
              <div class="text-caption text-blue-4 q-mb-xs">
                <q-icon name="inventory_2" size="12px" class="q-mr-xs" />{{ review.product }}
              </div>
              <!-- Stars -->
              <div class="row items-center q-gutter-xs q-mb-sm">
                <q-icon
                  v-for="n in 5"
                  :key="n"
                  name="star"
                  size="16px"
                  :color="n <= review.rating ? 'amber-5' : 'grey-2'"
                />
                <span class="text-caption text-blue-7">({{ review.rating }}/5)</span>
              </div>
              <div class="review-text">{{ review.comment }}</div>
            </q-card-section>

            <q-separator style="opacity: 0.1" />
            <q-card-actions>
              <template v-if="review.status === 'pending'">
                <q-btn
                  label="Approve"
                  flat
                  size="sm"
                  color="positive"
                  no-caps
                  icon="check_circle"
                  @click="approveReview(review)"
                  class="col"
                />
                <q-btn
                  label="Reject"
                  flat
                  size="sm"
                  color="negative"
                  no-caps
                  icon="cancel"
                  @click="rejectReview(review)"
                  class="col"
                />
              </template>
              <template v-else>
                <q-btn-dropdown
                  :label="review.status === 'approved' ? 'Approved' : 'Rejected'"
                  flat
                  size="sm"
                  :color="statusColor(review.status)"
                  no-caps
                  :icon="review.status === 'approved' ? 'check_circle' : 'cancel'"
                  auto-close
                >
                  <q-list>
                    <q-item clickable @click="approveReview(review)">
                      <q-item-section
                        ><q-item-label class="text-positive">Approve</q-item-label></q-item-section
                      >
                    </q-item>
                    <q-item clickable @click="rejectReview(review)">
                      <q-item-section
                        ><q-item-label class="text-negative">Reject</q-item-label></q-item-section
                      >
                    </q-item>
                  </q-list>
                </q-btn-dropdown>
              </template>
            </q-card-actions>
          </q-card>
        </div>

        <div v-if="!filteredReviews.length" class="col-12 column flex-center q-pa-xl text-blue-7">
          <q-icon name="rate_review" size="56px" class="q-mb-sm" />
          <div>No reviews found</div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
const tab = ref('all')
const search = ref('')
const ratingFilter = ref('All Ratings')

const reviews = ref([
  {
    id: 1,
    reviewer: 'Rahul Sharma',
    product: 'Wireless Earbuds Pro',
    rating: 5,
    comment: 'Amazing sound quality! Noise cancellation is top notch. Highly recommend.',
    status: 'pending',
    created_at: '2024-01-15',
  },
  {
    id: 2,
    reviewer: 'Priya Mehta',
    product: 'Cotton T-Shirt Classic',
    rating: 4,
    comment: 'Good fabric quality, fits true to size. Color faded slightly after wash.',
    status: 'approved',
    created_at: '2024-01-14',
  },
  {
    id: 3,
    reviewer: 'Ankit Patel',
    product: 'Running Shoes X1',
    rating: 2,
    comment: 'Very uncomfortable after 30 mins. Size runs smaller than expected.',
    status: 'pending',
    created_at: '2024-01-14',
  },
  {
    id: 4,
    reviewer: 'Sneha Joshi',
    product: 'Mechanical Keyboard',
    rating: 5,
    comment: 'Absolutely love this keyboard. Typing feel is fantastic and build quality is solid.',
    status: 'approved',
    created_at: '2024-01-13',
  },
  {
    id: 5,
    reviewer: 'Vikram Singh',
    product: 'Wireless Earbuds Pro',
    rating: 3,
    comment: 'Average battery life. Sound is decent but not worth the price.',
    status: 'rejected',
    created_at: '2024-01-12',
  },
  {
    id: 6,
    reviewer: 'Divya Rao',
    product: 'Python Programming',
    rating: 5,
    comment: 'Best book for beginners. Very well explained concepts with practical examples.',
    status: 'pending',
    created_at: '2024-01-11',
  },
])

const filteredReviews = computed(() =>
  reviews.value.filter((r) => {
    const ms =
      !search.value ||
      r.product.toLowerCase().includes(search.value.toLowerCase()) ||
      r.reviewer.toLowerCase().includes(search.value.toLowerCase())
    const mt = tab.value === 'all' || r.status === tab.value
    const mr = ratingFilter.value === 'All Ratings' || r.rating === parseInt(ratingFilter.value)
    return ms && mt && mr
  }),
)

const pendingCount = computed(() => reviews.value.filter((r) => r.status === 'pending').length)
const statusColor = (s) =>
  ({ approved: 'positive', pending: 'warning', rejected: 'negative' })[s] || 'grey'
const avatarColors = ['blue-8', 'purple-8', 'teal-8', 'indigo-8', 'cyan-8', 'green-8']
const avatarColor = (id) => avatarColors[id % avatarColors.length]
const approveReview = (r) => {
  const i = reviews.value.findIndex((x) => x.id === r.id)
  reviews.value[i].status = 'approved'
}
const rejectReview = (r) => {
  const i = reviews.value.findIndex((x) => x.id === r.id)
  reviews.value[i].status = 'rejected'
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
.review-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: transform 0.2s;
}
.review-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
}
.review-text {
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
}
</style>
