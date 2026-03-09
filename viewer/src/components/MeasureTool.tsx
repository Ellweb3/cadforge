import { useState, useEffect, useCallback, useRef } from 'react'
import { useThree } from '@react-three/fiber'
import { Html, Line } from '@react-three/drei'
import * as THREE from 'three'
import { useStore } from '../store/useStore'
import './MeasureTool.css'

// measureMode and toggleMeasure are defined in useStore.ts

export function MeasureTool() {
  const active = useStore(s => s.measureMode)
  const { scene, camera, gl } = useThree()
  const [points, setPoints] = useState<THREE.Vector3[]>([])
  const raycasterRef = useRef(new THREE.Raycaster())
  const mouseRef = useRef(new THREE.Vector2())

  // Clear points when deactivated
  useEffect(() => {
    if (!active) setPoints([])
  }, [active])

  // Click handler: raycast into scene, place measurement points
  const handleClick = useCallback(
    (e: MouseEvent) => {
      if (!active) return

      const rect = gl.domElement.getBoundingClientRect()
      mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
      mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1

      raycasterRef.current.setFromCamera(mouseRef.current, camera)

      // Collect visible meshes
      const meshes: THREE.Mesh[] = []
      scene.traverse((obj) => {
        if (
          (obj as THREE.Mesh).isMesh &&
          obj.visible &&
          obj.parent?.visible !== false
        ) {
          meshes.push(obj as THREE.Mesh)
        }
      })

      const intersects = raycasterRef.current.intersectObjects(meshes, false)
      if (intersects.length === 0) return

      const point = intersects[0].point.clone()

      setPoints((prev) => {
        if (prev.length < 2) {
          return [...prev, point]
        }
        // Third click: clear and start new measurement
        return [point]
      })
    },
    [active, scene, camera, gl],
  )

  // ESC handler: clear measurement
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && active) {
        setPoints([])
      }
    },
    [active],
  )

  // Attach/detach event listeners
  useEffect(() => {
    if (!active) return

    gl.domElement.addEventListener('click', handleClick)
    window.addEventListener('keydown', handleKeyDown)

    return () => {
      gl.domElement.removeEventListener('click', handleClick)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [active, handleClick, handleKeyDown, gl])

  if (!active) return null

  const distance =
    points.length === 2 ? points[0].distanceTo(points[1]) / 1000 : null

  const midpoint =
    points.length === 2
      ? points[0].clone().lerp(points[1], 0.5)
      : null

  return (
    <group>
      {points.map((p, i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[80]} />
          <meshBasicMaterial color="#ffcc00" />
        </mesh>
      ))}
      {points.length === 2 && midpoint && (
        <>
          <Line
            points={[points[0], points[1]]}
            color="#ffcc00"
            lineWidth={2}
            dashed
            dashSize={100}
            gapSize={50}
          />
          <Html position={midpoint}>
            <div className="measure-label">{distance!.toFixed(2)} m</div>
          </Html>
        </>
      )}
    </group>
  )
}
