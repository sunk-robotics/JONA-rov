<script setup lang="ts">
import { onMounted, ref, type Ref } from 'vue';
import SensorData from './SensorData.vue';

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
    z_accel: number| null,
    speed_multiplier: number | null,
    depth_anchor_enabled: boolean | null,
    yaw_anchor_enabled: boolean | null,
    roll_anchor_enabled: boolean | null,
    pitch_anchor_enabled: boolean | null,
    motor_lock_enabled: boolean | null
}

let history: { timestamp: number, val: number }[] = [];
const { data, field } = defineProps<{ data: Ref<SensorData>, field: keyof SensorData }>()
let ctx: CanvasRenderingContext2D;

const graph = ref<HTMLCanvasElement | null>(null)
onMounted(() => {
    graph.value?.focus()
    ctx = graph.value?.getContext("2d")!
})


let curr_sec = 0;
setInterval(() => {
    let val = data.value[field];
    history.push({ timestamp: curr_sec, val: val as number })

    curr_sec += 0.5
}, 500)

function drawGraph(curr_sec: number) {
    let len = history.length >= 3 ? 3 : history.length;

    for (const { timestamp, val } of  history) {
        ctx.strokeStyle = "black"
    }
    
}
</script>

<template>
    <canvas>

    </canvas>
</template>