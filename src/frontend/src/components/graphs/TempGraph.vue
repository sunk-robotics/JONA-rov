<script setup lang="ts">
import { type Ref } from 'vue';
import Graph from "../Graph.vue";

type SensorData = {
    internal_temp: number | null,
    external_temp: number | null,
    cpu_temp: number | null,
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
};
</script>

<template>
    <div>
        <Graph :field="'internal_temp'" :header="'Internal Temperature (°C)'" :range="[0, 100]" />
        <Graph :field="'external_temp'" :header="'External Temperature (°C)'" :range="[0, 100]" />
        <Graph :field="'cpu_temp'" :header="'CPU Temperature (°C)'" :range="[0, 100]" />
    </div>
</template>

<style scoped>
div {
    width: 100%;
    height: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr;
    background-color: rgb(51, 51, 51);
    box-sizing: border-box;
}
</style>
