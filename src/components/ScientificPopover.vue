<template>
  <div class="scientific-popover" role="dialog" aria-label="Scientific controls">
    <header>
      <div>
        <h3>Scientific Tools</h3>
        <p>Tools to investigate the modality gap. For more info, click the Info button in the bottom-left corner.</p>
      </div>
      <IconButton label="Close" @click="emit('close')" />
    </header>

    <section class="popover-body">
      <label class="science-toggle">
        <input type="checkbox" :checked="props.enabled" @change="onToggle" />
        <span>Centroid alignment (text -&gt; image)</span>
      </label>

      <div class="science-slider" :class="{ dim: !props.enabled }">
        <div class="science-slider__row">
          <span>Strength</span>
          <span class="science-slider__value">{{ props.alpha.toFixed(2) }}</span>
        </div>
        <input
          type="range"
          min="0"
          max="2"
          step="0.05"
          :value="props.alpha"
          :disabled="!props.enabled"
          @input="onAlphaInput"
        />
      </div>

      <button class="science-reset" type="button" @click="emit('reset')">
        Restore defaults
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import IconButton from './IconButton.vue'

const props = defineProps<{
  enabled: boolean
  alpha: number
}>()

const emit = defineEmits<{
  (event: 'close'): void
  (event: 'update:enabled', value: boolean): void
  (event: 'update:alpha', value: number): void
  (event: 'reset'): void
}>()

const onToggle = (event: Event) => {
  const input = event.target as HTMLInputElement | null
  emit('update:enabled', Boolean(input?.checked))
}

const onAlphaInput = (event: Event) => {
  const input = event.target as HTMLInputElement | null
  const value = input ? Number(input.value) : 1
  emit('update:alpha', value)
}
</script>
