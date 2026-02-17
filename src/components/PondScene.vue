<template>
  <section class="pond-scene">
    <CausticsCanvas />
    <div class="pond-ripples">
      <span v-for="ripple in ripples" :key="ripple.id" :style="ripple.style"></span>
    </div>

    <div class="lily-pads">
      <div v-for="pad in pads" :key="pad.id" class="lily-pad" :style="padStyle(pad)">
        <svg viewBox="0 0 120 120" aria-hidden="true">
          <path :d="pad.fillPath" :fill="pad.fill" fill-rule="evenodd" />
          <path
            :d="pad.strokePath"
            fill="none"
            :stroke="pad.edge"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>
    </div>

    <button
      v-for="lily in lilies"
      :key="lily.id"
      class="lily"
      :class="{ active: lily.id === activeId }"
      :style="lilyStyle(lily)"
      @click="emit('select', lily.id)"
    >
      <svg viewBox="0 0 120 120" aria-hidden="true">
        <path
          :d="lily.shapePath"
          :fill="lily.color"
          :stroke="lily.outline"
          stroke-width="2"
        />
      </svg>
    </button>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import CausticsCanvas from './CausticsCanvas.vue'

type Lily = {
  id: string
  color: string
  outline: string
  shapePath: string
  x?: number
  y?: number
}

type Pad = {
  id: string
  x: number
  y: number
  size: number
  rotation: number
  fill: string
  edge: string
  fillPath: string
  strokePath: string
}

const props = defineProps<{
  lilies: Lily[]
  activeId: string | null
}>()

const emit = defineEmits<{
  (event: 'select', id: string): void
}>()

const ambientPads = ref<Pad[]>([])

const ripples = computed(() =>
  Array.from({ length: 6 }).map((_, index) => ({
    id: `ripple-${index}`,
    style: {
      left: `${10 + Math.random() * 80}%`,
      top: `${10 + Math.random() * 80}%`,
      animationDelay: `${Math.random() * 6}s`,
      animationDuration: `${9 + Math.random() * 8}s`,
    },
  }))
)

const pads = computed(() => {
  const lilyPads = props.lilies.flatMap((lily) => createPadsNearLily(lily))
  return [...ambientPads.value, ...lilyPads]
})

const lilyStyle = (lily: Lily) => {
  const size = 90
  const x = lily.x ?? 0
  const y = lily.y ?? 0
  return {
    '--x': `${x}px`,
    '--y': `${y}px`,
    width: `${size}px`,
    height: `${size}px`,
  }
}

const padStyle = (pad: Pad) => ({
  width: `${pad.size}px`,
  height: `${pad.size}px`,
  transform: `translate(calc(-50% + ${pad.x}px), calc(-50% + ${pad.y}px)) rotate(${pad.rotation}deg)`,
})

const createPadsNearLily = (lily: Lily) => {
  const seed = hashString(lily.id)
  const random = mulberry32(seed)
  const count = 3 + Math.floor(random() * 3)
  return Array.from({ length: count }).map((_, index) => {
    const angle = random() * Math.PI * 2
    const distance = 50 + random() * 120
    const x = (lily.x ?? 0) + Math.cos(angle) * distance
    const y = (lily.y ?? 0) + Math.sin(angle) * distance
    return createPad(`${lily.id}-${index}`, x, y, random)
  })
}

const createPad = (id: string, x: number, y: number, random: () => number): Pad => {
  const size = 78 + random() * 88
  const hue = 102 + random() * 10
  const saturation = 36 + random() * 8
  const lightness = 30 + random() * 10
  const fill = `hsl(${hue.toFixed(1)} ${saturation.toFixed(1)}% ${lightness.toFixed(1)}%)`
  const edge = `hsl(${hue.toFixed(1)} ${(saturation + 6).toFixed(1)}% ${Math.max(18, lightness - 10).toFixed(1)}%)`
  const rotation = random() * 360
  const slitAngle = random() * Math.PI * 2
  const slitWidth = 0.45 + random() * 0.35
  const { fillPath, strokePath } = createPadPath(slitAngle, slitWidth)
  return {
    id: `pad-${id}`,
    x,
    y,
    size,
    rotation,
    fill,
    edge,
    fillPath,
    strokePath,
  }
}

const createPadPath = (slitAngle: number, slitWidth: number) => {
  const cx = 60
  const cy = 60
  const r = 56
  const start = slitAngle - slitWidth / 2
  const end = slitAngle + slitWidth / 2
  const startPoint = polarPoint(cx, cy, r + 1, start)
  const endPoint = polarPoint(cx, cy, r + 1, end)
  const largeArc = slitWidth > Math.PI ? 1 : 0

  const circle = `M ${cx + r} ${cy} A ${r} ${r} 0 1 0 ${cx - r} ${cy} A ${r} ${r} 0 1 0 ${cx + r} ${cy} Z`
  const wedge = `M ${cx} ${cy} L ${startPoint.x} ${startPoint.y} A ${r + 1} ${r + 1} 0 ${largeArc} 1 ${endPoint.x} ${endPoint.y} Z`
  const strokePath = `M ${cx} ${cy} L ${startPoint.x} ${startPoint.y} A ${r + 1} ${r + 1} 0 ${largeArc} 1 ${endPoint.x} ${endPoint.y} L ${cx} ${cy}`

  return {
    fillPath: `${circle} ${wedge}`,
    strokePath,
  }
}

const polarPoint = (cx: number, cy: number, r: number, angle: number) => ({
  x: (cx + r * Math.cos(angle)).toFixed(2),
  y: (cy + r * Math.sin(angle)).toFixed(2),
})

const hashString = (value: string) => {
  let hash = 0
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(i)
    hash |= 0
  }
  return hash >>> 0
}

const mulberry32 = (seed: number) => () => {
  let t = (seed += 0x6d2b79f5)
  t = Math.imul(t ^ (t >>> 15), t | 1)
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296
}

onMounted(() => {
  const seed = hashString('ambient-pads')
  const random = mulberry32(seed)
  const padCount = 8
  const margin = 120
  const width = window.innerWidth / 2 - margin
  const height = window.innerHeight / 2 - margin
  ambientPads.value = Array.from({ length: padCount }).map((_, index) => {
    const x = (random() * 2 - 1) * width
    const y = (random() * 2 - 1) * height
    return createPad(`ambient-${index}`, x, y, random)
  })
})
</script>
