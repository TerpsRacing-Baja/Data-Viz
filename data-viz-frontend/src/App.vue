<script setup lang="ts">
import PlaybackControl from "./components/PlaybackControl.vue";
import Map from "./components/Map.vue";
import CSVPicker from "./components/CSVPicker.vue";
import Speedometer from "./components/Speedometer.vue";
</script>

<template>
  
  <div id="map">
    <Map></Map>
  </div>

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

</template>

<style scoped>
#map {
  width: 100%;
  height: 60vh;
}

#vfill {
  height: 10vh;
}

#widgets {
  width: 100%;
  height: 20vh;
}
</style>
