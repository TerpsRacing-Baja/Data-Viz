<script setup lang="ts">
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faPlay, faPause } from '@fortawesome/free-solid-svg-icons'
const play = ref(false)
</script>

<template>
    <button @click="play = !play">
        <font-awesome-icon :icon="play ? faPlay : faPause"></font-awesome-icon>
    </button>
</template>

<style scoped></style>
