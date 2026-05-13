<template>
  <div>

    <!-- PRODUCTS SLOT -->
    <slot :paginatedProducts="paginatedProducts" />

    <!-- PAGINATION UI -->
    <div class="pagination-wrapper">
      <div class="pagination">

<button 
  class="nav-btn"
  @click="prevPage" 
  :disabled="currentPage === 1"
>
   Prev
</button>

        <button
          v-for="page in pages"
          :key="page"
          @click="goToPage(page)"
          :class="{ active: currentPage === page }"
        >
          {{ page }}
        </button>

<button 
  class="nav-btn"
  @click="nextPage" 
  :disabled="currentPage === totalPages"
>
  Next 
</button>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  products: {
    type: Array,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 16
  }
})

const currentPage = ref(1)

const totalPages = computed(() => {
  return Math.ceil(props.products.length / props.itemsPerPage)
})

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * props.itemsPerPage
  const end = start + props.itemsPerPage
  return props.products.slice(start, end)
})

const pages = computed(() => {
  return Array.from({ length: totalPages.value }, (_, i) => i + 1)
})

watch(() => props.products, () => {
  currentPage.value = 1
})

const goToPage = (page) => currentPage.value = page

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}
</script>

<style scoped lang="scss">

.pagination-wrapper {
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 10; /* safety */

  background: white;
  padding: 10px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
  
  
  border-radius: 10px;

}

/* COMMON BUTTON */
.pagination button {
  min-width: 36px;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #ddd;
  background: #fff;
  color: #333;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* HOVER 
.pagination button:hover:not(:disabled) {
  background: #f5f5f5;
}*/

/* ACTIVE PAGE */
.pagination button.active {
  background: teal;
  color: #fff;
  border-color: teal;
  font-weight: 500;
}

/* PREV / NEXT SPECIAL */
.pagination .nav-btn {
  font-weight: 500;
  padding: 0 14px;
}

/* DISABLED */
.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

</style>