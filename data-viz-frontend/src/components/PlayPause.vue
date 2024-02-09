<template>
    <div id="playback">
        Playback Controls:
        <button @click="play = !play">
            <font-awesome-icon :icon="play ? faPause : faPlay"></font-awesome-icon>
        </button>
        <input v-model="speedPercent" type="range" min="0" max="200" class="slider" @input="handleSpeedChange" />
        <label>Speed: {{ speedPercent }}%</label>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faPlay, faPause } from '@fortawesome/free-solid-svg-icons'


const play = ref(false)
const speedPercent = ref(100)

const handleSpeedChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    speedPercent.value = parseInt(target.value);
}
</script>

<style scoped>
#playback {
    width: 20%;
    display: flex;
    flex-direction: column;
    gap: 20px;
}
</style>
