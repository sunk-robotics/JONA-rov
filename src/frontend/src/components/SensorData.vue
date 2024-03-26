<script setup lang="ts">
import { ref, type Ref } from 'vue';
import Data from './Data.vue';

let mainWs = new WebSocket("ws://192.168.100.1:8765")
const wsInfo = { 'client_type': 'web_client_main' }

let isClosed = false;

mainWs.addEventListener('open', (event) => {
    mainWs.send(JSON.stringify(wsInfo));
    isClosed = false;
})

mainWs.addEventListener('close', () => isClosed = true)

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
    z_accel: number| null,
    speed_multiplier: number | null,
    depth_anchor_enabled: boolean | null,
    yaw_anchor_enabled: boolean | null,
    roll_anchor_enabled: boolean | null,
    pitch_anchor_enabled: boolean | null,
    motor_lock_enabled: boolean | null
}

const sensorData = ref<SensorData>({ 
    internal_temp: null, 
    external_temp: null, 
    temp: null, 
    depth: null, 
    yaw: null, 
    roll: null, 
    pitch: null, 
    voltage_5V: null, 
    current_5V: null, 
    voltage_12V: null, 
    current_12V: null,
    x_accel: null,
    y_accel: null,
    z_accel: null,
    speed_multiplier: null,
    depth_anchor_enabled: null,
    yaw_anchor_enabled: null,
    roll_anchor_enabled: null,
    pitch_anchor_enabled: null,
    motor_lock_enabled: null
})


mainWs.addEventListener('message', (event) => {
    let incomingData: SensorData = JSON.parse(event.data);
    sensorData.value = incomingData;
})

function changeDisplayMode(mode: dataDisplayStyle)  {
    displayMode.value = mode
    console.log(mode);
    
}
</script>

<template>
    <div class="sensor">
        <div>
            <button @click="changeDisplayMode('electric-graph')">Electric</button>
            <button>Motion</button>
            <button>Temperature</button>
            <button>Text</button>
        </div>
        <Data :data="sensorData" v-if="displayMode == 'text-all'"/>
    </div>
</template>

<style>
    .sensor {
        width: 100%;
        height: 100%;
    }
</style>