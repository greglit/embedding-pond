<template>
  <section class="pond-scene" @pointerdown="handlePointerDown">
    <div class="pond-ripples" aria-hidden="true">
      <span v-for="ripple in ripples" :key="ripple.id" class="ripple" :style="rippleStyle(ripple)">
        <span class="ring ring-1"></span>
        <span class="ring ring-2"></span>
        <span class="ring ring-3"></span>
      </span>
    </div>

    <div class="lily-pads">
      <div v-for="pad in pads" :key="pad.id" class="lily-pad" :style="padStyle(pad)">
        <div class="lily-pad-drift">
          <svg viewBox="0 0 120 120" aria-hidden="true">
            <path
              class="pad-outline"
              :d="pad.fillPath"
              transform="translate(60 60) scale(1.04) translate(-60 -60)"
              fill-rule="evenodd"
              :fill="pad.edge"
            />
            <path
              class="pad-fill"
              :d="pad.fillPath"
              fill-rule="evenodd"
              :fill="pad.fill"
            />
            <path
              class="pad-slit"
              :d="pad.slitPath"
              :stroke="pad.edge"
              fill="none"
              vector-effect="non-scaling-stroke"
            />
          </svg>
        </div>
      </div>
    </div>

    <button
      v-for="lily in lilies"
      :key="lily.id"
      class="lily"
      :class="{ active: lily.id === activeId }"
      :style="lilyStyle(lily)"
      @mouseenter="emit('hover', lily.id)"
      @mouseleave="emit('hover', null)"
      @focus="emit('hover', lily.id)"
      @blur="emit('hover', null)"
      @click="emit('select', lily.id)"
    >
      <div class="lily-drift" aria-hidden="true">
        <div class="lily-scale">
          <svg viewBox="0 0 120 120">
            <path
              :d="lily.shapePath"
              :fill="lily.color"
              :stroke="lily.outline"
              stroke-width="3"
            />
            <g class="lily-stamen">
              <circle cx="60" cy="54" r="3.3" fill="rgba(255, 244, 168, 0.95)" />
              <circle cx="53" cy="64" r="2.9" fill="rgba(255, 244, 168, 0.88)" />
              <circle cx="67" cy="65" r="2.8" fill="rgba(255, 244, 168, 0.82)" />
            </g>
          </svg>
        </div>
      </div>
    </button>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { createLilyPadPaths } from '../utils/lilyPad'

type Lily = {
  id: string
  color: string
  outline: string
  shapePath: string
  shadowBlur?: number
  shadowAlpha?: number
  shadowY?: number
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
  slitPath: string
  driftX: number
  driftY: number
  driftRot: number
  driftDuration: number
  driftDelay: number
}

const props = defineProps<{
  lilies: Lily[]
  activeId: string | null
}>()

const emit = defineEmits<{
  (event: 'select', id: string): void
  (event: 'hover', id: string | null): void
}>()

const ambientPads = ref<Pad[]>([])

type Ripple = {
  id: string
  left: number
  top: number
  size: number
  duration: number
  delay: number
}

const ripples = ref<Ripple[]>([])

const rippleStyle = (ripple: Ripple) => ({
  left: `${ripple.left}px`,
  top: `${ripple.top}px`,
  '--ripple-size': `${ripple.size}px`,
  '--ripple-duration': `${ripple.duration}s`,
  '--ripple-delay': `${ripple.delay}s`,
})

const spawnRipple = (left: number, top: number, opts?: Partial<Pick<Ripple, 'size' | 'duration' | 'delay'>>) => {
  const id = crypto.randomUUID()
  const ripple: Ripple = {
    id,
    left,
    top,
    size: opts?.size ?? 260,
    duration: opts?.duration ?? 3.6,
    delay: opts?.delay ?? 0,
  }
  ripples.value = [...ripples.value, ripple]
  window.setTimeout(() => {
    ripples.value = ripples.value.filter((item) => item.id !== id)
  }, (ripple.delay + ripple.duration + 0.9) * 1000)
}

const handlePointerDown = (event: PointerEvent) => {
  const target = event.target as HTMLElement | null
  if (target?.closest('.lily')) return
  spawnRipple(event.clientX, event.clientY, {
    size: 320 + Math.random() * 110,
    duration: 4.8 + Math.random() * 2.2,
  })
}

const pads = computed(() => {
  const lilyPads = props.lilies.flatMap((lily) => createPadsNearLily(lily))
  return [...ambientPads.value, ...lilyPads]
})

const lilyStyle = (lily: Lily) => {
  const size = 104
  const x = lily.x ?? 0
  const y = lily.y ?? 0
  const seed = hashString(`lily-drift-${lily.id}`)
  const random = mulberry32(seed)
  const driftX = (random() * 2 - 1) * 8.5
  const driftY = (random() * 2 - 1) * 6.8
  const driftRot = (random() * 2 - 1) * 2.2
  const driftDuration = 10 + random() * 12
  const driftDelay = -random() * driftDuration
  const shadowBlur = lily.shadowBlur ?? 18
  const shadowAlpha = lily.shadowAlpha ?? 0.26
  const shadowY = lily.shadowY ?? 10
  const shadowBlurHover = shadowBlur + 10
  const shadowAlphaHover = Math.min(0.36, shadowAlpha + 0.06)
  const shadowYHover = shadowY + 4
  return {
    '--x': `${x}px`,
    '--y': `${y}px`,
    '--lily-drift-x': `${driftX.toFixed(2)}px`,
    '--lily-drift-y': `${driftY.toFixed(2)}px`,
    '--lily-drift-rot': `${driftRot.toFixed(2)}deg`,
    '--lily-drift-duration': `${driftDuration.toFixed(2)}s`,
    '--lily-drift-delay': `${driftDelay.toFixed(2)}s`,
    '--shadow-blur': `${shadowBlur}px`,
    '--shadow-alpha': `${shadowAlpha}`,
    '--shadow-y': `${shadowY}px`,
    '--shadow-blur-hover': `${shadowBlurHover}px`,
    '--shadow-alpha-hover': `${shadowAlphaHover}`,
    '--shadow-y-hover': `${shadowYHover}px`,
    width: `${size}px`,
    height: `${size}px`,
  }
}

const padStyle = (pad: Pad) => ({
  width: `${pad.size}px`,
  height: `${pad.size}px`,
  transform: `translate(calc(-50% + ${pad.x}px), calc(-50% + ${pad.y}px)) rotate(${pad.rotation}deg)`,
  '--drift-x': `${pad.driftX.toFixed(2)}px`,
  '--drift-y': `${pad.driftY.toFixed(2)}px`,
  '--drift-rot': `${pad.driftRot.toFixed(2)}deg`,
  '--drift-duration': `${pad.driftDuration.toFixed(2)}s`,
  '--drift-delay': `${pad.driftDelay.toFixed(2)}s`,
})

const createPadsNearLily = (lily: Lily) => {
  const seed = hashString(lily.id)
  const random = mulberry32(seed)
  const count = 2 + Math.floor(random() * 2)
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
  const driftX = (random() * 2 - 1) * 14.0
  const driftY = (random() * 2 - 1) * 11.0
  const driftRot = (random() * 2 - 1) * 5.4
  const driftDuration = 9 + random() * 14
  const driftDelay = -random() * driftDuration
  const slitAngle = random() * Math.PI * 2
  const slitWidth = 0.45 + random() * 0.35
  const { fillPath, slitPath } = createPadPaths(slitAngle, slitWidth)
  return {
    id: `pad-${id}`,
    x,
    y,
    size,
    rotation,
    fill,
    edge,
    fillPath,
    slitPath,
    driftX,
    driftY,
    driftRot,
    driftDuration,
    driftDelay,
  }
}

const createPadPaths = (slitAngle: number, slitWidth: number) => createLilyPadPaths({ slitAngle, slitWidth })

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

onMounted(() => {
  // A single subtle ambient ripple so the pond isn't perfectly still.
  // Spawn it from the "New Waterlily" button.
  window.setTimeout(() => {
    const button = document.querySelector('.new-lily') as HTMLElement | null
    if (!button) {
      spawnRipple(window.innerWidth * 0.5, window.innerHeight * 0.5, { size: 520, duration: 5.8 })
      return
    }
    const rect = button.getBoundingClientRect()
    spawnRipple(rect.left + rect.width / 2, rect.top + rect.height / 2, { size: 520, duration: 5.8 })
  }, 350)
})

watch(
  () => props.lilies.length,
  async (next, prev) => {
    if (prev === undefined) return
    if (next <= prev) return

    // Wait a tick so the parent has a chance to write x/y.
    await Promise.resolve()

    const lily = props.lilies[next - 1]
    if (!lily) return
    const left = window.innerWidth / 2 + (lily.x ?? 0)
    const top = window.innerHeight / 2 + (lily.y ?? 0)
    spawnRipple(left, top, { size: 380, duration: 6.0 })
  }
)
</script>
