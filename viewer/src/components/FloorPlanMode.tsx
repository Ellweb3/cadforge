import { useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { useStore } from '../store/useStore'
import { useEffect, useRef } from 'react'

export function FloorPlanMode() {
  const floorPlanActive = useStore(s => s.floorPlanMode)
  const floorPlanHeight = useStore(s => s.floorPlanClipHeight)
  const clipEnabled = useStore(s => s.clipEnabled)
  const clipHeight = useStore(s => s.clipHeight)
  const { gl } = useThree()
  const planeRef = useRef(new THREE.Plane(new THREE.Vector3(0, 0, -1), 1200))

  // Unified clipping: floorPlan mode OR clip panel
  const active = floorPlanActive || clipEnabled
  const height = floorPlanActive ? floorPlanHeight : clipHeight

  useEffect(() => {
    if (active) {
      gl.localClippingEnabled = true
      planeRef.current.constant = height
      gl.clippingPlanes = [planeRef.current]
    } else {
      gl.clippingPlanes = []
    }
    return () => { gl.clippingPlanes = [] }
  }, [active, height, gl])

  if (!active) return null

  return (
    <mesh position={[11000, 27500, height]}>
      <planeGeometry args={[22000, 55000]} />
      <meshBasicMaterial color="#4488ff" transparent opacity={0.05} side={THREE.DoubleSide} />
    </mesh>
  )
}
