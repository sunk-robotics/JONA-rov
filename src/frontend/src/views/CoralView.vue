<script setup lang="ts">
    import * as Three from 'three';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const scene = new Three.Scene();
    const renderer = new Three.WebGLRenderer( {antialias: true} )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)

    scene.background = new Three.Color("black")

    const gltfLoader = new GLTFLoader();
    

    gltfLoader.load('/result.glb', (gltfObject) => {
    gltfObject.scene.traverse(obj => {
        if (obj instanceof Three.Mesh) {
        obj.castShadow = true;
        obj.receiveShadow = true;
        }
    })
    // make the object not obscenely large
    gltfObject.scene.scale.set(0.01, 0.01, 0.01)
    // for some reason, CadQuery produces GLTF files that are rotated 90 degrees,
    // this rotates it back
    gltfObject.scene.rotation.set(-Math.PI / 2, 0, 0)

    // centers the rotation around the center of the object, rather than the
    // world center
    const boundingBox = new Three.Box3().setFromObject(gltfObject.scene);
    boundingBox.getCenter(gltfObject.scene.position);
    gltfObject.scene.position.negate();
    let pivot = new Three.Group();
    scene.add(pivot);
    pivot.add(gltfObject.scene);

    scene.add(gltfObject.scene);

    }, undefined, function (error) {
    console.error(error);
    });

    // add some light from the sky
    {
    const skyColor = 0xB1E1FF;  // light blue
    const groundColor = 0xB97A20;  // brownish orange
    const intensity = 2;
    const light = new Three.HemisphereLight(skyColor, groundColor, intensity);
    scene.add(light);
    }

    // add light from all directions to get rid of annoying shadows
    // unfortunately, this rendering will be RTX off
    for (let i = -1; i <= 1; i++) {
    for (let j = -1; j <= 1; j++) {
        for (let k = -1; k <= 1; k++) {
        const color = 0xFF_FF_FF;
        const intensity = 0.3;
        const directionalLight = new Three.DirectionalLight(color, intensity);
        directionalLight.position.set(i, j, k);
        scene.add(directionalLight);
        scene.add(directionalLight.target);
        }
    }
    }

    const color = 0xFFFFFF;
    const intensity = 2.5;
    const light = new Three.DirectionalLight( color, intensity );
    light.castShadow = true;
    light.position.set( - 250, 800, - 850 );
    light.target.position.set( - 550, 40, - 450 );

    light.shadow.bias = - 0.004;
    light.shadow.mapSize.width = 2048;
    light.shadow.mapSize.height = 2048;

    scene.add( light );
    scene.add( light.target );

    const cam = light.shadow.camera;
    cam.near = 1;
    cam.far = 2000;
    cam.left = - 1500;
    cam.right = 1500;
    cam.top = 1500;
    cam.bottom = - 1500;

    const cameraHelper = new Three.CameraHelper( cam );
    scene.add( cameraHelper );
    cameraHelper.visible = false;
    const helper = new Three.DirectionalLightHelper( light, 100 );
    scene.add( helper );
    helper.visible = false;

    const alight = new Three.AmbientLight(0xffffff, 100)
    scene.add(alight)

    const fov = 70
    const camera = new Three.PerspectiveCamera(fov, window.innerWidth / window.innerHeight, 0.1, 1000);
    const controls = new OrbitControls(camera, renderer.domElement)
    camera.lookAt(new Three.Vector3())
    camera.position.z = 15;
    camera.position.y = 2
    camera.position.x = 0


    function animate() {
    requestAnimationFrame(animate);

    renderer.render(scene, camera);
    }

    animate();
</script>

<template>

</template>