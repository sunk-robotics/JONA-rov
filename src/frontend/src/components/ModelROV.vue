<script setup lang="ts">
import { PerspectiveCamera, Scene, WebGLRenderer} from 'three'
import { useSensorDataStore } from '@/stores/sensorData';
import { onMounted, ref, render } from 'vue';

const model = ref<HTMLCanvasElement | null>(null)
const scene = new Scene()
//TODO: Make sizing responsive
const camera = new PerspectiveCamera(75, 620 / 350, 0.1, 1000)

scene.add(camera)

onMounted(() => {
    const renderer = new WebGLRenderer({
        canvas: model.value as unknown as HTMLCanvasElement,
        antialias: true,
    });
    //TODO: Make sizing responsive
    renderer.setSize(620, 350)
    renderer.render(scene, camera)
})

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
<canvas ref="model"></canvas>
</template>
