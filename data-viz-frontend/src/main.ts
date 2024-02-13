import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

import OpenLayersMap from 'vue3-openlayers'
import "vue3-openlayers/styles.css"

import mitt from 'mitt'

const emitter = mitt()
const app = createApp(App)
app.use(OpenLayersMap)

app.provide('emitter', emitter);
app.mount('#app')
