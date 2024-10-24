// src/main.ts
import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import { EMITTER_KEY } from "./injection-keys";

import OpenLayersMap from "vue3-openlayers";
import "vue3-openlayers/styles.css";

import mitt from "mitt";
import router from './router'; // Import the router

const emitter = mitt();
const app = createApp(App);

app.use(OpenLayersMap);
app.use(router); // Use the router

// Everything needs a common emitter object
app.provide(EMITTER_KEY, emitter);
app.mount("#app");
