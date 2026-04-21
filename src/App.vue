<template>
  <main class="pond-app" :class="{ 'is-planting': Boolean(travelingLily), 'has-lilies': lilies.length > 0 }">
    <div class="pond-title" :class="{ compact: titleCompact }">
      <h1>{{ t('app.title') }}</h1>
      <h2>{{ t('app.subtitle') }}</h2>
    </div>

    <div class="language-switcher" role="group" :aria-label="t('language.switcherAria')">
      <button
        type="button"
        :class="{ active: currentLang === 'en' }"
        @click="switchLanguage('en')"
      >
        {{ t('language.en') }}
      </button>
      <button
        type="button"
        :class="{ active: currentLang === 'de' }"
        @click="switchLanguage('de')"
      >
        {{ t('language.de') }}
      </button>
    </div>

    <PondScene
      :lilies="lilies"
      :active-id="activeId"
      @select="handleSelect"
      @hover="handleHover"
    />

    <button class="new-lily" @click="openCreator">
      <span class="new-lily__label">{{ lilies.length === 0 ? t('app.newLilyFirst') : t('app.newLily') }}</span>
      <span class="new-lily__emoji" aria-hidden="true">🪷</span>
    </button>

    <button class="info-button" type="button" @click="toggleInfo" :aria-expanded="showInfo" :aria-label="t('app.info')">
      <span class="info-button__icon" aria-hidden="true">i</span>
      <span>{{ t('app.info') }}</span>
    </button>

    <button
      v-if="scientificMode"
      class="science-button"
      :class="{ expanded: showScientific }"
      type="button"
      @click="toggleScientific"
      :aria-expanded="showScientific"
    >
      <span class="science-button__icon" aria-hidden="true">
        <i class="fa-solid fa-flask"></i>
      </span>
      <span class="science-button__label">{{ t('app.science') }}</span>
    </button>

    <Transition name="overlay-fade">
      <LilyCreator
        v-if="showCreator"
        :is-loading="isEmbedding"
        :preview="draftLily"
        :is-first-lily="lilies.length === 0"
        @close="closeCreator"
        @grow="handleGrow"
        @plant="handlePlant"
        @phase="creatorPhase = $event"
      />
    </Transition>

    <LilyPopover
      v-if="activeLily && !showScientific"
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

    <ScientificPopover
      v-if="scientificMode && showScientific"
      :enabled="alignmentEnabled"
      :alpha="alignmentAlpha"
      @close="showScientific = false"
      @update:enabled="alignmentEnabled = $event"
      @update:alpha="alignmentAlpha = $event"
      @reset="resetScientificDefaults"
    />

    <div
      v-if="travelingLily"
      class="traveling-lily"
      :class="{ armed: travelArmed, visible: travelVisible }"
      :style="travelStyle"
      aria-hidden="true"
    >
      <div class="traveling-lily__inner" :class="{ armed: travelArmed }" :style="travelInnerStyle">
        <div class="lily-drift">
          <div class="lily-scale">
            <svg viewBox="0 0 120 120">
              <path :d="travelingLily.shapePath" :fill="travelingLily.color" :stroke="travelingLily.outline" stroke-width="3" />
              <g class="lily-stamen">
                <circle cx="60" cy="54" r="3.3" fill="rgba(255, 244, 168, 0.95)" />
                <circle cx="53" cy="64" r="2.9" fill="rgba(255, 244, 168, 0.88)" />
                <circle cx="67" cy="65" r="2.8" fill="rgba(255, 244, 168, 0.82)" />
              </g>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PondScene from './components/PondScene.vue'
import LilyCreator from './components/LilyCreator.vue'
import LilyPopover from './components/LilyPopover.vue'
import InfoPopover from './components/InfoPopover.vue'
import ScientificPopover from './components/ScientificPopover.vue'
import { computeEmbedding } from './utils/embedding'
import { computePcaLayout } from './utils/pca'
import { embeddingToPath } from './utils/shape'
import { buildVectorsForPca } from './utils/centroidAlign'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const currentLang = computed<'en' | 'de'>(() => (route.params.lang === 'de' ? 'de' : 'en'))
const scientificMode = computed(() => route.query.mode === 'scientific')

const switchLanguage = (lang: 'en' | 'de') => {
  if (lang === currentLang.value) return
  router.push({
    name: 'home',
    params: { lang },
    query: route.query,
    hash: route.hash,
  })
}

watch(
  () => currentLang.value,
  (lang) => {
    locale.value = lang
  },
  { immediate: true }
)
const alignmentEnabled = ref(false)
const alignmentAlpha = ref(0.75)

const plantedActiveScale = 1.18

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
const showScientific = ref(false)
const isEmbedding = ref(false)
const draftLily = ref<LilyInput | null>(null)
const creatorPhase = ref<'idle' | 'embedding' | 'ready'>('idle')
const travelArmed = ref(false)
const travelVisible = ref(false)
const travelingLily = ref<
  | (LilyInput & {
      x: number
      y: number
      scale: number
    })
  | null
>(null)

const activeLily = computed(() => lilies.value.find((lily) => lily.id === activeId.value) ?? null)

const hoverLily = computed(() => lilies.value.find((lily) => lily.id === hoverId.value) ?? null)

const titleCompact = computed(() => lilies.value.length > 0 || (lilies.value.length === 0 && Boolean(travelingLily.value)))

const travelStyle = computed(() => {
  if (!travelingLily.value) return {}
  return {
    transform: `translate(-50%, -50%) translate(${travelingLily.value.x}px, ${travelingLily.value.y}px)`,
  }
})

const travelInnerStyle = computed(() => {
  if (!travelingLily.value) return {}
  return {
    transform: `scale(${travelingLily.value.scale})`,
  }
})

const openCreator = () => {
  draftLily.value = null
  creatorPhase.value = 'idle'
  travelingLily.value = null
  travelArmed.value = false
  travelVisible.value = false
  showCreator.value = true
}

const closeCreator = () => {
  showCreator.value = false
  draftLily.value = null
  creatorPhase.value = 'idle'
  travelingLily.value = null
  travelArmed.value = false
  travelVisible.value = false
}

const toggleInfo = () => {
  showInfo.value = !showInfo.value
  if (showInfo.value) {
    activeId.value = null
    hoverId.value = null
    hoverAnchor.value = null
    showCreator.value = false
    showScientific.value = false
  }
}

const toggleScientific = () => {
  showScientific.value = !showScientific.value
  if (showScientific.value) {
    activeId.value = null
    hoverId.value = null
    hoverAnchor.value = null
    showCreator.value = false
    showInfo.value = false
  }
}

const resetScientificDefaults = () => {
  alignmentEnabled.value = false
  alignmentAlpha.value = 0.75
}


const handleSelect = (id: string) => {
  if (showScientific.value) return
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
        label: payload.type === 'text' ? payload.data.slice(0, 42) : t('common.imageInput'),
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

const handlePlant = async () => {
  if (!draftLily.value) return

  // If no traveling lily exists (e.g., ready phase watcher didn't run), create at center
  if (!travelingLily.value) {
    travelingLily.value = {
      ...draftLily.value,
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
      scale: 3.25,
    }
  }

  hoverId.value = null
  hoverAnchor.value = null
  activeId.value = null
  travelVisible.value = true

  // Close modal
  showCreator.value = false

  // Compute PCA layout
  const nextLilies = [...lilies.value, draftLily.value]
  const vectorsForPca = buildVectorsForPca(nextLilies, {
    enabled: scientificMode.value && alignmentEnabled.value,
    alpha: alignmentAlpha.value,
  })
  const layout = computePcaLayout(vectorsForPca)
  const target = layout[layout.length - 1] ?? { x: 0, y: 0 }

  // Move existing lilies to new positions (CSS will animate)
  lilies.value = lilies.value.map((lily, index) => ({
    ...lily,
    x: layout[index]?.x ?? 0,
    y: layout[index]?.y ?? 0,
  }))

  // Wait for modal to unmount and DOM to settle
  await nextTick()
  
  // Start the travel animation
  travelArmed.value = true
  
  // Wait for armed class to be applied
  await nextTick()
  
  // Move to target
  if (travelingLily.value) {
    travelingLily.value = {
      ...travelingLily.value,
      x: window.innerWidth / 2 + target.x,
      y: window.innerHeight / 2 + target.y,
      scale: plantedActiveScale,
    }
  }

  // After animation completes, add to pond
  window.setTimeout(() => {
    const planted = { ...draftLily.value!, x: target.x, y: target.y }
    lilies.value = [...lilies.value, planted]
    activeId.value = planted.id
    draftLily.value = null

    requestAnimationFrame(() => {
      travelingLily.value = null
      travelArmed.value = false
      travelVisible.value = false
    })
  }, 1200)
}

watch(
  () => [alignmentEnabled.value, alignmentAlpha.value],
  () => {
    if (!scientificMode.value) return
    if (travelingLily.value) return
    if (lilies.value.length < 2) return

    const layout = computePcaLayout(
      buildVectorsForPca(lilies.value, {
        enabled: alignmentEnabled.value,
        alpha: alignmentAlpha.value,
      })
    )

    lilies.value = lilies.value.map((lily, index) => ({
      ...lily,
      x: layout[index]?.x ?? 0,
      y: layout[index]?.y ?? 0,
    }))
  }
)

watch(
  () => [showCreator.value, draftLily.value, creatorPhase.value] as const,
  async ([isOpen, draft, phase]) => {
    if (!isOpen) return
    if (!draft) return
    if (phase !== 'ready') return
    if (travelArmed.value) return

    await nextTick()
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()))

    // Find the big-preview in the modal (now contains the lily SVG).
    const anchor = document.querySelector('.lily-panel .big-preview') as HTMLElement | null
    const rect = anchor?.getBoundingClientRect() ?? null
    if (!rect || rect.width < 10 || rect.height < 10) return

    const baseSize = 104
    const startScale = Math.min(4.8, Math.max(2.2, rect.width / baseSize))

    travelingLily.value = {
      ...draft,
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2,
      scale: startScale,
    }
    travelArmed.value = false
    travelVisible.value = false

    // Fade in the preview lily as soon as phase 3 (ready) starts.
    await nextTick()
    requestAnimationFrame(() => {
      travelVisible.value = true
    })
  }
)

watch(
  () => showCreator.value,
  (isOpen, wasOpen) => {
    if (isOpen) return
    // Only clear traveling lily when closing normally, not when planting
    // (planting sets showCreator to false but expects travel to continue)
    if (wasOpen && !travelingLily.value) {
      travelingLily.value = null
      travelArmed.value = false
      travelVisible.value = false
    }
  }
)

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
