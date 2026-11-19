import pytest
from circuit_store import CircuitStore, Component
from schematic_grid import SCHEMATIC_GRID_DEFINITIONS, get_schematic_grid
from builtin_components import BUILTIN_COMPONENTS, get_builtin_component
from schematic_canvas import SchematicCanvas, GhostPreview


def test_schematic_grid_rheostat_pins():
    """Requirement 1: Test schematicGrid.ts rheostat pin_c and pin_d coordinates

    are aligned with the right-side lead-out line: localX: 100, localY: 50, normalAngleDeg: 0.
    Ensure top isolated anchor point (50, 0) is removed.
    """
    grid_def = get_schematic_grid("rheostat")
    pins = grid_def["pins"]
    assert len(pins) == 4

    # Map pins by ID
    pins_by_id = {p["id"]: p for p in pins}

    # Verify pin_a (Left terminal)
    assert pins_by_id["pin_a"]["localX"] == 0
    assert pins_by_id["pin_a"]["localY"] == 50
    assert pins_by_id["pin_a"]["normalAngleDeg"] == 180

    # Verify pin_b (Right terminal)
    assert pins_by_id["pin_b"]["localX"] == 100
    assert pins_by_id["pin_b"]["localY"] == 50
    assert pins_by_id["pin_b"]["normalAngleDeg"] == 0

    # Verify pin_c (Slider terminal aligned right)
    assert pins_by_id["pin_c"]["localX"] == 100
    assert pins_by_id["pin_c"]["localY"] == 50
    assert pins_by_id["pin_c"]["normalAngleDeg"] == 0

    # Verify pin_d (Slider terminal aligned right)
    assert pins_by_id["pin_d"]["localX"] == 100
    assert pins_by_id["pin_d"]["localY"] == 50
    assert pins_by_id["pin_d"]["normalAngleDeg"] == 0

    # Ensure no pin is located at top center (50, 0)
    top_pins = [p for p in pins if p["localX"] == 50 and p["localY"] == 0]
    assert len(top_pins) == 0


def test_builtin_components_rheostat_schematic_pins():
    """Requirement 2: Test builtinComponents.ts schematicPins logicalPort 'P'

    is updated to gxOffset: 50, gyOffset: 0, normalAngleDeg: 0.
    """
    comp_def = get_builtin_component("rheostat")
    schematic_pins = comp_def["schematicPins"]
    assert len(schematic_pins) == 4

    p_ports = [p for p in schematic_pins if p["logicalPort"] == "P"]
    assert len(p_ports) == 2

    for p in p_ports:
        assert p["gxOffset"] == 50
        assert p["gyOffset"] == 0
        assert p["normalAngleDeg"] == 0


def test_schematic_canvas_pin_deduplication():
    """Requirement 3: Test SchematicCanvas coordinate deduplication for overlapping pins.

    Overlapping right pins (pin_b, pin_c, pin_d at localX: 100, localY: 50) must be merged into
    a single interactive dot at the right border midpoint, eliminating top isolated anchors.
    """
    canvas = SchematicCanvas()
    grid_def = get_schematic_grid("rheostat")
    raw_pins = grid_def["pins"]

    deduped = canvas.deduplicate_pins(raw_pins)

    # 4 raw pins -> 2 unique coordinate locations ((0, 50) and (100, 50))
    assert len(deduped) == 2

    left_dot = [p for p in deduped if p["localX"] == 0 and p["localY"] == 50][0]
    right_dot = [p for p in deduped if p["localX"] == 100 and p["localY"] == 50][0]

    assert left_dot["merged_pin_ids"] == ["pin_a"]
    assert set(right_dot["merged_pin_ids"]) == {"pin_b", "pin_c", "pin_d"}

    # Top center dot (50, 0) should not exist
    top_dots = [p for p in deduped if p["localX"] == 50 and p["localY"] == 0]
    assert len(top_dots) == 0


def test_schematic_canvas_render_interactive_dots():
    """Test render_interactive_dots calculates correct absolute canvas positions

    and renders only 2 interactive dots for a placed rheostat.
    """
    store = CircuitStore()
    canvas = SchematicCanvas(circuit_store=store)

    comp = store.addComponent("rheostat", x=200.0, y=140.0)
    dots = canvas.render_interactive_dots(comp)

    # Exactly 2 interactive dots rendered for rheostat
    assert len(dots) == 2

    left_dot = [d for d in dots if d["localX"] == 0][0]
    right_dot = [d for d in dots if d["localX"] == 100][0]

    # Verify left dot position: abs = comp (200, 140) + local (0, 50) = (200, 190)
    assert left_dot["absX"] == 200.0
    assert left_dot["absY"] == 190.0

    # Verify right dot position: abs = comp (200, 140) + local (100, 50) = (300, 190)
    assert right_dot["absX"] == 300.0
    assert right_dot["absY"] == 190.0


def test_schematic_canvas_drag_drop_flow():
    """Test complete SchematicCanvas drag and drop workflow for rheostat."""
    store = CircuitStore()
    canvas = SchematicCanvas(circuit_store=store, grid_size=20)

    # Drag enter
    preview = canvas.on_drag_enter({"type": "rheostat", "mouse_x": 105.0, "mouse_y": 195.0})
    assert preview["visible"] is True
    assert preview["component_type"] == "rheostat"
    assert preview["x"] == 100.0  # Snapped from 105
    assert preview["y"] == 200.0  # Snapped from 195

    # Drag over
    over_preview = canvas.on_drag_over({"type": "rheostat", "mouse_x": 142.0, "mouse_y": 161.0})
    assert over_preview["x"] == 140.0
    assert over_preview["y"] == 160.0

    # Drop
    dropped = canvas.on_drop({"type": "rheostat", "mouse_x": 142.0, "mouse_y": 161.0})
    assert dropped is not None
    assert dropped.component_type == "rheostat"
    assert dropped.x == 140.0
    assert dropped.y == 160.0
    assert dropped.selected is True
    assert store.selected_component_id == dropped.id

    # Render dots on dropped component
    dots = canvas.render_interactive_dots(dropped)
    assert len(dots) == 2
    assert sorted([d["absX"] for d in dots]) == [140.0, 240.0]
