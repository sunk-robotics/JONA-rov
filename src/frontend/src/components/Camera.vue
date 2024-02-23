<script setup lang="ts">
    import { onMounted, type Ref, ref } from 'vue';
    import { useImageStore } from "@/stores/image"

    const image = useImageStore()
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
        image.set(event.data)
        decoder = new ImageDecoder({
            type: "image/jpeg",
            data: event.data
        });

        let frame = decoder.decode().then((res: any) => {
            ctx.drawImage(res.image, 0, 0, 1280, 720)
        })
    })

    function redirectMeasure() {
        window.location.pathname = "measure"
    }
</script>

<template>
    <canvas ref="canvas" width=1280 height=720 @click="redirectMeasure"></canvas>
</template>

<style scoped>
    canvas {
        background: url("smpte_color_bars.gif");
        background-size: cover;
        aspect-ratio: 16/9;
        margin-left: 0.5em;
        margin-right: 0.5em;
        width: 45vw;
    }

    canvas:hover {
        cursor:grab;
    }
</style>