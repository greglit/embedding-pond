<template>
  <div class="info-popover" role="dialog" aria-modal="false" :aria-label="t('info.ariaLabel')">
    <header>
      <h2>{{ t('info.title') }}</h2>
      <IconButton :label="t('common.close')" @click="emit('close')" />
    </header>

    <div class="info-popover__body markdown-body" v-html="renderedHtml"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import MarkdownIt from 'markdown-it'
import IconButton from './IconButton.vue'
import infoEn from '../content/info.en.md?raw'
import infoDe from '../content/info.de.md?raw'

const { t } = useI18n()
const route = useRoute()
const md = new MarkdownIt({ html: true, linkify: true, breaks: false })

const currentLang = computed<'en' | 'de'>(() => (route.params.lang === 'de' ? 'de' : 'en'))

const renderedHtml = computed(() => {
  const source = currentLang.value === 'de' ? infoDe : infoEn
  return md.render(source)
})

const emit = defineEmits<{
  (event: 'close'): void
}>()
</script>
