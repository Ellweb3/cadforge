import { useEffect } from 'react'
import { useStore } from '../store/useStore'

export function useKeyboard() {
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const el = e.target as HTMLElement
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT' || el.isContentEditable) return

      const s = useStore.getState()

      switch(e.key) {
        case '1':
          window.dispatchEvent(new CustomEvent('cadforge:setView', { detail: 'top' }))
          break
        case '2':
          window.dispatchEvent(new CustomEvent('cadforge:setView', { detail: 'front' }))
          break
        case '3':
          window.dispatchEvent(new CustomEvent('cadforge:setView', { detail: 'right' }))
          break
        case '4':
          window.dispatchEvent(new CustomEvent('cadforge:setView', { detail: 'iso' }))
          break
        case 'w': case 'W':
          s.toggleWireframe()
          break
        case 'f': case 'F':
          s.toggleFly()
          break
        case 'g': case 'G':
          s.toggleGrid()
          break
        case 'p': case 'P':
          s.toggleFloorPlan()
          break
        case 'c': case 'C':
          s.toggleChat()
          break
        case 's': case 'S':
          s.toggleSunPanel()
          break
        case '?':
          s.toggleKeyboardHelp()
          break
        case 'Escape':
          useStore.setState({
            sunPanelOpen: false,
            showKeyboardHelp: false,
            clipPanelOpen: false,
            exportPanelOpen: false,
            measureMode: false,
          })
          break
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])
}
