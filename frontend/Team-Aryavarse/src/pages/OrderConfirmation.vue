<template>
  <q-page class="order-page flex flex-center column text-center">

    <div class="success-wrap">
      <div class="ring ring-one"></div>
      <div class="ring ring-two"></div>

      <div class="success-circle">
        <q-icon name="check" />
      </div>
    </div>

    <div class="title">
      Order Confirmed
    </div>

    <div class="subtitle">
      Your order has been placed successfully.
    </div>

    <q-btn
      label="Continue Shopping"
      class="custom-btn q-mt-lg"
      unelevated
      @click="router.push('/')"
    />

  </q-page>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.order-page {
  min-height: 100vh;
  height: 100vh;
  padding: 24px 16px;
  background:
    radial-gradient(circle at center, rgba(15, 108, 115, 0.16), transparent 34%),
    linear-gradient(135deg, #e6f7f6, #cfe3e3);
  font-family: 'DM Sans', sans-serif;
  overflow: hidden;
}

.success-wrap {
  position: relative;
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-circle {
  width: 105px;
  height: 105px;
  border-radius: 50%;
  background: linear-gradient(135deg, #20c96b, #0ca35b);
  color: white;
  font-size: 78px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 20px 45px rgba(12, 163, 91, 0.35),
    inset 0 -8px 16px rgba(0, 0, 0, 0.12);
  animation: boom 0.8s ease-out, breathe 2s ease-in-out infinite 1s;
  z-index: 2;
}

.ring {
  position: absolute;
  border-radius: 50%;
  border: 3px solid rgba(32, 201, 107, 0.45);
  animation: ripple 2s ease-out infinite;
}

.ring-one {
  width: 115px;
  height: 115px;
}

.ring-two {
  width: 115px;
  height: 115px;
  animation-delay: 0.7s;
}

.title {
  font-size: 54px;
  font-weight: 900;
  color: #082f35;
  margin-top: 26px;
  line-height: 1.1;
  animation: fadeUp 0.7s ease-out 0.25s both;
}

.subtitle {
  font-size: 17px;
  color: #5a7074;
  margin-top: 12px;
  padding: 0 12px;
  line-height: 1.5;
  animation: fadeUp 0.7s ease-out 0.45s both;
}

.custom-btn {
  background: #0f6c73;
  color: white;
  padding: 10px 26px;
  font-size: 14px;
  font-weight: 800;
  border-radius: 10px;
  box-shadow: 0 10px 22px rgba(15, 108, 115, 0.28);
  animation: fadeUp 0.7s ease-out 0.65s both;
  transition: 0.25s ease;
}

.custom-btn:hover {
  transform: translateY(-3px) scale(1.03);
  background: #168f96;
  box-shadow: 0 14px 30px rgba(15, 108, 115, 0.38);
}

@keyframes boom {
  0% {
    transform: scale(0.2);
    opacity: 0;
  }
  55% {
    transform: scale(1.18);
  }
  75% {
    transform: scale(0.94);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
    filter: brightness(1);
  }
  50% {
    transform: scale(1.08);
    filter: brightness(1.08);
  }
}

@keyframes ripple {
  0% {
    transform: scale(0.75);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.85);
    opacity: 0;
  }
}

@keyframes fadeUp {
  from {
    transform: translateY(24px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .success-wrap {
    width: 135px;
    height: 135px;
  }

  .success-circle {
    width: 95px;
    height: 95px;
    font-size: 70px;
  }

  .ring-one,
  .ring-two {
    width: 105px;
    height: 105px;
  }

  .title {
    font-size: 44px;
    margin-top: 22px;
  }

  .subtitle {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .order-page {
    padding: 20px 14px;
  }

  .success-wrap {
    width: 120px;
    height: 120px;
  }

  .success-circle {
    width: 84px;
    height: 84px;
    font-size: 62px;
  }

  .ring-one,
  .ring-two {
    width: 92px;
    height: 92px;
  }

  .title {
    font-size: 34px;
    margin-top: 18px;
  }

  .subtitle {
    font-size: 14px;
    max-width: 280px;
  }

  .custom-btn {
    padding: 9px 22px;
    font-size: 13px;
    border-radius: 9px;
  }
}

@media (max-width: 360px) {
  .title {
    font-size: 30px;
  }

  .subtitle {
    font-size: 13px;
  }

  .custom-btn {
    padding: 8px 18px;
    font-size: 12px;
  }
}
</style>

<style>
html,
body,
#q-app {
  height: 100%;
  overflow: hidden;
  background: #e6f7f6;
}
</style>
