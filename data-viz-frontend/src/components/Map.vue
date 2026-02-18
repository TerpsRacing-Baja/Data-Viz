<template>
  <div style="display: flex; flex-direction: column; height: 100%">
    <div style="padding: 10px; background: #f0f0f0; border-bottom: 1px solid #ccc">
      <label style="margin-right: 15px">
        <strong>Color By:</strong>
      </label>
      <label style="margin-right: 15px">
        <input type="radio" v-model="accelColorMode" value="avg" />
        Average Acceleration
      </label>
      <label style="margin-right: 15px">
        <input type="radio" v-model="accelColorMode" value="ax" />
        X Acceleration
      </label>
      <label style="margin-right: 15px">
        <input type="radio" v-model="accelColorMode" value="ay" />
        Y Acceleration
      </label>
      <label style="margin-right: 15px">
        <input type="radio" v-model="accelColorMode" value="az" />
        Z Acceleration
      </label>
    </div>
    <ol-map
      ref="mapRef"
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
            <ol-feature :properties="{ segIndex: idx }">
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
  </div>
</template>


<script setup lang="ts">
import { inject, ref, onMounted, watch } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import {
  PLAYBACK_UPDATE,
  Events,
  GPS_DATA,
  GPS_POINT,
  SESSION_RESET,
  ACCELERATION_DATA,
} from "../emitter-messages";
import type View from "ol/View";
import type VectorSource from "ol/source/vector";
import type Map from "ol/Map";
import type Feature from "ol/Feature";
import buggy from "../assets/buggy.svg";

const emitter = inject(EMITTER_KEY);

const mapRef = ref<{ map: Map }>();
const viewRef = ref<{ view: View }>();
const sourceRef = ref<{ source: VectorSource }>();

const center = ref([-77.4, 39.6]);
const projection = ref("EPSG:4326");
const zoom = ref(8);
const rotation = ref(0);
const segmentColors = ref<string[]>([]);   // visible window
const segmentAccel = ref<AccelData[]>([]);    // visible window

// Color mode: which acceleration component to use
const accelColorMode = ref<'avg' | 'ax' | 'ay' | 'az'>('avg');

// Global caches keyed by segment end index j
const segmentColorCache: Record<number, string> = {};
const segmentAccelCache: Record<number, AccelData> = {};


const strokeWidth = ref(10);

const path = ref<([[number, number]] | [[number, number], [number, number]])[]>([
  [[0, 0]],
]);
const curr = ref<[number, number]>([0, 0]);
const maxPathLength = ref(400);

let coords: [number, number][];
let i = 0;
let avgAccel = 0;
let newx, newy, newz = 0;

// Acceleration data type
interface AccelData {
  avg: number;
  ax: number;
  ay: number;
  az: number;
}

// Currently hovered segment info
const hoveredSegment = ref<{
  index: number;
  color: string;
  accel: AccelData;
} | null>(null);




onMounted(() => {
  if (!mapRef.value?.map || !viewRef.value?.view || !sourceRef.value?.source) {
    throw new Error("Map references are broken, rendering stopped");
  }
  if (!emitter) throw new Error("Toplevel failed to provide emitter");

  const map: Map = mapRef.value.map;
  const view: View = viewRef.value.view;
  const source: VectorSource = sourceRef.value.source;

  // events you already had
  emitter.on(GPS_DATA, (e) => handleGPSData(e, view, source));
  emitter.on(ACCELERATION_DATA, (e) => handleAccelerationData(e));
  emitter.on(PLAYBACK_UPDATE, (e) => handlePosUpdate(e, view, source));
  emitter.on(GPS_POINT, (e) => handlePointUpdate(e, view, source));
  emitter.on(SESSION_RESET, resetMapData);

  // Watch for mode changes to recalculate colors
  watch(() => accelColorMode.value, () => {
    // Clear the color cache and recalculate
    for (const k in segmentColorCache) delete segmentColorCache[k];
    
    // Regenerate colors for visible segments
    const newColors = segmentAccel.value.map(accel => 
      colorFromAccel(accel, accelColorMode.value)
    );
    segmentColors.value = newColors;
  });

  // new hover handler
  map.on("pointermove", (evt) => {
    if (evt.dragging) return;

    let hit = false;

    map.forEachFeatureAtPixel(evt.pixel, (feature) => {
      const f = feature as Feature;
      const segIndex = f.get("segIndex");

      if (typeof segIndex === "number") {
        const color = segmentColors.value[segIndex];
        const accel = segmentAccel.value[segIndex];

        hoveredSegment.value = {
          index: segIndex,
          color,
          accel,
        };

        console.log(
          "Hovered segment",
          segIndex,
          "color:",
          color,
          "accel:",
          accel
        );

        hit = true;
        return true; // stop after first hit
      }

      return false;
    });

    if (!hit) {
      hoveredSegment.value = null;
    }

    // Optional cursor feedback
    const target = map.getTargetElement();
    if (target) {
      target.style.cursor = hit ? "pointer" : "";
    }
  });
});

function handleAccelerationData(accel: Events["acceleration-data"]){
  if (!accel) throw new Error("accel given was empty!");
  
  newx = parseFloat(accel["ax"]);
  newy = parseFloat(accel["ay"]);
  newz = parseFloat(accel["az"]);

  //console.log("Accel Data Received: ", newx, newy, newz);

  avgAccel = Math.sqrt(newx*newx + newy*newy + newz*newz);



}


const MIN_ACCEL = 0;
const MID_ACCEL = 1.5;  // midpoint where color becomes yellow
const MAX_ACCEL = 3; // upper limit where color becomes red

const SINGLE_MIN_ACCEL = -0.8; //blue
const SINGLE_MAX_ACCEL = 0.8; //red

const Z_AXIS_MIN_ACCEL = -0.8; 
const Z_AXIS_MAX_ACCEL = 0.8;



function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

function rgb(r: number, g: number, b: number) {
  return `rgb(${r}, ${g}, ${b})`;
}

function colorFromAccel(accelData: AccelData, mode: 'avg' | 'ax' | 'ay' | 'az' = 'avg') {
  let a = 0;
  
  // Select the requested component. For axis-specific modes preserve sign
  // so negative values map to red and positive values to blue. For `avg`
  // we keep the magnitude as before.
  if (mode === 'avg') {
    a = accelData.avg;
  } else if (mode === 'ax') {
    a = accelData.ax;
  } else if (mode === 'ay') {
    a = accelData.ay;
  } else if (mode === 'az') {
    a = accelData.az;
  }

  


  if (mode=='avg'){
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
  } else if (mode == "az") {
    // Z-axis mode: blend red -> white -> blue (negative -> zero -> positive)
    if (a <= Z_AXIS_MIN_ACCEL) {
      return "rgb(255, 0, 0)"; // very negative => red
    }
    if (a >= Z_AXIS_MAX_ACCEL) {
      return "rgb(0, 0, 255)"; // very positive => blue
    }

    if (a <= 0) {
      // [Z_AXIS_MIN_ACCEL, 0] -> red to white
      const t = (a - Z_AXIS_MIN_ACCEL) / (0 - Z_AXIS_MIN_ACCEL);
      const r = 255;
      const g = lerp(0, 255, t);
      const b = lerp(0, 255, t);
      return rgb(r, g, b); // red -> white
    } else {
      // [0, Z_AXIS_MAX_ACCEL] -> white to blue
      const t = a / Z_AXIS_MAX_ACCEL;
      const r = lerp(255, 0, t);
      const g = lerp(255, 0, t);
      const b = 255;
      return rgb(r, g, b); // white -> blue
    }
  } else {
    // Single-axis (ax/ay) mode: negative -> red, positive -> blue
    if (a <= SINGLE_MIN_ACCEL) {
      return "rgb(255, 0, 0)"; // very negative => red
    }
    if (a >= SINGLE_MAX_ACCEL) {
      return "rgb(0, 0, 255)"; // very positive => blue
    }

    if (a <= 0) {
      // [SINGLE_MIN_ACCEL, 0] -> red to white
      const t = (a - SINGLE_MIN_ACCEL) / (0 - SINGLE_MIN_ACCEL);
      const r = 255;
      const g = lerp(0, 255, t);
      const b = lerp(0, 255, t);
      return rgb(r, g, b);
    } else {
      // [0, SINGLE_MAX_ACCEL] -> white to blue
      const t = a / SINGLE_MAX_ACCEL;
      const r = lerp(255, 0, t);
      const g = lerp(255, 0, t);
      const b = 255;
      return rgb(r, g, b);
    }
  }
}



function handleGPSData(gps: Events["gps-data"],
view: View,
source: VectorSource
) {
  if (!gps) throw new Error("Empty GPS update!");
  console.log("HELLO")

  const accelData: AccelData = {
    avg: avgAccel,
    ax: newx,
    ay: newy,
    az: newz,
  };
  
  const color = colorFromAccel(accelData, accelColorMode.value);
  
  segmentColors.value.push(color);
  segmentAccel.value.push(accelData);


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

  segmentColors.value = [];
  segmentAccel.value = [];

  // Clear caches
  for (const k in segmentColorCache) delete segmentColorCache[k];
  for (const k in segmentAccelCache) delete segmentAccelCache[k];
}



function handlePosUpdate(
  newIndex: Events["playback-update"],
  view: View,
  source: VectorSource
) {
  if (!newIndex) throw new Error("Index update to map was empty!");

  const targetIndex = newIndex.index;

  if (targetIndex < 0 || targetIndex >= coords.length) {
    throw new Error("Index update out of bounds");
  }

  if (coords[targetIndex] == null ||
      coords[targetIndex][0] === undefined ||
      coords[targetIndex][1] === undefined) {
    return;
  }

  // Update icon position
  curr.value = coords[targetIndex];

  // Special case for index 0
  if (targetIndex === 0) {
    path.value = [[coords[0]]];
    segmentColors.value = [];
    segmentAccel.value = [];
    i = 0;
    view.fit(source.getExtent(), { padding: [50, 50, 50, 50] });
    return;
  }

  const maxLen = maxPathLength.value;
  const startIndex = Math.max(0, targetIndex - maxLen);

  const newPath: [ [number, number], [number, number] ][] = [];
  const newColors: string[] = [];
  const newAccel: AccelData[] = [];

  // Build only the window [startIndex + 1, targetIndex]
  for (let j = startIndex + 1; j <= targetIndex; j++) {
    const c0 = coords[j - 1];
    const c1 = coords[j];
    if (!c0 || !c1) continue;

    // Get or compute per-segment accel
    let accel = segmentAccelCache[j];
    if (accel === undefined) {
      // First time we ever visit this segment: lock in the current accel
      accel = {
        avg: avgAccel,
        ax: newx,
        ay: newy,
        az: newz,
      };
      segmentAccelCache[j] = accel;
    }

    // Get or compute per-segment color
    let color = segmentColorCache[j];
    if (!color) {
      color = colorFromAccel(accel, accelColorMode.value);
      segmentColorCache[j] = color;
    }

    newPath.push([c0, c1]);
    newColors.push(color);
    newAccel.push(accel);
  }

  path.value = newPath;
  segmentColors.value = newColors;
  segmentAccel.value = newAccel;

  i = targetIndex;

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