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
    internal_temp: number | null,
    external_temp: number | null,
    depth: number | null,
    yaw: number | null,
    roll: number | null,
    pitch: number | null,
    voltage_5V: number | null,
    current_5V: number | null,
    voltage_12V: number | null,
    current_12V: number | null
}

const sensorData = ref<SensorData>({ internal_temp: null, external_temp: null, temp: null, depth: null, yaw: null, roll: null, pitch: null, voltage_5V: null, current_5V: null, voltage_12V: null, current_12V: null })




mainWs.addEventListener('message', (event) => {
    let incomingData: SensorData = JSON.parse(event.data);
    sensorData.value = incomingData;
})
</script>

<template>
    <ul v-if="!isClosed">
        <li>Internal Temperature: {{ sensorData.internal_temp != null ? `${sensorData.internal_temp}°C` : "Unknown" }}</li>
        <li>External Temperature: {{ sensorData.external_temp != null ? `${(sensorData.external_temp).toFixed(1)}°C` : "Unknown" }}</li>
        <li>Depth: {{ sensorData.depth != null ? `${(sensorData.depth).toFixed(1)} m` : "Unknown" }}</li>
        <li>Yaw: {{ sensorData.yaw != null ? `${(sensorData.yaw).toFixed(1)}°` : "Unknown" }}</li>
        <li>Roll: {{ sensorData.roll != null ? `${(sensorData.roll).toFixed(1)}°` : "Unknown" }}</li>
        <li>Pitch: {{ sensorData.pitch != null ? `${(sensorData.pitch).toFixed(1)}°` : "Unknown" }}</li>
        <li>5V Rail Voltage: {{ sensorData.voltage_5V != null ? `${(sensorData.voltage_5V).toFixed(2)} V` : "Unknown" }}</li>
        <li>5V Rail Current: {{ sensorData.current_5V != null ? `${(sensorData.current_5V).toFixed(1)} A` : "Unknown" }}</li>
        <li>12V Rail Voltage: {{ sensorData.voltage_12V != null ? `${(sensorData.voltage_12V).toFixed(2)} V` : "Unknown" }}</li>
        <li>12V Rail Current: {{ sensorData.current_12V != null ? `${(sensorData.current_12V).toFixed(1)} A` : "Unknown" }}</li>
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
