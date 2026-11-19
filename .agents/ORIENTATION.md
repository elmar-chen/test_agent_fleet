# Project Orientation

## Core Architecture
- `calculator.py`: Pure mathematical helper functions (`add`, `multiply`, `divide`).
- `wire.py`: Wire and WireManager classes for schematic wire editing (selection, endpoint dragging/reconnection when selected, new wire creation when unselected).
- `left_toolbar.py`: LeftToolbar component library drag support (`application/x-electric-component`), cursor style management (`grab`/`grabbing`), single-click viewport center component spawning, and mode tool decoupling (`MODE_TOOLS` vs `COMPONENT_ITEMS`).
- `test_calculator.py`: Pytest suite for calculator module.
- `test_wire.py`: Pytest suite covering wire management and drag-reconnect / new line logic.
- `test_left_toolbar.py`: Pytest suite for LeftToolbar drag-and-drop, mode tool decoupling, cursor state, and single-click spawning.

