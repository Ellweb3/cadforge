import { useRef, useEffect } from 'react'
import './Minimap.css'

const PLOT_W = 22000, PLOT_D = 55000
const SCALE = 150 / PLOT_W  // ~0.0068

function mmToCanvas(x: number, y: number): [number, number] {
  return [x * SCALE, (PLOT_D - y) * SCALE]  // flip Y for canvas
}

export function Minimap() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const ctx = canvasRef.current?.getContext('2d')
    if (!ctx) return

    const W = 150, H = Math.round(PLOT_D * SCALE)
    ctx.clearRect(0, 0, W, H)

    // Ground
    ctx.fillStyle = 'rgba(53, 88, 40, 0.3)'
    ctx.fillRect(0, 0, W, H)

    // Plot border
    ctx.strokeStyle = '#555'
    ctx.lineWidth = 1
    ctx.strokeRect(0, 0, W, H)

    // Main house — L-shape: Block B (left wing) + Block A (right wing)
    // Block B: x=4700, y=24000, size 3800x12000
    ctx.fillStyle = 'rgba(140, 140, 160, 0.7)'
    const [bx, by] = mmToCanvas(4700, 36000)
    ctx.fillRect(bx, by, 3800 * SCALE, 12000 * SCALE)

    // Block A: x=8500, y=31600, size 8800x4400
    const [ax, ay] = mmToCanvas(8500, 36000)
    ctx.fillRect(ax, ay, 8800 * SCALE, 4400 * SCALE)

    // Guest house: x=16000, y=4000, size 3000x11000
    ctx.fillStyle = 'rgba(140, 140, 160, 0.5)'
    const [gx, gy] = mmToCanvas(16000, 15000)
    ctx.fillRect(gx, gy, 3000 * SCALE, 11000 * SCALE)

    // Pool: x=8000, y=38000, size 6000x3000
    ctx.fillStyle = 'rgba(56, 104, 136, 0.7)'
    const [px, py] = mmToCanvas(8000, 41000)
    ctx.fillRect(px, py, 6000 * SCALE, 3000 * SCALE)
  }, [])

  const height = Math.round(PLOT_D * SCALE)

  return (
    <div className="minimap">
      <canvas ref={canvasRef} width={150} height={height} />
    </div>
  )
}
