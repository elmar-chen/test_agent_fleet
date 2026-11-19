"""
Unit tests for PictorialCanvas drag-and-drop receiving, ghost preview, grid snapping, and circuitStore instantiation.
Issue #121 (Epic #119).
"""

import pytest
from circuit_store import CircuitStore
from pictorial_canvas import (
    Terminal,
    PictorialComponent,
    GhostPreview,
    PictorialCanvas,
)


def test_grid_snapping_20px_and_10px():
    """Test 20px and 10px grid snapping logic."""
    canvas_20 = PictorialCanvas(grid_size=20.0)
    assert canvas_20.snap_to_grid(23.0, 47.0) == (20.0, 40.0)
    assert canvas_20.snap_to_grid(31.0, 58.0) == (40.0, 60.0)

    canvas_10 = PictorialCanvas(grid_size=10.0)
    assert canvas_10.snap_to_grid(23.0, 47.0) == (20.0, 50.0)
    assert canvas_10.snap_to_grid(36.0, 54.0) == (40.0, 50.0)


def test_coordinate_conversion_and_centering():
    """Test mouse coordinate conversion with canvas offset and center alignment."""
    canvas = PictorialCanvas(canvas_offset=(50.0, 100.0))

    # Mouse at (250, 300), component size (100, 60)
    # Canvas relative mouse: (200, 200)
    # Top-left centered: (200 - 50, 200 - 30) = (150, 170)
    top_left = canvas.calculate_centered_position(250.0, 300.0, 100.0, 60.0)
    assert top_left == (150.0, 170.0)


def test_on_drag_over_ghost_preview_and_terminals():
    """Test onDragOver renders semi-transparent blue dashed Ghost box and terminal indicator points."""
    canvas = PictorialCanvas(canvas_offset=(0.0, 0.0), grid_size=20.0)

    terminals = [
        {"id": "t1", "rel_x": 0, "rel_y": 20, "label": "VCC"},
        {"id": "t2", "rel_x": 80, "rel_y": 20, "label": "GND"},
    ]

    event = {
        "mouse_x": 105.0,
        "mouse_y": 215.0,
        "type": "resistor",
        "width": 80.0,
        "height": 40.0,
        "terminals": terminals,
        "grid_size": 20,
    }

    render_data = canvas.onDragOver(event, center_align=True)

    # Centered top-left: raw_x = 105 - 40 = 65, raw_y = 215 - 20 = 195
    # 20px grid snapped: 65 -> 60, 195 -> 200
    assert render_data["visible"] is True
    assert render_data["component_type"] == "resistor"
    assert render_data["position"] == (60.0, 200.0)
    assert render_data["size"] == (80.0, 40.0)

    # Semi-transparent blue dashed Ghost style verification
    style = render_data["box"]["style"]
    assert style["stroke"] == "#1890ff"
    assert style["stroke_dasharray"] == "4 4"
    assert "rgba" in style["fill"]

    # Terminal indicator points verification
    terms = render_data["terminals"]
    assert len(terms) == 2
    assert terms[0]["id"] == "t1"
    assert terms[0]["x"] == 60.0 + 0
    assert terms[0]["y"] == 200.0 + 20
    assert terms[1]["id"] == "t2"
    assert terms[1]["x"] == 60.0 + 80
    assert terms[1]["y"] == 200.0 + 20


def test_on_drag_over_10px_grid_snapping():
    """Test onDragOver with 10px grid snapping mode."""
    canvas = PictorialCanvas(grid_size=10.0)

    render_data = canvas.onDragOver(
        105.0,
        215.0,
        component_type="switch",
        size=(60.0, 30.0),
        grid_size=10,
        center_align=True,
    )

    # Centered top-left: raw_x = 105 - 30 = 75, raw_y = 215 - 15 = 200
    # 10px grid snapped: 75 -> 80, 200 -> 200
    assert render_data["position"] == (80.0, 200.0)


def test_on_drag_leave():
    """Test onDragLeave resets and hides ghost preview."""
    canvas = PictorialCanvas()
    canvas.onDragOver(100.0, 100.0, component_type="battery", size=(40.0, 20.0))

    assert canvas.ghost_preview is not None
    assert canvas.render_ghost_preview()["visible"] is True

    canvas.onDragLeave()

    assert canvas.ghost_preview is None
    assert canvas.render_ghost_preview()["visible"] is False


def test_on_drop_instantiates_and_auto_selects_component():
    """Test onDrop instantiates component via circuitStore.addComponent and auto selects it."""
    store = CircuitStore()
    canvas = PictorialCanvas(circuit_store=store, grid_size=20.0)

    terminals = [(0.0, 10.0), (50.0, 10.0)]
    comp = canvas.onDrop(
        120.0,
        160.0,
        component_type="bulb",
        size=(50.0, 30.0),
        terminals=terminals,
        grid_size=20,
        center_align=True,
    )

    # Centered top-left: raw_x = 120 - 25 = 95, raw_y = 160 - 15 = 145
    # 20px grid snapped: 95 -> 100, 145 -> 140
    assert comp.component_type == "bulb"
    assert comp.position == (100.0, 140.0)
    assert comp.size == (50.0, 30.0)
    assert comp.selected is True

    # Check store state
    assert len(store.components) == 1
    assert store.selected_component_id == comp.id
    assert store.selected_component == comp

    # Ghost preview should be cleared after drop
    assert canvas.ghost_preview is None


def test_on_drop_multiple_components_selection_switch():
    """Test dropping a second component automatically switches selection to the new component."""
    store = CircuitStore()
    canvas = PictorialCanvas(circuit_store=store)

    comp1 = canvas.onDrop(100.0, 100.0, component_type="battery", size=(40.0, 20.0))
    assert comp1.selected is True
    assert store.selected_component_id == comp1.id

    comp2 = canvas.onDrop(200.0, 200.0, component_type="resistor", size=(60.0, 20.0))
    assert comp1.selected is False
    assert comp2.selected is True
    assert store.selected_component_id == comp2.id
    assert len(store.components) == 2


def test_circuit_store_selection_and_clear():
    """Test CircuitStore selection management and clear function."""
    store = CircuitStore()
    c1 = store.addComponent("battery", 0.0, 0.0)
    c2 = store.addComponent("resistor", 100.0, 0.0)

    assert store.selected_component_id == c2.id
    assert c1.selected is False
    assert c2.selected is True

    store.selectComponent(c1.id)
    assert store.selected_component_id == c1.id
    assert c1.selected is True
    assert c2.selected is False

    store.clear()
    assert len(store.components) == 0
    assert store.selected_component_id is None
