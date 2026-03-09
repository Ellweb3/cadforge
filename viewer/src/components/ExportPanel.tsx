import { useStore } from '../store/useStore'
import { sceneRef } from './SceneExporter'
import { STLExporter } from 'three/examples/jsm/exporters/STLExporter.js'
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js'
import './ExportPanel.css'

function getDateStamp(): string {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function exportPNG() {
  window.dispatchEvent(new Event('cadforge:screenshot'))
}

async function exportGLB() {
  const resp = await fetch('/dist/model.glb')
  const blob = await resp.blob()
  downloadBlob(blob, `cadforge-${getDateStamp()}.glb`)
}

function exportSTL() {
  if (!sceneRef) return
  const exporter = new STLExporter()
  const result = exporter.parse(sceneRef, { binary: false })
  const blob = new Blob([result as string], { type: 'application/octet-stream' })
  downloadBlob(blob, `cadforge-${getDateStamp()}.stl`)
}

function exportOBJ() {
  if (!sceneRef) return
  const exporter = new OBJExporter()
  const result = exporter.parse(sceneRef)
  const blob = new Blob([result], { type: 'text/plain' })
  downloadBlob(blob, `cadforge-${getDateStamp()}.obj`)
}

async function exportCadforge() {
  const resp = await fetch('/api/export/cadforge')
  if (!resp.ok) { alert('Export failed — cadforge server required'); return }
  const blob = await resp.blob()
  downloadBlob(blob, `cadforge-${getDateStamp()}.cadforge`)
}

async function exportFreeCADScript() {
  const resp = await fetch('/api/export/freecad-script')
  if (!resp.ok) { alert('Export failed — cadforge server required'); return }
  const blob = await resp.blob()
  downloadBlob(blob, `cadforge-${getDateStamp()}.py`)
}

const formats = [
  { name: 'PNG Screenshot', desc: 'Current viewport as image', action: exportPNG },
  { name: 'GLB Model', desc: 'Download original 3D model', action: exportGLB },
  { name: 'STL Export', desc: 'Triangulated mesh (3D printing)', action: exportSTL },
  { name: 'OBJ Export', desc: 'Wavefront OBJ (universal)', action: exportOBJ },
  { name: 'CadForge Project', desc: 'Full project archive (.cadforge)', action: exportCadforge },
  { name: 'FreeCAD Script', desc: 'Standalone Python script (.py)', action: exportFreeCADScript },
]

export function ExportPanel() {
  const exportPanelOpen = useStore(s => s.exportPanelOpen)
  const toggleExportPanel = useStore(s => s.toggleExportPanel)

  if (!exportPanelOpen) return null

  return (
    <>
      <div className="export-overlay" onClick={toggleExportPanel} />
      <div className="panel export-panel">
        <div className="export-header">
          <span className="export-title">Export Model</span>
          <button className="export-close" onClick={toggleExportPanel}>&times;</button>
        </div>
        <div className="export-list">
          {formats.map(f => (
            <div className="export-row" key={f.name}>
              <div className="export-format">
                <span className="export-format-name">{f.name}</span>
                <span className="export-format-desc">{f.desc}</span>
              </div>
              <button className="export-btn" onClick={() => { f.action(); toggleExportPanel(); }}>
                Download
              </button>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
