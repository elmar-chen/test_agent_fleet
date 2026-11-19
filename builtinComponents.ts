export interface SchematicPin {
  id: string;
  logicalPort: string;
  gxOffset: number;
  gyOffset: number;
  normalAngleDeg: number;
}

export interface BuiltinComponent {
  type: string;
  name: string;
  schematicPins: SchematicPin[];
}

export const builtinComponents: Record<string, BuiltinComponent> = {
  rheostat: {
    type: 'rheostat',
    name: '滑动变阻器',
    schematicPins: [
      { id: 'pin_a', logicalPort: 'A', gxOffset: -50, gyOffset: 0, normalAngleDeg: 180 },
      { id: 'pin_b', logicalPort: 'B', gxOffset: 50, gyOffset: 0, normalAngleDeg: 0 },
      { id: 'pin_c', logicalPort: 'P', gxOffset: 50, gyOffset: 0, normalAngleDeg: 0 },
      { id: 'pin_d', logicalPort: 'P', gxOffset: 50, gyOffset: 0, normalAngleDeg: 0 },
    ],
  },
  resistor: {
    type: 'resistor',
    name: '电阻',
    schematicPins: [
      { id: 'pin_a', logicalPort: 'A', gxOffset: -50, gyOffset: 0, normalAngleDeg: 180 },
      { id: 'pin_b', logicalPort: 'B', gxOffset: 50, gyOffset: 0, normalAngleDeg: 0 },
    ],
  },
  battery: {
    type: 'battery',
    name: '电源',
    schematicPins: [
      { id: 'pin_a', logicalPort: 'A', gxOffset: -50, gyOffset: 0, normalAngleDeg: 180 },
      { id: 'pin_b', logicalPort: 'B', gxOffset: 50, gyOffset: 0, normalAngleDeg: 0 },
    ],
  },
};
