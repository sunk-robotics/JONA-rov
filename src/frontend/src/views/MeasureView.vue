<script setup lang="ts">
    import { useImageStore } from '@/stores/image';
import { onMounted, ref } from 'vue';
    const image = useImageStore()

    const frame = ref<HTMLCanvasElement | null>(null)
    onMounted(() => {
        frame.value?.focus()
        let ctx = frame.value?.getContext("2d")
        ctx?.drawImage(image.get(), 0, 0, 1280, 720)
    })
</script>

<template>
    <canvas ref="frame"></canvas>
</template>