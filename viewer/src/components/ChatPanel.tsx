import { useState, useRef, useEffect, useCallback } from 'react'
import Markdown from 'react-markdown'
import { useStore } from '../store/useStore'
import './ChatPanel.css'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  text: string
}

const TOOL_LABELS: Record<string, string> = {
  thinking: 'Thinking...',
  Read: 'Reading file...',
  Edit: 'Editing file...',
  Write: 'Writing file...',
  Bash: 'Running command...',
  Glob: 'Searching files...',
  Grep: 'Searching code...',
}

function toolLabel(tool: string) {
  return TOOL_LABELS[tool] || `Using ${tool}...`
}

export function ChatPanel() {
  const chatOpen = useStore(s => s.chatOpen)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'system', text: 'Chat with Claude about your project. Try: "move the house 2m to the right" or "make the walls taller"' },
  ])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [activeTool, setActiveTool] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  // Connect to WebSocket
  useEffect(() => {
    if (!chatOpen) return

    let reconnectTimer: ReturnType<typeof setTimeout>
    let closed = false

    function connect() {
      const ws = new WebSocket('ws://localhost:3132')

      ws.onopen = () => {
        wsRef.current = ws
        setConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          switch (data.type) {
            case 'chat_start':
              setStreaming(true)
              setActiveTool('thinking')
              setMessages(prev => [...prev, { role: 'assistant', text: '' }])
              break

            case 'chat_delta':
              setActiveTool(null)
              setMessages(prev => {
                const updated = [...prev]
                const last = updated[updated.length - 1]
                if (last && last.role === 'assistant') {
                  updated[updated.length - 1] = { ...last, text: last.text + data.text }
                }
                return updated
              })
              break

            case 'chat_tool':
              setActiveTool(data.tool)
              break

            case 'chat_done':
              setStreaming(false)
              setActiveTool(null)
              break
          }
        } catch {
          // ignore non-JSON messages
        }
      }

      ws.onclose = () => {
        wsRef.current = null
        setConnected(false)
        if (!closed) {
          reconnectTimer = setTimeout(connect, 2000)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      closed = true
      clearTimeout(reconnectTimer)
      wsRef.current?.close()
      wsRef.current = null
      setConnected(false)
    }
  }, [chatOpen])

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input when opened
  useEffect(() => {
    if (chatOpen) inputRef.current?.focus()
  }, [chatOpen])

  const sendMessage = useCallback(() => {
    const text = input.trim()
    if (!text || streaming) return

    // Always show user's message
    setMessages(prev => [...prev, { role: 'user', text }])
    setInput('')

    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: 'system', text: 'Not connected to server. Make sure cadforge is running.' }])
      return
    }

    ws.send(JSON.stringify({ type: 'chat', message: text }))
  }, [input, streaming])

  if (!chatOpen) return null

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span className="chat-title">Claude</span>
        <span className={`chat-status ${connected ? 'chat-status-ok' : 'chat-status-off'}`}>
          {connected ? 'connected' : 'offline'}
        </span>
        <button className="chat-close" onClick={() => useStore.getState().toggleChat()}>x</button>
      </div>
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg chat-${msg.role}`}>
            {msg.role === 'user' && <span className="chat-role">You</span>}
            {msg.role === 'assistant' && <span className="chat-role">Claude</span>}
            <div className="chat-text">
              {msg.role === 'assistant' ? <Markdown>{msg.text}</Markdown> : msg.text}
              {streaming && i === messages.length - 1 && msg.text && <span className="chat-cursor">|</span>}
            </div>
          </div>
        ))}
        {streaming && activeTool && (
          <div className="chat-activity">
            <span className="chat-activity-dot" />
            {toolLabel(activeTool)}
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-row">
        <input
          ref={inputRef}
          className="chat-input"
          type="text"
          placeholder={streaming ? 'Claude is thinking...' : 'Ask Claude...'}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          disabled={streaming}
        />
        <button
          className="chat-send"
          onClick={sendMessage}
          disabled={streaming || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  )
}
