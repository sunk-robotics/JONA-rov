<script setup lang="ts">
import type { Ref } from 'vue';

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

const props = defineProps<{ data: Ref<SensorData> }>();
let sensorData = props.data;
</script>

<template>
    <ul>
        <li>Internal Temperature: {{ sensorData.internal_temp != null ? `${sensorData.internal_temp}°C` : "N/A" }}</li>
        <li>External Temperature: {{ sensorData.external_temp != null ? `${(sensorData.external_temp).toFixed(1)}°C` : "N/A" }}</li>
        <li>Depth: {{ sensorData.depth != null ? `${(sensorData.depth).toFixed(1)} m` : "Unknown" }}</li>
        <li>Yaw: {{ sensorData.yaw != null ? `${(sensorData.yaw).toFixed(1)}°` : "N/A" }}</li>
        <li>Roll: {{ sensorData.roll != null ? `${(sensorData.roll).toFixed(1)}°` : "N/A" }}</li>
        <li>Pitch: {{ sensorData.pitch != null ? `${(sensorData.pitch).toFixed(1)}°` : "N/A" }}</li>
        <li>5V Rail Voltage: {{ sensorData.voltage_5V != null ? `${(sensorData.voltage_5V).toFixed(2)} V` : "N/A" }}</li>
        <li>5V Rail Current: {{ sensorData.current_5V != null ? `${(sensorData.current_5V).toFixed(1)} A` : "N/A" }}</li>
        <li>12V Rail Voltage: {{ sensorData.voltage_12V != null ? `${(sensorData.voltage_12V).toFixed(2)} V` : "N/A" }}</li>
        <li>12V Rail Current: {{ sensorData.current_12V != null ? `${(sensorData.current_12V).toFixed(1)} A` : "N/A" }}</li>
        <li>X Acceleration: {{ sensorData.x_accel != null ? sensorData.x_accel.toString() : "N/A" }}</li>
        <li>Y Acceleration: {{ sensorData.y_accel != null ? sensorData.y_accel.toString() : "N/A"}}</li>
        <li>Z Acceleration: {{ sensorData.z_accel != null ? sensorData.z_accel.toString() : "N/A" }}</li>
        <li>Speed Multiplier: {{ sensorData.speed_multiplier != null ? sensorData.speed_multiplier.toString() : "N/A" }}</li>
        <li>Depth Anchor Enabled?: {{ sensorData.depth_anchor_enabled != null ? sensorData.depth_anchor_enabled.toString() : "N/A" }}</li>
        <li>Yaw Anchor Enabled?: {{ sensorData.yaw_anchor_enabled != null ? sensorData.yaw_anchor_enabled.toString() : "N/A" }}</li>
        <li>Roll Anchor Enabled?: {{ sensorData.roll_anchor_enabled != null ? sensorData.roll_anchor_enabled.toString() : "N/A" }}</li>
        <li>Pitch Anchor Enabled?: {{ sensorData.pitch_anchor_enabled != null ? sensorData.pitch_anchor_enabled.toString() : "N/A" }}</li>
        <li>Motor Lock Enabled?: {{ sensorData.motor_lock_enabled != null ? sensorData.motor_lock_enabled.toString() : "N/A" }}</li>
    </ul>
</template>

<style scoped>
ul {
    width: 90%;
    height: 100%;
    /* align-items: center; */
    list-style-type: none;
    padding: 0;
    display: grid;
    grid-template-rows: repeat(5, 1fr);
    grid-auto-flow: column;
    font-size: small;
}

li {
    text-wrap: nowrap;
}
</style>