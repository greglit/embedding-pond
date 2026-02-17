<template>
  <div class="lily-popover">
    <header>
      <div>
        <h3>Embedding waterlilly</h3>
        <p>{{ lily.sourceType === 'text' ? 'Text input' : 'Image input' }}</p>
      </div>
      <button class="icon" @click="emit('close')">Close</button>
    </header>

    <section>
      <h4>Input</h4>
      <p v-if="lily.sourceType === 'text'">{{ lily.content }}</p>
      <img v-else :src="lily.content" alt="Embedded input" />
    </section>

    <section>
      <h4>Embedding values</h4>
      <div class="embedding-values">
        <span v-for="(value, index) in fullEmbedding" :key="index">
          {{ value }}
        </span>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Lily = {
  sourceType: 'text' | 'image'
  content: string
  embedding: number[]
}

const props = defineProps<{
  lily: Lily
}>()

const emit = defineEmits<{
  (event: 'close'): void
}>()

const fullEmbedding = computed(() => props.lily.embedding.map((value) => String(value)))
</script>
