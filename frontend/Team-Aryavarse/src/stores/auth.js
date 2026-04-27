import { defineStore } from 'pinia'
import { api } from 'boot/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    id_token: localStorage.getItem('id_token') || null,
    user_id: localStorage.getItem('user_id') || null
  }),

  actions: {
    async setAuth(token, userData) {
      this.token = token
      this.user = userData
      this.id_token = userData?.id_token || userData?.token || null

      // support different backend response shapes
      const userId =
        userData?.id ||
        userData?.user_id ||
        userData?.user?.id ||
        userData?.data?.id ||
        null

      console.log('setAuth userData:', userData)
      console.log('resolved userId:', userId)

      if (!userId) {
        console.error('user_id missing in userData', userData)
        return
      }

      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('id_token', userData?.id_token || '')
      localStorage.setItem('user_id', String(userId))

      this.user_id = String(userId)

      const guestUuid = localStorage.getItem('guest_uuid')

      if (guestUuid) {
        try {
          await api.post('/cart/merge', {
            guest_uuid: guestUuid,
            user_id: Number(userId)
          })

          console.log('Cart merged successfully')
          localStorage.removeItem('guest_uuid')
        } catch (err) {
          console.error('Merge failed:', err?.response?.data || err.message)
        }
      }
    },

    logout() {
      this.token = null
      this.user = null
      this.id_token = null
      this.user_id = null

      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('id_token')
      localStorage.removeItem('user_id')
    }
  }
})
