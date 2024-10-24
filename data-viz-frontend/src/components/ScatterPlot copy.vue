<template>
  <Scatter :data="chartData" :options="options" />
</template>

<script lang="ts">
import { inject, ref, computed, onMounted } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { Events, ROTATION } from "../emitter-messages";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Scatter } from 'vue-chartjs';

// Register Chart.js components
ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export default {
  name: 'ScatterPlot',
  components: {
    Scatter
  },
  setup() {
    const emitter = inject(EMITTER_KEY);
    const pitch = ref(-1);
    const yaw = ref(-1);
    const rawData = ref([]);

    // Computed property for chart data to trigger reactivity
    const chartData = computed(() => ({
      datasets: [
        {
          label: 'Yaw vs. Pitch',
          backgroundColor: '#42A5F5',
          data: rawData.value // Reactively tracks rawData changes
        }
      ]
    }));

    onMounted(() => {
      if (!emitter) throw new Error("Toplevel failed to provide emitter");
      emitter.on(ROTATION, (e) => handleRotationUpdate(e));
    });

    function handleRotationUpdate(newRot: Events["rotation"]) {
      if (!newRot) throw new Error("rotation event is empty!");

      const newpitch = parseFloat(newRot["pitch"]);
      const newyaw = parseFloat(newRot["yaw"]);
      if (!isNaN(newpitch) && !isNaN(newyaw)) {
        pitch.value = newpitch;
        yaw.value = newyaw;

        // Update data and trigger reactivity
        console.log("going");
        rawData.value = [...rawData.value, { x: yaw.value, y: pitch.value }];

        // Limit to 100 data points
        if (rawData.value.length > 100) {
          rawData.value.shift(); // Remove the oldest point
        }
      }
    }

    return {
      chartData, // Expose computed chart data
    };
  },
  data() {
    return {
      options: {
        responsive: true,
        scales: {
          x: {
            type: 'linear',
            position: 'bottom',
            title: {
              display: true,
              text: 'Yaw'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Pitch'
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
};
</script>

<style scoped>
/* Add any specific styles if needed */
</style>
