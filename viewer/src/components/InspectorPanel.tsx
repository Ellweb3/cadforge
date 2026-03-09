import { useStore } from '../store/useStore'
import { useMemo } from 'react'
import * as THREE from 'three'
import './InspectorPanel.css'

export function InspectorPanel() {
  const selectedName = useStore(s => s.selectedName)
  const selectedMesh = useStore(s => s.selectedMesh)

  const info = useMemo(() => {
    if (!selectedMesh) return null
    const box = new THREE.Box3().setFromObject(selectedMesh)
    const size = box.getSize(new THREE.Vector3())
    const pos = box.getCenter(new THREE.Vector3())
    const mats = Array.isArray(selectedMesh.material) ? selectedMesh.material : [selectedMesh.material]
    const mat = mats[0] as THREE.MeshStandardMaterial | undefined
    const color = mat?.color ? '#' + mat.color.getHexString() : '#888'
    const opacity = mat?.opacity ?? 1
    return {
      width: (size.x / 1000).toFixed(2),
      depth: (size.y / 1000).toFixed(2),
      height: (size.z / 1000).toFixed(2),
      x: (pos.x / 1000).toFixed(1),
      y: (pos.y / 1000).toFixed(1),
      z: (pos.z / 1000).toFixed(1),
      color,
      opacity: Math.round(opacity * 100),
    }
  }, [selectedMesh])

  if (!selectedName || selectedName === '-' || !info) return null

  return (
    <div className="panel inspector-panel">
      <h3>{selectedName}</h3>
      <div className="inspector-row">
        <span className="inspector-label">Size:</span>
        <span>{info.width} &times; {info.depth} &times; {info.height} m</span>
      </div>
      <div className="inspector-row">
        <span className="inspector-label">Pos:</span>
        <span>{info.x}, {info.y}, {info.z}</span>
      </div>
      <div className="inspector-row">
        <span className="inspector-label">Color:</span>
        <span className="inspector-color" style={{ background: info.color }} />
        <span>{info.color}</span>
      </div>
      {info.opacity < 100 && (
        <div className="inspector-row">
          <span className="inspector-label">Opacity:</span>
          <span>{info.opacity}%</span>
        </div>
      )}
    </div>
  )
}
