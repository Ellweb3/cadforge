/**
 * NOAA Solar Position Algorithm.
 * Returns azimuth (0=N, 90=E, 180=S, 270=W) and elevation in degrees.
 */
export function solarPosition(
  lat: number,
  lon: number,
  localTimeMinutes: number,
  dateStr: string,
  tzOffset: number | null,
): { azimuth: number; elevation: number } {
  const rad = Math.PI / 180
  const parts = dateStr.split('-')
  const year = +parts[0], month = +parts[1], day = +parts[2]
  const localHours = localTimeMinutes / 60

  const tz = tzOffset !== null ? tzOffset : Math.round(lon / 15)
  const utcHours = localHours - tz

  // Julian Day
  const a = Math.floor((14 - month) / 12)
  const y2 = year + 4800 - a
  const m2 = month + 12 * a - 3
  const JDN = day + Math.floor((153 * m2 + 2) / 5) + 365 * y2
    + Math.floor(y2 / 4) - Math.floor(y2 / 100) + Math.floor(y2 / 400) - 32045
  const JD = JDN + (utcHours - 12) / 24
  const T = (JD - 2451545.0) / 36525.0

  let L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360
  if (L0 < 0) L0 += 360
  let M0 = (357.52911 + T * (35999.05029 - T * 0.0001537)) % 360
  if (M0 < 0) M0 += 360
  const ecc = 0.016708634 - T * (0.000042037 + T * 0.0000001267)

  const C = (1.914602 - T * (0.004817 + T * 0.000014)) * Math.sin(M0 * rad)
    + (0.019993 - T * 0.000101) * Math.sin(2 * M0 * rad)
    + 0.000289 * Math.sin(3 * M0 * rad)
  const sunLon = L0 + C

  const omega = 125.04 - 1934.136 * T
  const eps0 = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60
  const eps = eps0 + 0.00256 * Math.cos(omega * rad)

  const lambda = sunLon - 0.00569 - 0.00478 * Math.sin(omega * rad)
  const dec = Math.asin(Math.sin(eps * rad) * Math.sin(lambda * rad))

  const tanHalfEps = Math.tan(eps * rad / 2)
  const yy = tanHalfEps * tanHalfEps
  const eqTime = 4 / rad * (
    yy * Math.sin(2 * L0 * rad)
    - 2 * ecc * Math.sin(M0 * rad)
    + 4 * ecc * yy * Math.sin(M0 * rad) * Math.cos(2 * L0 * rad)
    - 0.5 * yy * yy * Math.sin(4 * L0 * rad)
    - 1.25 * ecc * ecc * Math.sin(2 * M0 * rad)
  )

  const solarTime = localTimeMinutes + eqTime + 4 * lon - 60 * tz
  let ha = solarTime / 4 - 180
  if (ha < -180) ha += 360
  if (ha > 180) ha -= 360

  const latR = lat * rad
  const haR = ha * rad

  const sinElev = Math.sin(latR) * Math.sin(dec) + Math.cos(latR) * Math.cos(dec) * Math.cos(haR)
  const elevation = Math.asin(clamp(sinElev, -1, 1)) / rad

  const cosAz = (Math.sin(dec) - Math.sin(latR) * sinElev)
    / (Math.cos(latR) * Math.cos(Math.asin(clamp(sinElev, -1, 1))))
  let azimuth: number
  if (ha > 0) {
    azimuth = (360 - Math.acos(clamp(cosAz, -1, 1)) / rad) % 360
  } else {
    azimuth = Math.acos(clamp(cosAz, -1, 1)) / rad
  }

  return { azimuth, elevation }
}

function clamp(v: number, min: number, max: number) {
  return Math.min(Math.max(v, min), max)
}
