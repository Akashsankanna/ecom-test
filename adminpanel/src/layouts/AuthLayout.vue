<template>
  <q-layout>
    <div
      class="auth-wrapper"
      style="background-image: url('src/assets/login_bg/Medi frame scrubs.png')"
    >
      <div class="auth-overlay"></div>

      <div class="auth-form-area">
        <router-view />
      </div>
    </div>
  </q-layout>
</template>

<style scoped lang="scss">
.auth-wrapper {
  min-height: 100vh;
  width: 100%;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30px 60px;
  overflow: hidden;
}

.auth-overlay {
  position: absolute;
  inset: 0;
  
  backdrop-filter: blur(1px);
}

.auth-form-area {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 430px;
  display: flex;
  justify-content: center;
}

@media (max-width: 992px) {
  .auth-wrapper {
    justify-content: center;
    padding: 20px;
    background-position: center;
  }

  .auth-form-area {
    max-width: 100%;
  }
}
</style>