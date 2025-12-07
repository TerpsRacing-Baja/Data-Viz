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
import { SESSION_RESET, PLOT_POINT } from "../emitter-messages"; // Import the session reset message

// Register the necessary Chart.js components
ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export default {
  name: 'Custom Plot',
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
          label: 'Data',
          backgroundColor: rawData.value.map((_, index) => {
            const totalPoints = rawData.value.length;
            const lastPoints = 30; // Number of points for gradient fade-out
            const recentHighlight = 5; // The most recent points to highlight distinctly

            if (index >= totalPoints - recentHighlight) {
              return '#8B0000'; // Dark Red for last 5 points
            } else if (index < totalPoints - lastPoints) {
              return '#D3D3D3'; // Older points stay light grey
            } else {
              // Compute gradient color from black (#000000) to light grey (#D3D3D3)
              const ratio = (index - (totalPoints - lastPoints)) / lastPoints; // Normalize between 0 and 1
              const gray = Math.round(0 + (211 - 0) * ratio); // 0 is black, 211 is light grey
              return `rgb(${gray},${gray},${gray})`; // Smooth transition from black to light grey
            }

          }),
            
          data: rawData.value // Reactive data binding
          
        }
      ]
    }));

    // Function to update the graph with incoming event data
    function updateGraph(newVals: Events["plot-point"]) {
      if (!newVals) throw new Error("Received RPM data was empty!");

      const _x = parseFloat(newVals["xPoint"]);
      const _y = parseFloat(newVals["yPoint"]);
      

      // Update the reactive rawData array with new values
      rawData.value = [...rawData.value, { x: _x, y: _y }];
    }

    onMounted(() => {
      if (!emitter) throw new Error("Toplevel failed to provide emitter");

      // Listen for SESSION_RESET event to reset rawData
      emitter?.on(SESSION_RESET, () => {
        resetData();
      });

      // Listen for RPM_DATA event to update the graph
      emitter.on(PLOT_POINT, (e) => updateGraph(e));
    });

    // Function to reset rawData
    const resetData = () => {
      console.log("Custom data has reset")
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
              text: 'Tick'
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
        },
        //animation: rawDataRPM1.value.length > 30 ? false : {
        //  duration: 200,  // Keep animation for small datasets
        //  easing: 'easeOutQuad',
        //}
        animation: false,
      }
    };
  }
}
</script>
