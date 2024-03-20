<script async setup lang="ts">
import { onMounted, ref } from 'vue';
import { useImageStore } from "@/stores/image"
import axios from 'axios';

axios.defaults.withCredentials = true;

let imageStore = useImageStore()
let ctx: CanvasRenderingContext2D;
const frame = ref<HTMLCanvasElement | null>(null)
onMounted(() => {
    frame.value?.focus()

    ctx = frame.value?.getContext("2d")!
    ctx.drawImage(imageStore.get(), 0, 0, 640, 480)
})


// measurement
const REF_OBJ_LEN = 3;

type Fields = "pixPerInch" | "leftSide" | "rightSide" | "topSide" | "fullLen" | "fullHgt" | null
let lenObj = ref({
    pixPerInch: 0,
    leftSide: 0,
    rightSide: 0,
    topSide: 0,
    fullLen: 0,
    fullHgt: 0
})
let metreMode = ref<Fields>("pixPerInch")

let points: { x: number, y: number }[] = []
function handleClicks(e: MouseEvent) {
    
    const [x, y] = [e.offsetX, e.offsetY];
    drawPoint(x, y)

    switch (metreMode.value) {
        case "pixPerInch":
            points.push({ x, y })

            if (points.length == 2) {
                const pixLen = Math.sqrt(
                    (points[0].x - points[1].x) ** 2 +
                    (points[0].y - points[1].y) ** 2
                )

                lenObj.value.pixPerInch = pixLen / REF_OBJ_LEN
            }
            break;

        case null:
            break

        default:
            points.push({ x, y })
            if (points.length == 2) {
                const pixLen = Math.sqrt(
                    (points[0].x - points[1].x) ** 2 +
                    (points[0].y - points[1].y) ** 2
                )

                lenObj.value[metreMode.value] = pixLen / lenObj.value.pixPerInch
                console.log(metreMode.value, " is ", lenObj.value[metreMode.value]);
            }
            break;
    }
    if (points.length == 2) {
        points = []
        
    }
    lenObj.value.topSide = 1000
}

function drawPoint(x: number, y: number) {
    ctx.fillStyle = "red"
    ctx.arc(x, y, 8, 0, 2*Math.PI)
    ctx.fill()
    ctx.closePath()
}

function changeMode(mode: Fields) {
    metreMode.value = mode
    console.log("measuring: ", mode);
    
    points = []
}

async function submitData() {
    const { leftSide, rightSide, topSide } = lenObj.value
    

    if (leftSide == 0 || rightSide == 0 || topSide == 0) {
        return
    }
    console.log("sending data...");
    
    const url = `http://127.0.0.1:3000/left=${leftSide}&right=${rightSide}&top=${topSide}`
    await axios.get(url)
}

</script>

<template>
    <div>
        <canvas ref="frame" width="640" height="480" @click="handleClicks"></canvas>
        <ul>
            <li><button>Reference Obj. Len: {{ REF_OBJ_LEN }} cms</button></li>
            <li><button @click="changeMode('leftSide')">Left Side Length: {{ lenObj.leftSide }} cms</button></li>
            <li><button @click="changeMode('rightSide')">Right Side Length: {{ lenObj.rightSide }} cms</button></li>
            <li><button @click="changeMode('topSide')">Top Side Length: {{ lenObj.topSide }} cms</button></li>
            <li><button @click="changeMode('fullLen')">Full Length: {{ lenObj.fullLen }} cms</button></li>
            <li><button @click="changeMode('fullHgt')">Full Height: {{ lenObj.fullHgt }} cms</button></li>
            <li><button >click me idk</button></li>
        </ul>
        <button class="submit" @click="submitData">Send Data</button>
    </div>
</template>

<style scoped>
div {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 3rem;
}

.submit {
    position: fixed;
    top: 10rem;
    font-size: 3rem;
}
</style>