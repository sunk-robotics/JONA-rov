<script setup lang="ts">
    import Camera from '@/components/Camera.vue';
    import SensorData from '@/components/SensorData.vue';
</script>

<template>
    <main>
<<<<<<< HEAD
        <Camera cam-url="ws://localhost:8000/" />
        <!-- <Camera cam-url="ws://192.168.100.1:3000"/>
        <Camera cam-url="ws://192.168.100.4:3000"/>
        <Camera cam-url="ws://192.168.100.3:3000"/>
        <SensorData /> -->
=======
        <Camera cam-url="ws://192.168.100.1:3000"/>
        <Camera cam-url="ws://192.168.100.4:3001"/>
        <Camera cam-url="ws://192.168.100.3:3002"/>
        <SensorData />
>>>>>>> 699dfb48244737d2c20dfa19c581f0e3117d7453
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
