<script setup lang="ts">
    import { onMounted, type Ref, ref } from 'vue';
    import { RouterLink } from 'vue-router';
    import { useImageStore } from '@/stores/image';

    let imageStore = useImageStore()
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
            const image = res.image;
            imageStore.set(image)
            ctx.drawImage(image, 0, 0, image.codedWidth, image.codedHeight, 0, 0, 1920, 1080)
        })

    })

</script>

<template>
    <router-link to="/measure">
        <canvas ref="canvas" width=1920 height=1080></canvas>
    </router-link>
</template>

<style scoped>
    canvas {
        background: url("smpte_color_bars.gif");
        background-size: cover;
        aspect-ratio: 16/9;
        margin-left: 0.5em;
        margin-right: 0.5em;
        width: 45vw;
        border-radius: 1rem;
    }

    canvas:hover {
        cursor:grab;
    }
</style>
