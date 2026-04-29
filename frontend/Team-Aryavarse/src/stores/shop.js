import { ref } from 'vue'
import { api } from 'boot/axios'

import { womenProducts } from 'src/data/womenProducts'
import { menProducts } from 'src/data/menProducts'
import { apronsProducts } from 'src/data/apronsProducts'

import {
  addToCartApi,
  getCartApi,
  updateCartItemApi,
  removeCartItemApi
} from 'src/service/cart'

// ----------------------
// FRONTEND PRODUCT DATA
// ----------------------
const allFrontendProducts = [
  ...womenProducts,
  ...menProducts,
  ...apronsProducts
]

// ----------------------
// ASSET RESOLVE
// ----------------------
const assetModules = import.meta.glob('../assets/**/*.{png,jpg,jpeg,webp,avif,svg}', {
  eager: true,
  import: 'default'
})

const placeholderImage = 'https://via.placeholder.com/120x120?text=No+Image'

const normalizeAssetPath = (imgPath) => {
  if (!imgPath) return ''

  if (
    imgPath.startsWith('http://') ||
    imgPath.startsWith('https://') ||
    imgPath.startsWith('/')
  ) {
    return imgPath
  }

  if (imgPath.startsWith('src/assets/')) {
    return imgPath.replace('src/assets/', '../assets/')
  }

  return imgPath
}

const resolveAssetImage = (imgPath) => {
  const normalized = normalizeAssetPath(imgPath)

  if (!normalized) return placeholderImage

  if (
    normalized.startsWith('http://') ||
    normalized.startsWith('https://') ||
    normalized.startsWith('/')
  ) {
    return normalized
  }

  return assetModules[normalized] || placeholderImage
}

const getFrontendImage = (item) => {
  const backendName = String(item.product_name || item.name || item.title || '').trim().toLowerCase()
  const backendVariant = String(item.variant_name || item.color || '').trim().toLowerCase()

  const byColorVariantId = allFrontendProducts.find((p) =>
    Array.isArray(p.colors) &&
    p.colors.some((c) => Number(c.variant_id) === Number(item.variant_id))
  )

  if (byColorVariantId?.colors?.length) {
    const matchedColor = byColorVariantId.colors.find(
      (c) => Number(c.variant_id) === Number(item.variant_id)
    )
    if (matchedColor?.images?.[0]) return matchedColor.images[0]
  }

  const byVariantId = allFrontendProducts.find(
    (p) => Number(p.variant_id) === Number(item.variant_id)
  )

  if (byVariantId?.image) return byVariantId.image

  const byExactName = allFrontendProducts.find(
    (p) => String(p.title || p.name || '').trim().toLowerCase() === backendName
  )

  if (byExactName?.image) return byExactName.image

  const byLooseName = allFrontendProducts.find((p) => {
    const title = String(p.title || p.name || '').trim().toLowerCase()
    return title.includes(backendName) || backendName.includes(title)
  })

  if (byLooseName?.image) return byLooseName.image

  const byColorName = allFrontendProducts.find((p) => {
    const title = String(p.title || p.name || '').trim().toLowerCase()
    const color = String(p.color || '').trim().toLowerCase()

    return (
      (title.includes(backendName) || backendName.includes(title)) &&
      (backendVariant.includes(color) || color.includes(backendVariant))
    )
  })

  if (byColorName?.image) return byColorName.image

  return ''
}

// ----------------------
// AUTH HELPERS
// ----------------------
const getUserId = () => {
  return localStorage.getItem('user_id')
}

const getGuestUuid = () => {
  return localStorage.getItem('guest_uuid')
}

const getAuthParams = () => {
  const userId = getUserId()
  return userId ? `?user_id=${userId}` : ''
}

const getGuestHeaders = () => {
  const guestUuid = getGuestUuid()

  if (!getUserId() && guestUuid) {
    return {
      headers: {
        'guest-uuid': guestUuid
      }
    }
  }

  return {}
}

// ----------------------
// CART STATE
// ----------------------
export const cart = ref([])

// ----------------------
// WISHLIST STATE - BACKEND
// ----------------------
export const wishlist = ref([])

// ----------------------
// LOAD CART FROM BACKEND
// ----------------------
export const loadCart = async () => {
  try {
    const data = await getCartApi()
    const items = Array.isArray(data?.items) ? data.items : []

    cart.value = items.map((item) => {
      const finalImage = resolveAssetImage(item.image_url || getFrontendImage(item))

      return {
        id: Number(item.cart_item_id || item.id || 0),
        cart_item_id: Number(item.cart_item_id || item.id || 0),
        cart_id: Number(item.cart_id || 0),

        product_id: Number(item.product_id || 0),
        variant_id: Number(item.variant_id || 0),

        product_name: item.product_name || item.name || '',
        name: item.product_name || item.name || '',
        title: item.product_name || item.name || '',
        variant_name: item.variant_name || '',

        price: Number(item.price || 0),
        customization_total: Number(item.customization_total || 0),
        line_total: Number(item.line_total || 0),

        qty: Number(item.quantity || item.qty || 1),
        quantity: Number(item.quantity || item.qty || 1),

        stock: Number(item.stock || 0),
        size: item.size || '',
        color: item.color || '',

        image_url: finalImage,
        image: finalImage
      }
    })

    console.log('RAW CART API DATA:', data)
    console.log('MAPPED CART:', cart.value)
  } catch (err) {
    console.error('LOAD CART ERROR:', err)
    cart.value = []
  }
}

// ----------------------
// ADD TO CART
// supports:
// 1) addToCart(variantId, quantity)
// 2) addToCart(productObject)
// ----------------------
export const addToCart = async (productOrVariantId, quantity = 1) => {
  try {
    let variantId = null
    let qty = Number(quantity || 1)

    if (typeof productOrVariantId === 'object' && productOrVariantId !== null) {
      const product = productOrVariantId

      qty = Number(product.qty || product.quantity || 1)

      variantId =
        product.variant_id ||
        product.default_variant_id ||
        product.selected_variant_id ||
        null

      if (!variantId && Array.isArray(product.colors) && product.color) {
        const matchedColor = product.colors.find(
          (c) =>
            String(c.name || '').trim().toLowerCase() ===
            String(product.color || '').trim().toLowerCase()
        )

        variantId = matchedColor?.variant_id || null
      }
    } else {
      variantId = Number(productOrVariantId)
    }

    if (!variantId || Number(variantId) === 0) {
      console.error('ADD TO CART ERROR: variant_id missing', {
        input: productOrVariantId
      })
      return
    }

    await addToCartApi({
      variant_id: Number(variantId),
      quantity: Number(qty || 1)
    })

    await loadCart()
  } catch (err) {
    console.error('ADD TO CART ERROR:', err)
    throw err
  }
}

// ----------------------
// REMOVE FROM CART
// ----------------------
export const removeFromCart = async (productOrCartItemId) => {
  try {
    let cartItemId = null

    if (typeof productOrCartItemId === 'object' && productOrCartItemId !== null) {
      cartItemId = productOrCartItemId.cart_item_id || productOrCartItemId.id
    } else {
      cartItemId = productOrCartItemId
    }

    if (!cartItemId) return

    await removeCartItemApi(Number(cartItemId))
    await loadCart()
  } catch (err) {
    console.error('REMOVE CART ERROR:', err)
    throw err
  }
}

// ----------------------
// UPDATE CART QTY
// ----------------------
export const updateQty = async (productOrId, type) => {
  try {
    let item = null

    if (typeof productOrId === 'object' && productOrId !== null) {
      const id = productOrId.cart_item_id || productOrId.id

      item = cart.value.find(
        (i) => Number(i.id) === Number(id) || Number(i.cart_item_id) === Number(id)
      )
    } else {
      item = cart.value.find(
        (i) =>
          Number(i.id) === Number(productOrId) ||
          Number(i.cart_item_id) === Number(productOrId)
      )
    }

    if (!item) return

    let newQty = Number(item.qty || item.quantity || 1)

    if (type === 'inc') newQty++

    if (type === 'dec') {
      if (newQty > 1) {
        newQty--
      } else {
        await removeFromCart(item.cart_item_id || item.id)
        return
      }
    }

    await updateCartItemApi(Number(item.cart_item_id || item.id), Number(newQty))
    await loadCart()
  } catch (err) {
    console.error('UPDATE QTY ERROR:', err)
    throw err
  }
}

// ----------------------
// LOAD WISHLIST FROM BACKEND
// ----------------------
export const loadWishlist = async () => {
  try {
    const params = getAuthParams()
    const config = getGuestHeaders()

    if (!getUserId() && !getGuestUuid()) {
      wishlist.value = []
      return
    }

    const res = await api.get(`/wishlist/${params}`, config)

    const items = Array.isArray(res.data) ? res.data : []

    wishlist.value = items.map((item) => {
      const finalImage = resolveAssetImage(item.image_url || item.image || getFrontendImage(item))

      return {
        id: Number(item.wishlist_item_id || item.id || 0),
        wishlist_item_id: Number(item.wishlist_item_id || item.id || 0),

        product_id: Number(item.product_id || item.db_product_id || 0),
        db_product_id: Number(item.product_id || item.db_product_id || 0),

        variant_id: Number(item.variant_id || 0),

        product_name: item.product_name || item.name || item.title || '',
        name: item.name || item.product_name || item.title || '',
        title: item.title || item.name || item.product_name || '',

        description: item.description || '',

        price: Number(item.price || 0),
        size: item.size || '',
        color: item.color || '',
        hex_code: item.hex_code || '',
        stock: Number(item.stock || 0),

        image_url: finalImage,
        image: finalImage
      }
    })

    console.log('RAW WISHLIST API DATA:', res.data)
    console.log('MAPPED WISHLIST:', wishlist.value)
  } catch (err) {
    console.error('LOAD WISHLIST ERROR:', err)
    wishlist.value = []
  }
}

// ----------------------
// TOGGLE WISHLIST HEART
// ----------------------
export const toggleWishlist = async (product) => {
  try {
    const params = getAuthParams()
    const config = getGuestHeaders()

    if (!getUserId() && !getGuestUuid()) {
      console.error('WISHLIST ERROR: user_id or guest_uuid missing')
      return
    }

    const variantId =
      product.variant_id ||
      product.default_variant_id ||
      product.selected_variant_id ||
      null

    if (!variantId || Number(variantId) === 0) {
      console.error('WISHLIST ERROR: variant_id missing', product)
      return
    }

    const exists = wishlist.value.some(
      (item) => Number(item.variant_id) === Number(variantId)
    )

    if (exists) {
      await api.delete(`/wishlist/remove${params}`, {
        ...config,
        data: {
          variant_id: Number(variantId)
        }
      })
    } else {
      await api.post(
        `/wishlist/add${params}`,
        {
          variant_id: Number(variantId)
        },
        config
      )
    }

    await loadWishlist()
  } catch (err) {
    console.error('WISHLIST TOGGLE ERROR:', err)
    throw err
  }
}

// ----------------------
// REMOVE FROM WISHLIST
// supports variant_id or item object
// ----------------------
export const removeFromWishlist = async (itemOrVariantId) => {
  try {
    const params = getAuthParams()
    const config = getGuestHeaders()

    let variantId = null

    if (typeof itemOrVariantId === 'object' && itemOrVariantId !== null) {
      variantId =
        itemOrVariantId.variant_id ||
        itemOrVariantId.default_variant_id ||
        itemOrVariantId.selected_variant_id ||
        null
    } else {
      variantId = itemOrVariantId
    }

    if (!variantId || Number(variantId) === 0) {
      console.error('REMOVE WISHLIST ERROR: variant_id missing', itemOrVariantId)
      return
    }

    await api.delete(`/wishlist/remove${params}`, {
      ...config,
      data: {
        variant_id: Number(variantId)
      }
    })

    await loadWishlist()
  } catch (err) {
    console.error('REMOVE WISHLIST ERROR:', err)
    throw err
  }
}

// ----------------------
// CHECK HEART ACTIVE
// supports product object or variant_id
// ----------------------
export const isInWishlist = (productOrVariantId) => {
  let variantId = null

  if (typeof productOrVariantId === 'object' && productOrVariantId !== null) {
    variantId =
      productOrVariantId.variant_id ||
      productOrVariantId.default_variant_id ||
      productOrVariantId.selected_variant_id ||
      null
  } else {
    variantId = productOrVariantId
  }

  if (!variantId) return false

  return wishlist.value.some(
    (item) => Number(item.variant_id) === Number(variantId)
  )
}

// ----------------------
// CART COUNT
// ----------------------
export const cartCount = () => {
  return cart.value.reduce(
    (total, item) => total + Number(item.qty || item.quantity || 0),
    0
  )
}

// ----------------------
// WISHLIST COUNT
// ----------------------
export const wishlistCount = () => {
  return wishlist.value.length
}