<template>
  <main class="pond-app">
    <PondScene
      :lilies="lilies"
      :active-id="activeId"
      @select="handleSelect"
    />

    <button class="new-lily" @click="openCreator">
      New Waterlilly
    </button>

    <LilyCreator
      v-if="showCreator"
      :is-loading="isEmbedding"
      :preview="draftLily"
      @close="closeCreator"
      @grow="handleGrow"
    />

    <LilyPopover
      v-if="activeLily"
      :lily="activeLily"
      @close="activeId = null"
    />

    <div v-if="travelingLily" class="traveling-lily" :style="travelStyle">
      <svg viewBox="0 0 120 120" aria-hidden="true">
        <path
          :d="travelingLily.shapePath"
          :fill="travelingLily.color"
          :stroke="travelingLily.outline"
          stroke-width="2"
        />
      </svg>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import PondScene from './components/PondScene.vue'
import LilyCreator from './components/LilyCreator.vue'
import LilyPopover from './components/LilyPopover.vue'
import { computeEmbedding } from './utils/embedding'
import { computePcaLayout } from './utils/pca'
import { embeddingToPath } from './utils/shape'

type LilyInput = {
  id: string
  label: string
  sourceType: 'text' | 'image'
  content: string
  embedding: number[]
  shapePath: string
  color: string
  outline: string
  x?: number
  y?: number
}

const lilies = ref<LilyInput[]>([])
const activeId = ref<string | null>(null)
const showCreator = ref(false)
const isEmbedding = ref(false)
const draftLily = ref<LilyInput | null>(null)
const travelingLily = ref<
  | (LilyInput & {
      x: number
      y: number
    })
  | null
>(null)
let autoPlantTimer: number | null = null

const activeLily = computed(() =>
  lilies.value.find((lily) => lily.id === activeId.value) ?? null
)

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
  if (autoPlantTimer) {
    window.clearTimeout(autoPlantTimer)
    autoPlantTimer = null
  }
}

const handleSelect = (id: string) => {
  activeId.value = id
}

const handleGrow = async (payload: { type: 'text' | 'image'; data: string }) => {
  isEmbedding.value = true
  try {
    const embedding = await computeEmbedding(payload.type, payload.data)
    const shade = randomBlush()
    const outline = deepenColor(shade, 0.22)
    const shapePath = embeddingToPath(embedding)
    draftLily.value = {
      id: crypto.randomUUID(),
      label: payload.type === 'text' ? payload.data.slice(0, 42) : 'Image input',
      sourceType: payload.type,
      content: payload.data,
      embedding,
      shapePath,
      color: shade,
      outline,
    }
    if (autoPlantTimer) {
      window.clearTimeout(autoPlantTimer)
    }
    autoPlantTimer = window.setTimeout(() => {
      handlePlant()
    }, 4000)
  } finally {
    isEmbedding.value = false
  }
}

const handlePlant = () => {
  if (!draftLily.value) return
  if (autoPlantTimer) {
    window.clearTimeout(autoPlantTimer)
    autoPlantTimer = null
  }

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
    showCreator.value = false
    travelingLily.value = null
  }, 1200)
}

const randomBlush = () => {
  const hue = 342 + Math.random() * 18
  const saturation = 36 + Math.random() * 24
  const lightness = 85 + Math.random() * 8
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
