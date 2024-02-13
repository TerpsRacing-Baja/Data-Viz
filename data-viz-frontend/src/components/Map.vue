<template>
    <ol-map :loadTilesWhileAnimating="true" :loadTilesWhileInteracting="true" style="height: 100%; width: 100%">
        <ol-view ref="view" :center="center" :rotation="rotation" :zoom="zoom" :projection="projection" />
        <ol-tile-layer>
            <ol-source-osm />
        </ol-tile-layer>
        <ol-vector-layer>
            <ol-source-vector ref="sourceRef">
                <ol-feature>
                    <ol-geom-multi-line-string :coordinates="path"></ol-geom-multi-line-string>
                    <ol-style>
                        <ol-style-stroke :color="strokeColor" :width="strokeWidth"></ol-style-stroke>
                    </ol-style>
                </ol-feature>
            </ol-source-vector>
        </ol-vector-layer>
    </ol-map>
</template>
  
<script setup lang="ts">
import { inject, ref, onMounted } from 'vue'
import type VectorSource from "ol/source/vector";

const sourceRef = ref<{ source: VectorSource }>(null);
const emitter = inject('emitter')
const center = ref([-77.4, 39.6])
const projection = ref('EPSG:4326')
const zoom = ref(8)
const rotation = ref(0)

const strokeWidth = ref(10);
const strokeColor = ref("red");

const path = ref([])

onMounted(() => {
    const source = sourceRef.value?.source
    emitter.on('car-state', e => handlePosUpdate(e, source))
});

function handlePosUpdate(newPos, source) {
    if (path.value.length == 0)
        path.value.push([[newPos['lon'], newPos['lat']]])
    else
        path.value.push([path.value.slice(-1).pop().slice(-1).pop(), [newPos['lon'], newPos['lat']]])
    console.log(path.value)
}
</script>