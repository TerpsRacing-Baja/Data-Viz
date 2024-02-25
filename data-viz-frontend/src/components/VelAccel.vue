    <script setup lang="ts">
  import { inject, ref, onMounted } from "vue";
  import { EMITTER_KEY } from "../injection-keys";
  import { CAR_SPEED, Events } from "../emitter-messages";
  const emitter = inject(EMITTER_KEY);
  
  let speed = ref(0);
  let acceleration = ref(0);
  
  onMounted(() => {
    // get a reference to OL objects so their methods can be used
    if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking
  
    // sets up a listener callback for car-state update
    emitter.on(CAR_SPEED, (e) => handleSpeedUpdate(e));
  });
  
  function handleSpeedUpdate(
    newSpeed: Events["car-speeds"]
  ){
    if (!newSpeed) throw new Error("Speeds given was empty!");
    speed.value = newSpeed["velocity"]
    acceleration.value = newSpeed["acceleration"]
  }
  
  </script>

<template>
    <div class="speedometer">
      <div class="speedometer-container">
        <div class="speedometer-arrow" :style="{ transform: 'rotate(' + (speed * 9 + 270 )  + 'deg)' }"></div>
      </div>
      <div class="speedometer-reading">{{ speed }} km/h</div>
    </div>
  </template>
  
  <style scoped>
  .speedometer {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .speedometer-container {
    position: relative;
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background-color: #f0f0f0;
  }
  
  .speedometer-arrow {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 2px;
    height: 80px;
    background-color: #3498db;
    transform-origin: bottom;
    transform: translate(-50%, -100%);
  }
  
  .speedometer-reading {
    margin-top: 10px;
    font-size: 24px;
    color: #333;
  }
  </style>
  