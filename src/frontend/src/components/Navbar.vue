<script setup lang="ts">
import { useSensorDataStore } from '@/stores/sensorData';

const sensorData = useSensorDataStore()

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

</script>

<template>
    <nav>
        <div v-if="sensorData.get('depth_anchor_enabled')" class="depth-anchor-on indicator">Depth</div>
        <div v-else class="depth-anchor-off indicator">Depth</div>

        <div v-if="sensorData.get('yaw_anchor_enabled')" class="yaw-anchor-on indicator">Yaw</div>
        <div v-else class="yaw-anchor-off indicator">Yaw</div>

        <div v-if="sensorData.get('roll_anchor_enabled')" class="roll-anchor-on indicator">Roll</div>
        <div v-else class="roll-anchor-off indicator">Roll</div>

        <div v-if="sensorData.get('pitch_anchor_enabled')" class="pitch-anchor-on indicator">Pitch</div>
        <div v-else class="pitch-anchor-off indicator">Pitch</div>

    </nav>
</template>

<style scoped>
@font-face {
    font-family: moonWalk;
    src: url('public/fonts/moonWalk.otf');
}

nav {
    height: 3rem;
    background-color: rgb(22, 22, 22);
    padding: 1rem;
    font-family: moonWalk;
}
  
.indicator {
    display: inline-block;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 1rem;
    height: 1rem;
    width: 4rem;
    border-radius: 1rem;
    margin-left: 1rem;
    box-shadow: 0.3rem 0.3rem 0.2rem rgb(19, 19, 19);
}

.depth-anchor-on {
    color: rgb(255, 255, 255);
    background-color: rgba(255, 208, 0, 0.884);
    box-shadow: 0rem 0rem 0.2rem 0.2rem rgba(255, 208, 0, 0.884);
}

.yaw-anchor-on {
    color: white;
    background-color: rgba(79, 41, 250, 0.733);
    box-shadow: 0rem 0rem 0.2rem 0.2rem rgba(62, 41, 250, 0.733);
}

.pitch-anchor-on {
    color: white;
    background-color: rgba(51, 255, 0, 0.653);
    box-shadow: 0rem 0rem 0.2rem 0.2rem rgba(51, 255, 0, 0.653);
}

.roll-anchor-on {
    color: white;
    background-color: rgb(208, 30, 30);
    box-shadow: 0rem 0rem 0.2rem 0.2rem rgb(208, 30, 30);
}

.depth-anchor-off {
    color: rgba(255, 255, 255, 0.282);
    background-color: rgb(48, 48, 48);
}

.yaw-anchor-off {
    color: rgba(255, 255, 255, 0.282);
    background-color: rgb(48, 48, 48);
}

.pitch-anchor-off {
    color: rgba(255, 255, 255, 0.282);
    background-color: rgb(48, 48, 48);
}

.roll-anchor-off {
    color: rgba(255, 255, 255, 0.282);
    background-color: rgb(48, 48, 48);
}
</style>
