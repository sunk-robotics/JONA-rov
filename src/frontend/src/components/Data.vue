<script setup lang="ts">
import type { Ref } from 'vue';
import { useSensorDataStore } from '@/stores/sensorData';

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
</script>

<template>
    <ul>
        <li>Internal Temperature: {{ sensorData.get('internal_temp') != null ? `${sensorData.get('internal_temp')}°C` :
            "Unknown" }}</li>
        <li>External Temperature: {{ sensorData.get('external_temp') != null ?
            `${sensorData.get('external_temp').toFixed(1)}°C` : "Unknown" }}</li>
        <li>Depth: {{ sensorData.get('depth') != null ? `${sensorData.get('depth').toFixed(2)} m` : "Unknown" }}</li>
        <li>Yaw: {{ sensorData.get('yaw') != null ? `${sensorData.get('yaw').toFixed(1)}°` : "Unknown" }}</li>
        <li>Roll: {{ sensorData.get('roll') != null ? `${sensorData.get('roll').toFixed(1)}°` : "Unknown" }}</li>
        <li>Pitch: {{ sensorData.get('pitch') != null ? `${sensorData.get('pitch').toFixed(1)}°` : "Unknown" }}</li>
        <li>5V Rail Voltage: {{ sensorData.get('voltage_5V') != null ? `${sensorData.get('voltage_5V').toFixed(2)} V` :
            "Unknown" }}</li>
        <li>5V Rail Current: {{ sensorData.get('current_5V') != null ? `${sensorData.get('current_5V').toFixed(2)} A` :
            "Unknown" }}</li>
        <li>12V Rail Voltage: {{ sensorData.get('voltage_12V') != null ? `${sensorData.get('voltage_12V').toFixed()} V`
            : "Unknown" }}</li>
        <li>12V Rail Current: {{ sensorData.get('current_12V') != null ? `${sensorData.get('current_12V').toFixed()} A`
            : "Unknown" }}</li>
        <!-- Not currently needed
        <li>X Acceleration: {{ sensorData.get('x_accel') != null ? `${sensorData.get('x_accel')!.toFixed(1)}m/s^2` : "Unknown" }}</li>
        <li>Y Acceleration: {{ sensorData.get('y_accel') != null ? `${sensorData.get('y_accel')!.toFixed(1)}m/s^2` : "Unknown"}}</li>
        <li>Z Acceleration: {{ sensorData.get('z_accel') != null ? `${sensorData.get('z_accel')!.toFixed(1)}m/s^2` : "Unknown" }}</li>
        -->
        <li>Speed Multiplier: {{ sensorData.get('speed_multiplier') != null ? `${sensorData.get('speed_multiplier')}x` :
            "Unknown" }}</li>
        <li>Motor Lock: {{ sensorData.get('motor_lock_enabled') ? "Enabled" : "Disabled" }}</li>
    </ul>
</template>

<style scoped>
ul {
    width: 100%;
    height: 100%;
    /* align-items: center; */
    list-style-type: none;
    padding: 0;
    display: grid;
    grid-template-rows: repeat(5, 1fr);
    grid-auto-flow: column;
    font-size: medium;
}

li {
    text-wrap: nowrap;
    line-height: 4rem;
}
</style>
