<template>
  <div style="display: flex; flex-direction: column; height: 100vh;">
    <SignalSender></SignalSender>
    <h1>This is the new page!</h1>
    <router-link to="/">Go back to Home</router-link>
    <button @click="startNewSession">Start New Session</button>
    <button @click="retryConnection">Retry Connection</button>

    <!-- Expandable Section for Custom Plot Settings -->
    <details>
      <summary>Custom Plot Settings</summary>
      <div>
        <label>
          <input type="checkbox" v-model="showScatterPlot" /> Show Scatter Plot (RPM vs RPM)
        </label>
        <label>
          <input type="checkbox" v-model="showAnotherScatter" /> Show Scatter Plot (RPM vs Ticks)
        </label>
        <label>
          <input type="checkbox" v-model="showCustom" /> Show Custom Plot
        </label>
        <label>
          <input type="checkbox" v-model="showMap" /> Show Map
        </label>
        <br>
        <label>
          Custom X Column Index:
          <input type="number" v-model.number="customXCol" />
        </label>
        <label>
          Custom Y Column Index:
          <input type="number" v-model.number="customYCol" />
        </label>
      </div>
    </details>

    <!-- Conditional Rendering of Components -->
    <ScatterPlot v-if="showScatterPlot" :chartData="chartData" />
    <AnotherScatter v-if="showAnotherScatter" :chartData="chartDataRPMTicks" />
    <CustomPlot v-if="showCustom" :xCol="customXCol" :yCol="customYCol" />
    <div v-if="showMap" style="flex-grow: 1; min-height: 400px;">
      <Map />
    </div>
  </div>
</template>

<script lang="ts">
import { PLAYBACK_UPDATE, GPS_DATA, RPM_DATA, SESSION_RESET, PLOT_POINT } from "../emitter-messages";
import { ref, computed, onMounted, inject, watch } from 'vue';
import { EMITTER_KEY } from "../injection-keys";
import ScatterPlot from '../components/RPMvRPMScatterPlot.vue'; 
import AnotherScatter from '../components/RPMvTicksScatterPlot.vue';
import SignalSender from '../components/SignalSender.vue';
import CustomPlot from '../components/CustomPlot.vue';
import Map from '../components/Map.vue';
import { saveAs } from 'file-saver';

export default {
  name: 'LiveData',
  components: {
    ScatterPlot,
    AnotherScatter,
    SignalSender,
    CustomPlot,
    Map
  },
  setup() {
    const emitter = inject(EMITTER_KEY);
    const rawDataRPM1 = ref([]);
    const rawDataRPM2 = ref([]);
    const csvData = ref([]);
    const ticks = ref(0);

    // Toggle visibility states
    const showScatterPlot = ref(false);
    const showAnotherScatter = ref(false);
    const showMap = ref(false);
    const showCustom  = ref(false);
    const customXCol = ref(1);
    const customYCol = ref(2);

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
    
    function emitCustomPlotPoint(emitter, _x: number, _y: number) {
      if (!emitter) throw new Error("Toplevel failed to provide emitter 4"); // Error checking
      // Emits the current speed to Speedometer.vue
      console.log("sending data to custom plot")
      emitter.emit(PLOT_POINT, {
        xPoint: _x,
        yPoint: _y
      });
    }

    function emitGPSCoordinates(emitter, _latitude: number, _longitude: number) {
      if (!emitter) throw new Error("Toplevel failed to provide emitter 3"); // Error checking
      // Emits the current GPS coordinates to Map.vue
      console.log(_latitude, _longitude)
      emitter.emit(GPS_DATA, {
        point: [_latitude, _longitude]
      });
    }

    function saveCsv() {
      if (csvData.value.length === 0) return;

      const headers = Object.keys(csvData.value[0]).join(',');
      const csvContent = 
        headers + '\n' +
        csvData.value.map(e => Object.values(e).join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, `data_${new Date().toISOString()}.csv`);
    }

    let socket;
    onMounted(() => {
      connectWebSocket();
    });

    const connectWebSocket = () => {
      socket = new WebSocket("ws://localhost:8765");
      const iRpm1 = 0
      const iRpm2 = 1
      const iCordx = 2
      const iCordy = 3
      const iTicks = 4 

      socket.onmessage = function(event) {
        const data = event.data.split(',');
        const dataNum = data.map(Number);

        if (!isNaN(dataNum[iRpm1]) && !isNaN(dataNum[iRpm2]) && !isNaN(dataNum[iTicks]) && !isNaN(dataNum[iCordx]) && !isNaN(dataNum[iCordy])) {
          ticks.value = dataNum[iTicks];

          if (showAnotherScatter.value || showScatterPlot.value) {
            emitRpmTick(emitter, dataNum[iRpm1], dataNum[iRpm2], dataNum[iTicks])
          }

          if (showMap.value) {
            emitGPSCoordinates(emitter, dataNum[iCordx], dataNum[iCordy])
          }

          if (showCustom.value) {
            emitCustomPlotPoint(emitter, dataNum[customXCol.value], dataNum[customYCol.value])
          }

          const dataObj = dataNum.reduce((acc, value, index) => {
            acc[`col${index}`] = value;
            return acc;
          }, {});

          csvData.value.push(dataObj);
        }
      };

      socket.onopen = () => console.log("WebSocket connection established.");
      socket.onclose = () => console.log("WebSocket connection closed.");
      socket.onerror = (error) => console.log("WebSocket error: ", error);
    };

    const retryConnection = () => {
      if (socket) {
        socket.close();
      }
      connectWebSocket();
    };

    return {
      retryConnection,
      chartData,
      chartDataRPMTicks,
      startNewSession,
      rawDataRPM1,
      rawDataRPM2,
      csvData,
      ticks,
      showScatterPlot,
      showAnotherScatter,
      showMap,
      showCustom,
      customXCol,
      customYCol
    };
  }
};
</script>