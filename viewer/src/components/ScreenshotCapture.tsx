import { useThree } from '@react-three/fiber'
import { useEffect } from 'react'

/**
 * R3F component that listens for `cadforge:screenshot` custom events
 * and captures the current canvas as a PNG download.
 *
 * IMPORTANT: The parent <Canvas> must have `preserveDrawingBuffer: true`
 * in its `gl` prop for `toDataURL()` to return a non-blank image:
 *
 *   <Canvas gl={{ antialias: true, preserveDrawingBuffer: true }} ... >
 */
export function ScreenshotCapture() {
  const { gl, scene, camera } = useThree()

  useEffect(() => {
    function handleScreenshot() {
      gl.render(scene, camera)
      const url = gl.domElement.toDataURL('image/png')
      const a = document.createElement('a')
      a.download = `cadforge-${new Date().toISOString().slice(0, 10)}.png`
      a.href = url
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }

    window.addEventListener('cadforge:screenshot', handleScreenshot)
    return () => window.removeEventListener('cadforge:screenshot', handleScreenshot)
  }, [gl, scene, camera])

  return null
}
