<script setup lang="ts">
import { onMounted, ref, type Ref } from 'vue';
import SensorData from './SensorData.vue';
import { useSensorDataStore } from '@/stores/sensorData';
const sensorData = useSensorDataStore()


const X_SIZE = 50;
const Y_SIZE = 50;

type SensorData = {
    internal_temp: number | null,
    external_temp: number | null,
    temp: number | null,
    depth: number | null,
    yaw: number | null,
    roll: number | null,
    pitch: number | null,
    voltage_5V: number | null,
    current_5V: number | null,
    voltage_12V: number | null,
    current_12V: number | null,
    x_accel: number | null,
    y_accel: number | null,
    z_accel: number | null,
    speed_multiplier: number | null,
    depth_anchor_enabled: boolean | null,
    yaw_anchor_enabled: boolean | null,
    roll_anchor_enabled: boolean | null,
    pitch_anchor_enabled: boolean | null,
    motor_lock_enabled: boolean | null
}

let history: { timestamp: number, val: number }[] = [];
const { field, header, range } = defineProps<{ field: keyof SensorData, header: string, range: [number, number] }>()
let ctx: CanvasRenderingContext2D | undefined = undefined;

const graph = ref<HTMLCanvasElement | null>(null)
onMounted(() => {
    graph.value?.focus()
    ctx = graph.value?.getContext("2d")!
    console.log("mounting");
    ctx!.strokeStyle = "black"
})

let curr_sec = 0;
setInterval(() => {
    if (ctx) {
        history.push({ timestamp: curr_sec, val: sensorData.get(field) as number })
        drawGraph()
    }
    curr_sec += 0.5
}, 500)

function drawGraph() {
    ctx?.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)

    let his_slice = history.length >= 5 ? history.slice(-5) : history;

    let x_pos = 20
    const hScalar = (range[1] - range[0]) / 5

    for (const { timestamp, val } of his_slice) {
        ctx?.lineTo(x_pos, ctx.canvas.height - 21 - (val * 7))
        ctx?.stroke()
        ctx?.fillText(timestamp.toString(), x_pos, ctx.canvas.height - 10)
        x_pos += 60
    }

    let count = 0
    for (let i = range[0]; i <= range[1]; i += hScalar) {
        ctx?.fillText(i.toString(), 10, ctx.canvas.height - 23 - (count * 7))
        count += 3
    }

    let tWidth = ctx?.measureText(header).width
    let offset = (ctx?.canvas.width! - tWidth!) / 2
    ctx?.fillText(header, offset, 20)
}
</script>

<template>
    <canvas ref="graph"></canvas>
</template>

<style scoped>
canvas {
    border: 2px solid black;
    width: 100%;
    height: 100%;
}
</style>