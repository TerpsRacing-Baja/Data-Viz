<script setup lang="ts">
import { inject, ref, onMounted, onUnmounted } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { ROTATION } from "../emitter-messages";

const emitter = inject(EMITTER_KEY);
const isPooling = ref(false); // Track if pooling is active
let intervalId: number | null = null;

onMounted(() => {
  if (!emitter) throw new Error("Toplevel failed to provide emitter");
});

// Function to start pooling
function start() {
  poolForData();
  isPooling.value = true;
}

// Function to stop pooling
function stop() {
  if (intervalId !== null) {
    clearInterval(intervalId);
    intervalId = null;
  }
  isPooling.value = false;
}

// Function to simulate data pooling
function poolForData() {
  intervalId = setInterval(() => {
    sendData();
  }, 500);
}

// Function to send random rotation data for testing
function sendData() {
  if (!emitter) throw new Error("Toplevel failed to provide emitter");
  emitter.emit(ROTATION, {
    pitch: Math.random() * 360,
    yaw: Math.random() * 360,
    roll: 1
  });
}

// Function to handle button click
function togglePooling() {
  if (isPooling.value) {
    stop();
  } else {
    start();
  }
}

// **Stop pooling automatically when the component is unmounted**
onUnmounted(() => {
  stop();
});
</script>

<template>
  <div>
    <!-- Button to start/stop pooling -->
    <button @click="togglePooling">
      {{ isPooling ? 'Stop Pooling' : 'Start Pooling' }}
    </button>
  </div>
</template>
