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
import { SESSION_RESET, RPM_DATA } from "../emitter-messages"; // Import the session reset message

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

    // Function to update the graph with incoming event data
    function updateGraph(newVals: Events["rpm-data"]) {
      if (!newVals) throw new Error("Received RPM data was empty!");

      const rpm1 = parseFloat(newVals["rpm1"]);
      const rpm2 = parseFloat(newVals["rpm2"]);
      const tick = parseFloat(newVals["tick"]);

      // Update the reactive rawData array with new values
      rawData.value = [...rawData.value, { x: rpm1, y: rpm2 }];
    }

    onMounted(() => {
      if (!emitter) throw new Error("Toplevel failed to provide emitter");

      // Listen for SESSION_RESET event to reset rawData
      emitter?.on(SESSION_RESET, () => {
        resetData();
      });

      // Listen for RPM_DATA event to update the graph
      emitter.on(RPM_DATA, (e) => updateGraph(e));
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
        //animation: {
        //  duration: 100,  // Reduce this value for faster animation (default is 1000ms)
         // easing: 'easeOutQuad',  // Adjust the easing for different animations (optional)
        //}
        animation: false,
      }
    };
  }
}
</script>
