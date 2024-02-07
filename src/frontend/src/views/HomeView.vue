<script setup lang="ts">
    import Camera from '@/components/Camera.vue';
</script>

<template>
    <main>
        <Camera cam-url="ws://192.168.100.2:3000"/>
        <Camera cam-url="ws://192.168.100.3:3000"/>
        <Camera cam-url="ws://192.168.100.4:3000"/>
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
    }
</style>