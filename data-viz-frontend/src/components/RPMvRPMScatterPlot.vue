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
  name: 'ScatterPlot',
  components: {
    Scatter
  },
  setup() {
    const emitter = inject(EMITTER_KEY); // Inject the emitter
    const rawData = ref([]);  // Reactive data for the scatter plot

    // Reactive data for chart configuration
    const chartData = computed(() => ({
      datasets: [
        {
          label: 'RPM Data',
          backgroundColor: '#42A5F5',
          data: rawData.value // Reactive data binding
        }
      ]
    }));

    onMounted(() => {
      // Listen for SESSION_RESET event to reset rawData
      emitter?.on(SESSION_RESET, () => {
        resetData();
      });

      // Connect to the WebSocket server
      const socket = new WebSocket("ws://localhost:8765");

      // Handle incoming WebSocket messages
      socket.onmessage = function(event) {
        const data = event.data.split(',');  // Assuming CSV format
        const [rpm1, rpm2, ticks] = data.map(Number);  // Parse values as numbers

        if (!isNaN(rpm1) && !isNaN(rpm2)) {
          // Update the reactive rawData array
          rawData.value = [...rawData.value, { x: rpm1, y: rpm2 }];
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

    // Function to reset rawData
    const resetData = () => {
      rawData.value = []; // Clear the rawData array
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
              text: 'RPM1'
            }
          },
          y: {
            title: {
              display: true,
              text: 'RPM2'
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
