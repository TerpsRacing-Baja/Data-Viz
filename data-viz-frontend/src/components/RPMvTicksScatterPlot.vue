<template>
  <Line :data="chartData" :options="options" />
</template>

<script lang="ts">
import { ref, computed, onMounted, inject } from "vue";
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';
import { EMITTER_KEY } from "../injection-keys"; // Import the emitter key
import { SESSION_RESET, RPM_DATA } from "../emitter-messages"; // Import event messages

// Register the necessary Chart.js components
ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export default {
  name: 'RPMGraph',
  components: {
    Line // Update to use the 'Line' component for a line chart
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
          fill: false,  // Line without filling
          data: rawDataRPM1.value // RPM1 data vs ticks
        },
        {
          label: 'RPM2',
          backgroundColor: '#FFA726',
          borderColor: '#FFA726',
          fill: false,  // Line without filling
          data: rawDataRPM2.value // RPM2 data vs ticks
        }
      ]
    }));

    // Listen for events and update the graph data accordingly
    onMounted(() => {
      if (!emitter) throw new Error("Toplevel failed to provide emitter");

      // Listen for SESSION_RESET event to reset graph data
      emitter.on(SESSION_RESET, () => {
        resetGraphData();
      });

      // Listen for RPM_DATA event to update the graph with new values
      emitter.on(RPM_DATA, (data: { rpm1: number, rpm2: number, tick: number }) => {
        updateGraph(data);
      });
    });

    // Function to update the graph with incoming event data
    function updateGraph(newVals: { rpm1: number, rpm2: number, tick: number }) {
      if (!newVals) throw new Error("Received RPM data was empty!");

      const { rpm1, rpm2, tick } = newVals;

      // Update the reactive rawData arrays with new values
      rawDataRPM1.value = [...rawDataRPM1.value, { x: tick, y: rpm1 }];
      rawDataRPM2.value = [...rawDataRPM2.value, { x: tick, y: rpm2 }];
    }

    // Function to reset graph data
    const resetGraphData = () => {
      console.log("RPMvTicks has reset")
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
        },
        //animation: {
         // duration: 200,  // Reduce this value for faster animation (default is 1000ms)
          //easing: 'easeOutQuad',  // Adjust the easing for different animations (optional)
        //}
        animation: false, // Disable animation
      }
    };
  }
}
</script>
