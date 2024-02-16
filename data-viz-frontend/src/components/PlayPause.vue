<script setup lang="ts">
import { inject, ref } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { PLAYBACK_UPDATE } from "../emitter-messages";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faPlay, faPause } from "@fortawesome/free-solid-svg-icons";
import csv from "../assets/rc_30.csv"; // Annoying, VSCode will complain about this, but it works so hey

const emitter = inject(EMITTER_KEY);
const speed = ref(100);
const time = ref(100);

let play = ref(false);
let reverse = ref(false);
let i = 0;
let csv_length = csv.length-1;

// console.log(csv) // for debugging purposes, otherwise the contents of csv as an object are opaque

// Right now this is just grabbing from the test data, later should go to flask
function pubData(recursive = true) {
  if (i > csv_length) i = 0; // because we are using this only for teting
  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

  reverse.value = speed.value < 0;

  emitter.emit(PLAYBACK_UPDATE, {
    lat: csv[i]['Latitude|"Degrees"|-180.0|180.0|25'],
    lon: csv[i]['Longitude|"Degrees"|-180.0|180.0|25'],
    reversing: reverse.value,
  });
  
  

  if (!reverse.value) {
    i++;
    
  } else {
    i--;
    
    i = Math.max(i, 0);
  }
  
  if (recursive){
    time.value = i;
    waitThenPub();
  }
}

// Mutual recursion through setTimeout, needed to allow for control flow
function waitThenPub() {
  if (play.value) {
    reverse.value = (speed.value< 0);
    setTimeout(pubData, 200 - Math.abs(speed.value)); // So bar to the left is slower, right is faster
  }
}

// Each time button is pressed, serves as a restart and depends on boolean check in above
function toggleAndStartPub() {
  play.value = !play.value;

  waitThenPub();
}

function scrub(){
  play.value = false; //stop playing when touching scrub bar. Done to avoid any complications
  
  while (i!= time.value){
    console.log("hello", time.value);
    console.log(i);
    if(i > time.value){
      console.log("please reverse");
     
      reverse.value = true;
      pubData(false)
    }
    if(i<time.value){
      console.log("please go");
      
      reverse.value = false;
      pubData(false)
    }
  }
}
</script>

<template>
  <div id="playback">
    <label>Scrub a dub dub: {{ time/100 }} seconds</label>
    <input v-model="time" type="range" min="0" :max="csv_length" class="slider" @input="scrub"  />
    <label>Speed: x{{ speed/200 }}</label>
    
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
