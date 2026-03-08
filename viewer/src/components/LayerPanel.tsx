import { useStore } from '../store/useStore'

export function LayerPanel() {
  const layers = useStore(s => s.layers)
  const { toggleLayer, setAllLayers } = useStore()

  return (
    <div className="panel layer-panel">
      <h3>Layers</h3>
      <div className="layer-controls">
        <button onClick={() => setAllLayers(true)}>All</button>
        <button onClick={() => setAllLayers(false)}>None</button>
      </div>
      {layers.map((layer, i) => (
        <label key={layer.name} className="layer-item">
          <input
            type="checkbox"
            checked={layer.visible}
            onChange={() => toggleLayer(i)}
          />
          {layer.label} ({layer.meshes.length})
        </label>
      ))}
    </div>
  )
}
