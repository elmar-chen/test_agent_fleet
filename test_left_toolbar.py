"""
Unit tests for LeftToolbar component library drag support and mode tool decoupling (Issue #120 / Epic #119).
"""

import json
import pytest
from left_toolbar import (
    LeftToolbar,
    ComponentItem,
    ModeToolItem,
    MODE_TOOLS,
    COMPONENT_ITEMS,
    MIME_TYPE_ELECTRIC_COMPONENT,
)


def test_tool_categorization_and_decoupling():
    toolbar = LeftToolbar()

    # Check mode tools
    expected_modes = ["select", "wire", "eraser", "pan"]
    assert MODE_TOOLS == expected_modes
    for mode in expected_modes:
        assert toolbar.is_mode_tool(mode)
        assert not toolbar.is_component_item(mode)

    # Check component items
    expected_components = [
        "battery",
        "switch",
        "bulb",
        "resistor",
        "rheostat",
        "ammeter",
        "voltmeter",
        "junction",
    ]
    assert COMPONENT_ITEMS == expected_components
    for comp in expected_components:
        assert toolbar.is_component_item(comp)
        assert not toolbar.is_mode_tool(comp)

    # Decoupling test: setting mode tools works
    assert toolbar.active_mode == "select"
    toolbar.set_active_mode("wire")
    assert toolbar.active_mode == "wire"

    # Decoupling test: setting component asset as active mode raises ValueError
    for comp in expected_components:
        with pytest.raises(ValueError, match="Modes and components are decoupled"):
            toolbar.set_active_mode(comp)

    # Active mode remains unchanged after failed attempts
    assert toolbar.active_mode == "wire"


def test_html5_draggable_and_drag_data_encapsulation():
    toolbar = LeftToolbar()

    # Component items must be draggable=True
    for comp_id in COMPONENT_ITEMS:
        props = toolbar.get_button_props(comp_id)
        assert props["draggable"] is True
        assert props["category"] == "component"

    # Mode tools must be draggable=False
    for mode_id in MODE_TOOLS:
        props = toolbar.get_button_props(mode_id)
        assert props["draggable"] is False
        assert props["category"] == "mode"

    # Test drag start data encapsulation for all component items
    data_transfer = {}
    drag_info = toolbar.handle_drag_start("battery", data_transfer)

    assert drag_info["mime_type"] == MIME_TYPE_ELECTRIC_COMPONENT
    assert "data" in drag_info
    payload = drag_info["payload"]
    assert payload["type"] == "battery"
    assert payload["category"] == "component"

    # Verify data_transfer dict was populated with application/x-electric-component key
    assert MIME_TYPE_ELECTRIC_COMPONENT in data_transfer
    parsed_data = json.loads(data_transfer[MIME_TYPE_ELECTRIC_COMPONENT])
    assert parsed_data["type"] == "battery"

    # Invalid item drag start raises ValueError
    with pytest.raises(ValueError, match="not a valid component asset item"):
        toolbar.handle_drag_start("invalid_item")


def test_cursor_styles_grab_grabbing():
    toolbar = LeftToolbar()
    comp_item = toolbar.component_items["resistor"]

    # Default cursor is 'grab'
    assert comp_item.cursor == "grab"
    props = toolbar.get_button_props("resistor")
    assert props["cursor"] == "grab"

    # On drag start, cursor updates to 'grabbing'
    toolbar.handle_drag_start("resistor")
    assert comp_item.cursor == "grabbing"
    assert comp_item.is_dragging is True
    props_dragging = toolbar.get_button_props("resistor")
    assert props_dragging["cursor"] == "grabbing"

    # On drag end, cursor resets to 'grab'
    toolbar.handle_drag_end("resistor")
    assert comp_item.cursor == "grab"
    assert comp_item.is_dragging is False
    props_reset = toolbar.get_button_props("resistor")
    assert props_reset["cursor"] == "grab"


def test_single_click_viewport_center_spawning():
    custom_center = (500.0, 400.0)
    toolbar = LeftToolbar(viewport_center=custom_center)

    # Initial active mode is 'select'
    assert toolbar.active_mode == "select"

    # Click component button: spawns component at viewport center without changing active_mode
    spawn_result = toolbar.handle_single_click("bulb")
    assert isinstance(spawn_result, dict)
    assert spawn_result["component_type"] == "bulb"
    assert spawn_result["position"] == (500.0, 400.0)
    assert spawn_result["created_via"] == "single_click"

    # Active mode remains 'select' (decoupled!)
    assert toolbar.active_mode == "select"

    # Test explicit custom center parameter
    spawn_custom = toolbar.spawn_component_at_center("voltmeter", custom_center=(100.0, 200.0))
    assert spawn_custom["component_type"] == "voltmeter"
    assert spawn_custom["position"] == (100.0, 200.0)

    # Test mode tool single click changes active mode
    result_mode = toolbar.handle_single_click("pan")
    assert result_mode == "pan"
    assert toolbar.active_mode == "pan"


def test_component_and_mode_item_edge_cases():
    with pytest.raises(ValueError, match="Unknown component type"):
        ComponentItem("unknown_component")

    with pytest.raises(ValueError, match="Unknown mode tool type"):
        ModeToolItem("unknown_mode")

    with pytest.raises(ValueError, match="Unknown item id"):
        toolbar = LeftToolbar()
        toolbar.handle_single_click("nonexistent")
