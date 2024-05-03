<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useImageStore } from "@/stores/image"
import axios from 'axios';
import router from '@/router';

axios.defaults.withCredentials = true;

let imageStore = useImageStore()
let ctx: CanvasRenderingContext2D;
const frame = ref<HTMLCanvasElement | null>(null)
onMounted(() => {
    
    frame.value?.focus()
    ctx = frame.value?.getContext("2d")!
    if (imageStore.image == null) {
        return
    }
    ctx.drawImage(imageStore.get(), 0, 0, 854, 480);
    imageStore.set(null);

})


// length of the reference object in centimeters
const REF_OBJ_LEN = 32;

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
                rollMode()
            }
            break;
    }
    if (points.length == 2) {
        points = []
    }
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
    
    const url = `http://127.0.0.1:3000/left=${Math.round(leftSide) * 10}&right=${Math.round(rightSide) * 10}&top=${Math.round(topSide) * 10}`
    try { 
        await fetch(url, { credentials: "omit" } ) 
    } catch (e) {
        console.log("error...");
        
    }
    console.log("redirecting...");
    
    router.push("/coral")
}

function rollMode(): Fields {
    switch (metreMode.value) {
        case 'leftSide':
            return 'rightSide'
        
        case 'rightSide':
            return 'topSide'

        case 'topSide':
            return 'fullLen'

        case 'fullLen':
            return 'fullHgt'
            
        default:
            break
    }
    return null
}

function clearData() {
    for (let key in lenObj) {
        lenObj.value[key as keyof typeof lenObj.value] = 0
    }
}
</script>

<template>
    <div>
        <canvas ref="frame" width="854" height="480" @click="handleClicks"></canvas>
        <ul>
            <li><button>Reference Obj. Len: {{ REF_OBJ_LEN }} cms</button></li>
            <li><button @click="changeMode('leftSide')">Left Side Length: {{ lenObj.leftSide.toPrecision(4) }} cms</button></li>
            <li><button @click="changeMode('rightSide')">Right Side Length: {{ lenObj.rightSide.toPrecision(4) }} cms</button></li>
            <li><button @click="changeMode('topSide')">Top Side Length: {{ lenObj.topSide.toPrecision(4) }} cms</button></li>
            <li><button >Full Length: {{ lenObj.fullLen.toPrecision(4) }} cms</button></li>
            <li><button >Full Height: {{ lenObj.fullHgt.toPrecision(4) }} cms</button></li>
        </ul>
        <button class="submit" @click="submitData">Send Data</button>
        <button class="submit" @click="clearData">Clear Data</button>
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
    width: auto;
    
}

li {
   width: 100%; 
}

button {
    width: 100%;
    text-align: center;
}
</style>
