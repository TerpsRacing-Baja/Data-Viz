<script setup lang="ts">
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faPlay, faPause } from '@fortawesome/free-solid-svg-icons'
const play = ref(false)
const speedPercent = ref(100)
</script>

<template>
    <button @click="play = !play">
        <font-awesome-icon :icon="play ? faPlay : faPause"></font-awesome-icon>
    </button>
    <input v-model="speedPercent" type="range" min="0" max="200" class="slider" />
</template>

<style scoped></style>
