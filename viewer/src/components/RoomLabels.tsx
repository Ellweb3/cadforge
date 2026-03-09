import { Html } from "@react-three/drei";
import "./RoomLabels.css";

/**
 * Room data derived from project/config.py.
 *
 * Coordinate system: X = left-right, Y = front(road)-back, Z = up.
 * All values in mm (FreeCAD native units).
 *
 * Config constants used:
 *   M = 1000
 *   PLOT_W = 22000, FLAT_ZONE = 50000
 *   A_W = 8800, A_D = 4400, B_W = 3800, B_D = 12000
 *   TOTAL_W = 12600, TOTAL_D = 12000
 *   HOUSE_X = (22000 - 12600) / 2 = 4700
 *   HOUSE_Y = (50000 - 12000) / 2 + 5000 = 24000
 *   BX = 4700, BY = 24000
 *   AX = 4700 + 3800 = 8500, AY = 24000 + 12000 - 4400 = 31600
 *   CORR_W = 900, room_w = 3800 - 900 = 2900
 *   GX = 16000, GY = 4000, G_W = 3000, G_L = 11000
 */

interface RoomInfo {
  name: string;
  area: number; // m²
  position: [number, number, number]; // [x, y, z]
}

const ROOMS: RoomInfo[] = [
  // ── Block A ──
  {
    name: "Cocina / Living",
    area: 38.7,
    position: [12900, 33800, 500],
  },

  // ── Block B (stacked bottom-to-top from BY = 24000) ──
  {
    name: "Dormitorio 1",
    area: 9.6,
    position: [6150, 25650, 500],
  },
  {
    name: "Baño 1",
    area: 5.2,
    position: [6150, 28200, 500],
  },
  {
    name: "Baño 2",
    area: 5.2,
    position: [6150, 30000, 500],
  },
  {
    name: "Dormitorio 2",
    area: 8.1,
    position: [6150, 32300, 500],
  },
  {
    name: "Dormitorio 3",
    area: 8.7,
    position: [6150, 35200, 500],
  },
  {
    name: "Pasillo",
    area: 10.8,
    position: [8050, 30000, 500],
  },

  // ── Guest House (GX=16000, GY=4000, stacked bottom-to-top) ──
  {
    name: "Baño (guest)",
    area: 6.0,
    position: [17500, 5000, 500],
  },
  {
    name: "Dormitorio (guest)",
    area: 12.0,
    position: [17500, 8000, 500],
  },
  {
    name: "Living (guest)",
    area: 15.0,
    position: [17500, 12500, 500],
  },
];

interface RoomLabelsProps {
  floorPlanMode?: boolean;
  showRoomLabels?: boolean;
}

export default function RoomLabels({
  floorPlanMode = false,
  showRoomLabels = false,
}: RoomLabelsProps) {
  if (!floorPlanMode && !showRoomLabels) return null;

  return (
    <group>
      {ROOMS.map((room) => (
        <Html
          key={room.name}
          position={room.position}
          center
          style={{ pointerEvents: "none" }}
        >
          <div className="room-label">
            <div className="room-name">{room.name}</div>
            <div className="room-area">{room.area.toFixed(1)} m²</div>
          </div>
        </Html>
      ))}
    </group>
  );
}
