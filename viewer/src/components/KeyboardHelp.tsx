import { Fragment } from 'react'
import { useStore } from '../store/useStore'
import './KeyboardHelp.css'

const shortcuts = [
  { key: '1', action: 'Top View' },
  { key: '2', action: 'Front View' },
  { key: '3', action: 'Right View' },
  { key: '4', action: 'Isometric View' },
  { key: 'W', action: 'Wireframe' },
  { key: 'F', action: 'Fly Mode' },
  { key: 'G', action: 'Grid' },
  { key: 'P', action: 'Floor Plan' },
  { key: 'S', action: 'Sun Panel' },
  { key: 'C', action: 'Chat' },
  { key: '?', action: 'This Help' },
  { key: 'Esc', action: 'Close Panels' },
]

export function KeyboardHelp() {
  const show = useStore(s => s.showKeyboardHelp)

  if (!show) return null

  const close = () => useStore.getState().toggleKeyboardHelp()

  return (
    <div className="keyboard-help-backdrop" onClick={close}>
      <div className="keyboard-help-card" onClick={e => e.stopPropagation()}>
        <h2>
          Keyboard Shortcuts
          <button className="keyboard-help-close" onClick={close}>&times;</button>
        </h2>
        <div className="keyboard-help-grid">
          {shortcuts.map(s => (
            <Fragment key={s.key}>
              <span className="keyboard-help-key">{s.key}</span>
              <span className="keyboard-help-action">{s.action}</span>
            </Fragment>
          ))}
        </div>
      </div>
    </div>
  )
}
