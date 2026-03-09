import { create } from 'zustand'
import * as THREE from 'three'

interface LayerGroup {
  name: string
  label: string
  meshes: THREE.Mesh[]
  visible: boolean
}

interface ViewerState {
  // Model
  modelUrl: string
  modelVersion: number
  objectCount: number
  selectedName: string
  buildTime: string

  // Status
  status: string
  statusType: 'ok' | 'building' | 'error'

  // Modes
  flyMode: boolean
  wireframeMode: boolean
  gridVisible: boolean

  // Layers
  layers: LayerGroup[]

  // Chat
  chatOpen: boolean
  toggleChat: () => void

  // Sun
  sunPanelOpen: boolean
  sunLat: number
  sunLon: number
  sunNorthDeg: number
  sunTzOffset: number | null
  sunTimeMinutes: number
  sunDateStr: string
  sunAnimating: boolean
  sunAnimSpeed: number

  // Log
  logMessages: string[]

  // Actions
  reload: () => void
  setStatus: (text: string, type: 'ok' | 'building' | 'error') => void
  toggleFly: () => void
  toggleWireframe: () => void
  toggleGrid: () => void
  toggleSunPanel: () => void
  setLayers: (layers: LayerGroup[]) => void
  toggleLayer: (index: number) => void
  setAllLayers: (visible: boolean) => void
  setSunTime: (minutes: number) => void
  setSunDate: (date: string) => void
  setSunLat: (lat: number) => void
  setSunLon: (lon: number) => void
  setSunNorth: (deg: number) => void
  setSunTz: (tz: number) => void
  setSunAnimating: (v: boolean) => void
  setSunAnimSpeed: (s: number) => void
  setObjectCount: (n: number) => void
  setSelectedName: (n: string) => void
  setBuildTime: (t: string) => void
  log: (msg: string) => void
}

const savedLat = localStorage.getItem('sunLat')
const savedLon = localStorage.getItem('sunLon')
const savedNorth = localStorage.getItem('sunNorth')
const savedTz = localStorage.getItem('sunTz')

export const useStore = create<ViewerState>((set, get) => ({
  modelUrl: '/dist/model.glb',
  modelVersion: 0,
  objectCount: 0,
  selectedName: '-',
  buildTime: '-',

  status: 'Ready',
  statusType: 'ok',

  flyMode: false,
  wireframeMode: false,
  gridVisible: false,

  layers: [],

  chatOpen: true,
  toggleChat: () => set(s => ({ chatOpen: !s.chatOpen })),

  sunPanelOpen: false,
  sunLat: savedLat ? +savedLat : -34.925261,
  sunLon: savedLon ? +savedLon : -54.916241,
  sunNorthDeg: savedNorth ? +savedNorth : 0,
  sunTzOffset: savedTz ? +savedTz : null,
  sunTimeMinutes: 720,
  sunDateStr: new Date().toISOString().slice(0, 10),
  sunAnimating: false,
  sunAnimSpeed: 60,

  logMessages: [],

  reload: () => set(s => ({ modelVersion: s.modelVersion + 1 })),
  setStatus: (text, type) => set({ status: text, statusType: type }),
  toggleFly: () => set(s => ({ flyMode: !s.flyMode })),
  toggleWireframe: () => set(s => ({ wireframeMode: !s.wireframeMode })),
  toggleGrid: () => set(s => ({ gridVisible: !s.gridVisible })),
  toggleSunPanel: () => set(s => ({ sunPanelOpen: !s.sunPanelOpen })),
  setLayers: (layers) => set({ layers }),
  toggleLayer: (index) => set(s => {
    const layers = [...s.layers]
    layers[index] = { ...layers[index], visible: !layers[index].visible }
    layers[index].meshes.forEach(m => { m.visible = layers[index].visible })
    return { layers }
  }),
  setAllLayers: (visible) => set(s => {
    const layers = s.layers.map(l => {
      l.meshes.forEach(m => { m.visible = visible })
      return { ...l, visible }
    })
    return { layers }
  }),
  setSunTime: (minutes) => set({ sunTimeMinutes: minutes }),
  setSunDate: (date) => set({ sunDateStr: date }),
  setSunLat: (lat) => { localStorage.setItem('sunLat', String(lat)); set({ sunLat: lat }) },
  setSunLon: (lon) => { localStorage.setItem('sunLon', String(lon)); set({ sunLon: lon }) },
  setSunNorth: (deg) => { localStorage.setItem('sunNorth', String(deg)); set({ sunNorthDeg: deg }) },
  setSunTz: (tz) => { localStorage.setItem('sunTz', String(tz)); set({ sunTzOffset: tz }) },
  setSunAnimating: (v) => set({ sunAnimating: v }),
  setSunAnimSpeed: (s) => set({ sunAnimSpeed: s }),
  setObjectCount: (n) => set({ objectCount: n }),
  setSelectedName: (n) => set({ selectedName: n }),
  setBuildTime: (t) => set({ buildTime: t }),
  log: (msg) => set(s => ({
    logMessages: [...s.logMessages.slice(-19), `[${new Date().toLocaleTimeString()}] ${msg}`],
  })),
}))
