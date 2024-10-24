<!-- RPMvTicks -->
<template>
  <Scatter :data="chartData" :options="options" />
</template>

<script lang="ts">
import { ref, computed, onMounted, inject } from "vue";
import { Scatter } from 'vue-chartjs';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';
import { EMITTER_KEY } from "../injection-keys"; // Import the emitter key
import { SESSION_RESET } from "../emitter-messages"; // Import the session reset message

// Register the necessary Chart.js components
ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export default {
  name: 'RPMGraph',
  components: {
    Scatter
  },
  setup() {
    const emitter = inject(EMITTER_KEY); // Inject the emitter
    const rawDataRPM1 = ref([]);  // Data for RPM1
    const rawDataRPM2 = ref([]);  // Data for RPM2
    const ticks = ref(0);  // Time or ticks

    // Reactive data for chart configuration
    const chartData = computed(() => ({
      datasets: [
        {
          label: 'RPM1',
          backgroundColor: '#42A5F5',
          borderColor: '#42A5F5',
          fill: false,
          data: rawDataRPM1.value // RPM1 data vs ticks
        },
        {
          label: 'RPM2',
          backgroundColor: '#FFA726',
          borderColor: '#FFA726',
          fill: false,
          data: rawDataRPM2.value // RPM2 data vs ticks
        }
      ]
    }));

    onMounted(() => {
      // Listen for SESSION_RESET event to reset graph data
      emitter?.on(SESSION_RESET, () => {
        resetGraphData();
      });

      // Connect to the WebSocket server
      const socket = new WebSocket("ws://localhost:8765");

      // Handle incoming WebSocket messages
      socket.onmessage = function(event) {
        const data = event.data.split(',');  // Assuming CSV format
        const [rpm1, rpm2, receivedTicks] = data.map(Number);  // Parse values as numbers

        if (!isNaN(rpm1) && !isNaN(rpm2)) {
          // Increment the tick
          ticks.value = receivedTicks;  // Update the ticks ref

          // Add new points to both datasets
          rawDataRPM1.value = [...rawDataRPM1.value, { x: ticks.value, y: rpm1 }];
          rawDataRPM2.value = [...rawDataRPM2.value, { x: ticks.value, y: rpm2 }];
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

    // Function to reset graph data
    const resetGraphData = () => {
      rawDataRPM1.value = [];
      rawDataRPM2.value = [];
      ticks.value = 0; // Reset ticks
    };

    return {
      chartData,  // Expose reactive chartData to the template
      options: {
        responsive: true,
        scales: {
          x: {
            type: 'linear',
            position: 'bottom',
            title: {
              display: true,
              text: 'Ticks'
            }
          },
          y: {
            title: {
              display: true,
              text: 'RPM'
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          }
        }
      }
    };
  }
}
</script>
