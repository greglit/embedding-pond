<template>
  <div class="overlay">
    <div class="modal">
      <header>
        <h2>Grow a waterlilly</h2>
        <button class="icon" @click="emit('close')">Close</button>
      </header>

      <div class="input-toggle">
        <button
          :class="{ active: mode === 'text' }"
          @click="mode = 'text'"
          type="button"
        >
          Text
        </button>
        <button
          :class="{ active: mode === 'image' }"
          @click="mode = 'image'"
          type="button"
        >
          Image
        </button>
      </div>

      <div class="input-area">
        <textarea
          v-if="mode === 'text'"
          v-model="textInput"
          placeholder="Type a thought, a sentence, or a memory..."
          rows="6"
        ></textarea>
        <div v-else class="image-input">
          <input type="file" accept="image/*" @change="handleImage" />
          <div v-if="imagePreview" class="preview">
            <img :src="imagePreview" alt="Preview" />
          </div>
        </div>
      </div>

      <div class="actions">
        <button
          type="button"
          class="primary"
          :disabled="isLoading || !canGrow"
          @click="grow"
        >
          {{ isLoading ? 'Growing...' : 'Grow waterlilly' }}
        </button>
      </div>

      <div v-if="preview" class="preview-card">
        <div class="preview-lily" :style="previewStyle">
          <svg viewBox="0 0 120 120" aria-hidden="true">
            <path
              :d="preview.shapePath"
              :fill="preview.color"
              :stroke="preview.outline"
              stroke-width="2"
            />
          </svg>
        </div>
        <div class="preview-info">
          <p>{{ preview.label }}</p>
          <small>{{ preview.sourceType === 'text' ? 'Text' : 'Image' }}</small>
        </div>
        <p class="preview-note">Planting in 4 seconds...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

type LilyPreview = {
  label: string
  sourceType: 'text' | 'image'
  shapePath: string
  color: string
  outline: string
}

const props = defineProps<{
  isLoading: boolean
  preview: LilyPreview | null
}>()

const emit = defineEmits<{
  (event: 'close'): void
  (event: 'grow', payload: { type: 'text' | 'image'; data: string }): void
}>()

const mode = ref<'text' | 'image'>('text')
const textInput = ref('')
const imageData = ref('')
const imagePreview = ref('')

const canGrow = computed(() => {
  if (mode.value === 'text') return textInput.value.trim().length > 0
  return imageData.value.length > 0
})

const grow = () => {
  if (mode.value === 'text') {
    emit('grow', { type: 'text', data: textInput.value.trim() })
  } else if (imageData.value) {
    emit('grow', { type: 'image', data: imageData.value })
  }
}

const handleImage = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const objectUrl = URL.createObjectURL(file)
  imageData.value = objectUrl
  imagePreview.value = objectUrl
}

const previewStyle = computed(() => {
  if (!props.preview) return {}
  return {
    background: props.preview.color,
    borderColor: props.preview.outline,
  }
})
</script>
