import * as three from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new three.Scene();

const renderer = new three.WebGLRenderer( {antialias: true} );
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);


// scene.background = new three.Color("#FFFFFF");
scene.background = new three.Color("#DEFEFF")
// scene.background = new three.Color("black")

const loader = new GLTFLoader();

loader.load('/result.glb', function (gltf) {
  gltf.scene.traverse(obj => {
    if (obj instanceof three.Mesh) {
      // obj.material = new three.MeshPhongMaterial()
      obj.castShadow = true
      obj.receiveShadow = false;
    }
  })
  gltf.scene.scale.set(0.01, 0.01, 0.01)
  gltf.scene.rotation.set(-Math.PI / 2, 0, 0)
  console.log(gltf.scene.position);

  scene.add(gltf.scene);
  scene.position.x = -5

}, undefined, function (error) {

  console.error(error);

});

{
  const skyColor = 0xB1E1FF;  // light blue
  const groundColor = 0xB97A20;  // brownish orange
  const intensity = 2;
  const light = new three.HemisphereLight(skyColor, groundColor, intensity);
  scene.add(light);
}

for (let i = -1; i <= 1; i++) {
  for (let j = -1; j <= 1; j++) {
    for (let k = -1; k <= 1; k++) {
      const color = 0xFF_FF_FF;
      const intensity = 0.3;
      const directionalLight = new three.DirectionalLight(color, intensity);
      directionalLight.position.set(i, j, k);
      scene.add(directionalLight);
      scene.add(directionalLight.target);
    }
  }
}

const color = 0xFFFFFF;
const intensity = 2.5;
const light = new three.DirectionalLight( color, intensity );
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

const cameraHelper = new three.CameraHelper( cam );
scene.add( cameraHelper );
cameraHelper.visible = false;
const helper = new three.DirectionalLightHelper( light, 100 );
scene.add( helper );
helper.visible = false;




const alight = new three.AmbientLight(0xffffff, 100)
scene.add(alight)

// const light = new three.PointLight(0xffffff, 50, 2)
// light.position.set(10, 10, 10)
// light.castShadow = true
// scene.add(light)

const fov = 70
const camera = new three.PerspectiveCamera(fov, window.innerWidth / window.innerHeight, 0.1, 1000);
const controls = new OrbitControls(camera, renderer.domElement)
camera.lookAt(new three.Vector3())
camera.position.z = 15;
camera.position.y = 4
camera.position.x = 5

// const tloader = new three.TextureLoader()
// tloader.load("/pool.jpg", (texture) => { scene.background = texture })
// scene.background = three.Color('#FF0000')


function animate() {
  requestAnimationFrame(animate);

  renderer.render(scene, camera);
}

animate();

