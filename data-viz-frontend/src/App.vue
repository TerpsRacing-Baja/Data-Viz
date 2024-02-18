<script setup lang="ts">
import PlaybackControl from "./components/PlaybackControl.vue";
import Map from "./components/Map.vue";
import Vectors from "./components/VelAccel.vue";
</script>

<template>
  <div id="map">
    <Map></Map>
  </div>

  <div id="vfill" />

  <div id="widgets">
    <PlaybackControl></PlaybackControl>
  </div>
  <div id="vfill" />

  <div id="widgets">
    <Vectors></Vectors>
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
