<template>
  <div class="reviews-section">

    <!-- HEADER -->
    <div class="review-header">
      <h2>Customer Reviews</h2>
      <button class="write-btn" @click="openDialog">
        {{ triggerLabel }}
      </button>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="reviews-loading">
      <q-spinner color="primary" size="36px" />
    </div>

    <!-- REVIEW LIST -->
    <div v-else-if="reviewsList.length" class="reviews-grid">
      <div
        v-for="review in reviewsList"
        :key="review.id"
        class="review-card"
      >
        <div class="review-top">

          <!-- USER -->
          <div class="user-info">
            <div class="avatar">
              {{
                (review.user_name || review.user_email || 'A')
                  .charAt(0)
                  .toUpperCase()
              }}
            </div>
            <div>
              <strong>
                {{
                  review.user_name ||
                  (review.user_email
                    ? review.user_email.split('@')[0]
                    : 'Anonymous')
                }}
              </strong>
              <div class="review-date">
                {{ formatDate(review.created_at) }}
              </div>
            </div>
          </div>

          <!-- STARS -->
          <div class="stars">
            <span v-for="n in 5" :key="n">
              {{ n <= review.rating ? '★' : '☆' }}
            </span>
          </div>

        </div>

        <!-- TITLE -->
        <h4 v-if="review.title" class="review-title">
          {{ review.title }}
        </h4>

        <!-- COMMENT -->
        <p class="review-text">{{ review.comment }}</p>

      </div>
    </div>

    <!-- EMPTY -->
    <p v-else class="no-reviews">
      No reviews yet. Be the first to review!
    </p>

    <!-- REVIEW POPUP -->
    <q-dialog v-model="reviewDialog">
      <div class="review-popup">

        <button class="close-btn" @click="reviewDialog = false">✕</button>

        <h3>{{ dialogTitle }}</h3>

        <!-- RATING -->
        <div class="field">
          <label>Rating <span class="req">*</span></label>
          <div class="stars-input">
            <span
              v-for="n in 5"
              :key="n"
              @click="reviewRating = n"
              :class="{ active: n <= reviewRating }"
            >★</span>
          </div>
          <p v-if="errors.rating" class="error">{{ errors.rating }}</p>
        </div>

        <!-- TITLE -->
        <div class="field">
          <label>Review Title</label>
          <q-input
            v-model="reviewTitle"
            placeholder="Short review title"
            outlined
            dense
          />
        </div>

        <!-- COMMENT -->
        <div class="field">
          <label>Your Review <span class="req">*</span></label>
          <q-input
            v-model="reviewComment"
            type="textarea"
            maxlength="1000"
            counter
            placeholder="Write your experience..."
            outlined
            class="limited-textarea"
          />
          <p v-if="errors.comment" class="error">{{ errors.comment }}</p>
        </div>

        <!-- API ERROR -->
        <p v-if="submitError" class="error submit-error">
          {{ submitError }}
        </p>

        <!-- ACTIONS -->
        <div class="actions">
          <q-btn
            :label="submitLabel"
            :loading="submitting"
            :disable="submitting"
            @click="submitReview"
          />
        </div>

      </div>
    </q-dialog>

  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'

/* ── Props ───────────────────────────────────────────────── */
const props = defineProps({
  productId : { type: Number, required: true },
  reviews   : { type: Array,  default: () => [] }
})

const emit = defineEmits(['updateReviews'])

/* ── Store ───────────────────────────────────────────────── */
const authStore = useAuthStore()

/* ── State ───────────────────────────────────────────────── */
const localReviews  = ref([])
const loading       = ref(false)
const reviewDialog  = ref(false)
const submitting    = ref(false)
const submitError   = ref('')
const reviewTitle   = ref('')
const reviewComment = ref('')
const reviewRating  = ref(0)
const errors        = ref({ rating: '', comment: '' })

// tracks the current user's existing review (null = no review yet)
const existingReview = ref(null)

/* ── Computed ────────────────────────────────────────────── */
const reviewsList = computed(() => localReviews.value || [])

// true when user already has a review for this product
const isEditMode = computed(() => !!existingReview.value)

// dynamic button/header labels
const dialogTitle  = computed(() => isEditMode.value ? 'Edit Your Review' : 'Write Your Review')
const submitLabel  = computed(() => isEditMode.value ? 'Update Review'    : 'Submit Review')
const triggerLabel = computed(() => isEditMode.value ? 'Edit Your Review' : 'Write Your Review')

/* ── Token resolution ────────────────────────────────────── */
/*
  Always read authStore.token (Pinia, set on login) first.
  Fall back to localStorage 'token' key (access_token only).
  NEVER use 'id_token' for API calls — Keycloak rejects it.
*/
const resolveToken = () => {
  return authStore.token || localStorage.getItem('token') || null
}

/* ── Fetch reviews (public) ──────────────────────────────── */
const fetchReviews = async () => {
  if (!props.productId) return
  loading.value = true
  try {
    const res = await api.get(`/api/v1/reviews/${props.productId}`)
    localReviews.value = Array.isArray(res.data) ? res.data : []
    emit('updateReviews', localReviews.value)
  } catch (err) {
    console.error('Fetch reviews error:', err?.response?.data || err)
    localReviews.value = []
  } finally {
    loading.value = false
  }
}

// fetch the current user's own review for this product
// only called when user is logged in — silently does nothing if not authed
const fetchMyReview = async () => {
  if (!props.productId) return
  if (!resolveToken()) return  // not logged in — skip silently

  try {
    const res = await api.get(`/api/v1/reviews/my/${props.productId}`)
    // backend returns null (HTTP 200) if no review exists yet
    existingReview.value = res.data || null
  } catch (err) {
    // 401 = not logged in, 404 = no review — both are fine, just clear
    existingReview.value = null
  }
}

/* ── Lifecycle ───────────────────────────────────────────── */
onMounted(() => {
  if (props.reviews?.length) localReviews.value = props.reviews
  fetchReviews()
  fetchMyReview()
})

watch(() => props.productId, async (v) => {
  if (v) {
    await fetchReviews()
    await fetchMyReview()  // re-check when product changes
  }
})

/* ── Dialog ──────────────────────────────────────────────── */
const openDialog = () => {
  resetForm()

  // if user already has a review, prefill the form
  if (existingReview.value) {
    reviewRating.value  = existingReview.value.rating  || 0
    reviewTitle.value   = existingReview.value.title   || ''
    reviewComment.value = existingReview.value.comment || ''
  }

  reviewDialog.value = true
}

/* ── Validation ──────────────────────────────────────────── */
const validateForm = () => {
  errors.value = { rating: '', comment: '' }
  let valid = true
  if (!reviewRating.value) {
    errors.value.rating = 'Please select a rating'
    valid = false
  }
  if (!reviewComment.value?.trim()) {
    errors.value.comment = 'Review is required'
    valid = false
  }
  return valid
}

/* ── Submit / Update review ──────────────────────────────── */
const submitReview = async () => {
  submitError.value = ''

  // check auth store first — if there is no session at all, stop early.
  // an expired-but-refreshable token is handled by the axios interceptor automatically.
  if (!authStore.token && !localStorage.getItem('token')) {
    submitError.value = 'Please log in to submit a review.'
    return
  }

  if (!validateForm()) return

  submitting.value = true

  try {
    const payload = {
      product_id : props.productId,
      rating     : reviewRating.value,
      title      : reviewTitle.value?.trim() || null,
      comment    : reviewComment.value.trim(),
    }

    if (isEditMode.value) {
      // PUT to update existing review
      await api.put(`/api/v1/reviews/${existingReview.value.id}`, payload)
    } else {
      // POST for new review
      await api.post('/api/v1/reviews', payload)
    }

    reviewDialog.value = false
    resetForm()
    await fetchReviews()
    await fetchMyReview()  // refresh existing review state after submit

  } catch (err) {
    const status = err?.response?.status
    const detail = err?.response?.data?.detail

    if (status === 409) {
      submitError.value = 'You have already reviewed this product.'
    } else if (status === 403) {
      submitError.value = 'You can only edit your own review.'
    } else if (status === 401) {
      // only reaches here if refresh also failed inside the interceptor
      submitError.value = 'Session expired. Please log out and log in again.'
    } else if (status === 422) {
      submitError.value = 'Invalid data. Please check your review and try again.'
    } else if (typeof detail === 'string') {
      submitError.value = detail
    } else {
      submitError.value = 'Something went wrong. Please try again.'
    }
  } finally {
    submitting.value = false
  }
}

/* ── Reset ───────────────────────────────────────────────── */
const resetForm = () => {
  reviewTitle.value   = ''
  reviewComment.value = ''
  reviewRating.value  = 0
  submitError.value   = ''
  errors.value        = { rating: '', comment: '' }
}

/* ── Date format ─────────────────────────────────────────── */
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}
</script>

<style scoped>
.reviews-section {
  margin-top: 60px;
  padding: 40px 25px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow:
    0 10px 30px rgba(0,0,0,0.08),
    0 2px 10px rgba(0,0,0,0.05);
  transition: 0.3s ease;
}

.review-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 35px;
}

.review-header h2 {
  position: relative;
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  color: #111;
  text-align: center;
}

.review-header h2::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -10px;
  width: 65px;
  height: 4px;
  border-radius: 20px;
  background: linear-gradient(90deg, #007b7f, #00c6ff);
  transform: translateX(-50%);
}

.write-btn {
  position: absolute;
  right: 0;
  white-space: nowrap;
  background: linear-gradient(135deg, #007b7f, #00c6ff);
  color: #fff;
  padding: 12px 18px;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s ease;
}

.write-btn:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 10px 25px rgba(0, 123, 127, 0.3);
}

.reviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 340px));
  justify-content: center;
  gap: 20px;
}

.review-card {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border-radius: 18px;
  padding: 20px;
  border: 1px solid #eee;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(30px);
  animation: fadeUp 0.6s ease forwards;
}

.review-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: 0.3s;
}

.review-card:hover::before { opacity: 1; }

.review-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 15px 35px rgba(0,0,0,0.1);
}

.review-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007b7f, #00c6ff);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.user-info strong { font-size: 15px; }
.review-date { font-size: 12px; color: #888; }
.review-title { margin: 10px 0 4px; font-size: 15px; font-weight: 700; }
.review-text { margin-top: 12px; font-size: 14px; color: #444; line-height: 1.6; }

.stars { font-size: 16px; }
.stars span { color: #fbbf24; transition: 0.2s; }

@keyframes fadeUp {
  to { opacity: 1; transform: translateY(0); }
}

.reviews-section p { text-align: center; color: gray; margin-top: 20px; }

.review-popup {
  position: relative;
  width: 92vw;
  max-width: 520px;
  background: #fff;
  border-radius: 18px;
  padding: 28px 24px;
  box-sizing: border-box;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  gap: 14px;
  animation: popupFade 0.25s ease;
}

.review-popup h3 {
  text-align: center;
  font-size: 30px;
  font-weight: 800;
  margin: 0 0 15px;
  color: #111;
  white-space: nowrap;
}

.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: #f1f5f9;
  color: #111;
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1000;
  transition: 0.25s ease;
}
.close-btn:hover { background: #111; color: white; }

.field { margin-bottom: 14px; }
.field label { font-size: 14px; font-weight: 600; display: block; margin-bottom: 6px; }
.req { color: #e53935; }

.stars-input { display: flex; gap: 6px; margin-top: 6px; }
.stars-input span { font-size: 26px; cursor: pointer; color: #d1d5db; transition: 0.25s ease; }
.stars-input span.active { color: #fbbf24; transform: scale(1.15); }
.stars-input span:hover { transform: scale(1.2); }

:deep(.limited-textarea textarea) {
  resize: vertical;
  min-height: 60px;
  max-height: 120px;
  overflow-y: auto;
}

.error { font-size: 12px; color: #d93025; margin-top: 4px; }
.submit-error { text-align: center; margin-top: 0; }

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.actions .q-btn:first-child {
  background: #000 !important;
  color: #fff !important;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
}

@keyframes popupFade {
  from { opacity: 0; transform: scale(0.92); }
  to   { opacity: 1; transform: scale(1); }
}

@media (max-width: 768px) {
  .reviews-section { padding: 24px 14px; }
  .review-header { justify-content: space-between; gap: 8px; }
  .review-header h2 { font-size: 18px; flex: 1; text-align: left; }
  .write-btn { position: static; padding: 8px 10px; font-size: 11px; flex-shrink: 0; }
  .review-header h2::after { left: 40px; transform: none; }
  .reviews-grid { grid-template-columns: 1fr; }
  .review-card { padding: 16px; }
  .review-top { flex-direction: column; align-items: flex-start; gap: 10px; }
  .review-popup { width: 94vw; padding: 22px 16px; border-radius: 16px; }
  .review-popup h3 { font-size: 22px; }
  .stars-input span { font-size: 24px; }
}

@media (max-width: 480px) {
  .write-btn { font-size: 12px; padding: 9px 12px; }
  .review-popup { width: 95vw; padding: 20px 14px; }
  .review-popup h3 { font-size: 20px; }
  .close-btn { width: 28px; height: 28px; font-size: 15px; }
  .actions .q-btn:first-child { width: 100%; }
}
</style>