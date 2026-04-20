export default [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      // HOME
      { path: '', component: () => import('pages/HomePage.vue') },
      { path: 'home', component: () => import('pages/HomePage.vue') },

      // CATEGORY PAGES
      { path: 'men', component: () => import('pages/MenPage.vue') },
      { path: 'women', component: () => import('pages/WomenPage.vue') },
      { path: 'aprons', component: () => import('pages/Aprons.vue') },

      // BULK
      { path: 'bulk', component: () => import('pages/BulkOrder.vue') },

      // PRODUCT DETAILS
      { path: 'product/:id', component: () => import('pages/ProductDetailsPage.vue') },
      { path: 'men-product/:id', component: () => import('pages/MenProductDetailsPage.vue') },
      { path: 'women-product/:id', component: () => import('pages/WomenProductDetails.vue') },
      { path: 'aprons-product/:id', component: () => import('pages/ApronsProductDetail.vue') },

      // USER FEATURES
      { path: 'cart', component: () => import('pages/CartPage.vue') },
      { path: 'wishlist', component: () => import('pages/WishlistPage.vue') },
      { path: 'profile', component: () => import('pages/ProfilePage.vue') },

      // ✅ ADD THESE CHECKOUT ROUTES
      { path: 'checkout/address', component: () => import('pages/CheckoutAddress.vue') },
      { path: 'checkout/payment', component: () => import('pages/CheckoutPayment.vue') },
      { path: 'checkout/summary', component: () => import('pages/CheckoutSummary.vue') },
       { path: 'checkout/confirmation', component: () => import('pages/CheckoutConfirmation.vue') },

      // FOOTER / INFO
      { path: 'about', component: () => import('pages/AboutPage.vue') },
      { path: 'contact', component: () => import('pages/ContactPage.vue') },
    ]
  },

  {
    path: '/',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      { path: 'login', component: () => import('pages/auth/LoginPage.vue') },
      { path: 'signup', component: () => import('pages/auth/SignupPage.vue') },
      { path: 'forgot-password', component: () => import('pages/auth/ForgotPassword.vue') }
    ]
  },

  {
    path: '/auth/callback',
    component: () => import('pages/AuthCallback.vue')
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]
