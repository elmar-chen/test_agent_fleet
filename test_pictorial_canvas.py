"""
Unit tests for PictorialCanvas drag & drop, ghost preview, and grid snapping (Task 12.2).
"""
import pytest
from pictorial_canvas import PictorialCanvas, Component, CircuitStore, GhostPreview, Terminal


def test_pictorial_canvas_grid_snapping():
    canvas = PictorialCanvas(grid_size=10.0)
    assert canvas.snap_to_grid(12.3, 17.8) == (10.0, 20.0)
    assert canvas.snap_to_grid(26.0, 24.9) == (30.0, 20.0)
    assert canvas.snap_to_grid(44.0, 88.0, grid_size=20.0) == (40.0, 80.0)


def test_pictorial_canvas_centered_position():
    canvas = PictorialCanvas(canvas_offset=(10.0, 5.0))
    # Mouse at (100, 100), canvas offset (10, 5) -> relative (90, 95)
    # Center calculation: (90 - 40/2, 95 - 20/2) = (70, 85)
    # Note: calculate_centered_position converts cursor position relative to offset
    pos = canvas.calculate_centered_position(mouse_x=100.0, mouse_y=100.0, width=40.0, height=20.0)
    assert pos == (90.0, 95.0)


def test_pictorial_canvas_drag_over_ghost_preview():
    canvas = PictorialCanvas(grid_size=10.0)
    payload = {
        "type": "resistor",
        "name": "Resistor",
        "mouse_x": 42.0,
        "mouse_y": 68.0,
        "width": 40.0,
        "height": 20.0,
    }

    # Drag enter
    ghost = canvas.on_drag_enter(payload)
    assert ghost is not None
    assert ghost["visible"] is True
    assert ghost["component_type"] == "resistor"
    assert ghost["position"] == (40.0, 70.0)
    assert ghost["box"]["style"]["stroke"] == "#1890ff"
    assert ghost["box"]["style"]["stroke_dasharray"] == "4 4"

    # Drag over
    ghost_over = canvas.on_drag_over({"type": "resistor", "mouse_x": 84.0, "mouse_y": 102.0})
    assert ghost_over["visible"] is True
    assert ghost_over["position"] == (80.0, 100.0)


def test_pictorial_canvas_drag_leave():
    canvas = PictorialCanvas(grid_size=10.0)
    canvas.on_drag_enter({"type": "bulb", "mouse_x": 50.0, "mouse_y": 50.0})
    assert canvas.ghost_preview is not None

    canvas.on_drag_leave()
    assert canvas.ghost_preview is None


def test_pictorial_canvas_drop_placement():
    circuit_store = CircuitStore()
    canvas = PictorialCanvas(circuit_store=circuit_store, grid_size=10.0)

    payload = {
        "type": "battery",
        "name": "Battery 9V",
        "mouse_x": 34.0,
        "mouse_y": 56.0,
        "size": (60.0, 30.0),
        "props": {"voltage": 9.0},
    }

    comp = canvas.on_drop(payload)
    assert comp is not None
    assert isinstance(comp, Component)
    assert comp.type == "battery"
    assert comp.position == (30.0, 60.0)
    assert comp.selected is True
    assert circuit_store.selected_component_id == comp.id
    assert len(circuit_store.components) == 1
    assert canvas.ghost_preview is None


def test_pictorial_canvas_invalid_drag_and_drop():
    canvas = PictorialCanvas()
    ghost = canvas.on_drag_over({"x": 10.0, "y": 10.0})  # missing type
    assert ghost is None

    comp = canvas.on_drop({"x": 10.0, "y": 10.0})  # missing type
    assert comp is None
    assert len(canvas.components) == 0
