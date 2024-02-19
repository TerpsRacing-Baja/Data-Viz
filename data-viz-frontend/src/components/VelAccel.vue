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
  <div id="playback">
    <label> Hello: {{ speed }} </label>
    
  </div>
</template>

<style scoped>
#playback {
  width: 20%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
