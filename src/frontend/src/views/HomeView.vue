<script setup lang="ts">
    import Camera from '@/components/Camera.vue';
    import SensorData from '@/components/SensorData.vue';
</script>

<template>
    <main>
        <Camera cam-url="ws://192.168.100.1:3000"/>
        <Camera cam-url="ws://192.168.100.4:3001"/>
        <Camera cam-url="ws://192.168.100.3:3002"/>
        <SensorData />
    </main>
</template>

<style>
    main {
        width: 100vw;
        height: 100vh;
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        justify-items: center;
        align-items: center;
        /* padding: 1rem; */
        gap: 1rem;
        box-sizing: border-box;
    }
</style>
