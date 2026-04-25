// quasar.config.js
// Merged safely from both files without breaking logic

import { defineConfig } from '#q-app/wrappers'
import checker from 'vite-plugin-checker'

export default defineConfig(() => {
  return {
    // Boot files
    boot: [
      'axios',
      'auth'
    ],

    // CSS
    css: [
      'app.scss'
    ],

    // Extras
    extras: [
      'roboto-font',
      'material-icons'
    ],

    // Build
    build: {
      target: {
        browser: 'baseline-widely-available',
        node: 'node22'
      },

      // Keep hash mode as original
      vueRouterMode: 'hash',

      vitePlugins: [
        [
          checker,
          {
            eslint: {
              lintCommand:
                'eslint -c ./eslint.config.js "./src*/**/*.{js,mjs,cjs,vue}"',
              useFlatConfig: true
            }
          },
          { server: false }
        ]
      ]
    },

    // Dev Server
    devServer: {
      open: true
    },

    // Framework
   framework: {
  config: {
    notify: {}
  },

  plugins: [
    'Notify',
    'Dialog',
    'Loading'
  ]
},

    // Animations
    animations: [],

    // SSR
    ssr: {
      prodPort: 3000,

      middlewares: [
        'render'
      ],

      pwa: false
    },

    // PWA
    pwa: {
      workboxMode: 'GenerateSW'
    },

    // Cordova
    cordova: {},

    // Capacitor
    capacitor: {
      hideSplashscreen: true
    },

    // Electron
    electron: {
      preloadScripts: ['electron-preload'],

      inspectPort: 5858,

      bundler: 'packager',

      packager: {},

      builder: {
        // kept your custom app id
        appId: 'ecommerce-frontend'
      }
    },

    // Browser Extension
    bex: {
      extraScripts: []
    }
  }
})