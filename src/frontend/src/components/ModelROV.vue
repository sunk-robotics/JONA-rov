<script async setup lang="ts">
import { TresCanvas, useLoader } from '@tresjs/core';
import * as Three from 'three';
import { OrbitControls, FBXModel, useFBX } from '@tresjs/cientos'
import { useSensorDataStore } from '@/stores/sensorData';
import { color, mod } from 'three/examples/jsm/nodes/Nodes.js';

let scene = new Three.Scene()

const sensorData = useSensorDataStore()
let model = await useFBX('./jona.fbx')

const boundingBox = new Three.Box3().setFromObject(model)
boundingBox.getCenter(model.position)
let pivot = new Three.Group()
scene.add(pivot)
pivot.add(model)
model.position.set(0, -150, 0)

scene.add(pivot)
pivot.rotateX(- Math.PI / 2)

// x is pitch, y is roll, z is yaw
let currRotation = { x: 0, y: 0, z: 0 }
function rotateModel(x: number, y: number, z: number) {
    pivot.rotateX(x - currRotation.x)
    pivot.rotateY(y - currRotation.y)
    pivot.rotateZ(z - currRotation.z)
    currRotation.x = x;
    currRotation.y = y;
    currRotation.z = z;
}


function animate() {
    requestAnimationFrame(animate)
    let { yaw, pitch, roll } = sensorData.getAll()
    rotateModel(yaw! * Math.PI / 180, pitch! * Math.PI / 180, yaw!  * Math.PI / 180)
    console.log("-------" + yaw! * Math.PI / 360);
    
}
animate()
</script>
<template>
    <div>
        <TresCanvas clear-color="white" alpha shadows style="border-radius: 1rem;">
            <TresDirectionalLight :position="[-4, 8, 4]" :intensity="1.5" cast-shadow />
            <TresAmbientLight />
            <TresPerspectiveCamera :position="[0, 0, 800]" :look-at="[0, 0, 0]"/>
            <primitive :object="scene" />
        </TresCanvas>
    </div>
</template>

<style scoped>
div {
    width: 40vw;
    height: 18vw;
    padding-top: 0.5rem;
}
</style>