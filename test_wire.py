import pytest
from wire import Wire, WireManager


def test_wire_initialization():
    wire = Wire((0, 0), (10, 10), wire_id="wire_1", selected=True)
    assert wire.wire_id == "wire_1"
    assert wire.start_point == (0.0, 0.0)
    assert wire.end_point == (10.0, 10.0)
    assert wire.selected is True
    assert "Wire(id=wire_1" in repr(wire)


def test_wire_selection_management():
    wm = WireManager()
    w1 = wm.create_wire((0, 0), (5, 5))
    w2 = wm.create_wire((10, 10), (20, 20))

    assert len(wm.wires) == 2
    assert len(wm.get_selected_wires()) == 0

    wm.select_wire(w1.wire_id)
    assert w1.selected is True
    assert w2.selected is False
    assert wm.get_selected_wires() == [w1]

    wm.deselect_wire(w1.wire_id)
    assert w1.selected is False
    assert len(wm.get_selected_wires()) == 0

    wm.select_wire(w1.wire_id)
    wm.select_wire(w2.wire_id)
    assert len(wm.get_selected_wires()) == 2

    wm.deselect_all()
    assert len(wm.get_selected_wires()) == 0


def test_drag_endpoint_when_selected_reconnects_start_point():
    """
    CR Requirement: When wire is selected, dragging endpoint moves/reconnects line.
    Testing start point move.
    """
    wm = WireManager()
    wire = wm.create_wire((0.0, 0.0), (10.0, 10.0))
    wm.select_wire(wire.wire_id)

    initial_wire_count = len(wm.wires)

    # Drag start endpoint (0, 0) to new location (2.0, 3.0)
    result_wire = wm.handle_drag_endpoint(
        start_pos=(0.0, 0.0), new_pos=(2.0, 3.0), wire_id=wire.wire_id
    )

    assert result_wire.wire_id == wire.wire_id
    assert result_wire.start_point == (2.0, 3.0)
    assert result_wire.end_point == (10.0, 10.0)
    # Total wire count should remain unchanged (reconnected existing wire)
    assert len(wm.wires) == initial_wire_count


def test_drag_endpoint_when_selected_reconnects_end_point():
    """
    CR Requirement: When wire is selected, dragging endpoint moves/reconnects line.
    Testing end point move.
    """
    wm = WireManager()
    wire = wm.create_wire((0.0, 0.0), (10.0, 10.0))
    wm.select_wire(wire.wire_id)

    initial_wire_count = len(wm.wires)

    # Drag end endpoint (10, 10) to new location (15.0, 20.0)
    result_wire = wm.handle_drag_endpoint(
        start_pos=(10.0, 10.0), new_pos=(15.0, 20.0), wire_id=wire.wire_id
    )

    assert result_wire.wire_id == wire.wire_id
    assert result_wire.start_point == (0.0, 0.0)
    assert result_wire.end_point == (15.0, 20.0)
    assert len(wm.wires) == initial_wire_count


def test_drag_endpoint_when_unselected_creates_new_wire():
    """
    CR Requirement: When wire is not selected, dragging creates a new wire.
    """
    wm = WireManager()
    existing_wire = wm.create_wire((0.0, 0.0), (10.0, 10.0))
    # Note: existing_wire is NOT selected

    initial_wire_count = len(wm.wires)

    # Drag from (0, 0) to (5.0, 5.0) on unselected wire
    result_wire = wm.handle_drag_endpoint(
        start_pos=(0.0, 0.0), new_pos=(5.0, 5.0), wire_id=existing_wire.wire_id
    )

    # A new wire should be created
    assert result_wire.wire_id != existing_wire.wire_id
    assert result_wire.start_point == (0.0, 0.0)
    assert result_wire.end_point == (5.0, 5.0)

    # Original wire remains unchanged
    assert existing_wire.start_point == (0.0, 0.0)
    assert existing_wire.end_point == (10.0, 10.0)

    # Total wire count increases by 1
    assert len(wm.wires) == initial_wire_count + 1
    assert result_wire in wm.wires


def test_drag_endpoint_no_wire_id_unselected_creates_new_wire():
    """
    When no wire ID is provided and no selected wire is near start_pos, dragging creates a new wire.
    """
    wm = WireManager()
    result_wire = wm.handle_drag_endpoint(start_pos=(1.0, 1.0), new_pos=(5.0, 5.0))

    assert len(wm.wires) == 1
    assert result_wire.start_point == (1.0, 1.0)
    assert result_wire.end_point == (5.0, 5.0)


def test_drag_endpoint_auto_detect_selected_wire():
    """
    When wire_id is None but a selected wire has an endpoint at start_pos, it reconnects that wire.
    """
    wm = WireManager()
    wire = wm.create_wire((0.0, 0.0), (10.0, 10.0))
    wm.select_wire(wire.wire_id)

    result_wire = wm.handle_drag_endpoint(start_pos=(10.0, 10.0), new_pos=(20.0, 20.0))

    assert result_wire.wire_id == wire.wire_id
    assert result_wire.end_point == (20.0, 20.0)
    assert len(wm.wires) == 1
