import { useStore } from '../store/useStore'

export function InfoPanel() {
  const objectCount = useStore(s => s.objectCount)
  const buildTime = useStore(s => s.buildTime)
  const selectedName = useStore(s => s.selectedName)

  return (
    <div className="panel info-panel">
      <h3>CadForge</h3>
      <div className="row">
        <span className="label">Objects:</span>
        <span>{objectCount || '-'}</span>
      </div>
      <div className="row">
        <span className="label">Build:</span>
        <span>{buildTime}</span>
      </div>
      <div className="row">
        <span className="label">Selected:</span>
        <span>{selectedName}</span>
      </div>
    </div>
  )
}
