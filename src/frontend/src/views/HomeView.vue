<script setup lang="ts">
import Camera from '@/components/Camera.vue';
import SensorData from '@/components/SensorData.vue';
import Navbar from '@/components/Navbar.vue'
</script>

<template>
    <Navbar></Navbar>
    <main>
        <Camera url="ws://192.168.1.2:3002" />
        <Camera url="ws://192.168.1.3:3001" />
        <Camera url="ws://192.168.1.9:3000" />
        <!-- <Camera url="ws://127.0.0.1:3001" /> -->
        <!-- <Camera url="ws://192.168.1.1:3009" /> -->
        <SensorData />
    </main>
</template>

<style>
main {
    background-color: rgb(37, 37, 37);
    width: 100%;
    height: 90vh;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    justify-items: center;
    align-items: center;
    box-sizing: border-box;
}
</style>
