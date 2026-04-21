<template>
  <div ref="popoverRef" class="lily-popover" :class="{ 'is-hover': mode === 'hover' }" :style="popoverStyle">
    <header>
      <div>
        <h3>{{ t('popover.title', { sourceType: lily.sourceType === 'text' ? t('creator.text') : t('creator.image') }) }}</h3>
      </div>
      <IconButton v-if="mode === 'click'" :label="t('common.close')" @click="emit('close')" />
    </header>

    <section class="popover-body">
      <div class="input-preview" :aria-label="t('popover.inputPreviewAria')">
        <p v-if="lily.sourceType === 'text'" class="input-preview__text">{{ lily.content }}</p>
        <img v-else :src="lily.content" :alt="t('popover.inputImageAlt')" class="input-preview__image" />
      </div>

      <template v-if="mode === 'click'">
        <h4>{{ t('popover.embeddingValues') }}</h4>
        <div class="number-stream" :aria-label="t('popover.embeddingValues')">
          <div class="number-stream__content number-stream__content--static">
            <span v-for="(value, index) in fullEmbedding" :key="index">{{ value }}</span>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import IconButton from './IconButton.vue'

const { t } = useI18n()

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

const popoverRef = ref<HTMLElement | null>(null)

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Element
  const isOnLily = target.closest('.lily')
  if (!isOnLily && popoverRef.value && !popoverRef.value.contains(target)) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

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
