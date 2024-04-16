<script setup lang="ts">
import { useSensorDataStore } from '@/stores/sensorData';
import Thermometer from '/icons/thermometer.svg?raw';
import Depth from '/icons/MdiArrowUpDownBold.svg?raw';
import SpeedMult from '/icons/mdi-speedometer.svg?raw';

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
}

const sensorData = useSensorDataStore()

</script>

<template>
    <nav>
        <div class="anchor-card card">
            <div v-if="sensorData.get('depth_anchor_enabled')" class="depth-anchor-on anchor-indicator">Depth</div>
            <div v-else class="depth-anchor-off anchor-indicator">Depth</div>

            <div v-if="sensorData.get('yaw_anchor_enabled')" class="yaw-anchor-on anchor-indicator">Yaw</div>
            <div v-else class="yaw-anchor-off anchor-indicator">Yaw</div>

            <div v-if="sensorData.get('roll_anchor_enabled')" class="roll-anchor-on anchor-indicator">Roll</div>
            <div v-else class="roll-anchor-off anchor-indicator">Roll</div>

            <div v-if="sensorData.get('pitch_anchor_enabled')" class="pitch-anchor-on anchor-indicator">Pitch</div>
            <div v-else class="pitch-anchor-off anchor-indicator">Pitch</div>
        </div>

        <div class="card temp-card">
            <div class="card-icon" v-html="Thermometer"></div>
            <div class="card-data">{{ sensorData.get('external_temp') != null ? `${sensorData.get('external_temp').toFixed(1)}°C` : "?" }}</div>
        </div>
        <div class="card depth-card">
            <div class="card-icon" v-html="Depth"></div>
            <div class="card-data">{{ sensorData.get('depth') != null ? `${sensorData.get('depth').toFixed(2)} m` : "?" }}</div>
        </div>
        <div class="card speed-mult-card">
            <div class="card-icon" v-html="SpeedMult"></div>
            <div class="card-data">{{ sensorData.get('speed_multiplier') != null ? `${sensorData.get('speed_multiplier').toFixed(2)}x` : "?" }}</div>
        </div>
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
    padding-bottom: 1.707rem;
    font-family: moonWalk;
}

.card-icon {
    color: white;
    display: inline-block;
    height: fit-content;
}

.card-data {
    color: white;
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
    border-width: 6px;
    border-color: white;
}

.anchor-indicator {
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

.card {
    display: inline-block;
    justify-content: center;
    align-items: center;
    margin-right: 0.707rem;
    background-color: rgb(63, 63, 63);
    width: fit-content;
    padding: 1rem;
    padding-top: 0.3rem;
    padding-bottom: 0.5rem;
    border-radius: 0.7rem;
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
    margin-right: 1rem;
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
    margin-right: 1rem;
}

.roll-anchor-off {
    color: rgba(255, 255, 255, 0.282);
    background-color: rgb(48, 48, 48);
}
</style>
