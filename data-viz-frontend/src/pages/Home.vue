<!-- src/pages/Home.vue -->
<script setup lang="ts">
import PlaybackControl from "../components/PlaybackControl.vue";
import Map from "../components/Map.vue";
import CSVPicker from "../components/CSVPicker.vue";
import Speedometer from "../components/Speedometer.vue";
import Gyro from "../components/Rotation.vue";
import { useRouter } from 'vue-router'; // Import the router

const router = useRouter(); // Initialize the router

const goToNewPage = () => {
  router.push('/new-page'); // Redirect to the new page
};
</script>

<template>
  <div id="layout">
    <!-- Map and Scrollbar (PlaybackControl) Section -->
    <div id="left-section">
      <Map />
      <div id="playback-wrapper">
        <PlaybackControl />
      </div>
    </div>

    <!-- Widgets Section -->
    <div id="right-section">
      <Speedometer />
      <Gyro />
      <CSVPicker />
      <button @click="goToNewPage">Go to New Page</button> <!-- Button to redirect -->
    </div>
  </div>
</template>

<style scoped>
/* Same styles as before */
#layout {
  display: flex;
  justify-content: space-between;
  height: 80vh;
}

#left-section {
  width: 66.66%;
  display: flex;
  flex-direction: column;
}

#left-section > div:first-child {
  height: 70vh;
  width: 100%;
}

#playback-wrapper {
  width: 100%;
  height: 5vh;
  margin-top: 1vh;
}

#right-section {
  width: 30%;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  gap: 30vh;
}

#right-section > * {
  height: 20vh;
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
}

#right-section > *:not(:last-child) {
  margin-bottom: 1vh;
}
</style>
