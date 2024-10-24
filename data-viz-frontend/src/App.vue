<!-- src/App.vue -->
<script setup lang="ts">
<<<<<<< Updated upstream
import PlaybackControl from "./components/PlaybackControl.vue";
import Map from "./components/Map.vue";
import CSVPicker from "./components/CSVPicker.vue";
import Speedometer from "./components/Speedometer.vue";
=======
>>>>>>> Stashed changes
</script>

<template>
  <div id="app">
    <router-view /> <!-- This will render the matched route -->
  </div>
<<<<<<< Updated upstream

  <div id="vfill" /> 
  <div id="widgets">
    <Speedometer></Speedometer>
  </div>

  <div id="widgets">
    <PlaybackControl></PlaybackControl>
  </div>

  <div id="vfill"/>
  <div id="widgets">
    <CSVPicker></CSVPicker>
  </div>

=======
>>>>>>> Stashed changes
</template>

<style scoped>
/* Add any global styles if needed */
</style>
