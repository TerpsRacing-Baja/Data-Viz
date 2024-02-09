<template>
    <div id="playback">
        Playback Controls:
        <button @click="play = !play">
            <font-awesome-icon :icon="play ? faPause : faPlay"></font-awesome-icon>
        </button>
        <input v-model="speedPercent" type="range" min="0" max="200" class="slider" @change="getReponse" />
        <label>Speed: {{ speedPercent }}%</label>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faPlay, faPause } from '@fortawesome/free-solid-svg-icons'
import axios from 'axios'

const play = ref(false)
const speedPercent = ref(100)

const epic = () => {
    console.log("epic")
}

const handleSpeedChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    speedPercent.value = parseInt(target.value);
}

const getReponse = (event: Event) => {
    const path = 'http://localhost:5000/shark'
    const target = event.target as HTMLInputElement;
    speedPercent.value = parseInt(target.value);

    axios.get(path)
    .then ((res) => { 
        console.log(res.data)
                
    }) 
    .catch ((err) => {
        console.error(err)
    });
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
