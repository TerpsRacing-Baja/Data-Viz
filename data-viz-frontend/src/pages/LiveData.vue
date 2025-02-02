<template>
  <div style="display: flex; flex-direction: column; height: 100vh;">
    <SignalSender></SignalSender>
    <h1>This is the new page!</h1>
    <router-link to="/">Go back to Home</router-link>
    
    <button @click="startNewSession">Start New Session</button>

    <ScatterPlot :chartData="chartData" />
    <AnotherScatter :chartData="chartDataRPMTicks" />

    <div style="flex-grow: 1; min-height: 400px;">
      <Map />
    </div>
  </div>
</template>


<script lang="ts">

import { PLAYBACK_UPDATE, GPS_DATA, Events, CAR_SPEED, ROTATION, RPM_DATA } from "../emitter-messages";
import { ref, computed, onMounted, inject } from 'vue';
import { EMITTER_KEY } from "../injection-keys"; // Import the emitter key
import { SESSION_RESET, RPM_DATA, GPS_POINT, GPS_DATA } from "../emitter-messages"; // Import the session reset message
import ScatterPlot from '../components/RPMvRPMScatterPlot.vue'; 
import AnotherScatter from '../components/RPMvTicksScatterPlot.vue';
import SignalSender from '../components/SignalSender.vue';
import Map from '../components/Map.vue'
import { saveAs } from 'file-saver'; // For saving CSV

//data sending functions
const emitter = inject(EMITTER_KEY);
onMounted(() => {  
  if (!emitter) throw new Error("Toplevel failed to provide emitter!"); // Error checking
});


function emitRpmTick(emitter , _rpm1: number, _rpm2: number, _tick: number){ 
  if (!emitter) throw new Error("Toplevel failed to provide emitter 2"); // Error checking
  // Emits the current speed to Speedometer.vue
  emitter.emit(RPM_DATA, {
    rpm1: _rpm1,
    rpm2: _rpm2,
    tick: _tick
  });
}


function emitGPSCoordinates(emitter, _latitude: number, _longitude: number) {
  if (!emitter) throw new Error("Toplevel failed to provide emitter 3"); // Error checking
  // Emits the current GPS coordinates to Map.vue
  emitter.emit(GPS_DATA, {
    point: [_latitude, _longitude]
  });
}


//reading and sending data
export default {
  name: 'LiveData',
  components: {
    ScatterPlot,
    AnotherScatter,
    SignalSender,
    Map
  },
  setup() {
    const emitter = inject(EMITTER_KEY); // Inject the emitter
    const rawDataRPM1 = ref([]); // Data for RPM1
    const rawDataRPM2 = ref([]); // Data for RPM2
    const csvData = ref([]); // Data to save in CSV
    const ticks = ref(0); // Track ticks

    // Reactive data for chart configurations
    const chartData = computed(() => ({
      datasets: [
        {
          label: 'RPM1',
          backgroundColor: '#42A5F5',
          borderColor: '#42A5F5',
          fill: false,
          data: rawDataRPM1.value // RPM1 data vs RPM2
        },
        {
          label: 'RPM2',
          backgroundColor: '#FFA726',
          borderColor: '#FFA726',
          fill: false,
          data: rawDataRPM2.value // RPM2 data vs RPM1
        }
      ]
    }));

    const chartDataRPMTicks = computed(() => ({
      datasets: [
        {
          label: 'RPM1 vs Ticks',
          backgroundColor: '#42A5F5',
          borderColor: '#42A5F5',
          fill: false,
          data: rawDataRPM1.value.map((item) => ({ x: ticks.value, y: item.y })) // RPM1 vs ticks
        },
        {
          label: 'RPM2 vs Ticks',
          backgroundColor: '#FFA726',
          borderColor: '#FFA726',
          fill: false,
          data: rawDataRPM2.value.map((item) => ({ x: ticks.value, y: item.y })) // RPM2 vs ticks
        }
      ]
    }));

    // Function to start a new session, clear the chart and save the current CSV data
    const startNewSession = () => {
      // Save the current data as CSV before clearing
      saveCsv();

      // Clear the data for charts
      rawDataRPM1.value = [];
      rawDataRPM2.value = [];
      csvData.value = [];
      ticks.value = 0; // Reset ticks

      // Emit the session reset event
      emitter?.emit(SESSION_RESET); // Emit SESSION_RESET to notify other components
    };



    // Save the CSV data to a file
    const saveCsv = () => {
      const csvContent = 'data:text/csv;charset=utf-8,'
        + 'RPM1,RPM2,Ticks,Latitude,Longitude \n' // CSV headers
        + csvData.value.map(e => e.join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, `data_${new Date().toISOString()}.csv`);
    };

    // WebSocket connection to receive rpm1, rpm2, and ticks
    onMounted(() => {
      const socket = new WebSocket("ws://localhost:8765");

      socket.onmessage = function(event) {
        
        const data = event.data.split(','); // Assuming data format is rpm1, rpm2, ticks

        //console.log(data)
        const [rpm1, rpm2, cordx, cordy,receivedTicks] = data.map(Number); // Parse values as numbers
        //console.log(receivedTicks)
        //console.log(cordx, cordy)

        if (!isNaN(rpm1) && !isNaN(rpm2) && !isNaN(receivedTicks) && !isNaN(cordx) && !isNaN(cordy)) {//TODO: Update this in the future to handle data that is bad
          ticks.value = receivedTicks;
          console.log(ticks.value)

          // Add new points to the data
          rawDataRPM1.value.push({ x: receivedTicks, y: rpm1 });
          rawDataRPM2.value.push({ x: receivedTicks, y: rpm2 });

          // Save the new values for CSV

          csvData.value.push([rpm1, rpm2, cordx, cordy, receivedTicks]);

          emitRpmTick(emitter, rpm1, rpm2, receivedTicks)

          emitGPSCoordinates(emitter, cordx, cordy)

        }
      };

      socket.onopen = () => {
        console.log("WebSocket connection established.");
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };

      socket.onerror = (error) => {
        console.log("WebSocket error: ", error);
      };
    });

    return {
      chartData,
      chartDataRPMTicks,
      startNewSession,
      rawDataRPM1,
      rawDataRPM2,
      csvData,
      ticks
    };
  }
};
</script>
