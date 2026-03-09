import { useStore } from '../store/useStore'
import './ClipPanel.css'

export function ClipPanel() {
  const clipPanelOpen = useStore(s => s.clipPanelOpen)
  const clipEnabled = useStore(s => s.clipEnabled)
  const clipHeight = useStore(s => s.clipHeight)

  if (!clipPanelOpen) return null

  const heightM = (clipHeight / 1000).toFixed(1)

  return (
    <div className="panel clip-panel">
      <div className="clip-header">
        <span className="clip-title">Section Plane</span>
        <label className="clip-toggle">
          <input type="checkbox" checked={clipEnabled}
            onChange={() => useStore.getState().setClipEnabled(!clipEnabled)} />
          Active
        </label>
      </div>
      <div className="clip-row">
        <span className="clip-label">Height:</span>
        <input type="range" min={0} max={5000} step={50} value={clipHeight}
          onChange={e => useStore.getState().setClipHeight(+e.target.value)}
          className="clip-slider" />
        <span className="clip-value">{heightM}m</span>
      </div>
      <div className="clip-presets">
        {([['Floor', 120], ['Sill', 1200], ['Ceiling', 2800], ['Roof', 4000]] as const).map(([label, h]) => (
          <button key={label} onClick={() => useStore.getState().setClipHeight(h)}
            className={clipHeight === h ? 'active' : ''}>
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
