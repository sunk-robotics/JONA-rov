<script setup lang="ts">
import { onMounted, type Ref, ref } from 'vue';
    let decoder;

    const props = defineProps<{camUrl: string}>();

    let wsFeed = new WebSocket(props.camUrl);
    wsFeed.binaryType = "arraybuffer";

    let ctx: CanvasRenderingContext2D;

    const canvas = ref<HTMLCanvasElement | null>(null);
    onMounted(() => {
        canvas.value?.focus();
        ctx = canvas.value?.getContext("2d")!;
    })

    wsFeed.addEventListener("message", (event) => {
        decoder = new ImageDecoder({
            type: "image/jpeg",
            data: event.data
        });

        let frame = decoder.decode().then((res: any) => {
            ctx.drawImage(res.image, 0, 0)
        })
    })
</script>

<template>
    <canvas ref="canvas"></canvas>
</template>

<style scoped>
    canvas {
        height: 95%;
        aspect-ratio: 16/9;
        background: url("smpte_color_bars.gif");
        background-size: cover;
    }
</style>