import { useEffect, useRef, useState } from 'react'
import { useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { useStore } from '../store/useStore'

const GROUP_LABELS: Record<string, string> = {
  'site-ground': 'Site',
  'site-landscape': 'Landscape',
  'houses-main_house': 'Main House',
  'houses-guest_house': 'Guest House',
  'interior-walls': 'Interior Walls',
  'interior-furniture': 'Furniture',
  'exterior-roofs': 'Roofs',
  'exterior-windows': 'Windows',
  'exterior-finishing': 'Finishing',
}

export function ModelLoader({
  onCenterUpdate,
}: {
  onCenterUpdate: (center: [number, number, number]) => void
}) {
  const { scene } = useThree()
  const groupRef = useRef<THREE.Group | null>(null)
  const loaderRef = useRef(new GLTFLoader())
  const objectNamesRef = useRef<Map<string, string>>(new Map())

  const modelVersion = useStore(s => s.modelVersion)
  const modelUrl = useStore(s => s.modelUrl)
  const wireframeMode = useStore(s => s.wireframeMode)
  const { setStatus, setObjectCount, setLayers, log } = useStore()

  // Load / reload model
  useEffect(() => {
    let disposed = false

    async function load() {
      log('Fetching model...')
      try {
        const resp = await fetch(modelUrl, { cache: 'no-store' })
        if (!resp.ok) {
          log(`HTTP ${resp.status}: ${resp.statusText}`)
          setStatus('No build yet — run: cadforge build', 'error')
          return
        }
        const buf = await resp.arrayBuffer()
        log(`Downloaded ${(buf.byteLength / 1024).toFixed(0)} KB`)
        setStatus('Parsing model...', 'building')

        loaderRef.current.parse(buf, '', (gltf) => {
          if (disposed) return

          // Remove old
          if (groupRef.current) {
            scene.remove(groupRef.current)
            groupRef.current.traverse(c => {
              if ((c as THREE.Mesh).isMesh) {
                const m = c as THREE.Mesh
                m.geometry.dispose()
                if (Array.isArray(m.material)) m.material.forEach(mat => mat.dispose())
                else m.material.dispose()
              }
            })
          }

          const model = gltf.scene
          groupRef.current = model
          scene.add(model)

          // Collect layers
          const names = new Map<string, string>()
          const layerMap: Record<string, THREE.Mesh[]> = {}

          model.traverse(child => {
            if (!(child as THREE.Mesh).isMesh) return
            const mesh = child as THREE.Mesh

            let fullName = ''
            let node: THREE.Object3D | null = mesh
            while (node && node !== model) {
              if (node.name && node.name.includes('--')) {
                fullName = node.name
                break
              }
              if (node.name) fullName = node.name
              node = node.parent
            }
            if (!fullName) fullName = 'unnamed'

            const sep = fullName.indexOf('--')
            const group = sep > -1 ? fullName.substring(0, sep) : 'other'
            const objName = (sep > -1 ? fullName.substring(sep + 2) : fullName).replace('.stl', '')

            names.set(mesh.uuid, objName)
            mesh.castShadow = true
            mesh.receiveShadow = true

            if (!layerMap[group]) layerMap[group] = []
            layerMap[group].push(mesh)
          })

          objectNamesRef.current = names

          const layers = Object.entries(layerMap)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([name, meshes]) => ({
              name,
              label: GROUP_LABELS[name] || name,
              meshes,
              visible: true,
            }))
          setLayers(layers)

          // Center
          const box = new THREE.Box3().setFromObject(model)
          const center = box.getCenter(new THREE.Vector3())
          onCenterUpdate([center.x, center.y, 0])

          const count = names.size
          setObjectCount(count)
          log(`Loaded ${count} objects`)
          setStatus(`Loaded: ${count} objects`, 'ok')
        }, (err: any) => {
          log(`Parse error: ${err?.message || err}`)
          setStatus('Parse error', 'error')
        })
      } catch (err: any) {
        log(`Fetch error: ${err.message}`)
        setStatus('Load error', 'error')
      }
    }

    load()
    return () => { disposed = true }
  }, [modelVersion])

  // Wireframe toggle
  useEffect(() => {
    groupRef.current?.traverse(child => {
      if ((child as THREE.Mesh).isMesh) {
        const mat = (child as THREE.Mesh).material as THREE.Material
        if ('wireframe' in mat) (mat as any).wireframe = wireframeMode
      }
    })
  }, [wireframeMode])

  // Picking
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (!groupRef.current) return
      const raycaster = new THREE.Raycaster()
      const mouse = new THREE.Vector2(
        (e.clientX / window.innerWidth) * 2 - 1,
        -(e.clientY / window.innerHeight) * 2 + 1,
      )
      const camera = scene.getObjectByProperty('isCamera', true) as THREE.Camera
      if (!camera) return
      raycaster.setFromCamera(mouse, camera)

      const meshes: THREE.Mesh[] = []
      groupRef.current.traverse(c => { if ((c as THREE.Mesh).isMesh) meshes.push(c as THREE.Mesh) })
      const hits = raycaster.intersectObjects(meshes)

      if (hits.length > 0) {
        const name = objectNamesRef.current.get(hits[0].object.uuid) || 'unknown'
        useStore.getState().setSelectedName(name)
      } else {
        useStore.getState().setSelectedName('-')
      }
    }

    window.addEventListener('click', handler)
    return () => window.removeEventListener('click', handler)
  }, [])

  return null
}
