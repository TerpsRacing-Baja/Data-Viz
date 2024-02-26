<script setup lang="ts">
import PlaybackControl from "./components/PlaybackControl.vue";
import Map from "./components/Map.vue";
</script>

<template>
  <div id="map">
    <Map></Map>
  </div>

  <div id="vfill" />

  <div id="widgets">
    <PlaybackControl></PlaybackControl>
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
