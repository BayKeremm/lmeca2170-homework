import {
    BoxGeometry,
    Color,
    Mesh,
    InstancedMesh,
    MeshStandardMaterial,
    PlaneGeometry, SphereGeometry,
    PerspectiveCamera,
    Scene,
    WebGLRenderer,
    Box3, Vector3, Matrix4, Matrix3, Quaternion,
    TextureLoader,
    PointLight
} from 'three';

import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

const container = document.querySelector('#scene');

const scene = new Scene();

const fov = 90;
const aspect = container.clientWidth / container.clientHeight;
const near = 0.01;
const far = 500;

const camera = new PerspectiveCamera(fov, aspect, near, far);

camera.position.set(0, 0, 0);

const renderer = new WebGLRenderer();
renderer.setClearColor(0xffffff, 0);
renderer.shadowMap.enabled = true;

renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio);

container.append(renderer.domElement);
const controls = new PointerLockControls(camera, renderer.domElement);

let holdingForward  = false;
let holdingBackward = false;
let holdingLeft  = false;
let holdingRight = false;
let holdingUp   = false;
let holdingDown = false;

container.addEventListener("click", (_ev) => {
    if (controls.isLocked)
        controls.unlock();
    else
        controls.lock();
});

window.addEventListener("keyup", (ev) => {
    if (ev.key == "ArrowLeft") holdingLeft = false;
    if (ev.key == "ArrowUp") holdingForward = false;
    if (ev.key == "ArrowRight") holdingRight = false;
    if (ev.key == "ArrowDown") holdingBackward = false;
    if (ev.key == " ") holdingUp = false;
    if (ev.key == "Shift") holdingDown = false;
});

window.addEventListener("keydown", (ev) => {
    if (ev.key == "ArrowLeft") holdingLeft = true;
    if (ev.key == "ArrowUp") holdingForward = true;
    if (ev.key == "ArrowRight") holdingRight = true;
    if (ev.key == "ArrowDown") holdingBackward = true;
    if (ev.key == " ") holdingUp = true;
    if (ev.key == "Shift") holdingDown = true;
});

const connection = new WebSocket("ws://localhost:9345");
connection.binaryType = 'arraybuffer';

const connectionEstablished = new Promise((resolve, reject) => {
    if (connection.readyState == WebSocket.OPEN)
        resolve();
    else {
        const onError = () => { reject(); };
        connection.addEventListener("error", onError);

        connection.addEventListener("open", () => {
            connection.removeEventListener("error", onError);
            resolve();
        });
    }
});

class MessageQueue {
    constructor(socket) {
        this.socket = socket;

        this.receivedMessages = [];
        this.waitingCallbacks = [];

        socket.addEventListener("message", (msg) => {
            this.receivedMessages.push(msg);
            while (this.receivedMessages.length > 0 &&
                   this.waitingCallbacks.length > 0) {
                this.waitingCallbacks.shift()(this.receivedMessages.shift());
            }
        });
    }

    async nextMessage() {
        if (this.receivedMessages.length > 0 && this.waitingCallbacks == 0)
            return this.receivedMessages.shift();
        else
            return new Promise((resolve) => { this.waitingCallbacks.push(resolve); });
    }
}

const messageQueue = new MessageQueue(connection);

function computeAxis(x, y, z) {
    const world = new Vector3(x, y, z).applyMatrix4(camera.matrixWorld);
    return world.sub(camera.position).normalize();
}

const sphereGeometry = new SphereGeometry(1.0, 32, 16);
const planeGeometry = new PlaneGeometry(1, 1);

const DOMAIN_SIZE = 10.0;

{
    const light = new PointLight(0xffffff, 16.0);
    light.position.set(-DOMAIN_SIZE * 0.8, DOMAIN_SIZE * 0.8, -DOMAIN_SIZE * 0.8);
    scene.add(light);
}

{
    const light = new PointLight(0xffffff, 16.0);
    light.position.set(-DOMAIN_SIZE * 0.8, DOMAIN_SIZE * 0.8, +DOMAIN_SIZE * 0.8);
    scene.add(light);
}

{
    const light = new PointLight(0xffffff, 16.0);
    light.position.set(+DOMAIN_SIZE * 0.8, DOMAIN_SIZE * 0.8, -DOMAIN_SIZE * 0.8);
    scene.add(light);
}

{
    const light = new PointLight(0xffffff, 16.0);
    light.position.set(+DOMAIN_SIZE * 0.8, DOMAIN_SIZE * 0.8, +DOMAIN_SIZE * 0.8);
    scene.add(light);
}

{
    const light = new PointLight(0xffffff, 64.0);
    light.position.set(0, DOMAIN_SIZE * 0.8, 0);
    scene.add(light);
    light.castShadow = true;
}

{
    const light = new PointLight(0xffffff, 64.0);
    light.position.set(0, -DOMAIN_SIZE * 0.8, 0);
    scene.add(light);
    light.castShadow = true;
}

const planeNegX = new Mesh(
    planeGeometry,
    new MeshStandardMaterial({
        color: 0x813d9c,
        roughness: 0.42,
    }));
planeNegX.position.set(-DOMAIN_SIZE, 0, 0);
planeNegX.lookAt(new Vector3(0, 0, 0));
planeNegX.scale.set(2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE);
planeNegX.receiveShadow = true;
scene.add(planeNegX);

const planePosX = new Mesh(
    planeGeometry,
    new MeshStandardMaterial({
        color: 0x2ec27e,
        roughness: 0.42,
    }));
planePosX.receiveShadow = true;
planePosX.position.set(+DOMAIN_SIZE, 0, 0);
planePosX.lookAt(new Vector3(0, 0, 0));
planePosX.scale.set(2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE);
scene.add(planePosX);

const planeNegY = new Mesh(
    planeGeometry,
    new MeshStandardMaterial({
        color: 0xc0bfbc,
        roughness: 0.42,
    }));
planeNegY.receiveShadow = true;
planeNegY.position.set(0, -DOMAIN_SIZE, 0);
planeNegY.lookAt(new Vector3(0, 0, 0));
planeNegY.scale.set(2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE);
scene.add(planeNegY);

const planePosY = new Mesh(
    planeGeometry,
    new MeshStandardMaterial({
        color: 0xf5c211,
        roughness: 0.2,
        metallic: 1.0,
    }));
planePosY.receiveShadow = true;
planePosY.position.set(0, +DOMAIN_SIZE, 0);
planePosY.lookAt(new Vector3(0, 0, 0));
planePosY.scale.set(2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE);
scene.add(planePosY);

const planeNegZ = new Mesh(
    planeGeometry,
    new MeshStandardMaterial({
        color: 0x1c71d8,
        roughness: 0.42,
    }));
planeNegZ.receiveShadow = true;
planeNegZ.position.set(0, 0, -DOMAIN_SIZE);
planeNegZ.lookAt(new Vector3(0, 0, 0));
planeNegZ.scale.set(2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE);
scene.add(planeNegZ);

const planePosZ = new Mesh(
    planeGeometry,
    new MeshStandardMaterial({
        color: 0xc01c28,
        roughness: 0.42,
    }));
planePosZ.receiveShadow = true;
planePosZ.position.set(0, 0, +DOMAIN_SIZE);
planePosZ.lookAt(new Vector3(0, 0, 0));
planePosZ.scale.set(2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE, 2 * DOMAIN_SIZE);
scene.add(planePosZ);

const radii = [];
const texture =  new TextureLoader().load('images/texture.png');

let instancedSpheres = new InstancedMesh(
    sphereGeometry,
    new MeshStandardMaterial({
        color: 0xFFFFFF, roughness: 0.1, map: texture
    }),
    0
)

function colorForSphere(i, n) {
    return new Color().setHSL(i / n, 0.5, 0.5);
}

async function addSpheres(n, averageRadius) {
    await connectionEstablished;

    const oldSpheres = instancedSpheres;
    instancedSpheres = new InstancedMesh(
        sphereGeometry,
        oldSpheres.material,
        oldSpheres.count + n
    );

    instancedSpheres.castShadow = true;
    instancedSpheres.receiveShadow = true;

    scene.remove(oldSpheres);
    scene.add(instancedSpheres);

    const mat = new Matrix4();
    const col = new Color();
    for (let i = 0; i < oldSpheres.count; i++) {
        oldSpheres.getMatrixAt(i, mat)
        instancedSpheres.setMatrixAt(i, mat);

        oldSpheres.getColorAt(i, col)
        instancedSpheres.setColorAt(i, col);
    }

    const newPositions = [];
    const newRotations = [];
    const newRadii = [];

    for (let i = 0; i < n; i++) {
        const radius = averageRadius * (0.5 + Math.random());
        radii.push(radius);

        const x = 2 * (DOMAIN_SIZE - radius) * Math.random() - DOMAIN_SIZE;
        const y = 2 * (DOMAIN_SIZE - radius) * Math.random() - DOMAIN_SIZE;
        const z = 2 * (DOMAIN_SIZE - radius) * Math.random() - DOMAIN_SIZE;

        instancedSpheres.setMatrixAt(oldSpheres.count + i, new Matrix4().compose(
            new Vector3(x, y, z),
            new Quaternion(),
            new Vector3(radius, radius, radius)
        ))

        instancedSpheres.setColorAt(oldSpheres.count + i, colorForSphere(i, n));

        newPositions.push([x, y, z]);
        newRotations.push([0, 0, 0, 1]);
        newRadii.push(radius);
    }

    connection.send(JSON.stringify({
        "command": "add-objects",
        "positions": newPositions,
        "rotations": newRotations,
        "scales": newRadii
    }));

    instancedSpheres.instanceColor.needsUpdate = true;
    instancedSpheres.instanceMatrix.needsUpdate = true;

    oldSpheres.dispose();
}

addSpheres(20, 1.5);

document.querySelector("#spawn").addEventListener("click", () => {
    const n = parseInt(document.querySelector("#number").value || "20");
    const radius = parseFloat(document.querySelector("#radius").value || "1.0");
    addSpheres(n, radius);
});

scene.add(camera);

let clientWidth = container.clientWidth;
let clientHeight = container.clientHeight;
let pixelRatio = window.devicePixelRatio;

let lastTimestamp = null;

async function renderScene(renderer, scene, camera, timestamp) {
    await connectionEstablished;

    connection.send(JSON.stringify({"command": "step", "timestamp": timestamp / 1000.0}));

    if (clientWidth != container.clientWidth ||
        clientHeight != container.clientHeight) {
        renderer.setSize(container.clientWidth, container.clientHeight);

        clientWidth = container.clientWidth;
        clientHeight = container.clientHeight;

	camera.aspect = clientWidth / clientHeight;
	camera.updateProjectionMatrix();
    }

    if (pixelRatio != window.devicePixelRatio) {
        renderer.setPixelRatio(window.devicePixelRatio);
        pixelRatio = window.devicePixelRatio;
    }

    const cameraVelocity = 10.0;
    if (lastTimestamp) {
        let distance = Math.min(cameraVelocity * (timestamp - lastTimestamp) / 1000.0, 10.0);

        if (holdingForward)
            camera.position.add(computeAxis(0, 0, -1.0).multiplyScalar(distance));
        if (holdingBackward)
            camera.position.add(computeAxis(0, 0, +1.0).multiplyScalar(distance));

        if (holdingLeft)
            camera.position.add(computeAxis(-1.0, 0, 0.0).multiplyScalar(distance));
        if (holdingRight)
            camera.position.add(computeAxis(+1.0, 0, 0.0).multiplyScalar(distance));

        if (holdingUp)
            camera.position.add(computeAxis(0.0, +1.0, 0.0).multiplyScalar(distance));
        if (holdingDown)
            camera.position.add(computeAxis(0.0, -1.0, 0.0).multiplyScalar(distance));
    }

    lastTimestamp = timestamp;

    /* This assumes the WebSocket server is running on the same host, with the
     * same endianness. */
    const msg = await messageQueue.nextMessage();
    const positions = new Float32Array(msg.data);
    const rotations = new Float32Array((await messageQueue.nextMessage()).data);

    const pos = new Vector3();
    const quat = new Quaternion();
    const scale = new Vector3();
    const mat = new Matrix4();

    radii.forEach((radius, i) => {
        pos.fromArray(positions, 3 * i);
        quat.fromArray(rotations, 4 * i);
        scale.set(radius, radius, radius);
        instancedSpheres.setMatrixAt(i, mat.compose(pos, quat, scale));
    });

    instancedSpheres.instanceMatrix.needsUpdate = true;

    renderer.render(scene, camera);
    requestAnimationFrame((timestamp) => {
        renderScene(renderer, scene, camera, timestamp)
    });
}

requestAnimationFrame((timestamp) => renderScene(renderer, scene, camera, timestamp));
