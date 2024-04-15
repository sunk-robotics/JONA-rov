<script setup lang="ts">
import { onMounted, type Ref, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useImageStore } from '@/stores/image';

let ws: WebSocket;

let imageStore = useImageStore();

const props = defineProps<{ url: string }>();

let ctx: CanvasRenderingContext2D;

const canvas = ref<HTMLCanvasElement | null>(null);
onMounted(() => {
    canvas.value?.focus();
    ctx = canvas.value?.getContext("2d")!;
});

ws = new WebSocket(props.url);
ws.binaryType = "arraybuffer";
ws.addEventListener("open", (event) => {
    console.log("Camera connected!");
})

ws.addEventListener("message", (event) => {
    let decoder = new ImageDecoder({
        type: "image/jpeg",
        data: event.data
    });

    let frame = decoder.decode().then((res: any) => {
        const image = res.image;
        imageStore.set(image)
        ctx.drawImage(image, 0, 0, image.codedWidth, image.codedHeight, 0, 0, 1920, 1080)
    })

})

// if the WebSocket isn't connected, keep trying until it connects
setInterval(() => {
    if (ws != null && ws.readyState == 3) {
        ws = new WebSocket(props.url);
        ws.binaryType = "arraybuffer";
        ws.addEventListener("open", (event) => {
            console.log("Camera connected!");
        });

        ws.addEventListener("message", (event) => {
            let decoder = new ImageDecoder({
                type: "image/jpeg",
                data: event.data
            });

            let frame = decoder.decode().then((res: any) => {
                const image = res.image;
                imageStore.set(image)
                ctx.drawImage(image, 0, 0, image.codedWidth, image.codedHeight, 0, 0, 1920, 1080)
            })
        })

    }
}, 500);

function connectWebsocket(url: string) {
    if (ws != null && ws.readyState == 3) {
        ws = new WebSocket(url);
        ws.binaryType = "arraybuffer";
        ws.addEventListener("open", (event) => {
            console.log("Camera connected!");
        });

        ws.addEventListener("message", (event) => {
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

    }
}

</script>

<template>
    <router-link to="/measure">
        <canvas ref="canvas" width=1920 height=1080></canvas>
    </router-link>
</template>

<style scoped>
canvas {
    background: url("whitenoise.gif");
    background-size: cover;
    aspect-ratio: 16/9;
    margin-left: 0.5em;
    margin-right: 0.5em;
    padding: 1rem;
    height: 40vh;
    border-radius: 1rem;
    box-shadow: 1rem 1rem 0.5rem rgb(23, 23, 23);
}

canvas:hover {
    cursor: grab;
}
</style>
