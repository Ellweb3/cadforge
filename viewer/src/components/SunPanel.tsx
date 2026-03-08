import { useStore } from '../store/useStore'
import { useSunData } from './SunLight'

export function SunPanel() {
  const {
    sunPanelOpen, sunTimeMinutes, sunDateStr,
    sunLat, sunLon, sunNorthDeg, sunTzOffset,
    sunAnimating, sunAnimSpeed,
    setSunTime, setSunDate, setSunLat, setSunLon,
    setSunNorth, setSunTz, setSunAnimating, setSunAnimSpeed,
  } = useStore()

  const { azimuth, elevation } = useSunData()

  if (!sunPanelOpen) return null

  const hh = String(Math.floor(sunTimeMinutes / 60)).padStart(2, '0')
  const mm = String(Math.round(sunTimeMinutes % 60)).padStart(2, '0')
  const autoTz = Math.round(sunLon / 15)

  return (
    <div className="panel sun-panel">
      <div className="sun-header">
        <span className="sun-title">Sun</span>
        <span className="sun-info">Az {azimuth.toFixed(0)}° El {elevation.toFixed(1)}°</span>
      </div>

      <div className="sun-row">
        <input
          type="range" min={0} max={1439} step={1}
          value={sunTimeMinutes}
          onChange={e => setSunTime(+e.target.value)}
          className="sun-slider"
        />
        <span className="sun-time">{hh}:{mm}</span>
      </div>

      <div className="sun-row">
        <label className="sun-label">Date</label>
        <input
          type="date" value={sunDateStr}
          onChange={e => setSunDate(e.target.value)}
          className="sun-input"
        />
        <button
          className={`sun-play ${sunAnimating ? 'active' : ''}`}
          onClick={() => setSunAnimating(!sunAnimating)}
        >
          {sunAnimating ? '⏸' : '▶'}
        </button>
        <select
          value={sunAnimSpeed}
          onChange={e => setSunAnimSpeed(+e.target.value)}
          className="sun-select"
        >
          <option value={1}>1x</option>
          <option value={10}>10x</option>
          <option value={60}>60x</option>
          <option value={360}>360x</option>
          <option value={1440}>1440x</option>
        </select>
      </div>

      <div className="sun-row sun-coords">
        <span className="sun-label-sm">📍</span>
        <label className="sun-label">Lat</label>
        <input
          type="number" step={0.000001} value={sunLat}
          onChange={e => setSunLat(+e.target.value)}
          className="sun-input coord"
        />
        <label className="sun-label">Lon</label>
        <input
          type="number" step={0.000001} value={sunLon}
          onChange={e => setSunLon(+e.target.value)}
          className="sun-input coord"
        />
        <label className="sun-label">N°</label>
        <input
          type="number" step={1} value={sunNorthDeg}
          onChange={e => setSunNorth(+e.target.value)}
          className="sun-input small"
          title="Plot north: degrees from Y+ clockwise"
        />
        <label className="sun-label">UTC</label>
        <input
          type="number" step={1}
          value={sunTzOffset !== null ? sunTzOffset : autoTz}
          onChange={e => setSunTz(+e.target.value)}
          className="sun-input small"
          title="Timezone offset from UTC"
        />
      </div>
    </div>
  )
}
