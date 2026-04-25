import { ref, watch } from 'vue'

// cart data
export const cart = ref(JSON.parse(localStorage.getItem('cart') || '[]'))

// wishlist data
export const wishlist = ref(JSON.parse(localStorage.getItem('wishlist') || '[]'))

// save cart
watch(cart, (val) => {
  localStorage.setItem('cart', JSON.stringify(val))
}, { deep: true })

// save wishlist
watch(wishlist, (val) => {
  localStorage.setItem('wishlist', JSON.stringify(val))
}, { deep: true })

// add to cart
// check same id + same size + same color product already there (aahe ka )
export const addToCart = (product) => {
  const existing = cart.value.find(item =>
    item.id === product.id &&
    item.size === product.size &&
    item.color === product.color
  )

  if (existing) {
    existing.qty += product.qty || 1
  } else {
    cart.value.push({
      ...product,
      qty: product.qty || 1   
    })
  }
}

// Remove specific product from cart
export const removeFromCart = (product) => {
  cart.value = cart.value.filter(item =>
    !(
      item.id === product.id &&
      item.size === product.size &&
      item.color === product.color
    )
  )
}

// quantity update
export const updateQty = (product, type) => {
  // Find exact cart item
  const item = cart.value.find(i =>
    i.id === product.id &&
    i.size === product.size &&
    i.color === product.color
  )

  if (!item) return

   // Increase quantity
  if (type === 'inc') item.qty++

  // Decrease quantity
  if (type === 'dec') {
    if (item.qty > 1) {
      item.qty--
    } else {

      // Remove if qty becomes 0
      removeFromCart(product)
    }
  }
}

// Add/Remove wishlist
export const toggleWishlist = (product) => {
  const exists = wishlist.value.find(item => item.id === product.id)

  if (exists) {
    wishlist.value = wishlist.value.filter(item => item.id !== product.id)
    
  } else {
    wishlist.value.push(product)
    
  }
}

// remove wishlist item
export const removeFromWishlist = (id) => {
  wishlist.value = wishlist.value.filter(item => item.id !== id)
}

// check if in wishlist
export const isInWishlist = (id) => {
  return wishlist.value.some(item => item.id === id)
}

  // total selected products only
  export const cartCount = () => {
    return cart.value.length
}
