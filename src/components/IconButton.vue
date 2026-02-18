<template>
  <button class="icon-button" type="button" :aria-label="label" :title="label">
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
      <path
        d="M 6 6 L 18 18 M 18 6 L 6 18"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  label: string
}>()
</script>
