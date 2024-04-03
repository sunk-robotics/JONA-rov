<script setup lang="ts">
import { ref, type Ref } from 'vue';
import Data from './Data.vue';
import ElectricGraph from "./graphs/ElectricGraph.vue"
import MotionGraph from './graphs/MotionGraph.vue';
import TempGraph from './graphs/TempGraph.vue';
import { useSensorDataStore } from '@/stores/sensorData';

const sensorData = useSensorDataStore()
let url = "ws://192.168.0.106:8765";

let mainWs = new WebSocket(url)
const wsInfo = { 'client_type': 'web_client_main' }

mainWs.addEventListener('open', (event) => {
    mainWs.send(JSON.stringify(wsInfo));
})


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

mainWs.addEventListener('message', (event) => {
    let incomingData: SensorData = JSON.parse(event.data);
    sensorData.setAll(incomingData)
})

function changeDisplayMode(mode: dataDisplayStyle)  {
    displayMode.value = mode
    console.log(mode);
    
}
</script>

<template>
    <div class="sensor">
        <div class="buttons">
            <button @click="changeDisplayMode('electric-graph')">Electric</button>
            <button @click="changeDisplayMode('motion-graph')">Motion</button>
            <button @click="changeDisplayMode('temp-graph')">Temperature</button>
            <button @click="changeDisplayMode('text-all')">Text</button>
        </div>
        <Data :sensor-data="sensorData" v-if="displayMode == 'text-all'"/>
        <ElectricGraph v-if="displayMode == 'electric-graph'" />
        <MotionGraph v-if="displayMode == 'motion-graph'" />
        <TempGraph v-if="displayMode == 'temp-graph'"/>
    </div>
</template>

<style scoped>
    .sensor {
        display: flex;
        justify-content: center;
        width: 100%;
        height: 100%;
        position: relative;
    }

    .buttons {
        position: absolute;
        top: -1rem;
    }
</style>
