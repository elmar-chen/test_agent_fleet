"""
LeftToolbar Component Library Drag & Mode Tool Decoupling Module

Epic #119 / Issue #120 Requirements:
1. Decouple operation mode tools (select, wire, eraser, pan) from component asset items
   (battery, switch, bulb, resistor, rheostat, ammeter, voltmeter, junction).
2. Add HTML5 draggable={True} for component buttons, encapsulating application/x-electric-component
   data in onDragStart.
3. Adapt cursor styles (grab / grabbing) and retain single-click quick component generation at viewport center.
"""

import json
from typing import Dict, List, Optional, Tuple, Union

# Operation Mode Tools
MODE_TOOLS: List[str] = ["select", "wire", "eraser", "pan"]

# Component Asset Items
COMPONENT_ITEMS: List[str] = [
    "battery",
    "switch",
    "bulb",
    "resistor",
    "rheostat",
    "ammeter",
    "voltmeter",
    "junction",
]

MIME_TYPE_ELECTRIC_COMPONENT: str = "application/x-electric-component"


class ComponentItem:
    """
    Represents a component asset item in the LeftToolbar library.
    """

    def __init__(self, type_id: str, name: Optional[str] = None):
        if type_id not in COMPONENT_ITEMS:
            raise ValueError(f"Unknown component type: '{type_id}'")
        self.type_id: str = type_id
        self.name: str = name or type_id.capitalize()
        self.draggable: bool = True
        self.cursor: str = "grab"
        self.is_dragging: bool = False

    def on_drag_start(self, data_transfer: Optional[dict] = None) -> dict:
        """
        Handles HTML5 dragStart event.
        Encapsulates application/x-electric-component data payload and updates cursor to 'grabbing'.
        """
        self.is_dragging = True
        self.cursor = "grabbing"
        payload = {
            "type": self.type_id,
            "name": self.name,
            "category": "component",
        }
        json_data = json.dumps(payload)

        drag_data = {
            "mime_type": MIME_TYPE_ELECTRIC_COMPONENT,
            "data": json_data,
            "payload": payload,
        }

        if data_transfer is not None and isinstance(data_transfer, dict):
            data_transfer[MIME_TYPE_ELECTRIC_COMPONENT] = json_data

        return drag_data

    def on_drag_end(self) -> None:
        """
        Handles HTML5 dragEnd event.
        Resets cursor to 'grab'.
        """
        self.is_dragging = False
        self.cursor = "grab"

    def click_to_spawn(
        self, viewport_center: Tuple[float, float] = (400.0, 300.0)
    ) -> dict:
        """
        Generates component instance at the specified viewport center.
        """
        return {
            "component_type": self.type_id,
            "position": (float(viewport_center[0]), float(viewport_center[1])),
            "created_via": "single_click",
        }

    def to_props(self) -> dict:
        """
        Returns HTML5/React component prop representation.
        """
        return {
            "id": self.type_id,
            "label": self.name,
            "draggable": self.draggable,
            "cursor": self.cursor,
            "category": "component",
        }


class ModeToolItem:
    """
    Represents an operation mode tool (e.g., select, wire, eraser, pan).
    """

    def __init__(self, type_id: str, name: Optional[str] = None):
        if type_id not in MODE_TOOLS:
            raise ValueError(f"Unknown mode tool type: '{type_id}'")
        self.type_id: str = type_id
        self.name: str = name or type_id.capitalize()
        self.draggable: bool = False
        self.cursor: str = "pointer"

    def to_props(self) -> dict:
        return {
            "id": self.type_id,
            "label": self.name,
            "draggable": self.draggable,
            "cursor": self.cursor,
            "category": "mode",
        }


class LeftToolbar:
    """
    Manages the LeftToolbar state, decoupling operation mode tools from component items,
    handling HTML5 drag-and-drop component data packaging, cursor style management,
    and single-click viewport center component spawning.
    """

    def __init__(self, viewport_center: Tuple[float, float] = (400.0, 300.0)):
        self.mode_tools: Dict[str, ModeToolItem] = {
            m: ModeToolItem(m) for m in MODE_TOOLS
        }
        self.component_items: Dict[str, ComponentItem] = {
            c: ComponentItem(c) for c in COMPONENT_ITEMS
        }
        self.active_mode: str = "select"
        self.viewport_center: Tuple[float, float] = (
            float(viewport_center[0]),
            float(viewport_center[1]),
        )

    def set_active_mode(self, mode_id: str) -> str:
        """
        Sets active operation mode tool.
        Raises ValueError if mode_id is a component item (decoupling requirement) or invalid.
        """
        if mode_id in COMPONENT_ITEMS:
            raise ValueError(
                f"Cannot set component asset '{mode_id}' as active operation mode. Modes and components are decoupled."
            )
        if mode_id not in MODE_TOOLS:
            raise ValueError(f"Invalid operation mode tool: '{mode_id}'")
        self.active_mode = mode_id
        return self.active_mode

    def is_mode_tool(self, tool_id: str) -> bool:
        return tool_id in self.mode_tools

    def is_component_item(self, item_id: str) -> bool:
        return item_id in self.component_items

    def handle_drag_start(
        self, item_id: str, data_transfer: Optional[dict] = None
    ) -> dict:
        """
        Initiates drag for a component item.
        Ensures draggable=True and application/x-electric-component payload encapsulation.
        Does not change active_mode (decoupled).
        """
        if item_id not in self.component_items:
            raise ValueError(f"Item '{item_id}' is not a valid component asset item.")
        comp = self.component_items[item_id]
        return comp.on_drag_start(data_transfer)

    def handle_drag_end(self, item_id: str) -> None:
        """
        Resets drag state and cursor style for a component item.
        """
        if item_id in self.component_items:
            self.component_items[item_id].on_drag_end()

    def handle_single_click(
        self, item_id: str, custom_center: Optional[Tuple[float, float]] = None
    ) -> Union[str, dict]:
        """
        Handles button click:
        - If item_id is an operation mode tool, switches active_mode.
        - If item_id is a component asset item, spawns the component at viewport center
          WITHOUT changing active_mode (decoupling requirement).
        """
        if item_id in self.mode_tools:
            self.set_active_mode(item_id)
            return self.active_mode
        elif item_id in self.component_items:
            center = (
                custom_center if custom_center is not None else self.viewport_center
            )
            comp = self.component_items[item_id]
            return comp.click_to_spawn(viewport_center=center)
        else:
            raise ValueError(f"Unknown item id: '{item_id}'")

    def spawn_component_at_center(
        self, item_id: str, custom_center: Optional[Tuple[float, float]] = None
    ) -> dict:
        """
        Spawns component at viewport center (or custom center if provided).
        """
        if item_id not in self.component_items:
            raise ValueError(f"Item '{item_id}' is not a component item.")
        center = (
            custom_center if custom_center is not None else self.viewport_center
        )
        return self.component_items[item_id].click_to_spawn(viewport_center=center)

    def get_button_props(self, item_id: str) -> dict:
        """
        Returns rendering properties (draggable, cursor, etc.) for a toolbar button.
        """
        if item_id in self.mode_tools:
            props = self.mode_tools[item_id].to_props()
            props["is_active"] = item_id == self.active_mode
            return props
        elif item_id in self.component_items:
            props = self.component_items[item_id].to_props()
            props["is_active"] = False
            return props
        else:
            raise ValueError(f"Unknown item id: '{item_id}'")
