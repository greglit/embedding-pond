<template>
  <div class="overlay">
    <div class="modal">
      <header>
        <div class="header-content">
          <Transition name="fade" mode="out-in">
            <div v-if="phase === 'idle'" key="idle">
              <h2>Grow a waterlily from your data</h2>
              <p class="subhead">
                We'll extract the <strong>"condensed meaning"</strong> from your data in form of a long list of numbers. This is called an
                <strong>embedding</strong>. From those numbers, we'll grow a beautiful, unique waterlily.
              </p>
            </div>

            <div v-else-if="phase === 'ready'" key="ready">
              <h2>Look! A beautiful waterlily!</h2>
              <p class="subhead">
                This waterlily is shaped by the <strong>embedding</strong> values and carries the <strong>"essence"</strong> of your data.
              </p>
            </div>

            <div v-else key="embedding">
              <h2>Generating embeddings...</h2>
              <p class="subhead">These numbers capture the <strong>"condensed meaning"</strong> of your input.</p>
            </div>
          </Transition>
        </div>
        <IconButton label="Close" @click="emit('close')" />
      </header>

      <div class="modal-body">
        <template v-if="phase === 'idle'">
          <p class="helper">To begin, choose <strong>text</strong> or <strong>image</strong>.</p>
          <div class="input-toggle">
            <button :class="{ active: mode === 'text' }" @click="mode = 'text'" type="button">Text</button>
            <button :class="{ active: mode === 'image' }" @click="mode = 'image'" type="button">Image</button>
          </div>
          <div class="input-area">
            <textarea
              v-if="mode === 'text'"
              v-model="textInput"
              placeholder="Type a word, sentence, thought or memory..."
              rows="6"
            ></textarea>
            <div v-else class="image-input">
              <input type="file" accept="image/*" @change="handleImage" />
              <div v-if="imagePreview" class="preview">
                <img :src="imagePreview" alt="Preview" />
              </div>
            </div>
          </div>
        </template>

        <div v-else class="embedding-status" aria-live="polite">
          <Transition name="fade" mode="out-in">
            <div v-if="showStatus && phase === 'embedding'" key="embedding" class="embed-panel" aria-hidden="true">
              <div class="number-stream" :style="{ '--stream-duration': `${streamDurationSeconds}s` }">
                <div class="number-stream__content" :key="streamRunId">
                  <span v-for="(value, index) in streamValues" :key="index">{{ value }}</span>
                </div>
              </div>
            </div>

            <div v-else-if="preview && phase === 'ready'" key="lily" class="lily-panel" aria-hidden="true">
              <div class="big-preview" v-if="preview">
                <svg viewBox="0 0 120 120" class="preview-pad">
                  <path
                    class="pad-outline"
                    :d="padPaths.fillPath"
                    transform="translate(60 60) scale(1.04) translate(-60 -60)"
                    fill-rule="evenodd"
                    :fill="padColors.edge"
                  />
                  <path
                    class="pad-fill"
                    :d="padPaths.fillPath"
                    fill-rule="evenodd"
                    :fill="padColors.fill"
                  />
                  <path
                    class="pad-slit"
                    :d="padPaths.slitPath"
                    :stroke="padColors.edge"
                    fill="none"
                    vector-effect="non-scaling-stroke"
                  />
                </svg>
                <svg viewBox="0 0 120 120" class="preview-lily">
                  <path :d="preview.shapePath" :fill="preview.color" :stroke="preview.outline" stroke-width="3" />
                  <g class="lily-stamen">
                    <circle cx="60" cy="54" r="3.3" fill="rgba(255, 244, 168, 0.95)" />
                    <circle cx="53" cy="64" r="2.9" fill="rgba(255, 244, 168, 0.88)" />
                    <circle cx="67" cy="65" r="2.8" fill="rgba(255, 244, 168, 0.82)" />
                  </g>
                </svg>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <div class="actions">
        <button
          type="button"
          class="primary"
          :disabled="(phase === 'idle' && (props.isLoading || !canGrow)) || phase === 'embedding'"
          @click="phase === 'ready' ? emit('plant') : grow()"
        >
          {{ primaryButtonLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import IconButton from './IconButton.vue'
import { createLilyPadPaths } from '../utils/lilyPad'

type LilyPreview = {
  label: string
  sourceType: 'text' | 'image'
  shapePath: string
  color: string
  outline: string
  embeddingSample?: number[]
}

const props = defineProps<{
  isLoading: boolean
  preview: LilyPreview | null
  isFirstLily?: boolean
}>()

const emit = defineEmits<{
  (event: 'close'): void
  (event: 'grow', payload: { type: 'text' | 'image'; data: string }): void
  (event: 'plant'): void
  (event: 'phase', phase: Phase): void
}>()

const mode = ref<'text' | 'image'>('text')
const textInput = ref('')
const imageData = ref('')
const imagePreview = ref('')

type Phase = 'idle' | 'embedding' | 'ready'
const phase = ref<Phase>('idle')

const showStatus = ref(false)

const isFirstLily = computed(() => props.isFirstLily ?? false)

const totalSequenceMs = computed(() => (isFirstLily.value ? 8000 : 2600))
const streamDurationSeconds = computed(() => (isFirstLily.value ? 6.2 : 1.4))
const showStatusDelayMs = computed(() => (isFirstLily.value ? 260 : 120))

const streamRunId = ref(0)
const streamValues = ref<string[]>([])

const canGrow = computed(() => {
  if (mode.value === 'text') return textInput.value.trim().length > 0
  return imageData.value.length > 0
})

const padPaths = computed(() => {
  if (!props.preview) return { fillPath: '', slitPath: '' }
  // Deterministic based on preview to match the lily
  const seed = props.preview.label.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const random = mulberry32(seed)
  const slitAngle = random() * Math.PI * 2
  const slitWidth = 0.45 + random() * 0.35
  return createLilyPadPaths({ slitAngle, slitWidth })
})

const padColors = computed(() => {
  if (!props.preview) return { fill: '#2d5a3d', edge: '#1a3d28' }
  const seed = props.preview.label.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const random = mulberry32(seed)
  const hue = 102 + random() * 10
  const saturation = 36 + random() * 8
  const lightness = 30 + random() * 10
  const fill = `hsl(${hue.toFixed(1)} ${saturation.toFixed(1)}% ${lightness.toFixed(1)}%)`
  const edge = `hsl(${hue.toFixed(1)} ${(saturation + 6).toFixed(1)}% ${Math.max(18, lightness - 10).toFixed(1)}%)`
  return { fill, edge }
})

function mulberry32(seed: number) {
  return function () {
    let t = (seed += 0x6d2b79f5)
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const sequenceStart = ref<number | null>(null)

const grow = () => {
  if (phase.value !== 'idle') return
  phase.value = 'embedding'
  emit('phase', phase.value)
  sequenceStart.value = Date.now()
  showStatus.value = false
  streamValues.value = buildStreamValues()
  streamRunId.value += 1
  window.setTimeout(() => {
    showStatus.value = true
  }, showStatusDelayMs.value)
  if (mode.value === 'text') {
    emit('grow', { type: 'text', data: textInput.value.trim() })
  } else if (imageData.value) {
    emit('grow', { type: 'image', data: imageData.value })
  }
}

watch(
  () => phase.value,
  (next) => {
    emit('phase', next)
  },
  { immediate: true }
)

const handleImage = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const objectUrl = URL.createObjectURL(file)
  imageData.value = objectUrl
  imagePreview.value = objectUrl
}

const primaryButtonLabel = computed(() => {
  if (phase.value === 'ready') return 'Plant it! 🪷'
  if (props.isLoading || phase.value !== 'idle') return 'Growing... 🪷'
  return 'Grow it! 🪷'
})

let readyTimer: number | null = null

const buildStreamValues = (sample?: number[]) => {
  const base = (sample?.length ? sample : [-0.42, 1.08, -0.16, 0.73, 0.05, -1.21, 0.92, -0.64]).map((v) => v.toFixed(2))
  const values: string[] = []
  for (let i = 0; i < 760; i += 1) {
    values.push(base[i % base.length])
  }
  return values
}

watch(
  () => props.isLoading,
  (loading) => {
    if (phase.value === 'idle') return
    if (loading) return

    if (!props.preview) {
      phase.value = 'idle'
      return
    }

    // Embedding computed; keep the sequence ~8s from click.
    if (phase.value === 'embedding') {
      streamValues.value = buildStreamValues(props.preview.embeddingSample)
      streamRunId.value += 1

      const startedAt = sequenceStart.value ?? Date.now()
      const remaining = Math.max(0, startedAt + totalSequenceMs.value - Date.now())
      readyTimer = window.setTimeout(() => {
        phase.value = 'ready'
      }, remaining)
    }
  }
)

watch(
  () => props.preview,
  (next) => {
    if (phase.value === 'idle') return
    if (!next) {
      phase.value = 'idle'
      showStatus.value = false
      streamValues.value = []
    }
  }
)

watch(
  () => phase.value,
  (next) => {
    if (next === 'idle') {
      if (readyTimer) window.clearTimeout(readyTimer)
      readyTimer = null
      showStatus.value = false
      sequenceStart.value = null
    }
  }
)

</script>
