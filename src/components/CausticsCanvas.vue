<template>
  <canvas ref="canvas" class="caustics-canvas"></canvas>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'

const canvas = ref<HTMLCanvasElement | null>(null)

let renderer: THREE.WebGLRenderer | null = null
let animationId: number | null = null
let resizeObserver: ResizeObserver | null = null
let cleanup: (() => void) | null = null

// Programmatic ripple trigger.
// Coordinates are normalized canvas UV (0..1, 0..1) with (0,0)=top-left.
let rippleAtUv: ((u: number, v: number, radius?: number, strength?: number) => void) | null = null

const rippleAt = (u: number, v: number, radius = 0.04, strength = 0.8) => {
  rippleAtUv?.(u, v, radius, strength)
}

defineExpose({ rippleAt })

// Optional debug hook: call `window.__pondRippleUv(u, v)` from the console.
if (typeof window !== 'undefined') {
  ;(window as any).__pondRippleUv = rippleAt
}

const SIM_SIZE = 512
const CAUSTICS_ATLAS_URL = '/caustics/caustics_atlas_noalpha.png'

const vertexFullscreen = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`

// tSim stores: R=height, G=velocity, B=nx(0..1), A=ny(0..1)
const fragSim = /* glsl */ `
  precision highp float;
  uniform sampler2D tSim;
  uniform vec2 texel;
  uniform float damping;
  varying vec2 vUv;

  float decodeSigned(float v) {
  #ifdef PACKED_8
    return v * 2.0 - 1.0;
  #else
    return v;
  #endif
  }

  float encodeSigned(float v) {
  #ifdef PACKED_8
    return clamp(v * 0.5 + 0.5, 0.0, 1.0);
  #else
    return v;
  #endif
  }

  vec4 encodeOut(float h, float vel, vec2 nxy) {
    return vec4(
      encodeSigned(h),
      encodeSigned(vel),
      nxy.x * 0.5 + 0.5,
      nxy.y * 0.5 + 0.5
    );
  }

  void main() {
    vec4 s = texture2D(tSim, vUv);
    float h = decodeSigned(s.r);
    float v = decodeSigned(s.g);

    float l = decodeSigned(texture2D(tSim, vUv - vec2(texel.x, 0.0)).r);
    float r = decodeSigned(texture2D(tSim, vUv + vec2(texel.x, 0.0)).r);
    float b = decodeSigned(texture2D(tSim, vUv - vec2(0.0, texel.y)).r);
    float t = decodeSigned(texture2D(tSim, vUv + vec2(0.0, texel.y)).r);

    float lap = (l + r + b + t - 4.0 * h);
    v += lap * 1.65;
    v *= damping;
    h += v;

    // Keep values bounded to avoid NaNs/Inf on some GPUs.
    v = clamp(v, -1.0, 1.0);
    h = clamp(h, -1.0, 1.0);

    float dx = r - l;
    float dy = t - b;
    vec3 n = normalize(vec3(-dx, -dy, 1.0));

    gl_FragColor = encodeOut(h, v, n.xy);
  }
`

const fragDrop = /* glsl */ `
  precision highp float;
  uniform sampler2D tSim;
  uniform vec2 center;
  uniform float radius;
  uniform float strength;
  varying vec2 vUv;

  float decodeSigned(float v) {
  #ifdef PACKED_8
    return v * 2.0 - 1.0;
  #else
    return v;
  #endif
  }

  float encodeSigned(float v) {
  #ifdef PACKED_8
    return clamp(v * 0.5 + 0.5, 0.0, 1.0);
  #else
    return v;
  #endif
  }

  vec4 encodeOut(float h, float vel, vec2 nxy) {
    return vec4(
      encodeSigned(h),
      encodeSigned(vel),
      nxy.x * 0.5 + 0.5,
      nxy.y * 0.5 + 0.5
    );
  }

  void main() {
    vec4 s = texture2D(tSim, vUv);
    float h = decodeSigned(s.r);
    float v = decodeSigned(s.g);
    vec2 nxy = s.ba * 2.0 - 1.0;
    float d = distance(vUv, center);
    float a = smoothstep(radius, 0.0, d);
    // Raise/lower height and nudge velocity.
    h += a * strength;
    v += a * strength * 0.45;
    v = clamp(v, -1.0, 1.0);
    h = clamp(h, -1.0, 1.0);
    gl_FragColor = encodeOut(h, v, nxy);
  }
`

const fragInit = /* glsl */ `
  precision highp float;
  varying vec2 vUv;

  float encodeSigned(float v) {
  #ifdef PACKED_8
    return clamp(v * 0.5 + 0.5, 0.0, 1.0);
  #else
    return v;
  #endif
  }

  void main() {
    // h=0, vel=0, nxy=(0,0) -> BA = 0.5
    gl_FragColor = vec4(encodeSigned(0.0), encodeSigned(0.0), 0.5, 0.5);
  }
`

const fragWater = /* glsl */ `
  precision highp float;
  uniform sampler2D tSim;
  uniform sampler2D tCaustics;
  uniform float time;
  uniform vec2 aspect;
  varying vec2 vUv;

  float decodeSigned(float v) {
  #ifdef PACKED_8
    return v * 2.0 - 1.0;
  #else
    return v;
  #endif
  }

  vec3 overlay(vec3 base, vec3 blend) {
    return mix(2.0 * base * blend, 1.0 - 2.0 * (1.0 - base) * (1.0 - blend), step(0.5, base));
  }

  void main() {
    vec4 s = texture2D(tSim, vUv);
    float h = decodeSigned(s.r);
    vec2 nxy = s.ba * 2.0 - 1.0;

    // Distort UV by normals (ripples).
    vec2 distort = nxy * 0.045;

    // Caustics atlas: 4x4 frames.
    float frame = mod(floor(time * 18.0), 16.0);
    vec2 tile = vec2(mod(frame, 4.0), floor(frame / 4.0));

    // Slight scale anisotropy to reduce visible tiling.
    vec2 uv = vUv;
    uv = (uv - 0.5) * vec2(aspect.x, 1.0) + 0.5;

    vec2 caustUv = fract(uv * 1.55 + distort * 0.9 + vec2(time * 0.025, -time * 0.018));
    caustUv = (caustUv + tile) / 4.0;
    float caust = texture2D(tCaustics, caustUv).r;

    vec3 base = vec3(0.06, 0.45, 0.52);
    base += h * 0.22;

    float nMod = clamp(0.55 + 0.45 * (0.5 + 0.5 * nxy.y), 0.0, 1.0);
    float caustI = caust * (0.65 + 0.35 * nMod);
    vec3 caustCol = vec3(0.98, 0.99, 0.92) * caustI;
    vec3 color = overlay(base, caustCol);

    float spec = pow(clamp(1.0 - length(nxy), 0.0, 1.0), 6.0);
    color += spec * 0.06;

    gl_FragColor = vec4(color, 1.0);
  }
`

const makeRt = (w: number, h: number, type: THREE.TextureDataType) => {
  const rt = new THREE.WebGLRenderTarget(w, h, {
    minFilter: THREE.LinearFilter,
    magFilter: THREE.LinearFilter,
    wrapS: THREE.RepeatWrapping,
    wrapT: THREE.RepeatWrapping,
    depthBuffer: false,
    stencilBuffer: false,
    type,
  })
  rt.texture.generateMipmaps = false
  // Avoid gamma conversions affecting simulation textures.
  rt.texture.colorSpace = THREE.NoColorSpace

  // Half/float targets are not guaranteed to be filterable in WebGL1.
  // We'll override these after creation based on extension support.
  return rt
}

const pickSimType = (renderer: THREE.WebGLRenderer) => {
  const isWebGL2 = renderer.capabilities.isWebGL2

  // Rendering into float/half-float targets requires color buffer extensions.
  if (isWebGL2) {
    // If EXT_color_buffer_float exists, half float render targets are generally safe.
    if (renderer.extensions.has('EXT_color_buffer_float')) return THREE.HalfFloatType
    return THREE.UnsignedByteType
  }

  if (
    renderer.extensions.has('OES_texture_half_float') &&
    renderer.extensions.has('EXT_color_buffer_half_float')
  ) {
    return THREE.HalfFloatType
  }

  if (renderer.extensions.has('OES_texture_float') && renderer.extensions.has('WEBGL_color_buffer_float')) {
    return THREE.FloatType
  }
  return THREE.UnsignedByteType
}

const pickFilter = (renderer: THREE.WebGLRenderer, type: THREE.TextureDataType) => {
  if (type === THREE.UnsignedByteType) return THREE.LinearFilter
  if (type === THREE.HalfFloatType) {
    return renderer.capabilities.isWebGL2 || renderer.extensions.has('OES_texture_half_float_linear')
      ? THREE.LinearFilter
      : THREE.NearestFilter
  }
  if (type === THREE.FloatType) {
    return renderer.capabilities.isWebGL2 || renderer.extensions.has('OES_texture_float_linear')
      ? THREE.LinearFilter
      : THREE.NearestFilter
  }
  return THREE.NearestFilter
}

onMounted(async () => {
  if (!canvas.value) return

  const scene = new THREE.Scene()
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)
  camera.position.set(0, 0, 1)
  camera.lookAt(0, 0, 0)
  scene.add(camera)

  renderer = new THREE.WebGLRenderer({ canvas: canvas.value, antialias: true, alpha: true })
  renderer.setClearColor(0x000000, 0)
  renderer.autoClear = false
  renderer.outputColorSpace = THREE.SRGBColorSpace

  const texType = pickSimType(renderer)
  const packed8 = texType === THREE.UnsignedByteType

  const filter = pickFilter(renderer, texType)

  const simA = makeRt(SIM_SIZE, SIM_SIZE, texType)
  const simB = makeRt(SIM_SIZE, SIM_SIZE, texType)
  simA.texture.minFilter = filter
  simA.texture.magFilter = filter
  simB.texture.minFilter = filter
  simB.texture.magFilter = filter
  let simFront = simA
  let simBack = simB

  const quadGeo = new THREE.PlaneGeometry(2, 2)
  const quad = new THREE.Mesh(quadGeo, new THREE.MeshBasicMaterial())
  const simScene = new THREE.Scene()
  simScene.add(quad)
  const simCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)

  const texel = new THREE.Vector2(1 / SIM_SIZE, 1 / SIM_SIZE)

  const simHeader = packed8 ? '#define PACKED_8\n' : ''
  const fragSimSrc = simHeader + fragSim
  const fragDropSrc = simHeader + fragDrop
  const fragInitSrc = simHeader + fragInit
  const fragWaterSrc = simHeader + fragWater

  const matSim = new THREE.ShaderMaterial({
    vertexShader: vertexFullscreen,
    fragmentShader: fragSimSrc,
    uniforms: {
      tSim: { value: simFront.texture },
      texel: { value: texel },
      damping: { value: 0.985 },
    },
  })

  const matDrop = new THREE.ShaderMaterial({
    vertexShader: vertexFullscreen,
    fragmentShader: fragDropSrc,
    uniforms: {
      tSim: { value: simFront.texture },
      center: { value: new THREE.Vector2(0.5, 0.5) },
      radius: { value: 0.04 },
      strength: { value: 0.8 },
    },
  })

  const matInit = new THREE.ShaderMaterial({
    vertexShader: vertexFullscreen,
    fragmentShader: fragInitSrc,
  })

  const texLoader = new THREE.TextureLoader()
  const causticsTex = await new Promise<THREE.Texture>((resolve, reject) => {
    texLoader.load(
      CAUSTICS_ATLAS_URL,
      (t) => {
        t.wrapS = THREE.RepeatWrapping
        t.wrapT = THREE.RepeatWrapping
        t.minFilter = THREE.LinearFilter
        t.magFilter = THREE.LinearFilter
        t.generateMipmaps = false
        t.colorSpace = THREE.SRGBColorSpace
        resolve(t)
      },
      undefined,
      reject
    )
  })

  const waterMat = new THREE.ShaderMaterial({
    vertexShader: vertexFullscreen,
    fragmentShader: fragWaterSrc,
    uniforms: {
      tSim: { value: simFront.texture },
      tCaustics: { value: causticsTex },
      time: { value: 0 },
      aspect: { value: new THREE.Vector2(1, 1) },
    },
  })

  const waterMesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), waterMat)
  scene.add(waterMesh)

  const swapSim = () => {
    const tmp = simFront
    simFront = simBack
    simBack = tmp
  }

  const renderToSim = (mat: THREE.Material) => {
    if (!renderer) return
    quad.material = mat
    renderer.setRenderTarget(simBack)
    renderer.render(simScene, simCam)
    renderer.setRenderTarget(null)
    swapSim()
  }

  const initTarget = (target: THREE.WebGLRenderTarget) => {
    if (!renderer) return
    const oldTarget = renderer.getRenderTarget()
    quad.material = matInit
    renderer.setRenderTarget(target)
    renderer.render(simScene, simCam)
    renderer.setRenderTarget(oldTarget)
  }

  rippleAtUv = (u: number, v: number, radius = 0.04, strength = 0.8) => {
    matDrop.uniforms.tSim.value = simFront.texture
    ;(matDrop.uniforms.center.value as THREE.Vector2).set(u, 1 - v)
    matDrop.uniforms.radius.value = radius
    matDrop.uniforms.strength.value = strength
    renderToSim(matDrop)
  }

  const resize = () => {
    if (!canvas.value || !renderer) return
    const rect = canvas.value.getBoundingClientRect()
    const aspect = rect.width / rect.height || 1

    // Keep the visible area inside the fixed 2x2 plane ([-1,1] x [-1,1])
    // so edges are always out of frame.
    if (aspect >= 1) {
      camera.left = -1
      camera.right = 1
      camera.top = 1 / aspect
      camera.bottom = -1 / aspect
    } else {
      camera.left = -aspect
      camera.right = aspect
      camera.top = 1
      camera.bottom = -1
    }
    camera.updateProjectionMatrix()

    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    renderer.setPixelRatio(dpr)
    renderer.setSize(rect.width, rect.height, false)
    ;(waterMat.uniforms.aspect.value as THREE.Vector2).set(aspect, 1)
  }

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(canvas.value)
  resize()

  // Init sim buffers to a known state (avoids undefined/NaNs on some GPUs).
  initTarget(simA)
  initTarget(simB)

  // Seed a few ripples.
  for (let i = 0; i < 8; i += 1) {
    rippleAtUv(Math.random(), Math.random(), 0.03 + Math.random() * 0.03, (Math.random() * 2 - 1) * 0.9)
  }

  const clock = new THREE.Clock()
  const animate = () => {
    if (!renderer) return
    animationId = window.requestAnimationFrame(animate)

    // Two fixed steps per frame keeps it stable and lively.
    for (let i = 0; i < 2; i += 1) {
      matSim.uniforms.tSim.value = simFront.texture
      renderToSim(matSim)
    }

    waterMat.uniforms.tSim.value = simFront.texture
    waterMat.uniforms.time.value = clock.getElapsedTime()

    renderer.setRenderTarget(null)
    renderer.setClearColor(0x000000, 0)
    renderer.clear()
    renderer.render(scene, camera)
  }

  animationId = window.requestAnimationFrame(animate)

  cleanup = () => {
    if (animationId) window.cancelAnimationFrame(animationId)
    animationId = null

    if (resizeObserver && canvas.value) resizeObserver.unobserve(canvas.value)
    resizeObserver = null
    rippleAtUv = null

    quadGeo.dispose()
    ;(quad.material as THREE.Material).dispose()

    matSim.dispose()
    matDrop.dispose()
    matInit.dispose()
    waterMat.dispose()
    ;(waterMesh.geometry as THREE.BufferGeometry).dispose()
    causticsTex.dispose()

    simA.dispose()
    simB.dispose()

    renderer?.dispose()
    renderer = null
  }
})

onBeforeUnmount(() => {
  cleanup?.()
  cleanup = null
})
</script>
