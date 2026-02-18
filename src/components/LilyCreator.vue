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
              <div class="big-preview">
                <svg viewBox="-14 -14 148 148">
                  <g class="preview-pad">
                    <path
                      class="pad-outline"
                      :d="previewPad.fillPath"
                      transform="translate(60 60) scale(1.04) translate(-60 -60)"
                      fill-rule="evenodd"
                      :fill="previewPad.edge"
                    />
                    <path
                      class="pad-fill"
                      :d="previewPad.fillPath"
                      fill-rule="evenodd"
                      :fill="previewPad.fill"
                    />
                    <path
                      class="pad-slit"
                      :d="previewPad.slitPath"
                      :stroke="previewPad.edge"
                      fill="none"
                      vector-effect="non-scaling-stroke"
                    />
                  </g>
                  <g class="preview-lily">
                    <path
                      :d="preview.shapePath"
                      :fill="preview.color"
                      :stroke="preview.outline"
                      stroke-width="3"
                    />
                    <circle cx="60" cy="54" r="4.2" fill="rgba(255, 244, 168, 0.95)" />
                    <circle cx="52" cy="66" r="3.6" fill="rgba(255, 244, 168, 0.88)" />
                    <circle cx="68" cy="66" r="3.4" fill="rgba(255, 244, 168, 0.82)" />
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
import { createLilyPadPaths } from '../utils/lilyPad'
import IconButton from './IconButton.vue'

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

const sequenceStart = ref<number | null>(null)

const grow = () => {
  if (phase.value !== 'idle') return
  phase.value = 'embedding'
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

const previewPad = (() => {
  const slitAngle = -0.95
  const slitWidth = 0.82
  const { fillPath, slitPath } = createLilyPadPaths({ r: 60, slitAngle, slitWidth })
  return {
    fill: 'hsl(108 32% 34%)',
    edge: 'hsl(108 34% 22%)',
    fillPath,
    slitPath,
  }
})()
</script>
