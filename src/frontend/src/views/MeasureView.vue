<script setup lang="ts">
    import { useImageStore } from '@/stores/image';
    import { onMounted, ref } from 'vue';
    const image = useImageStore()

    const frame = ref<HTMLCanvasElement | null>(null)
    onMounted(async () => {
        frame.value?.focus()
        let ctx = frame.value?.getContext("2d")
        let decoder = new ImageDecoder({
            type: "image/jpeg",
            data: image.get()
        });
        ctx?.drawImage(await decoder.decode(), 0, 0, 1280, 720)
    })
</script>

<template>
    <canvas ref="frame"></canvas>
</template>