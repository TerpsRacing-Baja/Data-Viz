<script setup lang="ts">
import { inject, onMounted, ref } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { PLAYBACK_UPDATE, GPS_DATA, CSV_FILE, Events, CAR_SPEED } from "../emitter-messages";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faPlay, faPause } from "@fortawesome/free-solid-svg-icons";


const emitter = inject(EMITTER_KEY);
const speed = ref(100);
const time = ref(0);
const path = "../assets/";

let file_chosen = ref(false);
let csv = ref("");
let play = ref(false);
let reverse = ref(false);
let i: number = 0;
let map_index: number = 0;
let csv_length = ref(-1)
let coords: [number, number][] = [];
let data_csv = ref();

// onMounted constantly checks for a CSV file name delivered by CSVPicker.vue
onMounted(() => {  
  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking
  emitter.on(CSV_FILE, (e) => handleCSV(e));
});

async function extractFromCSV() {
  console.log("Extracting data from CSV");
  const data_module = await import(csv.value) // Dynamically imports csv filename into csv.value
  coords = []
  i = 0;
  time.value=0;
  data_csv.value = data_module.default;
  csv_length.value = data_csv.value.length;
  for (let j = 0; j < csv_length.value; j++) { // Populated 'coords' array with GPS coordinates
      if (
      data_csv.value[j]['Longitude|Degrees|-180.0|180.0|25'] !== 0 &&
      data_csv.value[j]['Longitude|Degrees|-180.0|180.0|25'] !== "0.0" &&
      data_csv.value[j]['Longitude|Degrees|-180.0|180.0|25'] !== '' &&
      data_csv.value[j]['Latitude|Degrees|-180.0|180.0|25'] !== 0 &&
      data_csv.value[j]['Latitude|Degrees|-180.0|180.0|25'] !== '0.0' &&
      data_csv.value[j]['Latitude|Degrees|-180.0|180.0|25'] !== ''
    ) {
      coords.push([
        data_csv.value[j]['Longitude|Degrees|-180.0|180.0|25'],
        data_csv.value[j]['Latitude|Degrees|-180.0|180.0|25'],
      ]);
    }

  }

  emitter?.emit(GPS_DATA, { coords: coords }); // Sends coords thru emitter to Map.vue
  try {
    emitter?.emit(PLAYBACK_UPDATE, { index: 0 });//centers view on first index. view.fit will complain but this works
  } catch (error) {console.error("Cannot fit empty extent provided as `geometry`")}
}

function getMapIndex(current_time: number, target_time: number) {
  // console.log(current_time)
  //console.log(target_time)
  while(current_time!=target_time){
    let downflag: boolean = false;
    if(current_time>target_time){
      current_time--;
      downflag = true;
    }
    if(current_time<target_time){
      current_time++;
    }

    if (
      data_csv.value[current_time]['Longitude|Degrees|-180.0|180.0|25'] !== 0 &&
      data_csv.value[current_time]['Longitude|Degrees|-180.0|180.0|25'] !== "0.0" &&
      data_csv.value[current_time]['Longitude|Degrees|-180.0|180.0|25'] !== '' &&
      data_csv.value[current_time]['Latitude|Degrees|-180.0|180.0|25'] !== 0 &&
      data_csv.value[current_time]['Latitude|Degrees|-180.0|180.0|25'] !== '0.0' &&
      data_csv.value[current_time]['Latitude|Degrees|-180.0|180.0|25'] !== ''
    ) {
      
      if(downflag){
        map_index--;
      }else{
        map_index++;
      }
    }
  }
  //console.log(map_index);

  return map_index;
  
 // console.log(data_csv.value[current_time]['Longitude|Degrees|-180.0|180.0|25'])
<<<<<<< Updated upstream
  
=======
}

//SingleEmit is a function that should only be called once when advancing or at the end of scrubbing.
//This si used to emit items that only need to be updated once, unlike scrub (used for updating the nodes on the map) which updates multiple times when scrubbing.
function singleEmit(index: number){ 
  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking
  // Emits the current speed to Speedometer.vue
  emitter.emit(CAR_SPEED, {
    velocity: data_csv.value[index]['Speed|mph|0.0|150.0|25']
  });
  emitter.emit(ROTATION,{
    pitch: data_csv.value[index]['Euler Pitch'],
    yaw: data_csv.value[index]['Euler Yaw'],
    roll: 1
  })
>>>>>>> Stashed changes
}

function iterateAndPub() {
  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  // so that 0 goes out at the beginning
  emitter.emit(PLAYBACK_UPDATE, {
    index: getMapIndex(time.value, i),
  });
  
  // Emits the current speed to Speedometer.vue
  emitter.emit(CAR_SPEED, {
    velocity: data_csv.value[i]['Speed|mph|0.0|150.0|25']
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
  if (!document) throw new Error("document is missing emitter"); // Error checking

  const fileChosenElement = document.getElementById("fileChosenText");
  const fileChosenValue = file_chosen.value;

  if (fileChosenElement && fileChosenValue !== null && fileChosenValue !== undefined) {
    if (fileChosenValue) {
      fileChosenElement.style.display = "none";
      play.value = !play.value;
      if (play.value) {
        console.log("Starting playback with file " + csv.value);
        // extractFromCSV();
        waitThenPub();
      }
    } else {
      fileChosenElement.style.display = "block";
    }
  }
}

// Scrubber that allows user traversal thru the visualization
function scrub() {
  play.value = false; //stop playing when touching scrub bar due to odd behavior

  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  emitter.emit(PLAYBACK_UPDATE, {
    index: Math.max(getMapIndex(i, time.value), 0),
  });

  i = time.value;

  emitter.emit(CAR_SPEED, {
    velocity: data_csv.value[i]['Speed|mph|0.0|150.0|25'],
  });
}

/* Handles the emitter sending a CSV file from CSVPicker.vue - note that CSVPicker.vue handles verification
   that the file is a CSV, but neither file ensures that it is a properly formatted CSV. */ 
function handleCSV(
    chosenCSV: Events["csv-file"]
  ){
    if (chosenCSV == null) throw new Error("No CSV file chosen!");
    csv.value = path + chosenCSV.file_name;
    file_chosen.value = true;
    console.log("PlaybackControl.vue recieved emission of CSV file " + csv.value);
    if(play.value) {
      play.value = false; // pauses the playing of the visualization if a new CSV is chosen while the visualization is playing
    }
    extractFromCSV();
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

    <label>Speed: x{{ speed/200 }}</label>
    <input v-model="speed" type="range" min="-200" max="200" class="slider" />

    <button @click="toggleAndStartPub()">
      <font-awesome-icon :icon="play ? faPause : faPlay"></font-awesome-icon>
    </button>
    <div id="fileChosenText" style="display: none;">File not chosen!</div>

  </div>
</template>

<style scoped>
#playback {
  width: 100%; /* Ensure the playback bar takes up the full width allocated to it */
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
