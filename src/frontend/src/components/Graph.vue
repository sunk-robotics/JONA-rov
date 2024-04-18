<template>
    <div class="graph">
        <Chart type="line" :data="chartData" :options="chartOptions" class="h-30rem" :plugins="[plugin]" :style="'width:100%;'"/>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Chart from "primevue/chart"
import { useSensorDataStore, type SensorData } from "@/stores/sensorData";

const sensorData = useSensorDataStore()

const { field, range, header } = defineProps<{ field: Field, header: string, range: [number, number]}>()
type Field = keyof SensorData

onMounted(() => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
});

const chartData = ref();
const chartOptions = ref();

    
let history: { data: SensorData[keyof SensorData ], timestamp: number }[] = []
const setChartData = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    
    let xAxis = history.map(({ timestamp }) => timestamp)
    let yAxis = history.map(({ data }) => data)

    return {
        labels: xAxis,
        datasets: [{
            label: header,
            data: yAxis,
            fill: false,
            borderColor: "grey",
            tension: 0.4,
        }]
    };
};
const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = "red";
    const textColorSecondary = "white";
    const surfaceBorder = "black";

    return {
        maintainAspectRatio: false,
        // aspectRatio: 0.6,
        
        scales: {
            x: {
                ticks: {
                    color: textColorSecondary
                },
                grid: {
                    color: surfaceBorder
                }
            },
            y: {
                grid: {
                    color: surfaceBorder
                },
                min: range[0],
                max: range[1]
            }
        },
        plugins: {
            customCanvasBackgroundColor: {
                color: 'rgb(51, 51, 51)',
            },
            legend: {
                labels: {
                    color: "white"
                }
            }
        },
        animation: {
            duration: 0
        },
        responsive: true
    };
}

let curr_sec = 0
setInterval(() => {
    let data = sensorData.get(field)
    history.push({ data, timestamp: curr_sec })
    chartData.value = setChartData()
    if (history.length > 10) history.shift();
    curr_sec += 0.5
}, 500)

const plugin = {
  id: 'customCanvasBackgroundColor',
  beforeDraw: (chart: any, args: any, options: any) => {
    const {ctx} = chart;
    ctx.save();
    ctx.globalCompositeOperation = 'destination-over';
    ctx.fillStyle = options.color || '#99ffff';
    ctx.fillRect(0, 0, chart.width, chart.height);
    ctx.restore();
  }
};
</script>

<style scoped>

    .graph {
        width: 100%;
        display: flex;
        justify-content: center;
    }

</style>