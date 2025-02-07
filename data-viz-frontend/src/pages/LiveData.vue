<template>
  <div style="display: flex; flex-direction: column; height: 100vh;">
    <SignalSender></SignalSender>
    <h1>This is the new page!</h1>
    <router-link to="/">Go back to Home</router-link>
    
    <button @click="startNewSession">Start New Session</button>

    <!-- Checkboxes to Toggle Visibility -->
    <div>
      <label>
        <input type="checkbox" v-model="showScatterPlot" /> Show Scatter Plot (RPM vs RPM)
      </label>
      <label>
        <input type="checkbox" v-model="showAnotherScatter" /> Show Scatter Plot (RPM vs Ticks)
      </label>
      <label>
        <input type="checkbox" v-model="showMap" /> Show Map
      </label>
    </div>

    <!-- Conditional Rendering of Components -->
    <ScatterPlot v-if="showScatterPlot" :chartData="chartData" />
    <AnotherScatter v-if="showAnotherScatter" :chartData="chartDataRPMTicks" />

    <div v-if="showMap" style="flex-grow: 1; min-height: 400px;">
      <Map />
    </div>
  </div>
</template>

<script lang="ts">
import { PLAYBACK_UPDATE, GPS_DATA, RPM_DATA, SESSION_RESET } from "../emitter-messages";
import { ref, computed, onMounted, inject, watch } from 'vue';
import { EMITTER_KEY } from "../injection-keys";
import ScatterPlot from '../components/RPMvRPMScatterPlot.vue'; 
import AnotherScatter from '../components/RPMvTicksScatterPlot.vue';
import SignalSender from '../components/SignalSender.vue';
import Map from '../components/Map.vue';
import { saveAs } from 'file-saver';

export default {
  name: 'LiveData',
  components: {
    ScatterPlot,
    AnotherScatter,
    SignalSender,
    Map
  },
  setup() {
    const emitter = inject(EMITTER_KEY);
    const rawDataRPM1 = ref([]);
    const rawDataRPM2 = ref([]);
    const csvData = ref([]);
    const ticks = ref(0);

    // Toggle visibility states
    const showScatterPlot = ref(true);
    const showAnotherScatter = ref(true);
    const showMap = ref(true);

    const chartData = computed(() => ({
      datasets: [
        {
          label: 'RPM1',
          backgroundColor: '#42A5F5',
          borderColor: '#42A5F5',
          fill: false,
          data: rawDataRPM1.value
        },
        {
          label: 'RPM2',
          backgroundColor: '#FFA726',
          borderColor: '#FFA726',
          fill: false,
          data: rawDataRPM2.value
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
          data: rawDataRPM1.value.map((item) => ({ x: ticks.value, y: item.y }))
        },
        {
          label: 'RPM2 vs Ticks',
          backgroundColor: '#FFA726',
          borderColor: '#FFA726',
          fill: false,
          data: rawDataRPM2.value.map((item) => ({ x: ticks.value, y: item.y }))
        }
      ]
    }));

    const startNewSession = () => {
      saveCsv();
      rawDataRPM1.value = [];
      rawDataRPM2.value = [];
      csvData.value = [];
      ticks.value = 0;
      emitter?.emit(SESSION_RESET);
      console.log("New session started.");
    };

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

    const saveCsv = () => {
      const csvContent = 'data:text/csv;charset=utf-8,' +
        'RPM1,RPM2,Ticks,Latitude,Longitude \n' +
        csvData.value.map(e => e.join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, `data_${new Date().toISOString()}.csv`);
    };

    let socket;

    onMounted(() => {
      socket = new WebSocket("ws://localhost:8765");

      socket.onmessage = function(event) {
        const data = event.data.split(',');
        const [rpm1, rpm2, cordx, cordy, receivedTicks] = data.map(Number);

        if (!isNaN(rpm1) && !isNaN(rpm2) && !isNaN(receivedTicks) && !isNaN(cordx) && !isNaN(cordy)) {
          ticks.value = receivedTicks;


          if (showAnotherScatter.value || showScatterPlot.value) {
            emitRpmTick(emitter, rpm1, rpm2, receivedTicks)
          }

          if (showMap.value) {
            emitGPSCoordinates(emitter, cordx, cordy)
          }

          csvData.value.push([rpm1, rpm2, cordx, cordy, receivedTicks]);
        }
      };

      socket.onopen = () => console.log("WebSocket connection established.");
      socket.onclose = () => console.log("WebSocket connection closed.");
      socket.onerror = (error) => console.log("WebSocket error: ", error);
    });

    // Watch for changes in visibility and stop updates when hidden
    watch([showScatterPlot, showAnotherScatter, showMap], ([scatter, anotherScatter, map]) => {
      if (!scatter && !anotherScatter && !map) {
        console.log("No visualizations active, stopping data processing.");
        socket.close();
      } else if (!socket || socket.readyState === WebSocket.CLOSED) {
        console.log("Reconnecting WebSocket...");
        socket = new WebSocket("ws://localhost:8765");
      }
    });

    return {
      chartData,
      chartDataRPMTicks,
      startNewSession,
      rawDataRPM1,
      rawDataRPM2,
      csvData,
      ticks,
      showScatterPlot,
      showAnotherScatter,
      showMap
    };
  }
};
</script>
