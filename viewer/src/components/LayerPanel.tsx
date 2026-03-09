import { useState, useCallback } from 'react'
import * as THREE from 'three'
import { useStore } from '../store/useStore'
import './LayerPanel.css'

const GROUPS = [
  { key: 'site', label: 'Site' },
  { key: 'houses', label: 'Houses' },
  { key: 'interior', label: 'Interior' },
  { key: 'exterior', label: 'Exterior' },
]

function setMeshOpacity(meshes: THREE.Mesh[], opacity: number) {
  meshes.forEach(m => {
    const materials = Array.isArray(m.material) ? m.material : [m.material]
    materials.forEach(mat => {
      if (mat && 'opacity' in mat) {
        ;(mat as THREE.MeshStandardMaterial).opacity = opacity
        ;(mat as THREE.MeshStandardMaterial).transparent = opacity < 1
        ;(mat as THREE.MeshStandardMaterial).needsUpdate = true
      }
    })
  })
}

export function LayerPanel() {
  const layers = useStore(s => s.layers)
  const { toggleLayer, setAllLayers } = useStore()

  const [search, setSearch] = useState('')
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})
  const [soloIndex, setSoloIndex] = useState<number | null>(null)
  const [opacities, setOpacities] = useState<Record<string, number>>({})

  const filtered = layers.filter(l =>
    l.label.toLowerCase().includes(search.toLowerCase())
  )

  const grouped = GROUPS.map(g => ({
    ...g,
    layers: filtered
      .map((l, idx) => ({ layer: l, globalIndex: layers.indexOf(l) }))
      .filter(({ layer }) => layer.name.startsWith(g.key + '-')),
  })).filter(g => g.layers.length > 0)

  // Ungrouped layers (don't match any prefix)
  const ungrouped = filtered
    .map(l => ({ layer: l, globalIndex: layers.indexOf(l) }))
    .filter(({ layer }) => !GROUPS.some(g => layer.name.startsWith(g.key + '-')))

  const toggleCollapse = useCallback((key: string) => {
    setCollapsed(prev => ({ ...prev, [key]: !prev[key] }))
  }, [])

  const handleSolo = useCallback((globalIndex: number) => {
    if (soloIndex === globalIndex) {
      // Unsolo: restore all to visible
      setSoloIndex(null)
      setAllLayers(true)
    } else {
      // Solo: hide all, show only this one
      setSoloIndex(globalIndex)
      setAllLayers(false)
      // Need to toggle the target layer on
      // setAllLayers(false) hides everything, now show just this one
      // We use toggleLayer which flips visibility
      toggleLayer(globalIndex)
    }
  }, [soloIndex, setAllLayers, toggleLayer])

  const handleOpacity = useCallback((name: string, meshes: THREE.Mesh[], value: number) => {
    setOpacities(prev => ({ ...prev, [name]: value }))
    setMeshOpacity(meshes, value)
  }, [])

  const totalMeshes = layers.reduce((sum, l) => sum + l.meshes.length, 0)

  const toggleGroupVisibility = useCallback((groupLayers: { layer: typeof layers[0]; globalIndex: number }[]) => {
    const allVisible = groupLayers.every(({ layer }) => layer.visible)
    groupLayers.forEach(({ layer, globalIndex }) => {
      if (allVisible && layer.visible) toggleLayer(globalIndex)
      else if (!allVisible && !layer.visible) toggleLayer(globalIndex)
    })
  }, [toggleLayer])

  return (
    <div className="panel layer-panel">
      <div className="lp-header">
        <h3>Layers</h3>
        <span className="lp-mesh-count">{totalMeshes} meshes</span>
      </div>

      <input
        className="lp-search"
        type="text"
        placeholder="Filter layers..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      <div className="layer-controls">
        <button onClick={() => { setAllLayers(true); setSoloIndex(null) }}>All</button>
        <button onClick={() => { setAllLayers(false); setSoloIndex(null) }}>None</button>
        {soloIndex !== null && (
          <button className="lp-solo-active" onClick={() => { setAllLayers(true); setSoloIndex(null) }}>
            Unsolo
          </button>
        )}
      </div>

      <div className="lp-groups">
        {grouped.map(group => (
          <div key={group.key} className="lp-group">
            <div
              className="lp-group-header"
              onClick={() => toggleCollapse(group.key)}
            >
              <span className="lp-caret">{collapsed[group.key] ? '▸' : '▾'}</span>
              <span className="lp-group-label">{group.label}</span>
              <span className="lp-group-count">{group.layers.length}</span>
              <button
                className="lp-group-toggle"
                onClick={e => { e.stopPropagation(); toggleGroupVisibility(group.layers) }}
                title="Toggle group"
              >
                {group.layers.every(({ layer }) => layer.visible) ? '👁' : '○'}
              </button>
            </div>

            {!collapsed[group.key] && (
              <div className="lp-group-items">
                {group.layers.map(({ layer, globalIndex }) => {
                  const opacity = opacities[layer.name] ?? 1
                  const isSoloed = soloIndex === globalIndex
                  return (
                    <div
                      key={layer.name}
                      className={`lp-item ${isSoloed ? 'lp-item-soloed' : ''}`}
                    >
                      <div className="lp-item-row">
                        <input
                          type="checkbox"
                          checked={layer.visible}
                          onChange={() => toggleLayer(globalIndex)}
                        />
                        <span
                          className="lp-item-label"
                          onDoubleClick={() => handleSolo(globalIndex)}
                          title="Double-click to solo"
                        >
                          {layer.label}
                        </span>
                        <span className="lp-item-meshes">{layer.meshes.length}</span>
                      </div>
                      <div className="lp-item-slider">
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.05"
                          value={opacity}
                          onChange={e => handleOpacity(layer.name, layer.meshes, parseFloat(e.target.value))}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        ))}

        {ungrouped.length > 0 && (
          <div className="lp-group">
            <div
              className="lp-group-header"
              onClick={() => toggleCollapse('_other')}
            >
              <span className="lp-caret">{collapsed['_other'] ? '▸' : '▾'}</span>
              <span className="lp-group-label">Other</span>
              <span className="lp-group-count">{ungrouped.length}</span>
            </div>
            {!collapsed['_other'] && (
              <div className="lp-group-items">
                {ungrouped.map(({ layer, globalIndex }) => {
                  const opacity = opacities[layer.name] ?? 1
                  const isSoloed = soloIndex === globalIndex
                  return (
                    <div
                      key={layer.name}
                      className={`lp-item ${isSoloed ? 'lp-item-soloed' : ''}`}
                    >
                      <div className="lp-item-row">
                        <input
                          type="checkbox"
                          checked={layer.visible}
                          onChange={() => toggleLayer(globalIndex)}
                        />
                        <span
                          className="lp-item-label"
                          onDoubleClick={() => handleSolo(globalIndex)}
                          title="Double-click to solo"
                        >
                          {layer.label}
                        </span>
                        <span className="lp-item-meshes">{layer.meshes.length}</span>
                      </div>
                      <div className="lp-item-slider">
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.05"
                          value={opacity}
                          onChange={e => handleOpacity(layer.name, layer.meshes, parseFloat(e.target.value))}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
