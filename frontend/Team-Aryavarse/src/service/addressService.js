import { api } from 'boot/axios'

// helper
function getUserId() {
  const id = localStorage.getItem('user_id')
  return id ? Number(id) : null
}

// ======================
// GET ALL ADDRESSES
// ======================
export async function fetchAddresses(userId) {
  const finalUserId = userId || getUserId()

  if (!finalUserId) {
    throw new Error('User ID missing')
  }

  const response = await api.get('/address/', {
    params: { user_id: finalUserId }
  })

  return response.data
}

// ======================
// GET SINGLE ADDRESS
// ======================
export async function fetchAddressById(addressId, userId) {
  const finalUserId = userId || getUserId()

  if (!finalUserId) {
    throw new Error('User ID missing')
  }

  const response = await api.get(`/address/${addressId}`, {
    params: { user_id: finalUserId }
  })

  return response.data
}

// ======================
// CREATE ADDRESS
// ======================
export async function createAddress(payload) {
  const userId = getUserId()

  if (!userId) {
    throw new Error('User not logged in')
  }

  const response = await api.post('/address/', {
    user_id: userId,
    ...payload
  })

  return response.data
}

// ======================
// UPDATE ADDRESS
// ======================
export async function updateAddress(addressId, payload) {
  const userId = getUserId()

  if (!userId) {
    throw new Error('User not logged in')
  }

  const response = await api.put(`/address/${addressId}`, {
    user_id: userId,
    ...payload
  })

  return response.data
}

// ======================
// DELETE ADDRESS
// ======================
export async function removeAddress(addressId, userId) {
  const finalUserId = userId || getUserId()

  if (!finalUserId) {
    throw new Error('User ID missing')
  }

  const response = await api.delete(`/address/${addressId}`, {
    params: { user_id: finalUserId }
  })

  return response.data
}
