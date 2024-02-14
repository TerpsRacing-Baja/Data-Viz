<template>
  <ol-map
    :loadTilesWhileAnimating="true"
    :loadTilesWhileInteracting="true"
    style="height: 100%; width: 100%"
  >
    <ol-view
      ref="viewRef"
      :center="center"
      :rotation="rotation"
      :zoom="zoom"
      :projection="projection"
    />
    <ol-tile-layer>
      <ol-source-osm />
    </ol-tile-layer>
    <ol-vector-layer>
      <ol-source-vector ref="sourceRef">
        <ol-feature>
          <ol-geom-multi-line-string
            ref="pathRef"
            :coordinates="path"
          ></ol-geom-multi-line-string>
          <ol-style>
            <ol-style-stroke
              :color="strokeColor"
              :width="strokeWidth"
            ></ol-style-stroke>
          </ol-style>
        </ol-feature>
        <ol-feature>
          <ol-geom-point :coordinates="curr"></ol-geom-point>
          <ol-style>
            <ol-style-icon :src="buggy" :scale="0.05"></ol-style-icon>
          </ol-style>
        </ol-feature>
      </ol-source-vector>
    </ol-vector-layer>
  </ol-map>
</template>

<script setup lang="ts">
import { inject, ref, onMounted } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { CAR_STATE, Events } from "../emitter-messages";
import type View from "ol/View";
import type VectorSource from "ol/source/vector";
import buggy from "../assets/buggy.svg";

const emitter = inject(EMITTER_KEY);
const viewRef = ref<{ view: View }>();
const sourceRef = ref<{ source: VectorSource }>();
const center = ref([-77.4, 39.6]);
const projection = ref("EPSG:4326");
const zoom = ref(8);
const rotation = ref(0);

const strokeWidth = ref(10);
const strokeColor = ref("red");

const path = ref<([[number, number]] | [[number, number], [number, number]])[]>(
  [[[0, 0]]]
);
const curr = ref<[number, number]>([0, 0]);

onMounted(() => {
  // get a reference to OL objects so their methods can be used
  if (!viewRef.value?.view || !sourceRef.value?.source)
    throw new Error("Map references are broken, rendering stopped");

  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  const view: View = viewRef.value?.view;
  const source: VectorSource = sourceRef.value?.source;

  // sets up a listener callback for car-state update
  emitter.on(CAR_STATE, (e) => handlePosUpdate(e, view, source));
});

function handlePosUpdate(
  newPos: Events["car-state"],
  view: View,
  source: VectorSource
) {
  if (!newPos) throw new Error("Position update to map was empty!");

  // Update position for the icon and add to the multilinestring array nesting
  curr.value = [newPos["lon"], newPos["lat"]];

  if (path.value[0][0][0] == 0 && path.value[0][0][1] == 0) {
    // 0, 0 is "null island", somewhere in international waters .. this is a safe initial state flag
    path.value = [[curr.value]];
  } else {
    path.value.push([
      path.value.slice(-1)[path.value.slice(-1).length - 1].slice(-1)[0],
      curr.value,
    ]); // this mess is so that we have an array of pairs of latlons
    // A nice-to-have, zooms the map in on the path, updating ever time the path changes
    view.fit(source.getExtent(), { padding: [50, 50, 50, 50] });
  }
}
</script>
