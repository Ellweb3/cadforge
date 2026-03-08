import { useStore } from '../store/useStore'
import './Toolbar.css'

export function Toolbar() {
  const flyMode = useStore(s => s.flyMode)
  const wireframeMode = useStore(s => s.wireframeMode)
  const gridVisible = useStore(s => s.gridVisible)
  const sunPanelOpen = useStore(s => s.sunPanelOpen)
  const {
    toggleFly, toggleWireframe, toggleGrid, toggleSunPanel, reload,
  } = useStore()

  return (
    <div className="toolbar">
      <button onClick={() => useStore.getState().reload()}>Reset</button>
      <ViewBtn view="top" />
      <ViewBtn view="front" />
      <ViewBtn view="right" />
      <ViewBtn view="iso" />
      <button
        className={wireframeMode ? 'active' : ''}
        onClick={toggleWireframe}
      >Wire</button>
      <button
        className={gridVisible ? '' : 'active'}
        onClick={toggleGrid}
      >Grid</button>
      <button className="reload-btn" onClick={reload}>Reload</button>
      <button
        className={flyMode ? 'active' : ''}
        onClick={toggleFly}
      >Fly</button>
      <button
        className={`sun-btn ${sunPanelOpen ? 'active' : ''}`}
        onClick={toggleSunPanel}
      >Sun</button>
    </div>
  )
}

function ViewBtn({ view }: { view: string }) {
  return (
    <button onClick={() => {
      // Dispatch custom event for Scene to handle
      window.dispatchEvent(new CustomEvent('cadforge:setView', { detail: view }))
    }}>
      {view.charAt(0).toUpperCase() + view.slice(1)}
    </button>
  )
}
