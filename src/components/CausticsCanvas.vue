<template>
  <canvas ref="canvas" class="caustics-canvas"></canvas>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

import waterVertex from '../../Caustics/threejs-caustics-master/shaders/water/vertex.glsl?raw'
import waterFragment from '../../Caustics/threejs-caustics-master/shaders/water/fragment.glsl?raw'
import envVertex from '../../Caustics/threejs-caustics-master/shaders/environment/vertex.glsl?raw'
import envFragment from '../../Caustics/threejs-caustics-master/shaders/environment/fragment.glsl?raw'
import envMapVertex from '../../Caustics/threejs-caustics-master/shaders/environment_mapping/vertex.glsl?raw'
import envMapFragment from '../../Caustics/threejs-caustics-master/shaders/environment_mapping/fragment.glsl?raw'
import simVertex from '../../Caustics/threejs-caustics-master/shaders/simulation/vertex.glsl?raw'
import simDropFragment from '../../Caustics/threejs-caustics-master/shaders/simulation/drop_fragment.glsl?raw'
import simUpdateFragment from '../../Caustics/threejs-caustics-master/shaders/simulation/update_fragment.glsl?raw'
import causticsVertex from '../../Caustics/threejs-caustics-master/shaders/caustics/water_vertex.glsl?raw'
import causticsFragment from '../../Caustics/threejs-caustics-master/shaders/caustics/water_fragment.glsl?raw'

const canvas = ref<HTMLCanvasElement | null>(null)
let renderer: THREE.WebGLRenderer | null = null
let animationId: number | null = null
let resizeObserver: ResizeObserver | null = null
let mouseMoveHandler: ((event: MouseEvent) => void) | null = null

// Debug-only ripple trigger. In the final app you'll likely call this
// programmatically instead of relying on pointer events.
let triggerRippleAt: ((x: number, y: number, radius?: number, strength?: number) => void) | null = null

// Programmatic ripple trigger.
// Coordinates are in the same plane space as the simulation: x/y in [-1, 1].
const rippleAt = (x: number, y: number, radius = 0.03, strength = 0.02) => {
  triggerRippleAt?.(x, y, radius, strength)
}

defineExpose({ rippleAt })

// Optional debug hook: call `window.__pondRipple(x, y)` from the console.
if (typeof window !== 'undefined') {
  ;(window as any).__pondRipple = rippleAt
}

const waterSize = 512
const waterPosition = new THREE.Vector3(0, 0, 0.8)
const near = 0
const far = 2

// Make the water plane large and keep the camera close.
// This avoids seeing the plane edges even with a perspective camera.
const waterWorldScale = 60

const black = new THREE.Color('black')
const white = new THREE.Color('white')

const light = [0, 0, -1]
const lightCamera = new THREE.OrthographicCamera(-1.2, 1.2, 1.2, -1.2, near, far)
lightCamera.position.set(0, 0, 1.5)
lightCamera.lookAt(0, 0, 0)

const loadSkybox = () => {
  const loader = new THREE.CubeTextureLoader()
  return loader.load([
    '/skybox_px.jpg',
    '/skybox_nx.jpg',
    '/skybox_py.jpg',
    '/skybox_ny.jpg',
    '/skybox_pz.jpg',
    '/skybox_nz.jpg',
  ])
}

class WaterSimulation {
  camera = new THREE.OrthographicCamera(0, 1, 1, 0, 0, 2000)
  geometry = new THREE.PlaneGeometry(2, 2)
  targetA = new THREE.WebGLRenderTarget(waterSize, waterSize, { type: THREE.FloatType })
  targetB = new THREE.WebGLRenderTarget(waterSize, waterSize, { type: THREE.FloatType })
  target = this.targetA
  dropMesh: THREE.Mesh
  updateMesh: THREE.Mesh

  constructor() {
    // Prevent edge pinching in the height field when sampling neighbors.
    for (const t of [this.targetA, this.targetB]) {
      t.texture.wrapS = THREE.MirroredRepeatWrapping
      t.texture.wrapT = THREE.MirroredRepeatWrapping
      t.texture.minFilter = THREE.LinearFilter
      t.texture.magFilter = THREE.LinearFilter
      t.texture.generateMipmaps = false
    }

    const dropMaterial = new THREE.RawShaderMaterial({
      uniforms: {
        center: { value: [0, 0] },
        radius: { value: 0 },
        strength: { value: 0 },
        texture: { value: null },
      },
      vertexShader: simVertex,
      fragmentShader: simDropFragment,
    })

    const updateMaterial = new THREE.RawShaderMaterial({
      uniforms: {
        delta: { value: [1 / 216, 1 / 216] },
        texture: { value: null },
      },
      vertexShader: simVertex,
      fragmentShader: simUpdateFragment,
    })

    this.dropMesh = new THREE.Mesh(this.geometry, dropMaterial)
    this.updateMesh = new THREE.Mesh(this.geometry, updateMaterial)
  }

  addDrop(renderer: THREE.WebGLRenderer, x: number, y: number, radius: number, strength: number) {
    this.dropMesh.material.uniforms.center.value = [x, y]
    this.dropMesh.material.uniforms.radius.value = radius
    this.dropMesh.material.uniforms.strength.value = strength
    this.render(renderer, this.dropMesh)
  }

  step(renderer: THREE.WebGLRenderer) {
    this.render(renderer, this.updateMesh)
  }

  render(renderer: THREE.WebGLRenderer, mesh: THREE.Mesh) {
    const oldTarget = renderer.getRenderTarget()
    const nextTarget = this.target === this.targetA ? this.targetB : this.targetA
    renderer.setRenderTarget(nextTarget)
    mesh.material.uniforms.texture.value = this.target.texture
    renderer.render(mesh, this.camera)
    renderer.setRenderTarget(oldTarget)
    this.target = nextTarget
  }
}

class Water {
  mesh: THREE.Mesh
  material: THREE.ShaderMaterial

  constructor(skybox: THREE.CubeTexture) {
    const geometry = new THREE.PlaneGeometry(2, 2, waterSize, waterSize)
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        light: { value: light },
        water: { value: null },
        envMap: { value: null },
        skybox: { value: skybox },
      },
      vertexShader: waterVertex,
      fragmentShader: waterFragment,
    })
    this.material.extensions = { derivatives: true }
    this.mesh = new THREE.Mesh(geometry, this.material)
    this.mesh.position.set(waterPosition.x, waterPosition.y, waterPosition.z)
  }

  setHeightTexture(texture: THREE.Texture) {
    this.material.uniforms.water.value = texture
  }

  setEnvMapTexture(texture: THREE.Texture) {
    this.material.uniforms.envMap.value = texture
  }
}

class EnvironmentMap {
  size = 1024
  target = new THREE.WebGLRenderTarget(this.size, this.size, { type: THREE.FloatType })
  material = new THREE.ShaderMaterial({
    vertexShader: envMapVertex,
    fragmentShader: envMapFragment,
  })
  meshes: THREE.Mesh[] = []

  constructor() {
    // Avoid edge artifacts when caustics sample outside [0, 1].
    this.target.texture.wrapS = THREE.MirroredRepeatWrapping
    this.target.texture.wrapT = THREE.MirroredRepeatWrapping
    this.target.texture.minFilter = THREE.LinearFilter
    this.target.texture.magFilter = THREE.LinearFilter
    this.target.texture.generateMipmaps = false
  }

  setGeometries(geometries: THREE.BufferGeometry[]) {
    this.meshes = geometries.map((geometry) => new THREE.Mesh(geometry, this.material))
  }

  render(renderer: THREE.WebGLRenderer) {
    const oldTarget = renderer.getRenderTarget()
    renderer.setRenderTarget(this.target)
    renderer.setClearColor(black, 0)
    renderer.clear()
    this.meshes.forEach((mesh) => renderer.render(mesh, lightCamera))
    renderer.setRenderTarget(oldTarget)
  }
}

class Caustics {
  target = new THREE.WebGLRenderTarget(waterSize * 3, waterSize * 3, { type: THREE.FloatType })
  material: THREE.ShaderMaterial
  mesh: THREE.Mesh

  constructor() {
    // Avoid edge artifacts when the environment shader samples the caustics map.
    this.target.texture.wrapS = THREE.MirroredRepeatWrapping
    this.target.texture.wrapT = THREE.MirroredRepeatWrapping
    this.target.texture.minFilter = THREE.LinearFilter
    this.target.texture.magFilter = THREE.LinearFilter
    this.target.texture.generateMipmaps = false

    const geometry = new THREE.PlaneGeometry(2, 2, waterSize, waterSize)
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        light: { value: light },
        env: { value: null },
        water: { value: null },
        deltaEnvTexture: { value: null },
      },
      vertexShader: causticsVertex,
      fragmentShader: causticsFragment,
      transparent: true,
    })

    this.material.blending = THREE.CustomBlending
    this.material.blendEquation = THREE.AddEquation
    this.material.blendSrc = THREE.OneFactor
    this.material.blendDst = THREE.OneFactor
    this.material.blendEquationAlpha = THREE.AddEquation
    this.material.blendSrcAlpha = THREE.OneFactor
    this.material.blendDstAlpha = THREE.ZeroFactor
    this.material.side = THREE.DoubleSide
    this.material.extensions = { derivatives: true }

    this.mesh = new THREE.Mesh(geometry, this.material)
  }

  setTextures(waterTexture: THREE.Texture, envTexture: THREE.Texture) {
    this.material.uniforms.env.value = envTexture
    this.material.uniforms.water.value = waterTexture
  }

  setDeltaEnvTexture(value: number) {
    this.material.uniforms.deltaEnvTexture.value = value
  }

  render(renderer: THREE.WebGLRenderer) {
    const oldTarget = renderer.getRenderTarget()
    renderer.setRenderTarget(this.target)
    renderer.setClearColor(black, 0)
    renderer.clear()
    renderer.render(this.mesh, lightCamera)
    renderer.setRenderTarget(oldTarget)
  }
}

class Environment {
  material: THREE.ShaderMaterial
  meshes: THREE.Mesh[] = []

  constructor() {
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        light: { value: light },
        caustics: { value: null },
        lightProjectionMatrix: { value: lightCamera.projectionMatrix },
        lightViewMatrix: { value: lightCamera.matrixWorldInverse },
      },
      vertexShader: envVertex,
      fragmentShader: envFragment,
    })
  }

  setGeometries(geometries: THREE.BufferGeometry[]) {
    this.meshes = geometries.map((geometry) => new THREE.Mesh(geometry, this.material))
  }

  updateCaustics(texture: THREE.Texture) {
    this.material.uniforms.caustics.value = texture
  }

  addTo(scene: THREE.Scene) {
    this.meshes.forEach((mesh) => scene.add(mesh))
  }
}

onMounted(async () => {
  if (!canvas.value) return

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(38, 1, 0.01, 50)
  camera.position.set(0, 0, 2.0)
  camera.up.set(0, 1, 0)
  camera.lookAt(0, 0, waterPosition.z)
  scene.add(camera)

  renderer = new THREE.WebGLRenderer({ canvas: canvas.value, antialias: true, alpha: true })
  renderer.autoClear = false

  const controls = new OrbitControls(camera, canvas.value)
  controls.enablePan = false
  controls.enableRotate = false
  controls.enableZoom = false
  controls.target = waterPosition

  const skybox = loadSkybox()
  scene.background = skybox

  const waterSimulation = new WaterSimulation()
  const water = new Water(skybox)
  const environmentMap = new EnvironmentMap()
  const environment = new Environment()
  const caustics = new Caustics()

  water.mesh.scale.set(waterWorldScale, waterWorldScale, 1)

  const floorGeometry = new THREE.PlaneGeometry(1000, 1000, 1, 1)
  environmentMap.setGeometries([floorGeometry])
  environment.setGeometries([floorGeometry])
  environment.addTo(scene)
  scene.add(water.mesh)
  caustics.setDeltaEnvTexture(1 / environmentMap.size)

  const renderTarget = new THREE.WebGLRenderTarget(1, 1)
  // When refraction samples outside the rendered envMap, default clamp-to-edge
  // produces a visible boundary. Mirrored repeat hides that edge.
  renderTarget.texture.wrapS = THREE.MirroredRepeatWrapping
  renderTarget.texture.wrapT = THREE.MirroredRepeatWrapping
  renderTarget.texture.minFilter = THREE.LinearFilter
  renderTarget.texture.magFilter = THREE.LinearFilter
  renderTarget.texture.generateMipmaps = false
  let targetMesh: THREE.Mesh | null = null

  const resize = () => {
    if (!canvas.value || !renderer) return
    const rect = canvas.value.getBoundingClientRect()
    const aspect = rect.width / rect.height || 1

    camera.aspect = aspect
    camera.updateProjectionMatrix()

    // Keep the light camera wide enough for caustics across the view.
    lightCamera.left = -1.6 * aspect
    lightCamera.right = 1.6 * aspect
    lightCamera.top = 1.6
    lightCamera.bottom = -1.6
    lightCamera.updateProjectionMatrix()

    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    renderer.setPixelRatio(dpr)
    renderer.setSize(rect.width, rect.height, false)
    renderTarget.setSize(Math.max(1, Math.floor(rect.width * dpr)), Math.max(1, Math.floor(rect.height * dpr)))
  }

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(canvas.value)
  resize()

  for (let i = 0; i < 5; i += 1) {
    waterSimulation.addDrop(
      renderer,
      Math.random() * 2 - 1,
      Math.random() * 2 - 1,
      0.03,
      (i % 2 === 0 ? 1 : -1) * 0.02
    )
  }

  const raycaster = new THREE.Raycaster()
  const mouse = new THREE.Vector2()
  const targetGeometry = new THREE.PlaneGeometry(2, 2)
  const positions = targetGeometry.attributes.position
  for (let i = 0; i < positions.count; i += 1) {
    positions.setZ(i, waterPosition.z)
  }
  positions.needsUpdate = true
  targetMesh = new THREE.Mesh(targetGeometry)
  targetMesh.position.set(0, 0, 0)
  targetMesh.scale.set(waterWorldScale, waterWorldScale, 1)

  triggerRippleAt = (x: number, y: number, radius = 0.03, strength = 0.02) => {
    if (!renderer) return
    waterSimulation.addDrop(renderer, x, y, radius, strength)
  }

  const onMouseMove = (event: MouseEvent) => {
    if (!canvas.value) return
    const rect = canvas.value.getBoundingClientRect()
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -(((event.clientY - rect.top) / rect.height) * 2 - 1)
    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObject(targetMesh)
    intersects.forEach((intersect) => {
      triggerRippleAt?.(intersect.point.x / waterWorldScale, intersect.point.y / waterWorldScale)
    })
  }

  mouseMoveHandler = onMouseMove
  canvas.value.addEventListener('click', onMouseMove)

  const clock = new THREE.Clock()

  const animate = () => {
    if (!renderer) return
    animationId = window.requestAnimationFrame(animate)

    if (clock.getElapsedTime() > 0.032) {
      waterSimulation.step(renderer)
      const waterTexture = waterSimulation.target.texture
      water.setHeightTexture(waterTexture)

      environmentMap.render(renderer)
      const envTexture = environmentMap.target.texture

      caustics.setTextures(waterTexture, envTexture)
      caustics.render(renderer)
      environment.updateCaustics(caustics.target.texture)
      clock.start()
    }

    renderer.setRenderTarget(renderTarget)
    renderer.setClearColor(white, 1)
    renderer.clear()

    water.mesh.visible = false
    renderer.render(scene, camera)

    water.setEnvMapTexture(renderTarget.texture)

    renderer.setRenderTarget(null)
    renderer.setClearColor(white, 1)
    renderer.clear()
    water.mesh.visible = true
    renderer.render(scene, camera)

    controls.update()
  }

  animationId = window.requestAnimationFrame(animate)
})

onBeforeUnmount(() => {
  if (animationId) window.cancelAnimationFrame(animationId)
  if (resizeObserver && canvas.value) resizeObserver.unobserve(canvas.value)
  if (canvas.value && mouseMoveHandler) canvas.value.removeEventListener('click', mouseMoveHandler)
  if (renderer) renderer.dispose()
  triggerRippleAt = null
})
</script>
