import { useStore } from '../store/useStore'

export function StatusBar() {
  const status = useStore(s => s.status)
  const statusType = useStore(s => s.statusType)

  return (
    <div className="panel status-bar">
      <span className={`dot ${statusType}`} />
      <span>{status}</span>
    </div>
  )
}
