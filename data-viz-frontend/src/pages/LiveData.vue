<template>
  <div>
    <h1>This is the new page!</h1>
    <router-link to="/">Go back to Home</router-link>
    
    <!-- Button to reset the chart and start a new CSV -->
    <button @click="startNewSession">Start New Session</button>

    <ScatterPlot :chartData="chartData" /> <!-- Pass chartData prop for RPM vs RPM -->
    <AnotherScatter :chartData="chartDataRPMTicks" /> <!-- Pass chartData prop for RPM vs Ticks -->
  </div>
</template>

<script lang="ts">
import { ref, computed, onMounted, inject } from 'vue';
import { EMITTER_KEY } from "../injection-keys"; // Import the emitter key
import { SESSION_RESET } from "../emitter-messages"; // Import the session reset message
import ScatterPlot from '../components/RPMvRPMScatterPlot.vue'; 
import AnotherScatter from '../components/RPMvTicksScatterPlot.vue';
import { saveAs } from 'file-saver'; // For saving CSV

export default {
  name: 'LiveData',
  components: {
    ScatterPlot,
    AnotherScatter,
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
        + 'RPM1,RPM2,Ticks\n' // CSV headers
        + csvData.value.map(e => e.join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, `data_${new Date().toISOString()}.csv`);
    };

    // WebSocket connection to receive rpm1, rpm2, and ticks
    onMounted(() => {
      const socket = new WebSocket("ws://localhost:8765");

      socket.onmessage = function(event) {
        const data = event.data.split(','); // Assuming data format is rpm1, rpm2, ticks
        const [rpm1, rpm2, receivedTicks] = data.map(Number); // Parse values as numbers

        if (!isNaN(rpm1) && !isNaN(rpm2) && !isNaN(receivedTicks)) {
          ticks.value = receivedTicks;

          // Add new points to the data
          rawDataRPM1.value.push({ x: ticks.value, y: rpm1 });
          rawDataRPM2.value.push({ x: ticks.value, y: rpm2 });

          // Save the new values for CSV
          csvData.value.push([rpm1, rpm2, ticks.value]);
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
