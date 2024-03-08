<template>
    <div class="container">
      <TresCanvas v-bind="gl">
            
        <TresPerspectiveCamera :position="[3, 3, 3]" />
        <OrbitControls />
        <TresMesh :position="[0, 0, 0]" :rotation="[pitch, yaw, roll]">
          <TresBoxGeometry :args="[1, 1.5, 3]" />
          <TresMeshToonMaterial color="#82DBC5" />
        </TresMesh>
        
        <TresGridHelper />
        <TresDirectionalLight :position="[0, 2, 4]" :intensity="1.2" cast-shadow />
      </TresCanvas>
    </div>
    <div class="reading">pitch: {{ pitch.toFixed(3) }} deg/sec</div>
    <div class="reading">yaw: {{ yaw.toFixed(3) }} deg/sec</div>
    <div class="reading">roll: {{ roll.toFixed(3) }} deg/sec</div>
  </template>
  
  <script setup lang="ts">
  
  import { BasicShadowMap, SRGBColorSpace, NoToneMapping } from 'three';
  import { TresCanvas } from '@tresjs/core';
  import { OrbitControls } from '@tresjs/cientos';
  import { CAR_ROTATION, Events } from "../emitter-messages";
  import { inject, ref, onMounted } from "vue";
  import { EMITTER_KEY } from "../injection-keys";
  const emitter = inject(EMITTER_KEY);
  
  const gl = {
    clearColor: '#82DBC5',
    shadows: true,
    alpha: false,
    shadowMapType: BasicShadowMap,
    outputColorSpace: SRGBColorSpace,
    toneMapping: NoToneMapping,
  };

  let yaw = ref(0);
  let pitch = ref(0);
  let roll = ref(0);
  
  onMounted(() => {
    if (!emitter) throw new Error("Toplevel failed to provide emitter");
  
    emitter.on(CAR_ROTATION, (e) => handleRotationUpdate(e));
  });

  function handleRotationUpdate(
    newRot: Events["car-speeds"]
  ){
    if (!newRot) throw new Error("Rotations given was empty!");
    yaw.value = (newRot["yaw"] * Math.PI/180)
    pitch.value = (newRot["pitch"] * Math.PI/180)
    roll.value = (newRot["roll"]* Math.PI/180)
  }
  

  </script>
  
  <style scoped>
  .container {
    width: 300px; /* Adjust the width as needed */
    height: 200px; /* Adjust the height as needed */
    margin: 0 auto; /* Center the container horizontally */
    border: 1px solid #ccc; /* Optional: Add a border for visual clarity */
  }

  .reading {
    margin-top: 10px;
    font-size: 24px;
    color: #333;
  }
  </style>
  