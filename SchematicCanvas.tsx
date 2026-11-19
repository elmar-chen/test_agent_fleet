import React from 'react';
import { schematicGrid, PinDefinition } from './schematicGrid';
import { builtinComponents, SchematicPin } from './builtinComponents';

export interface ComponentProps {
  id: string;
  type: string;
  x: number;
  y: number;
  width?: number;
  height?: number;
}

export interface InteractiveDot {
  id: string;
  localX: number;
  localY: number;
  absX: number;
  absY: number;
  normalAngleDeg: number;
  mergedPinIds: string[];
}

/**
 * Deduplicates overlapping pins sharing the exact same (localX, localY) coordinates,
 * ensuring only a single interactive dot is rendered per unique coordinate location.
 */
export function deduplicatePins(pins: PinDefinition[]): PinDefinition[] {
  const seen = new Map<string, PinDefinition>();

  for (const pin of pins) {
    const key = `${pin.localX},${pin.localY}`;
    if (!seen.has(key)) {
      seen.set(key, { ...pin });
    }
  }

  return Array.from(seen.values());
}

export const SchematicCanvas: React.FC<{ components: ComponentProps[] }> = ({ components }) => {
  return (
    <div className="schematic-canvas" style={{ position: 'relative', width: '100%', height: '100%' }}>
      {components.map((comp) => {
        const gridDef = schematicGrid[comp.type];
        const rawPins = gridDef?.pins || [];
        const uniquePins = deduplicatePins(rawPins);

        return (
          <div
            key={comp.id}
            className="schematic-component"
            style={{
              position: 'absolute',
              left: comp.x,
              top: comp.y,
              width: comp.width || 100,
              height: comp.height || 100,
            }}
          >
            {uniquePins.map((pin) => (
              <div
                key={pin.id}
                className="interactive-dot"
                data-pin-id={pin.id}
                style={{
                  position: 'absolute',
                  left: pin.localX,
                  top: pin.localY,
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  transform: 'translate(-50%, -50%)',
                  backgroundColor: '#1890ff',
                }}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
};
