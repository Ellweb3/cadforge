import { Scene } from './components/Scene'
import { Toolbar } from './components/Toolbar'
import { InfoPanel } from './components/InfoPanel'
import { LayerPanel } from './components/LayerPanel'
import { StatusBar } from './components/StatusBar'
import { SunPanel } from './components/SunPanel'
import { LogPanel } from './components/LogPanel'
import { ChatPanel } from './components/ChatPanel'
import { useWebSocket } from './hooks/useWebSocket'
import './App.css'

export default function App() {
  useWebSocket(3132)

  return (
    <>
      <Scene />
      <Toolbar />
      <InfoPanel />
      <LayerPanel />
      <StatusBar />
      <SunPanel />
      <LogPanel />
      <ChatPanel />
    </>
  )
}
