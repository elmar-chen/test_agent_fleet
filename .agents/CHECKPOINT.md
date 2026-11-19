# Living Memory Checkpoint

## Baseline Test Count
- Total Tests: 29 passed
- Baseline Status: 100% PASS

## Recent Changes & Issues
- **Issue #78**: Implemented schematic wire management in `wire.py` (`Wire` and `WireManager`), fulfilling requirement CR 8.9.1:
  - Selected wire endpoint dragging reconnects / moves existing wire endpoints.
  - Unselected wire endpoint dragging creates a new wire connection.
- **Issue #124**: Fixed rheostat schematic pin calibration bug:
  - Adjusted `rheostat` `pin_c` and `pin_d` coordinates in `schematicGrid.ts` / `schematic_grid.py` to `localX: 100, localY: 50, normalAngleDeg: 0`.
  - Updated `schematicPins` logicalPort `'P'` in `builtinComponents.ts` / `builtin_components.py` to `gxOffset: 50, gyOffset: 0, normalAngleDeg: 0`.
  - Implemented coordinate deduplication in `SchematicCanvas.tsx` / `schematic_canvas.py` (`deduplicate_pins` / `deduplicatePins`), merging overlapping right pins into a single interactive dot at `(100, 50)` and eliminating top isolated anchor point at `(50, 0)`.
