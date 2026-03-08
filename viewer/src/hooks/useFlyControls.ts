import { useEffect, useRef, useCallback } from 'react'
import { useThree, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useStore } from '../store/useStore'

export function useFlyControls(canvasRef: React.RefObject<HTMLCanvasElement | null>) {
  const { camera } = useThree()
  const flyMode = useStore(s => s.flyMode)
  const log = useStore(s => s.log)

  const keys = useRef<Record<string, boolean>>({})
  const yaw = useRef(0)
  const pitch = useRef(-0.3)
  const speed = useRef(100)
  const locked = useRef(false)

  // Init yaw/pitch from camera when entering fly mode
  useEffect(() => {
    if (flyMode) {
      const dir = new THREE.Vector3()
      camera.getWorldDirection(dir)
      yaw.current = Math.atan2(dir.y, dir.x)
      pitch.current = Math.asin(THREE.MathUtils.clamp(dir.z, -1, 1))
      canvasRef.current?.requestPointerLock()
    } else {
      if (document.pointerLockElement) document.exitPointerLock()
    }
  }, [flyMode])

  useEffect(() => {
    const onPointerLockChange = () => {
      locked.current = document.pointerLockElement === canvasRef.current
      if (!locked.current && flyMode) {
        useStore.getState().toggleFly()
      }
    }

    const onMouseMove = (e: MouseEvent) => {
      if (!locked.current) return
      const sensitivity = 0.0008
      yaw.current -= e.movementX * sensitivity
      pitch.current -= e.movementY * sensitivity
      pitch.current = THREE.MathUtils.clamp(pitch.current, -Math.PI / 2 + 0.05, Math.PI / 2 - 0.05)
    }

    const onKeyDown = (e: KeyboardEvent) => {
      keys.current[e.code] = true
      if (e.code === 'Equal' || e.code === 'NumpadAdd') {
        speed.current = Math.min(speed.current * 1.5, 5000)
        log(`Fly speed: ${speed.current.toFixed(0)}`)
      }
      if (e.code === 'Minus' || e.code === 'NumpadSubtract') {
        speed.current = Math.max(speed.current / 1.5, 10)
        log(`Fly speed: ${speed.current.toFixed(0)}`)
      }
    }

    const onKeyUp = (e: KeyboardEvent) => {
      keys.current[e.code] = false
    }

    const onWheel = (e: WheelEvent) => {
      if (!flyMode) return
      e.preventDefault()
      speed.current *= e.deltaY > 0 ? 0.8 : 1.25
      speed.current = THREE.MathUtils.clamp(speed.current, 10, 5000)
      log(`Fly speed: ${speed.current.toFixed(0)}`)
    }

    document.addEventListener('pointerlockchange', onPointerLockChange)
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('keyup', onKeyUp)
    canvasRef.current?.addEventListener('wheel', onWheel, { passive: false })

    return () => {
      document.removeEventListener('pointerlockchange', onPointerLockChange)
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('keyup', onKeyUp)
      canvasRef.current?.removeEventListener('wheel', onWheel)
    }
  }, [flyMode])

  useFrame((_, delta) => {
    if (!flyMode) return
    const k = keys.current
    const boost = (k['ShiftLeft'] || k['ShiftRight']) ? 5 : 1
    const spd = speed.current * boost * delta * 1000

    const lookDir = new THREE.Vector3(
      Math.cos(pitch.current) * Math.cos(yaw.current),
      Math.cos(pitch.current) * Math.sin(yaw.current),
      Math.sin(pitch.current),
    )
    const worldUp = new THREE.Vector3(0, 0, 1)
    const right = new THREE.Vector3().crossVectors(lookDir, worldUp).normalize()

    const move = new THREE.Vector3()
    if (k['KeyW'] || k['ArrowUp']) move.add(lookDir)
    if (k['KeyS'] || k['ArrowDown']) move.sub(lookDir)
    if (k['KeyA'] || k['ArrowLeft']) move.sub(right)
    if (k['KeyD'] || k['ArrowRight']) move.add(right)
    if (k['KeyQ'] || k['Space']) move.add(worldUp)
    if (k['KeyE']) move.sub(worldUp)

    if (move.lengthSq() > 0) {
      move.normalize().multiplyScalar(spd)
      camera.position.add(move)
    }

    const target = camera.position.clone().add(lookDir)
    camera.lookAt(target)
  })
}
