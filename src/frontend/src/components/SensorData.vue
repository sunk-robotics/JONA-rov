<script setup lang="ts">
import { ref } from 'vue';

let mainWs = new WebSocket("ws://192.168.100.1:8765")
const wsInfo = { 'client_type': 'web_client_main' }

let isClosed = false;

mainWs.addEventListener('open', (event) => {
    mainWs.send(JSON.stringify(wsInfo));
    isClosed = false;
})

mainWs.addEventListener('close', () => isClosed = true)

type SensorData = {
    temp: number | null,
    depth: number | null,
    yaw: number | null,
    roll: number | null,
    pitch: number | null
}

const sensorData = ref<SensorData>({ temp: null, depth: null, yaw: null, roll: null, pitch: null })

mainWs.addEventListener('message', (event) => {
    let incomingData: SensorData = JSON.parse(event.data);
    sensorData.value = incomingData;
})
</script>

<template>
    <ul v-if="!isClosed">
        <li v-for="[field, value] in Object.entries(sensorData)">{{ field }}: {{ value }}</li>
    </ul>
    <h1 v-else>No Data</h1>
</template>

<style scoped>
ul {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    list-style-type: none;
    padding: 0;
    justify-content: space-evenly;
    margin-left: 5rem;
}
</style>