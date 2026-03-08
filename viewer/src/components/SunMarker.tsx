import { useMemo, useRef, useEffect } from 'react'
import * as THREE from 'three'
import { Line } from '@react-three/drei'
import { useSunData } from './SunLight'

export function SunMarker({ center }: { center: [number, number, number] }) {
  const { elevation, markerX, markerY, markerZ } = useSunData()

  const glowTexture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 64; canvas.height = 64
    const ctx = canvas.getContext('2d')!
    const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32)
    grad.addColorStop(0, 'rgba(255,220,80,0.8)')
    grad.addColorStop(0.3, 'rgba(255,180,40,0.3)')
    grad.addColorStop(1, 'rgba(255,150,0,0)')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, 64, 64)
    return new THREE.CanvasTexture(canvas)
  }, [])

  const sunPos: [number, number, number] = [
    center[0] + markerX,
    center[1] + markerY,
    markerZ,
  ]

  if (elevation < -2) return null

  const sphereColor = elevation <= 0 ? '#994400' : elevation < 10 ? '#ff8800' : '#ffcc00'
  const glowOpacity = elevation <= 0 ? 0.2 : elevation < 10 ? 0.6 : 1.0

  const linePoints: [number, number, number][] = [
    sunPos,
    [sunPos[0], sunPos[1], 0],
  ]

  return (
    <group>
      {/* Sun sphere */}
      <mesh position={sunPos}>
        <sphereGeometry args={[1500, 16, 16]} />
        <meshBasicMaterial color={sphereColor} />
      </mesh>

      {/* Glow sprite */}
      <sprite position={sunPos} scale={[8000, 8000, 1]}>
        <spriteMaterial
          map={glowTexture}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          opacity={glowOpacity}
          transparent
        />
      </sprite>

      {/* Dashed line to ground */}
      <Line
        points={linePoints}
        color="#ffcc00"
        lineWidth={1}
        dashed
        dashSize={500}
        gapSize={300}
        opacity={0.5}
        transparent
      />

      {/* Ground dot */}
      <mesh position={[sunPos[0], sunPos[1], 5]}>
        <circleGeometry args={[800, 16]} />
        <meshBasicMaterial color="#ffaa00" opacity={0.4} transparent />
      </mesh>
    </group>
  )
}
