import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const PREFIX = '/admin/coupons'

const http = axios.create({
  baseURL: BASE_URL,
  timeout: 15000
})

function getToken() {
  return (
    localStorage.getItem('admin_token') ||
    localStorage.getItem('token') ||
    localStorage.getItem('access_token') ||
    localStorage.getItem('auth_token') ||
    ''
  )
}

http.interceptors.request.use((config) => {
  const token = getToken()

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  config.headers['Content-Type'] = 'application/json'
  return config
})

http.interceptors.response.use(
  (res) => res,
  (error) => {
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      'Unexpected error'

    return Promise.reject({
      status: error?.response?.status || 0,
      message
    })
  }
)

async function request(method, url, payload = null, params = null) {
  const config = { method, url }

  if (payload) config.data = payload
  if (params) config.params = params

  const res = await http(config)
  return res.data
}

/* CRUD */
const getAll = (filters = {}) =>
  request('get', `${PREFIX}/`, null, filters)

const list = getAll

const getById = (id) =>
  request('get', `${PREFIX}/${id}`)

const create = (payload) =>
  request('post', `${PREFIX}/`, payload)

const update = (id, payload) =>
  request('put', `${PREFIX}/${id}`, payload)

const deactivate = (id) =>
  request('delete', `${PREFIX}/${id}`)

const remove = deactivate

/* Analytics */
const getStats = () =>
  request('get', `${PREFIX}/stats`)

const stats = getStats

const getPerformance = (params = {}) =>
  request('get', `${PREFIX}/performance`, null, params)

const performance = getPerformance

const getUsageHistory = (params = {}) =>
  request('get', `${PREFIX}/usage`, null, params)

const usage = getUsageHistory

/* Apply */
const applyCoupon = (payload) =>
  request('post', `${PREFIX}/apply`, payload)

const apply = applyCoupon

/* Helpers */
const genCode = () =>
  'PROMO' + Math.random().toString(36).substring(2, 7).toUpperCase()

export default {
  /* old + new both */
  getAll,
  list,

  getById,
  create,
  update,

  deactivate,
  remove,

  getStats,
  stats,

  getPerformance,
  performance,

  getUsageHistory,
  usage,

  applyCoupon,
  apply,

  genCode
}