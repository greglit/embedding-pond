import { createApp } from 'vue'
import Root from './Root.vue'
import './style.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
import router from './router'
import i18n from './i18n'

createApp(Root).use(router).use(i18n).mount('#app')
