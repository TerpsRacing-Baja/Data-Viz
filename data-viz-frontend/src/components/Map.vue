<template>
    <ol-map :loadTilesWhileAnimating="true" :loadTilesWhileInteracting="true" style="height: 100%; width: 100%">
        <ol-view ref="view" :center="center" :rotation="rotation" :zoom="zoom" :projection="projection" />
        <ol-tile-layer>
            <ol-source-osm />
        </ol-tile-layer>
    </ol-map>
</template>
  
<script setup lang="ts">
import { ref } from "vue";

const center = ref([40, 40]);
const projection = ref("EPSG:4326");
const zoom = ref(8);
const rotation = ref(0);
</script>