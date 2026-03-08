import { useStore } from '../store/useStore'

export function LogPanel() {
  const messages = useStore(s => s.logMessages)
  if (messages.length === 0) return null

  return (
    <div className="panel log-panel">
      {messages.map((msg, i) => (
        <div key={i}>{msg}</div>
      ))}
    </div>
  )
}
