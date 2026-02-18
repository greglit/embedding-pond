<template>
  <main class="pond-app">
    <div class="pond-title" :class="{ compact: lilies.length > 0 }">
      <h1>The Embedding Pond</h1>
      <h2>Grow beautiful waterlilies and learn how AI makes sense of your data.</h2>
    </div>

    <PondScene
      :lilies="lilies"
      :active-id="activeId"
      @select="handleSelect"
      @hover="handleHover"
    />

    <button class="new-lily" @click="openCreator">
      <span class="new-lily__label">{{ lilies.length === 0 ? 'Grow your first Waterlily!' : 'New Waterlily' }}</span>
      <span class="new-lily__emoji" aria-hidden="true">🪷</span>
    </button>

    <button class="info-button" type="button" @click="toggleInfo" :aria-expanded="showInfo">
      <span class="info-button__icon" aria-hidden="true">i</span>
      <span>Info</span>
    </button>

    <LilyCreator
      v-if="showCreator"
      :is-loading="isEmbedding"
      :preview="draftLily"
      :is-first-lily="lilies.length === 0"
      @close="closeCreator"
      @grow="handleGrow"
      @plant="handlePlant"
    />

    <LilyPopover
      v-if="activeLily"
      mode="click"
      :lily="activeLily"
      @close="activeId = null"
    />

    <LilyPopover
      v-if="hoverLily && !activeLily && !showCreator"
      mode="hover"
      :lily="hoverLily"
      :anchor="hoverAnchor"
      @close="hoverId = null"
    />

    <div v-if="showInfo" class="overlay" @click.self="showInfo = false">
      <InfoPopover @close="showInfo = false" />
    </div>

    <div v-if="travelingLily" class="traveling-lily" :style="travelStyle">
      <svg viewBox="0 0 120 120" aria-hidden="true">
        <path
          :d="travelingLily.shapePath"
          :fill="travelingLily.color"
          :stroke="travelingLily.outline"
          stroke-width="3"
        />
        <g aria-hidden="true">
          <circle cx="60" cy="54" r="3.3" fill="rgba(255, 244, 168, 0.95)" />
          <circle cx="53" cy="64" r="2.9" fill="rgba(255, 244, 168, 0.88)" />
          <circle cx="67" cy="65" r="2.8" fill="rgba(255, 244, 168, 0.82)" />
        </g>
      </svg>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import PondScene from './components/PondScene.vue'
import LilyCreator from './components/LilyCreator.vue'
import LilyPopover from './components/LilyPopover.vue'
import InfoPopover from './components/InfoPopover.vue'
import { computeEmbedding } from './utils/embedding'
import { computePcaLayout } from './utils/pca'
import { embeddingToPath } from './utils/shape'

type LilyInput = {
  id: string
  label: string
  sourceType: 'text' | 'image'
  content: string
  embedding: number[]
  embeddingSample: number[]
  shapePath: string
  color: string
  outline: string
  shadowBlur: number
  shadowAlpha: number
  shadowY: number
  x?: number
  y?: number
}

const lilies = ref<LilyInput[]>([])
const activeId = ref<string | null>(null)
const hoverId = ref<string | null>(null)
const hoverAnchor = ref<{ x: number; y: number } | null>(null)
const showCreator = ref(false)
const showInfo = ref(false)
const isEmbedding = ref(false)
const draftLily = ref<LilyInput | null>(null)
const travelingLily = ref<
  | (LilyInput & {
      x: number
      y: number
    })
  | null
>(null)

const activeLily = computed(() => lilies.value.find((lily) => lily.id === activeId.value) ?? null)

const hoverLily = computed(() => lilies.value.find((lily) => lily.id === hoverId.value) ?? null)

const travelStyle = computed(() => {
  if (!travelingLily.value) return {}
  return {
    transform: `translate(-50%, -50%) translate(${travelingLily.value.x}px, ${travelingLily.value.y}px)`,
  }
})

const openCreator = () => {
  draftLily.value = null
  showCreator.value = true
}

const closeCreator = () => {
  showCreator.value = false
  draftLily.value = null
}

const toggleInfo = () => {
  showInfo.value = !showInfo.value
  if (showInfo.value) {
    activeId.value = null
    hoverId.value = null
    hoverAnchor.value = null
    showCreator.value = false
  }
}

const handleSelect = (id: string) => {
  activeId.value = id
  hoverId.value = null
  hoverAnchor.value = null
}

const handleHover = (id: string | null) => {
  if (activeId.value) return
  if (showCreator.value) return
  hoverId.value = id
  if (!id) {
    hoverAnchor.value = null
    return
  }
  const lily = lilies.value.find((item) => item.id === id)
  if (!lily) {
    hoverAnchor.value = null
    return
  }
  hoverAnchor.value = {
    x: window.innerWidth / 2 + (lily.x ?? 0),
    y: window.innerHeight / 2 + (lily.y ?? 0),
  }
}

const handleGrow = async (payload: { type: 'text' | 'image'; data: string }) => {
  isEmbedding.value = true
  try {
    const embedding = await computeEmbedding(payload.type, payload.data)
    const shade = embeddingToBlush(embedding)
    const outline = deepenColor(shade, 0.22)
    const shapePath = embeddingToPath(embedding)

     const maxAbs = embedding.reduce((acc, v) => Math.max(acc, Math.abs(v)), 0)
     const shadowBlur = 10 + maxAbs * 18
     const shadowAlpha = 0.18 + maxAbs * 0.16
     const shadowY = 7 + maxAbs * 4

     const sampleCount = 14
     const stride = Math.max(1, Math.floor(embedding.length / sampleCount))
     const embeddingSample = embedding.filter((_, idx) => idx % stride === 0).slice(0, sampleCount)

      draftLily.value = {
        id: crypto.randomUUID(),
        label: payload.type === 'text' ? payload.data.slice(0, 42) : 'Image input',
        sourceType: payload.type,
        content: payload.data,
        embedding,
        embeddingSample,
        shapePath,
        color: shade,
        outline,
        shadowBlur,
        shadowAlpha,
        shadowY,
      }
  } finally {
    isEmbedding.value = false
  }
}

const handlePlant = () => {
  if (!draftLily.value) return

  hoverId.value = null
  hoverAnchor.value = null

  // Close the creator immediately; planting continues via the travel animation.
  showCreator.value = false

  const nextLilies = [...lilies.value, draftLily.value]
  const layout = computePcaLayout(nextLilies.map((lily) => lily.embedding))
  const target = layout[layout.length - 1] ?? { x: 0, y: 0 }

  lilies.value = lilies.value.map((lily, index) => ({
    ...lily,
    x: layout[index]?.x ?? 0,
    y: layout[index]?.y ?? 0,
  }))

  travelingLily.value = {
    ...draftLily.value,
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  }

  requestAnimationFrame(() => {
    if (!travelingLily.value) return
    travelingLily.value = {
      ...travelingLily.value,
      x: window.innerWidth / 2 + target.x,
      y: window.innerHeight / 2 + target.y,
    }
  })

  window.setTimeout(() => {
    lilies.value = [...lilies.value, { ...draftLily.value!, x: target.x, y: target.y }]
    activeId.value = draftLily.value!.id
    draftLily.value = null
    travelingLily.value = null
  }, 1200)
}

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value))

const fract = (value: number) => value - Math.floor(value)

const embeddingToBlush = (embedding: number[]) => {
  // Deterministic but sensitive mapping.
  // Small embedding changes should noticeably change the color, while staying in a pink-to-white palette.
  const maxSamples = 96
  const stride = Math.max(1, Math.floor(embedding.length / maxSamples))

  // Two chaotic accumulators (in [0,1)).
  let s1 = 0.318309886
  let s2 = 0.271828182

  let count = 0
  for (let i = 0; i < embedding.length; i += stride) {
    const v = embedding[i] ?? 0

    // A tiny change in v changes the phase; fract keeps values bounded.
    const phase = v * 37.719 + (i + 1) * 11.131 + s1 * 97.17
    const n1 = Math.sin(phase) * 43758.5453
    const n2 = Math.sin(phase + s2 * 13.37) * 96321.9123

    s1 = fract(s1 + fract(n1) * 0.73 + fract(n2) * 0.19)
    s2 = fract(s2 + fract(n2) * 0.67 + fract(n1) * 0.23)

    count += 1
    if (count >= maxSamples) break
  }

  // Mix into three independent-ish controls.
  const u = fract(Math.sin((s1 + 0.17) * 91.7 + (s2 + 0.31) * 37.1) * 9999.9)
  const v = fract(Math.sin((s1 + 0.41) * 57.3 + (s2 + 0.23) * 81.9) * 9999.9)
  const w = fract(Math.sin((s1 + 0.07) * 13.9 + (s2 + 0.59) * 103.3) * 9999.9)

  // Original range we started with: dark-pink to near-white.
  // Deterministic (embedding-based) but not random.
  const hue = 342 + u * 18
  const saturation = 36 + v * 24
  const lightness = 85 + w * 8

  return `hsl(${hue.toFixed(1)} ${saturation.toFixed(1)}% ${lightness.toFixed(1)}%)`
}

const deepenColor = (hslColor: string, delta: number) => {
  const match = hslColor.match(/hsl\(([-\d.]+) ([\d.]+)% ([\d.]+)%\)/)
  if (!match) return hslColor
  const hue = Number(match[1])
  const saturation = Number(match[2])
  const lightness = Math.max(0, Number(match[3]) - delta * 100)
  return `hsl(${hue.toFixed(1)} ${saturation.toFixed(1)}% ${lightness.toFixed(1)}%)`
}

</script>
