import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useStore } from '../store/useStore'
import { solarPosition } from '../lib/solarPosition'

export function SunLight({ center }: { center: [number, number, number] }) {
  const dirRef = useRef<THREE.DirectionalLight>(null)
  const targetRef = useRef<THREE.Object3D>(null)

  const {
    sunLat, sunLon, sunNorthDeg, sunTzOffset,
    sunTimeMinutes, sunDateStr, sunAnimating, sunAnimSpeed,
    setSunTime, sunPanelOpen,
  } = useStore()

  // Expose computed sun data for other components
  const sunData = useRef({ azimuth: 0, elevation: 0, x: 0, y: 0, z: 0 })

  useFrame((_, delta) => {
    // Animate time
    let time = sunTimeMinutes
    if (sunAnimating) {
      time += sunAnimSpeed * delta / 60
      if (time >= 1440) time -= 1440
      if (time < 0) time += 1440
      setSunTime(time)
    }

    const { azimuth, elevation } = solarPosition(sunLat, sunLon, time, sunDateStr, sunTzOffset)
    const rad = Math.PI / 180
    const az = (azimuth - sunNorthDeg) * rad
    const el = Math.max(elevation, 0.5) * rad

    const dist = 80000
    const x = Math.sin(az) * Math.cos(el) * dist
    const y = Math.cos(az) * Math.cos(el) * dist
    const z = Math.sin(el) * dist

    sunData.current = { azimuth, elevation, x, y, z }

    const light = dirRef.current
    if (!light) return

    light.position.set(center[0] + x, center[1] + y, Math.max(z, 500))

    // Dynamic shadow frustum
    const shadowSize = elevation > 30 ? 40000 : elevation > 10 ? 60000 : 90000
    light.shadow.camera.left = -shadowSize
    light.shadow.camera.right = shadowSize
    light.shadow.camera.top = shadowSize
    light.shadow.camera.bottom = -shadowSize
    light.shadow.camera.updateProjectionMatrix()

    // Color & intensity by elevation
    if (elevation <= 0) {
      light.intensity = 0
    } else if (elevation < 5) {
      light.intensity = 0.3
      light.color.setHex(0xff8844)
    } else if (elevation < 20) {
      const t = (elevation - 5) / 15
      light.intensity = 0.3 + t * 0.7
      light.color.setHex(t < 0.5 ? 0xffaa66 : 0xffddaa)
    } else {
      light.intensity = 1.0
      light.color.setHex(0xffffff)
    }
  })

  return (
    <>
      <directionalLight
        ref={dirRef}
        castShadow
        shadow-mapSize-width={4096}
        shadow-mapSize-height={4096}
        shadow-camera-near={100}
        shadow-camera-far={300000}
        shadow-bias={-0.0005}
      >
        <object3D ref={targetRef} position={center} />
      </directionalLight>
    </>
  )
}

// Hook to read current sun data from any component
export function useSunData() {
  const {
    sunLat, sunLon, sunNorthDeg, sunTzOffset,
    sunTimeMinutes, sunDateStr,
  } = useStore()

  return useMemo(() => {
    const { azimuth, elevation } = solarPosition(sunLat, sunLon, sunTimeMinutes, sunDateStr, sunTzOffset)
    const rad = Math.PI / 180
    const az = (azimuth - sunNorthDeg) * rad
    const el = Math.max(elevation, 0.5) * rad
    const markerDist = 35000
    return {
      azimuth, elevation,
      markerX: Math.sin(az) * Math.cos(el) * markerDist,
      markerY: Math.cos(az) * Math.cos(el) * markerDist,
      markerZ: Math.sin(el) * markerDist,
    }
  }, [sunLat, sunLon, sunNorthDeg, sunTzOffset, sunTimeMinutes, sunDateStr])
}
