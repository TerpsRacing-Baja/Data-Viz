<script setup lang="ts">
import { inject, ref } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faPlay, faPause } from '@fortawesome/free-solid-svg-icons'
import csv from '../assets/rc_30.csv' // Annoying, VSCode will complain about this, but it works so hey

const emitter = inject('emitter')
const speed = ref(100)
let play = ref(false)

let i = 0
// console.log(csv) // for debugging purposes, otherwise the contents of csv as an object are opaque

// Right now this is just grabbing from the test data, later should go to flask
function pubData() {
    if (i > 5612) i = 0
    emitter.emit('car-state', { lat: csv[i]['Latitude|"Degrees"|-180.0|180.0|25'], lon: csv[i++]['Longitude|"Degrees"|-180.0|180.0|25'] })
    waitThenPub()
}

function waitThenPub() {
    if (play.value) {
        setTimeout(pubData, 200 - speed.value)
    }
}

function toggleAndStartPub() {
    play.value = !(play.value)

    waitThenPub()
}
</script>

<template>
    <div id="playback">
        Playback Controls:
        <button @click=toggleAndStartPub()>
            <font-awesome-icon :icon="play ? faPause : faPlay"></font-awesome-icon>
        </button>
        <input v-model="speed" type="range" min="0" max="200" class="slider" />
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
