<script setup lang="ts">
import { inject, onMounted, ref } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { PLAYBACK_UPDATE, GPS_DATA, CSV_FILE, Events } from "../emitter-messages";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faPlay, faPause } from "@fortawesome/free-solid-svg-icons";
//import csv from "../assets/rc_30.csv"; // Annoying, VSCode will complain about this, but it works so hey


const emitter = inject(EMITTER_KEY);
const speed = ref(100);
const time = ref(0);
const path = "../assets/";

let file_chosen = ref(false);
let csv = ref("");
let play = ref(false);
let reverse = ref(false);
let i = 0;
let csv_length = ref(-1)
//let csv_length = csv.length - 1;

onMounted(() => {  
  // let coords: [number, number][] = [];

  // for (let j = 0; j < csv.length; j++) {
  //   coords.push([
  //     csv[j]['Longitude|"Degrees"|-180.0|180.0|25'],
  //     csv[j]['Latitude|"Degrees"|-180.0|180.0|25'],
  //   ]);
  // }

  // emitter?.emit(GPS_DATA, { coords: coords });
  // emitter?.emit(PLAYBACK_UPDATE, { index: 0 }); // centers view on first index. view.fit will complain but this works
  emitter.on(CSV_FILE, (e) => handleCSV(e));

});

// console.log(csv) // for debugging purposes, otherwise the contents of csv as an object are opaque

async function extractFromCSV() {
  console.log("Extracting data from CSV");
  const data_module = await import(csv.value)
  const data_csv = data_module.default;
  csv_length.value = data_csv.length;
  let coords: [number, number][] = [];

  for (let j = 0; j < csv_length.value; j++) {
    coords.push([
      data_csv[j]['Longitude|"Degrees"|-180.0|180.0|25'],
      data_csv[j]['Latitude|"Degrees"|-180.0|180.0|25'],
    ]);
  }

  // for(let k = 0; k < csv_length.value; k++) {
  //   console.log(data_csv[k]);
  // }

emitter?.emit(GPS_DATA, { coords: coords });
emitter?.emit(PLAYBACK_UPDATE, { index: 0 }); // centers view on first index. view.fit will complain but this works
}

function iterateAndPub() {
  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  // so that 0 goes out at the beginning
  emitter.emit(PLAYBACK_UPDATE, {
    index: i,
  });

  time.value = i;

  // controls direction of index change
  reverse.value = speed.value < 0;

  // change index accordingly
  if (reverse.value) i--;
  else i++;

  // this could also wrap around, but caps make things easier, kind of make more sense in the context of playback
  if (i >= csv_length.value) i = csv_length.value - 1;
  if (i < 0) i = 0;

  waitThenPub();
}

// Mutual recursion through setTimeout, needed to allow for control flow
function waitThenPub() {
  if (play.value) {
    // If speed is not 0, go pub with appropriate delay, but if it is periodically check until it changes
    // The delay on the else is required to avoid overloading browser with recursive calls
    if (speed.value != 0)
      setTimeout(iterateAndPub, 200 - Math.abs(speed.value));
    else setTimeout(waitThenPub, 100);
  }
}

// Each time button is pressed, serves as a restart and depends on boolean check in above
function toggleAndStartPub() {
  if(file_chosen.value){
    play.value = !(play.value);
    if(play.value) {
      console.log("Starting playback with file " + csv.value);
      extractFromCSV();
      waitThenPub();
    }
  } else {
    console.log("File not chosen yet!");
  }
}

function scrub() {
  play.value = false; //stop playing when touching scrub bar due to odd behavior

  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  emitter.emit(PLAYBACK_UPDATE, {
    index: Math.max(time.value, 0),
  });

  i = time.value;
}

function handleCSV(
    chosenCSV: Events["csv-file"]
  ){
    if (chosenCSV == null) throw new Error("No CSV file chosen!");
    csv.value = path + chosenCSV.file_name;
    file_chosen.value = true;
    console.log("PlaybackControl.vue recieved emission of CSV file " + csv.value);
    if(play.value) {
      toggleAndStartPub(); // Essentially pauses the playing of the visualization
    }
  }
</script>

<template>
  <div id="playback">
    <label>Scrub a dub dub: {{ time / 2.5 }} seconds</label>
    <input
      v-model="time"
      type="range"
      min="1"
      :max="csv_length"
      class="slider"
      @input="scrub"
    />
    <label>Speed: x{{ speed / 200 }}</label>

    <input v-model="speed" type="range" min="-200" max="200" class="slider" />

    <button @click="toggleAndStartPub()">
      <font-awesome-icon :icon="play ? faPause : faPlay"></font-awesome-icon>
    </button>
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
