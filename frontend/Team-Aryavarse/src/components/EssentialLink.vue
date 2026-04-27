<template>
  <q-item
    clickable
    :tag="link ? 'a' : 'div'"
    :target="external ? '_blank' : undefined"
    :href="external ? link : undefined"
    @click="handleClick"
  >
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
      <q-item-label v-if="caption" caption>
        {{ caption }}
      </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  caption: {
    type: String,
    default: ''
  },
  link: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  external: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

function handleClick () {
  if (!props.link) return

  if (!props.external) {
    router.push(props.link)
  }
}
</script>
