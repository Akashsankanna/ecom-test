<template>
  <q-page class="order-page q-pa-md q-pa-lg-xl">
    <div class="page-container">
      <!-- Top Success Header -->
      <q-card flat class="top-card q-mb-lg">
        <div class="row items-center justify-between q-col-gutter-lg">
          <div class="col-12 col-md-7">
            <div class="row items-center no-wrap">
              <div class="success-icon-wrapper q-mr-md">
                <q-icon name="check_circle" size="40px" class="success-icon" />
              </div>

              <div>
                <div class="text-h5 text-weight-bold text-dark">
                  Order Confirmed
                </div>
                <div class="text-subtitle2 text-grey-7 q-mt-xs">
                  Your order has been placed successfully.
                </div>
                <div class="order-id q-mt-sm">
                  #ORD12345
                </div>
              </div>
            </div>
          </div>

          <div class="col-12 col-md-5 text-md-right">
            <div class="delivery-label">Estimated Delivery</div>
            <div class="delivery-date">25 Apr 2026</div>
            <div class="delivery-note text-grey-7">
              Standard delivery timeline
            </div>
          </div>
        </div>
      </q-card>

      <!-- Main Grid -->
      <div class="row q-col-gutter-lg">
        <!-- Left Column -->
        <div class="col-12 col-lg-7">
          <!-- Product Card -->
          <q-card flat class="section-card q-mb-lg">
            <div class="section-title">Product Details</div>

            <div class="product-box">
              <q-img
                src="https://via.placeholder.com/140x160?text=Product"
                class="product-image"
                fit="cover"
              />

              <div class="product-info">
                <div class="product-name">
                  Premium Medical Scrub Set
                </div>

                <div class="product-meta q-mt-sm">
                  Variant: Medium / Teal Blue
                </div>

                <div class="product-meta">
                  Quantity: 2
                </div>

                <div class="product-price q-mt-md">
                  ₹1,998
                </div>
              </div>
            </div>
          </q-card>

          <!-- Delivery Address -->
          <q-card flat class="section-card q-mb-lg">
            <div class="section-title">Delivery Address</div>

            <div class="info-block">
              <div class="info-name">Akash Sankanna</div>
              <div class="info-line">Flat 204, Sai Residency</div>
              <div class="info-line">College Road, Nashik</div>
              <div class="info-line">Maharashtra - 422005</div>
              <div class="info-line">Phone: +91 9876543210</div>
            </div>
          </q-card>

          <!-- Courier Details -->
          <q-card flat class="section-card">
            <div class="section-title">Courier / Tracking Info</div>

            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <div class="mini-info-label">Courier Partner</div>
                <div class="mini-info-value">Delhivery</div>
              </div>

              <div class="col-12 col-md-6">
                <div class="mini-info-label">Tracking ID</div>
                <div class="mini-info-value">TRK9823412456</div>
              </div>
            </div>
          </q-card>
        </div>

        <!-- Right Column -->
        <div class="col-12 col-lg-5">
          <!-- Tracking Status -->
          <q-card flat class="section-card q-mb-lg">
           <div class="section-title">Tracking Status</div>
           <div class="tracking-list">
     <div
       v-for="(step, index) in trackingSteps"
      :key="index"
      class="tracking-item"
     >
      <div class="tracking-left">

        <!-- DOT -->
        <div
          class="tracking-dot"
          :class="{
            completed: step.status === 'completed',
            active: step.status === 'active',
            pending: step.status === 'pending'
          }"
        >
          <q-icon v-if="step.status === 'completed'" name="check" size="16px" />
          <q-icon v-else-if="step.status === 'active'" name="schedule" size="15px" />
        </div>

        <!-- LINE -->
        <div
          v-if="index !== trackingSteps.length - 1"
          class="tracking-line"
          :class="{
            'line-completed':
              step.status === 'completed' ||
              step.status === 'active'
          }"
        />

      </div>

      <!-- TEXT -->
      <div class="tracking-content">
        <div class="tracking-title">
          {{ step.title }}
        </div>
        <div class="tracking-subtitle">
          {{ step.subtitle }}
        </div>
      </div>

    </div>
  </div>
</q-card>

          <!-- Payment Summary -->
          <q-card flat class="section-card q-mb-lg">
            <div class="section-title">Payment Summary</div>

            <div class="summary-row">
              <span>Subtotal</span>
              <span>₹1,694</span>
            </div>

            <div class="summary-row">
              <span>GST (18%)</span>
              <span>₹304</span>
            </div>

            <div class="summary-row">
              <span>Shipping</span>
              <span>Free</span>
            </div>

            <q-separator class="q-my-md" />

            <div class="summary-row total-row">
              <span>Total</span>
              <span>₹1,998</span>
            </div>

            <div class="payment-badge q-mt-md">
              <q-icon name="verified" size="18px" class="q-mr-xs" />
              Payment Successful
            </div>
          </q-card>

          <!-- Actions -->
          <div class="row q-col-gutter-sm">
            <div class="col-12 col-sm-6">
              <q-btn
                unelevated
                class="full-width action-btn secondary-btn"
                label="Continue Shopping"
                @click="$router.push('/')"
              />
            </div>

            <div class="col-12 col-sm-6">
              <q-btn
                unelevated
                class="full-width action-btn primary-btn"
                label="View Orders"
                @click="$router.push('/orders')"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
defineOptions({
  name: 'OrderConfirmationPage'
})
const trackingSteps = [
  {
    title: 'Order Placed',
    subtitle: 'Your order has been placed successfully',
    status: 'completed'
  },
  {
    title: 'Confirmed',
    subtitle: 'Your payment and order details are confirmed',
    status: 'completed'
  },
  {
    title: 'Processing',
    subtitle: 'Your items are being prepared for shipment',
    status: 'active'
  },
  {
    title: 'Shipped',
    subtitle: 'Your package will be dispatched soon',
    status: 'pending'
  },
  {
    title: 'Out for Delivery',
    subtitle: 'Courier partner will deliver your order',
    status: 'pending'
  },
  {
    title: 'Delivered',
    subtitle: 'Package delivered successfully',
    status: 'pending'
  }
]
</script>

<style scoped>
.order-page {
  background: linear-gradient(180deg, #f4fbfb 0%, #ffffff 100%);
  min-height: 100vh;
}

.page-container {
  max-width: 1320px;
  margin: 0 auto;
}

.top-card,
.section-card {
  background: #ffffff;
  border-radius: 22px;
  box-shadow: 0 10px 30px rgba(15, 157, 154, 0.08);
  border: 1px solid #e8f3f3;
}

.top-card {
  padding: 28px;
}

.section-card {
  padding: 24px;
}

.success-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: #e9f8f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-icon {
  color: #18a46b;
}

.text-dark {
  color: #17313b;
}

.order-id {
  display: inline-block;
  padding: 8px 14px;
  border-radius: 999px;
  background: #e8f7f7;
  color: #0f7f7c;
  font-weight: 700;
  font-size: 14px;
}

.delivery-label {
  font-size: 14px;
  color: #6c7a80;
  margin-bottom: 4px;
}

.delivery-date {
  font-size: 28px;
  font-weight: 700;
  color: #17313b;
}

.delivery-note {
  font-size: 13px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #17313b;
  margin-bottom: 20px;
}

.product-box {
  display: flex;
  gap: 18px;
  align-items: flex-start;
}

.product-image {
  width: 140px;
  min-width: 140px;
  height: 160px;
  border-radius: 18px;
  overflow: hidden;
  background: #f5f5f5;
}

.product-info {
  flex: 1;
}

.product-name {
  font-size: 22px;
  font-weight: 700;
  color: #17313b;
  line-height: 1.3;
}

.product-meta {
  font-size: 15px;
  color: #61737a;
  margin-bottom: 4px;
}

.product-price {
  font-size: 26px;
  font-weight: 700;
  color: #0f9d9a;
}

.info-block {
  line-height: 1.8;
}

.info-name {
  font-size: 17px;
  font-weight: 700;
  color: #17313b;
}

.info-line {
  color: #61737a;
  font-size: 15px;
}

.mini-info-label {
  font-size: 13px;
  color: #6d7b80;
  margin-bottom: 6px;
}

.mini-info-value {
  font-size: 17px;
  font-weight: 700;
  color: #17313b;
}

.tracking-list {
  position: relative;
}

.tracking-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  position: relative;
}

.tracking-left {
  width: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tracking-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 2;
}

.tracking-dot.completed {
  background: #18a46b;
}

.tracking-dot.active {
  background: #1e88e5;
}

.tracking-dot.pending {
  background: #d8e3e6;
}

.tracking-line {
  width: 3px;
  height: 42px;
  background: #d8e3e6;
  margin-top: 4px;
  border-radius: 999px;
}

.line-completed {
  background: #0f9d9a;
}

.tracking-content {
  padding-bottom: 22px;
}

.tracking-title {
  font-size: 16px;
  font-weight: 700;
  color: #17313b;
}

.tracking-subtitle {
  font-size: 14px;
  color: #6b7a80;
  margin-top: 4px;
  line-height: 1.5;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #42555d;
  font-size: 15px;
  margin-bottom: 12px;
}

.total-row {
  font-size: 20px;
  font-weight: 700;
  color: #17313b;
}

.payment-badge {
  display: inline-flex;
  align-items: center;
  background: #e9f8f5;
  color: #16875a;
  padding: 10px 14px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
}

.action-btn {
  height: 50px;
  border-radius: 14px;
  font-weight: 700;
  text-transform: none;
  font-size: 15px;
}

.primary-btn {
  background: #0f9d9a;
  color: white;
}

.secondary-btn {
  background: #eef8f8;
  color: #0f7f7c;
}

@media (max-width: 768px) {
  .top-card,
  .section-card {
    padding: 18px;
  }

  .product-box {
    flex-direction: column;
  }

  .product-image {
    width: 100%;
    min-width: 100%;
    height: 240px;
  }

  .delivery-date {
    font-size: 22px;
  }

  .product-name {
    font-size: 20px;
  }
}
</style>
