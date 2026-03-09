import { useRef, useState, useEffect, useCallback } from 'react'
import { Canvas, useThree, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import { useStore } from '../store/useStore'
import { useFlyControls } from '../hooks/useFlyControls'
import { ModelLoader } from './ModelLoader'
import { SunLight } from './SunLight'
import { SunMarker } from './SunMarker'
import { CompassRose } from './CompassRose'
import { FloorPlanMode } from './FloorPlanMode'
import { MeasureTool } from './MeasureTool'
import RoomLabels from './RoomLabels'
import { ScreenshotCapture } from './ScreenshotCapture'
import { SceneExporter } from './SceneExporter'

function SceneContent({ canvasRef }: { canvasRef: React.RefObject<HTMLCanvasElement | null> }) {
  const { camera, scene } = useThree()
  const controlsRef = useRef<any>(null)
  const flyMode = useStore(s => s.flyMode)
  const gridVisible = useStore(s => s.gridVisible)
  const sunPanelOpen = useStore(s => s.sunPanelOpen)
  const floorPlanMode = useStore(s => s.floorPlanMode)

  const [modelCenter, setModelCenter] = useState<[number, number, number]>([11000, 25000, 0])

  // Z-up
  useEffect(() => {
    camera.up.set(0, 0, 1)
    ;(camera as THREE.PerspectiveCamera).position.set(30000, -40000, 25000)
  }, [])

  // Fly controls
  useFlyControls(canvasRef)

  // Disable orbit when flying
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.enabled = !flyMode
    }
  }, [flyMode])

  // View presets
  useEffect(() => {
    const handler = (e: Event) => {
      const view = (e as CustomEvent).detail
      const box = new THREE.Box3().setFromObject(scene)
      if (box.isEmpty()) return
      const center = box.getCenter(new THREE.Vector3())
      const size = box.getSize(new THREE.Vector3())
      const d = Math.max(size.x, size.y, size.z) * 1.2

      const positions: Record<string, [number, number, number]> = {
        top: [center.x, center.y, center.z + d],
        front: [center.x, center.y - d, center.z + d * 0.1],
        right: [center.x + d, center.y, center.z + d * 0.1],
        iso: [center.x - d * 0.6, center.y - d * 0.8, center.z + d * 0.5],
      }

      const pos = positions[view] || positions.iso
      camera.position.set(...pos)
      camera.up.set(0, 0, 1)
      if (controlsRef.current) {
        controlsRef.current.target.copy(center)
        controlsRef.current.update()
      }
    }

    window.addEventListener('cadforge:setView', handler)
    return () => window.removeEventListener('cadforge:setView', handler)
  }, [camera])

  const handleCenterUpdate = useCallback((c: [number, number, number]) => {
    setModelCenter(c)
    if (controlsRef.current) {
      controlsRef.current.target.set(c[0], c[1], c[2] + 1500)
      controlsRef.current.update()
    }
    // Fit camera
    const box = new THREE.Box3().setFromObject(scene)
    if (box.isEmpty()) return
    const center = box.getCenter(new THREE.Vector3())
    const size = box.getSize(new THREE.Vector3())
    const maxDim = Math.max(size.x, size.y, size.z)
    camera.position.set(
      center.x - maxDim * 0.6,
      center.y - maxDim * 0.8,
      center.z + maxDim * 0.5,
    )
    camera.up.set(0, 0, 1)
  }, [camera, scene])

  return (
    <>
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.1}
        target={[modelCenter[0], modelCenter[1], 1500]}
      />

      {/* Lights */}
      <ambientLight intensity={0.5} />
      <SunLight center={modelCenter} />
      <directionalLight
        color={0x8888ff}
        intensity={0.3}
        position={[-15000, 20000, 10000]}
      />

      {/* Ground shadow plane */}
      <mesh position={[modelCenter[0], modelCenter[1], -5]} receiveShadow>
        <planeGeometry args={[120000, 120000]} />
        <shadowMaterial opacity={0.35} />
      </mesh>

      {/* Grid */}
      {gridVisible && (
        <gridHelper
          args={[60000, 60, 0x444466, 0x333355]}
          rotation={[Math.PI / 2, 0, 0]}
        />
      )}

      {/* Axes */}
      <axesHelper args={[5000]} />

      {/* Sun visuals */}
      {sunPanelOpen && (
        <>
          <SunMarker center={modelCenter} />
          <CompassRose center={modelCenter} />
        </>
      )}

      {/* Floor plan mode (clipping) */}
      <FloorPlanMode />

      {/* Measurement tool */}
      <MeasureTool />

      {/* Room labels */}
      <RoomLabels floorPlanMode={floorPlanMode} />

      {/* Screenshot capture */}
      <ScreenshotCapture />

      {/* Scene exporter (stores scene ref for export panel) */}
      <SceneExporter />

      {/* Model loader (imperative) */}
      <ModelLoader onCenterUpdate={handleCenterUpdate} />
    </>
  )
}

export function Scene() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  return (
    <Canvas
      ref={canvasRef}
      camera={{ fov: 45, near: 10, far: 200000, up: [0, 0, 1] }}
      shadows={{ type: THREE.PCFSoftShadowMap }}
      gl={{ antialias: true, preserveDrawingBuffer: true }}
      style={{ width: '100vw', height: '100vh', display: 'block' }}
      onCreated={({ gl }) => {
        gl.setClearColor(0x87cefa)
      }}
    >
      <SceneContent canvasRef={canvasRef} />
    </Canvas>
  )
}
