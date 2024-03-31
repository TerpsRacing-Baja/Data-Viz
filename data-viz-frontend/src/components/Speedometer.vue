<script setup lang="ts">
  import { inject, ref, onMounted } from "vue";
  import { EMITTER_KEY } from "../injection-keys";
  import { CAR_SPEED, Events } from "../emitter-messages";
  const emitter = inject(EMITTER_KEY);
  
  let speed = ref(0);
  
  onMounted(() => {
    if (!emitter) throw new Error("Toplevel failed to provide emitter");
  
    emitter.on(CAR_SPEED, (e) => handleSpeedUpdate(e));
  });
  
  function handleSpeedUpdate(
    newSpeed: Events["car-speeds"]
  ){
    if (!newSpeed) throw new Error("Speeds given was empty!");

    //check for undefined velocity given
    if (newSpeed["velocity"] == undefined){
      //console.log("undefined velocity");
      return;
    }
    // console.log("Speed update received");
    speed.value = newSpeed["velocity"]
  }
</script>

<template>
  <div class="speedometer">
    <div class="speedometer-container">
      <div class="speedometer-background"></div> <!-- New div for the background -->
      <div class="speedometer-arrow" :style="{ transform: 'rotate(' + (speed * 7 + 220 )  + 'deg)' }"></div>
    </div>
    <div class="speedometer-reading">{{ speed }} mph</div>
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
  /* Set background image */
  background-image: url('../assets/speedometer.svg');
  background-size: cover;
}

.speedometer-background {
  /* Set the same size and border-radius as the container to cover it */
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.speedometer-arrow {
  position: absolute;
  top: 10%; /* Adjust this value as needed */
  left: 50%;
  width: 2px;
  height: 80px;
  background-color: #3498db;
  transform-origin: bottom;
  transform: translateX(-50%); /* Updated to only translate horizontally */
}

.speedometer-reading {
  margin-top: 10px;
  font-size: 24px;
  color: #333;
}
</style>
