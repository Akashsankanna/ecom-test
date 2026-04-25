import { useAuthStore } from 'src/stores/auth'

export default () => {
  const authStore = useAuthStore()

  // ✅ restore from localStorage (optional safety)
  const token = localStorage.getItem('token')
  const user  = JSON.parse(localStorage.getItem('user'))

  if (token && user && !authStore.token) {
    authStore.setAuth(token, user)
  }
}