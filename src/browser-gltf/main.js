import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);


scene.background = new THREE.Color("#FFFFFF");

const loader = new GLTFLoader();

loader.load('/result.glb', function (gltf) {
  gltf.scene.traverse(obj => {
    if (obj instanceof THREE.Mesh) {
      // obj.material = new THREE.MeshPhongMaterial()
      obj.castShadow = true
    }
  })
  const skyColor = 0xB1E1FF;  // light blue
  const groundColor = 0xB97A20;  // brownish orange
  const intensity = 2;
  const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
  scene.add(light);
  
  var directionalLight = new THREE.DirectionalLight(0xffffff, 10);
  directionalLight.position.set(200, 100, 0);
  directionalLight.castShadow = true;
  scene.add(directionalLight);

  const alight = new THREE.AmbientLight(0xffffff)
  scene.add(alight, 10)

  gltf.scene.scale.set(0.01, 0.01, 0.01)
  gltf.scene.rotation.set(-Math.PI / 2, 0, 0)
  console.log(gltf.scene.position);

  scene.add(gltf.scene);
  scene.position.x = -10

}, undefined, function (error) {

  console.error(error);

});

const alight = new THREE.AmbientLight(0xffffff, 100)
scene.add(alight)

// const light = new THREE.PointLight(0xffffff, 50, 2)
// light.position.set(10, 10, 10)
// light.castShadow = true
// scene.add(light)

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const controls = new OrbitControls(camera, renderer.domElement)
camera.lookAt(new THREE.Vector3())
camera.position.z = 15;
camera.position.y = 3
camera.position.x = 5

const tloader = new THREE.TextureLoader()
tloader.load("/pool.jpg", (texture) => { scene.background = texture })


function animate() {
  requestAnimationFrame(animate);

  renderer.render(scene, camera);
}

animate();

