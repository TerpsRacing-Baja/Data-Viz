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
import { PLAYBACK_UPDATE, Events, GPS_DATA, GPS_POINT } from "../emitter-messages";
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

let coords: [number, number][];
let i = 0;

onMounted(() => {
  // get a reference to OL objects so their methods can be used
  if (!viewRef.value?.view || !sourceRef.value?.source)
    throw new Error("Map references are broken, rendering stopped");

  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  const view: View = viewRef.value?.view;
  const source: VectorSource = sourceRef.value?.source;

  // sets up listener callbacks
  emitter.on(GPS_DATA, (e) => handleGPSData(e, view, source));
  emitter.on(PLAYBACK_UPDATE, (e) => handlePosUpdate(e, view, source));
  emitter.on(GPS_POINT, (e)=> handlePointUpdate(e, view, source))
  
});

function handleGPSData(gps: Events["gps-data"],
view: View,
source: VectorSource
) {
  if (!gps) throw new Error("Empty GPS update!");

  coords = gps["point"];
  console.log(coords);
  
  const lastSegment = path.value[path.value.length - 1];

  if (lastSegment.length === 1) {
    // If last segment has only one point, complete it
    lastSegment.push(coords);
  } else {
    // Otherwise, create a new segment
    curr.value = coords
    path.value.push([lastSegment[1], coords]);
  }
  view.fit(source.getExtent(), { padding: [50, 50, 50, 50] });
}

function handlePosUpdate(
  newIndex: Events["playback-update"],
  view: View,
  source: VectorSource
) {
  if (!newIndex) throw new Error("Index update to map was empty!");
  if (i < 0 || i > coords.length) throw new Error("Index update out of bounds");

  //check if this index is null
  if (coords[newIndex.index] && coords[newIndex.index][0] !== undefined && coords[newIndex.index][1] !== undefined) {
    //console.log("Coordinates are defined:", coords[newIndex.index]);
  } else {
    //console.log("Coordinates are undefined or contain undefined values.");
    return;
  }

  // Update position for the icon and add to the multilinestring array nesting
  curr.value = coords[newIndex["index"]];

  // Should scale if we want to jump index, can add or remove path as required
  // Sneaky since there's a builtin if
  for (let j = i + 1; j <= newIndex["index"]; j++)
    path.value.push([coords[j - 1], coords[j]]);

  console.log(path.value)

  for (let j = i - 1; j >= newIndex["index"]; j--) path.value.pop();

  // Special case for index 0 to clear initial value
  if (newIndex["index"] == 0) path.value = [[coords[0]]];

  // Update for next time
  i = newIndex["index"];

  // A nice-to-have, zooms the map in on the path, updating ever time the path changes
  view.fit(source.getExtent(), { padding: [50, 50, 50, 50] });
}

function handlePointUpdate(
  newPoint: Events["gps-point"],
  view: View,
  source: VectorSource
) {
  if (!newPoint || !newPoint.point || !Array.isArray(newPoint.point) || newPoint.point.length !== 2) {
    throw new Error("Invalid GPS point data!");
  }

  const newCoord: [number, number] = newPoint.point;

  // If path is empty, initialize it
  if (path.value.length === 0) {
    path.value.push([newCoord]); // Start with a single-point array
  } else {
    // Append a segment connecting the last known position to the new point
    const lastSegment = path.value[path.value.length - 1];

    if (lastSegment.length === 1) {
      // If last segment has only one point, complete it
      lastSegment.push(newCoord);
    } else {
      // Otherwise, create a new segment
      path.value.push([lastSegment[1], newCoord]);
    }
  }

  // Update the view to fit the updated path
  view.fit(source.getExtent(), { padding: [50, 50, 50, 50] });
}

</script>