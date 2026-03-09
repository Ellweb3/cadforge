import type { ReactNode } from 'react'
import { useStore } from '../store/useStore'
import './ToolbarNew.css'

function ToolbarGroup({ children }: { children: ReactNode }) {
  return <div className="tb-group">{children}</div>
}

interface TBProps {
  icon: string
  label: string
  active?: boolean
  color?: string
  onClick: () => void
}

function TB({ icon, label, active, color, onClick }: TBProps) {
  return (
    <button
      className={`tb-btn ${active ? 'tb-active' : ''}`}
      style={active && color ? { borderColor: color, color } : undefined}
      onClick={onClick}
      title={label}
    >
      <span className="tb-icon">{icon}</span>
      <span className="tb-label">{label}</span>
    </button>
  )
}

export function ToolbarNew() {
  const wireframeMode = useStore(s => s.wireframeMode)
  const flyMode = useStore(s => s.flyMode)
  const floorPlanMode = useStore(s => s.floorPlanMode)
  const measureMode = useStore(s => s.measureMode)
  const clipPanelOpen = useStore(s => s.clipPanelOpen)
  const exportPanelOpen = useStore(s => s.exportPanelOpen)
  const gridVisible = useStore(s => s.gridVisible)
  const sunPanelOpen = useStore(s => s.sunPanelOpen)
  const chatOpen = useStore(s => s.chatOpen)
  const {
    reload, toggleWireframe, toggleFly, toggleFloorPlan,
    toggleMeasure, toggleClipPanel, toggleExportPanel,
    toggleGrid, toggleSunPanel, toggleChat, toggleKeyboardHelp,
  } = useStore()

  return (
    <div className="toolbar-new">
      <ToolbarGroup>
        <TB icon="⟲" label="Reset" onClick={reload} />
        <TB icon="⬆" label="Top" onClick={() => dispatchView('top')} />
        <TB icon="◻" label="Front" onClick={() => dispatchView('front')} />
        <TB icon="▶" label="Right" onClick={() => dispatchView('right')} />
        <TB icon="◇" label="Iso" onClick={() => dispatchView('iso')} />
      </ToolbarGroup>

      <ToolbarGroup>
        <TB icon="△" label="Wire" active={wireframeMode} color="#6c8cff" onClick={toggleWireframe} />
        <TB icon="✈" label="Fly" active={flyMode} color="#6c8cff" onClick={toggleFly} />
        <TB icon="⊞" label="Plan" active={floorPlanMode} color="#6c8cff" onClick={toggleFloorPlan} />
      </ToolbarGroup>

      <ToolbarGroup>
        <TB icon="📏" label="Measure" active={measureMode} color="#4caf50" onClick={toggleMeasure} />
        <TB icon="✂" label="Clip" active={clipPanelOpen} color="#4caf50" onClick={toggleClipPanel} />
        <TB icon="📷" label="Capture" color="#4caf50" onClick={() => window.dispatchEvent(new Event('cadforge:screenshot'))} />
        <TB icon="⬇" label="Export" active={exportPanelOpen} color="#4caf50" onClick={toggleExportPanel} />
      </ToolbarGroup>

      <ToolbarGroup>
        <TB icon="#" label="Grid" active={gridVisible} color="#a78bfa" onClick={toggleGrid} />
        <TB icon="☀" label="Sun" active={sunPanelOpen} color="#ff9800" onClick={toggleSunPanel} />
        <TB icon="💬" label="Chat" active={chatOpen} color="#a78bfa" onClick={toggleChat} />
        <TB icon="?" label="Keys" onClick={toggleKeyboardHelp} />
      </ToolbarGroup>
    </div>
  )
}

function dispatchView(view: string) {
  window.dispatchEvent(new CustomEvent('cadforge:setView', { detail: view }))
}
