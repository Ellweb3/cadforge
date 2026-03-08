import { useEffect } from 'react'
import { useStore } from '../store/useStore'

export function useWebSocket(port = 3132) {
  const { setStatus, setBuildTime, setObjectCount, reload, log } = useStore()

  useEffect(() => {
    let ws: WebSocket
    let reconnectTimer: ReturnType<typeof setTimeout>

    function connect() {
      ws = new WebSocket(`ws://localhost:${port}`)

      ws.onopen = () => {
        log('WS connected')
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        switch (data.type) {
          case 'build_start':
            setStatus('Building...', 'building')
            break
          case 'build_complete':
            setStatus(`Built in ${data.time}s — ${data.objects} objects`, 'ok')
            setBuildTime(`${data.time}s`)
            setObjectCount(data.objects)
            reload()
            break
          case 'build_error':
            setStatus('Build failed', 'error')
            break
        }
      }

      ws.onclose = () => {
        reconnectTimer = setTimeout(connect, 3000)
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      clearTimeout(reconnectTimer)
      ws?.close()
    }
  }, [port])
}
