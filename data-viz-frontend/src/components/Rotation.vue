<template>
    <div class="pitchometer">
      <img class="buggy" :style="{ transform: 'rotate(' + getPitch() + 'deg)' }" src="../assets/buggy.svg" alt="Buggy">
      <div class="pitchometer-reading">{{ formattedpitch }} pitch</div>
      <img class="buggy" :style="{ transform: 'rotate(' + getYaw() + 'deg)' }" src="../assets/buggy_front.svg" alt="Buggy">
      <div class="pitchometer-reading">{{ formattedyaw }} yaw</div>
    </div>
  </template>
  
  <script setup lang="ts">
    import { inject, ref, onMounted } from "vue";
    import { EMITTER_KEY } from "../injection-keys";
    import { Events, ROTATION } from "../emitter-messages";
  
    const emitter = inject(EMITTER_KEY);
    let pitch = ref(-1);
    let yaw = ref(-1);
    let roll = ref(-1);
    let formattedpitch = ref('');
    let formattedyaw = ref('');
    let formattedroll = ref('');

  
    onMounted(() => {
      if (!emitter) throw new Error("Toplevel failed to provide emitter");
  
      emitter.on(ROTATION, (e) => handleRotationUpdate(e));
    });
  
    function handleRotationUpdate(newRot: Events["rotation"]) {
      if (!newRot) throw new Error("pitchs given was empty!");
  
      if (newRot["pitch"] == '') {
        return;
      }
  
      const newpitch = parseFloat(newRot["pitch"]);
      const newyaw = parseFloat(newRot["yaw"]);
      const newroll = parseFloat(newRot["roll"]);
      if (!isNaN(newpitch)) {
        pitch.value = newpitch;
        yaw.value = newyaw;
        roll.value = newroll;
        formattedpitch.value = pitch.value.toFixed(3);
        formattedyaw.value = yaw.value.toFixed(3);
        formattedroll.value = roll.value.toFixed(3);
      }
    }
  
    function getPitch() {
      return pitch.value ; // Adjust multiplier and offset as needed
    }
    function getYaw() {
      return yaw.value ; // Adjust multiplier and offset as needed
    }
    function getRoll() {
      return roll.value ; // Adjust multiplier and offset as needed
    }
  </script>
  
  <style scoped>
    .pitchometer {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
  
    .buggy {
      width: 200px; /* Adjust size as needed */
      height: auto;
      margin-bottom: 10px; /* Add margin for spacing */
    }
  
    .pitchometer-reading {
      font-size: 24px;
      color: #333;
    }
  </style>
  