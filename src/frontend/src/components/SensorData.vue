<script setup lang="ts">
import { ref, type Ref } from 'vue';
import Data from './Data.vue';
import ElectricGraph from "./graphs/ElectricGraph.vue"
import MotionGraph from './graphs/MotionGraph.vue';
import TempGraph from './graphs/TempGraph.vue';
import { useSensorDataStore } from '@/stores/sensorData';

type dataDisplayStyle = "electric-graph" | "motion-graph" | "text-all" | "temp-graph"
let displayMode: Ref<dataDisplayStyle> = ref("text-all")

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

const sensorData = useSensorDataStore()

let ws: WebSocket;
const url = "ws://192.168.1.1:8765";
ws = new WebSocket(url);
const wsInfo = { 'client_type': 'web_client_main' }

ws.addEventListener('open', (event) => {
    ws.send(JSON.stringify(wsInfo));
})

ws.addEventListener('message', (event) => {
    let incomingData: SensorData = JSON.parse(event.data);
    sensorData.setAll(incomingData)
})


setInterval(() => {
    if (ws != null && ws.readyState == 3) {
        ws = new WebSocket(url);
        ws.addEventListener("open", (event) => {
            ws.send(JSON.stringify(wsInfo));
        })
        ws.addEventListener('message', (event) => {
            let incomingData: SensorData = JSON.parse(event.data);
            sensorData.setAll(incomingData)
        })
    }
}, 500);


function changeDisplayMode(mode: dataDisplayStyle) {
    displayMode.value = mode
    console.log(mode);

}
</script>

<template>
    <div class="sensor">
        <div class="buttons">
            <button @click="changeDisplayMode('text-all')" class="left-button">Text</button>
            <button @click="changeDisplayMode('temp-graph')">Temperature</button>
            <button @click="changeDisplayMode('electric-graph')"> Electric</button>
            <button @click="changeDisplayMode('motion-graph')" class="right-button">Motion</button>
        </div>
        <Data :sensor-data="sensorData" v-if="displayMode == 'text-all'" />
        <ElectricGraph v-if="displayMode == 'electric-graph'" />
        <MotionGraph v-if="displayMode == 'motion-graph'" />
        <TempGraph v-if="displayMode == 'temp-graph'" />
    </div>
</template>

<style scoped>
.sensor {
    background-color: rgb(84, 84, 84);
    display: flex;
    padding: 1rem;
    justify-content: center;
    width: 85%;
    height: fit-content;
    position: relative;
    border-radius: 1rem;
    box-shadow: 1rem 1rem 0.5rem rgb(23, 23, 23);
    color: rgb(255, 255, 255);
}

.buttons {
    position: absolute;
    top: -0.5rem;
    width: 100%;
}

button {
    background-color: rgb(63, 63, 63);
    color: white;
    width: 25%;
    height: 2rem;
    border: none;
}

button:hover {
    background-color: rgb(94, 94, 94);
}

.left-button {
    border-top-left-radius: 1rem;
}

.right-button {
    border-top-right-radius: 1rem;
}
</style>
