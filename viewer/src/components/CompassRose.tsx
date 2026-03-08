import { useMemo } from 'react'
import * as THREE from 'three'
import { useStore } from '../store/useStore'

function TextSprite({ text, color, position }: { text: string; color: string; position: [number, number, number] }) {
  const texture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 64; canvas.height = 64
    const ctx = canvas.getContext('2d')!
    ctx.font = 'bold 48px sans-serif'
    ctx.fillStyle = color
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(text, 32, 32)
    return new THREE.CanvasTexture(canvas)
  }, [text, color])

  return (
    <sprite position={position} scale={[2000, 2000, 1]}>
      <spriteMaterial map={texture} depthTest={false} />
    </sprite>
  )
}

const LABELS = [
  { text: 'N', angle: 0, color: '#ff4444' },
  { text: 'E', angle: 90, color: '#888888' },
  { text: 'S', angle: 180, color: '#888888' },
  { text: 'W', angle: 270, color: '#888888' },
]

export function CompassRose({ center, radius = 38000 }: { center: [number, number, number]; radius?: number }) {
  const sunNorthDeg = useStore(s => s.sunNorthDeg)
  const rad = Math.PI / 180

  return (
    <group>
      {LABELS.map(({ text, angle, color }) => {
        const a = (angle - sunNorthDeg) * rad
        const x = center[0] + Math.sin(a) * radius
        const y = center[1] + Math.cos(a) * radius
        return (
          <TextSprite
            key={text}
            text={text}
            color={color}
            position={[x, y, 200]}
          />
        )
      })}
    </group>
  )
}
