// import { boot } from 'quasar/wrappers'
// import axios from 'axios'

// const api = axios.create({
//   baseURL: 'http://localhost:8000'
// })

// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('token')

//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`
//   }

//   return config
// })

// export default boot(({ app }) => {
//   app.config.globalProperties.$api = api
// })

// export { api }
import { boot } from 'quasar/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/* Request Interceptor */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

/* Response Interceptor */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API ERROR:', error)

    if (error.response?.status === 401) {
      localStorage.removeItem('token')
    }

    return Promise.reject(error)
  }
)

export default boot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }