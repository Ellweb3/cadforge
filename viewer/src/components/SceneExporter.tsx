import { useThree } from '@react-three/fiber'
import { useEffect } from 'react'
import * as THREE from 'three'

// Global ref to scene for export
export let sceneRef: THREE.Scene | null = null

export function SceneExporter() {
  const { scene } = useThree()
  useEffect(() => { sceneRef = scene }, [scene])
  return null
}
