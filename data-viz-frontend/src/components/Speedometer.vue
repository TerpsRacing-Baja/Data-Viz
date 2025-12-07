<script setup lang="ts">
  import { inject, ref, onMounted } from "vue";
  import { EMITTER_KEY } from "../injection-keys";
  import { CAR_SPEED, Events } from "../emitter-messages";
  const emitter = inject(EMITTER_KEY);
  
  let speed = ref(-1);
  
  onMounted(() => {
    if (!emitter) throw new Error("Toplevel failed to provide emitter");
  
    emitter.on(CAR_SPEED, (e) => handleSpeedUpdate(e));
  });
  
  function handleSpeedUpdate(
    newSpeed: Events["car-speeds"]
  ){
    if (!newSpeed) throw new Error("Speeds given was empty!");
    //console.log(newSpeed["velocity"])
    //check for undefined velocity given
    if (newSpeed["velocity"] == ''){
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
  width: 80%;
  height: 80%;
}

.speedometer-container {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 100%; /* Maintain aspect ratio */
  border-radius: 50%;
  background-image: url('../assets/speedometer.svg');
  background-size: cover;
}

.speedometer-arrow {
  position: absolute;
  top: 10%;
  left: 50%;
  width: 2px;
  height: 40%;
  background-color: #3498db;
  transform-origin: bottom;
  transform: translateX(-50%);
  z-index: 2;
}

.speedometer-reading {
  margin-top: 10px;
  font-size: 24px;
  color: #333;
}
</style>