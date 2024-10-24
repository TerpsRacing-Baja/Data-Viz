<script setup lang="ts">
import { inject, ref, onMounted } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { ROTATION } from "../emitter-messages";

const emitter = inject(EMITTER_KEY);
const isPooling = ref(false); // Ref to track if pooling is active

onMounted(() => {
  if (!emitter) throw new Error("Toplevel failed to provide emitter");
});

// Ref to store the interval ID, so we can clear it when stopping the pool
let intervalId: number | null = null;

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


function poolingForReal(){
    //wait for signal
        //send signal
}

// Function to send random rotation data for testing stuff
function sendData() {
  if (!emitter) throw new Error("Toplevel failed to provide emitter");
  emitter.emit(ROTATION, {
    pitch: Math.random() * 360, // Random pitch
    yaw: Math.random() * 360,   // Random yaw
    roll: 1                     // Fixed roll value
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

</script>

<template>
  <div>
    <!-- Button to start/stop pooling -->
    <button @click="togglePooling">
      {{ isPooling ? 'Stop Pooling' : 'Start Pooling' }}
    </button>
  </div>
</template>
