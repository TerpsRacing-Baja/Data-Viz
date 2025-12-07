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

        <!-- One line per segment -->
        <template v-for="(segment, idx) in path" :key="idx">
          <ol-feature>
            <ol-geom-line-string :coordinates="segment" />
            <ol-style>
              <ol-style-stroke
                :color="segmentColors[idx] || 'gray'"
                :width="strokeWidth"
              />
            </ol-style>
          </ol-feature>
        </template>

        <!-- Icon -->
        <ol-feature>
          <ol-geom-point :coordinates="curr" />
          <ol-style>
            <ol-style-icon :src="buggy" :scale="0.05" />
          </ol-style>
        </ol-feature>

      </ol-source-vector>
    </ol-vector-layer>
  </ol-map>
</template>


<script setup lang="ts">
import { inject, ref, onMounted } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { PLAYBACK_UPDATE, Events, GPS_DATA, GPS_POINT, SESSION_RESET, ACCELERATION_DATA } from "../emitter-messages";
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
const segmentColors = ref<string[]>([]);


const strokeWidth = ref(10);
const strokeColor = ref("red");


const path = ref<([[number, number]] | [[number, number], [number, number]])[]>(
  [[[0, 0]]]
);
const curr = ref<[number, number]>([0, 0]);

const maxPathLength = ref(400); // Maximum length of the path

let coords: [number, number][];
let i = 0;
let avgAccel = 0;



onMounted(() => {
  // get a reference to OL objects so their methods can be used
  if (!viewRef.value?.view || !sourceRef.value?.source)
    throw new Error("Map references are broken, rendering stopped");

  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  const view: View = viewRef.value?.view;
  const source: VectorSource = sourceRef.value?.source;

  // sets up listener callbacks
  emitter.on(GPS_DATA, (e) => handleGPSData(e, view, source));
  emitter.on(ACCELERATION_DATA, (e) => handleAccelerationData(e));
  emitter.on(PLAYBACK_UPDATE, (e) => handlePosUpdate(e, view, source));
  emitter.on(GPS_POINT, (e)=> handlePointUpdate(e, view, source));
  emitter.on(SESSION_RESET, resetMapData);
});

function handleAccelerationData(accel: Events["acceleration-data"]){
  if (!accel) throw new Error("accel given was empty!");
  const newx = parseFloat(accel["ax"]);
  const newy = parseFloat(accel["ay"]);
  const newz = parseFloat(accel["az"]);

  console.log("Accel Data Received: ", newx, newy, newz);

  avgAccel = Math.sqrt(newx*newx + newy*newy + newz*newz);



}
const MIN_ACCEL = 0;
const MID_ACCEL = 1;  // midpoint where color becomes yellow
const MAX_ACCEL = 2; // upper limit where color becomes red

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

function rgb(r: number, g: number, b: number) {
  return `rgb(${r}, ${g}, ${b})`;
}

function colorFromAccel(a: number) {
  if (a <= MIN_ACCEL) return "rgb(0, 255, 0)";   // green
  if (a >= MAX_ACCEL) return "rgb(255, 0, 0)";   // red

  // Blend green to yellow below midpoint
  if (a <= MID_ACCEL) {
    const t = (a - MIN_ACCEL) / (MID_ACCEL - MIN_ACCEL);
    const r = lerp(0, 255, t);
    const g = 255;
    const b = 0;
    return rgb(r, g, b); // green to yellow
  }

  // Blend yellow to red above midpoint
  const t = (a - MID_ACCEL) / (MAX_ACCEL - MID_ACCEL);
  const r = 255;
  const g = lerp(255, 0, t);
  const b = 0;
  return rgb(r, g, b);   // yellow to red
}



function handleGPSData(gps: Events["gps-data"],
view: View,
source: VectorSource
) {
  if (!gps) throw new Error("Empty GPS update!");
  //console.log(gps)

  const color = colorFromAccel(avgAccel);
  segmentColors.value.push(color);


  coords = gps["coords"];
  //console.log(coords);
  console.log("Loaded GPS data", coords )
  
  const lastSegment = path.value[path.value.length - 1];

  if (lastSegment.length === 1) {
    // If last segment has only one point, complete it
    lastSegment.push(coords);
  } else {
    // Otherwise, create a new segment
    curr.value = coords
    path.value.push([lastSegment[1], coords]);
  }

  // Check if path length exceeds the limit
  while (path.value.length > maxPathLength.value) {
    path.value.shift(); // Remove the oldest segment
  }

  view.fit(source.getExtent(), { padding: [50, 50, 50, 50] });
}

function resetMapData() {
  console.log("Map data has been reset");
  path.value = [[[0, 0]]];
  curr.value = [0, 0];
  coords = [];
  i = 0;
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
  // for (let j = i + 1; j <= newIndex["index"]; j++)
  //   path.value.push([coords[j - 1], coords[j]]);

  // console.log(path.value)
  for (let j = i + 1; j <= newIndex.index; j++) {
    path.value.push([coords[j - 1], coords[j]]);
    segmentColors.value.push(colorFromAccel(avgAccel));
  }


  for (let j = i - 1; j >= newIndex["index"]; j--) path.value.pop();

  // Special case for index 0 to clear initial value
  if (newIndex["index"] == 0) path.value = [[coords[0]]];

  // Check if path length exceeds the limit
  while (path.value.length > maxPathLength.value) {
    path.value.shift(); // Remove the oldest segment
    segmentColors.value.shift();
  }

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