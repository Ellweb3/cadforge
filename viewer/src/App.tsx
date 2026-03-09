import { Scene } from './components/Scene'
import { ToolbarNew } from './components/ToolbarNew'
import { InfoPanel } from './components/InfoPanel'
import { LayerPanel } from './components/LayerPanel'
import { StatusBar } from './components/StatusBar'
import { SunPanel } from './components/SunPanel'
import { ClipPanel } from './components/ClipPanel'
import { LogPanel } from './components/LogPanel'
import { ChatPanel } from './components/ChatPanel'
import { InspectorPanel } from './components/InspectorPanel'
import { ExportPanel } from './components/ExportPanel'
import { KeyboardHelp } from './components/KeyboardHelp'
import { Minimap } from './components/Minimap'
import { useWebSocket } from './hooks/useWebSocket'
import { useKeyboard } from './hooks/useKeyboard'
import './App.css'

export default function App() {
  useWebSocket(3132)
  useKeyboard()

  return (
    <>
      <Scene />
      <ToolbarNew />
      <InfoPanel />
      <LayerPanel />
      <StatusBar />
      <SunPanel />
      <ClipPanel />
      <LogPanel />
      <ChatPanel />
      <InspectorPanel />
      <ExportPanel />
      <KeyboardHelp />
      <Minimap />
    </>
  )
}
