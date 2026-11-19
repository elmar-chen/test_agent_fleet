export interface PinDefinition {
  id: string;
  localX: number;
  localY: number;
  normalAngleDeg: number;
  name?: string;
  logicalPort?: string;
}

export interface ComponentGridDefinition {
  width: number;
  height: number;
  pins: PinDefinition[];
}

export const schematicGrid: Record<string, ComponentGridDefinition> = {
  rheostat: {
    width: 100,
    height: 100,
    pins: [
      { id: 'pin_a', localX: 0, localY: 50, normalAngleDeg: 180, logicalPort: 'A' },
      { id: 'pin_b', localX: 100, localY: 50, normalAngleDeg: 0, logicalPort: 'B' },
      { id: 'pin_c', localX: 100, localY: 50, normalAngleDeg: 0, logicalPort: 'P' },
      { id: 'pin_d', localX: 100, localY: 50, normalAngleDeg: 0, logicalPort: 'P' },
    ],
  },
  resistor: {
    width: 100,
    height: 100,
    pins: [
      { id: 'pin_a', localX: 0, localY: 50, normalAngleDeg: 180, logicalPort: 'A' },
      { id: 'pin_b', localX: 100, localY: 50, normalAngleDeg: 0, logicalPort: 'B' },
    ],
  },
  battery: {
    width: 100,
    height: 100,
    pins: [
      { id: 'pin_a', localX: 0, localY: 50, normalAngleDeg: 180, logicalPort: 'A' },
      { id: 'pin_b', localX: 100, localY: 50, normalAngleDeg: 0, logicalPort: 'B' },
    ],
  },
  bulb: {
    width: 100,
    height: 100,
    pins: [
      { id: 'pin_a', localX: 0, localY: 50, normalAngleDeg: 180, logicalPort: 'A' },
      { id: 'pin_b', localX: 100, localY: 50, normalAngleDeg: 0, logicalPort: 'B' },
    ],
  },
  switch: {
    width: 100,
    height: 100,
    pins: [
      { id: 'pin_a', localX: 0, localY: 50, normalAngleDeg: 180, logicalPort: 'A' },
      { id: 'pin_b', localX: 100, localY: 50, normalAngleDeg: 0, logicalPort: 'B' },
    ],
  },
};
