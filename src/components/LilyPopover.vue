<template>
  <div class="lily-popover" :class="{ 'is-hover': mode === 'hover' }" :style="popoverStyle">
    <header>
      <div>
        <h3>Waterlily based on {{ lily.sourceType }}</h3>
      </div>
      <IconButton v-if="mode === 'click'" label="Close" @click="emit('close')" />
    </header>

    <section class="popover-body">
      <div class="input-preview" aria-label="Input preview">
        <p v-if="lily.sourceType === 'text'" class="input-preview__text">{{ lily.content }}</p>
        <img v-else :src="lily.content" alt="Input image" class="input-preview__image" />
      </div>

      <template v-if="mode === 'click'">
        <h4>Embedding values</h4>
        <div class="number-stream" aria-label="Embedding values">
          <div class="number-stream__content number-stream__content--static">
            <span v-for="(value, index) in fullEmbedding" :key="index">{{ value }}</span>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import IconButton from './IconButton.vue'

type Lily = {
  sourceType: 'text' | 'image'
  content: string
  embedding: number[]
}

const props = defineProps<{
  lily: Lily
  anchor?: { x: number; y: number } | null
  mode?: 'click' | 'hover'
}>()

const mode = computed(() => props.mode ?? 'click')

const emit = defineEmits<{
  (event: 'close'): void
}>()

const fullEmbedding = computed(() => props.lily.embedding.map((value) => value.toFixed(2)))

const popoverStyle = computed(() => {
  if (!props.anchor) return {}

  const offsetX = 18
  const offsetY = -12

  const width = 340
  const height = 260
  const margin = 12

  const rawLeft = props.anchor.x + offsetX
  const rawTop = props.anchor.y + offsetY

  const maxLeft = Math.max(margin, window.innerWidth - width - margin)
  const maxTop = Math.max(margin, window.innerHeight - height - margin)

  const left = Math.min(Math.max(margin, rawLeft), maxLeft)
  const top = Math.min(Math.max(margin, rawTop), maxTop)

  return {
    left: `${left}px`,
    top: `${top}px`,
    right: 'auto',
  }
})
</script>
