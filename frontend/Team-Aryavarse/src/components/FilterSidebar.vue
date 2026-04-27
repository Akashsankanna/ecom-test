<template>
  <div class="filter-wrapper">
    <!-- DESKTOP -->
    <aside class="filters-sidebar desktop-filters">
      <h2>Filters</h2>

      <div
        v-for="group in filterGroups"
        :key="group.key"
        class="filter-group"
      >
        <p>{{ group.label }}</p>

        <label
          v-for="item in group.options"
          :key="item"
          class="filter-label"
        >
          <input
            type="checkbox"
            :value="item"
            :checked="group.selected.includes(item)"
            @change="toggle(group.key, item)"
          />
          {{ item }}
        </label>
      </div>
    </aside>

    <!-- MOBILE BAR -->
    <div class="mobile-filter-bar">
      <button class="mobile-action-btn" @click="drawerOpen = !drawerOpen">
        <span>⚙</span>
        Filter
        <span v-if="activeCount > 0" class="active-badge">
          {{ activeCount }}
        </span>
      </button>

      <div class="divider"></div>

      <div class="mobile-sort-slot">
        <slot name="sort-btn" />
      </div>
    </div>

    <!-- MOBILE OVERLAY -->
    <div
      class="filter-overlay"
      :class="{ open: drawerOpen }"
      @click="drawerOpen = false"
    />

    <!-- MOBILE DRAWER -->
    <div class="filter-drawer" :class="{ open: drawerOpen }">
      <div class="drawer-header">
        <span class="drawer-title">Filters</span>
        <button class="drawer-close" @click="drawerOpen = false">✕</button>
      </div>

      <div class="drawer-body">
        <div
          v-for="group in filterGroups"
          :key="group.key"
          class="filter-group"
        >
          <p>{{ group.label }}</p>

          <label
            v-for="item in group.options"
            :key="item"
            class="filter-label"
          >
            <input
              type="checkbox"
              :value="item"
              :checked="group.selected.includes(item)"
              @change="toggle(group.key, item)"
            />
            {{ item }}
          </label>
        </div>
      </div>

      <div class="drawer-footer">
        <button class="clear-btn" @click="clearAll">Clear All</button>
        <button class="apply-btn" @click="drawerOpen = false">
          Apply Filters
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  filterCategories: { type: Array, default: () => [] },
  fabrics: { type: Array, default: () => [] },
  sleeves: { type: Array, default: () => [] },
  colors: { type: Array, default: () => [] },

  selectedCategories: { type: Array, default: () => [] },
  selectedFabrics: { type: Array, default: () => [] },
  selectedSleeves: { type: Array, default: () => [] },
  selectedColors: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'update:selectedCategories',
  'update:selectedFabrics',
  'update:selectedSleeves',
  'update:selectedColors',
])

const drawerOpen = ref(false)

const filterGroups = computed(() => [
  {
    key: 'categories',
    label: 'Category',
    options: props.filterCategories,
    selected: props.selectedCategories,
    event: 'update:selectedCategories',
  },
  {
    key: 'fabrics',
    label: 'Fabric',
    options: props.fabrics,
    selected: props.selectedFabrics,
    event: 'update:selectedFabrics',
  },
  {
    key: 'sleeves',
    label: 'Style',
    options: props.sleeves,
    selected: props.selectedSleeves,
    event: 'update:selectedSleeves',
  },
  {
    key: 'colors',
    label: 'Color',
    options: props.colors,
    selected: props.selectedColors,
    event: 'update:selectedColors',
  },
])

const activeCount = computed(() =>
  filterGroups.value.reduce((total, group) => {
    return total + group.selected.length
  }, 0)
)

function toggle(type, value) {
  const group = filterGroups.value.find(item => item.key === type)
  if (!group) return

  const updated = group.selected.includes(value)
    ? group.selected.filter(item => item !== value)
    : [...group.selected, value]

  emit(group.event, updated)
}

function clearAll() {
  filterGroups.value.forEach(group => {
    emit(group.event, [])
  })
}
</script>

<style scoped lang="scss">
@import 'src/css/filters.scss';
</style>
