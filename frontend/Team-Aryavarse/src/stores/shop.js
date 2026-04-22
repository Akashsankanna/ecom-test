import { ref, watch } from 'vue'
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
  const backendName = String(item.product_name || item.title || '').trim().toLowerCase()
  const backendVariant = String(item.variant_name || '').trim().toLowerCase()

  // 1. exact color variant_id match inside colors[]
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

  // 2. exact top-level variant_id match
  const byVariantId = allFrontendProducts.find(
    (p) => Number(p.variant_id) === Number(item.variant_id)
  )
  if (byVariantId?.image) return byVariantId.image

  // 3. exact title match
  const byExactName = allFrontendProducts.find(
    (p) => String(p.title || '').trim().toLowerCase() === backendName
  )
  if (byExactName?.image) return byExactName.image

  // 4. loose title match
  const byLooseName = allFrontendProducts.find((p) => {
    const title = String(p.title || '').trim().toLowerCase()
    return title.includes(backendName) || backendName.includes(title)
  })
  if (byLooseName?.image) return byLooseName.image

  // 5. title + color/variant name match
  const byColorName = allFrontendProducts.find((p) => {
    const title = String(p.title || '').trim().toLowerCase()
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
// CART (BACKEND)
// ----------------------
export const cart = ref([])

// ----------------------
// WISHLIST (LOCAL SAME)
// ----------------------
export const wishlist = ref(JSON.parse(localStorage.getItem('wishlist') || '[]'))

watch(
  wishlist,
  (val) => {
    localStorage.setItem('wishlist', JSON.stringify(val))
  },
  { deep: true }
)

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

        product_name: item.product_name || '',
        title: item.product_name || '',
        variant_name: item.variant_name || '',

        price: Number(item.price || 0),
        customization_total: Number(item.customization_total || 0),
        line_total: Number(item.line_total || 0),

        qty: Number(item.quantity || 1),
        quantity: Number(item.quantity || 1),

        stock: Number(item.stock || 0),
        size: item.size || '',
        color: item.color || '',

        image_url: finalImage,
        image: finalImage,
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
// ADD TO CART (BACKEND ONLY)
// supports both:
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

      // first try direct product variant_id
      variantId = product.variant_id

      // then try color-level variant_id
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

    if (!variantId) {
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
// REMOVE FROM CART (BACKEND)
// supports:
// 1) removeFromCart(cartItemId)
// 2) removeFromCart(productObject with id/cart_item_id)
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
    console.error('REMOVE ERROR:', err)
    throw err
  }
}

// ----------------------
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
// WISHLIST (LOCAL SAME)
// ----------------------
export const toggleWishlist = (product) => {
  const exists = wishlist.value.find(item => item.id === product.id)

  if (exists) {
    wishlist.value = wishlist.value.filter(item => item.id !== product.id)
  } else {
    wishlist.value.push(product)
  }
}

export const removeFromWishlist = (id) => {
  wishlist.value = wishlist.value.filter(item => item.id !== id)
}

export const isInWishlist = (id) => {
  return wishlist.value.some(item => item.id === id)
}

// ----------------------
// CART COUNT
// ----------------------
export const cartCount = () => {
  return cart.value.reduce((total, item) => total + Number(item.qty || item.quantity || 0), 0)
}
