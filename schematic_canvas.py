from typing import Dict, List, Optional, Tuple, Union, Any
from circuit_store import CircuitStore, Component
from schematic_grid import SCHEMATIC_GRID_DEFINITIONS, get_schematic_grid
from builtin_components import BUILTIN_COMPONENTS, get_builtin_component

# Export alias for SchematicComponent
SchematicComponent = Component


class GhostPreview:
    """Represents the 100x100 GB/中考 standard symbol ghost preview frame during drag."""

    GRID_SIZE: int = 20
    DEFAULT_WIDTH: int = 100
    DEFAULT_HEIGHT: int = 100

    def __init__(
        self,
        component_type: str = "",
        gx: int = 0,
        gy: int = 0,
        x: float = 0.0,
        y: float = 0.0,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        is_visible: bool = False,
    ):
        self.component_type: str = component_type
        self.gx: int = gx
        self.gy: int = gy
        self.x: float = float(x)
        self.y: float = float(y)
        self.width: int = width
        self.height: int = height
        self.is_visible: bool = is_visible
        self.specification: str = "GB/中考 100x100 Standard"

    def update(self, component_type: str, gx: int, gy: int, x: float, y: float) -> None:
        self.component_type = component_type
        self.gx = gx
        self.gy = gy
        self.x = float(x)
        self.y = float(y)
        self.is_visible = True

    def clear(self) -> None:
        self.is_visible = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_visible": self.is_visible,
            "visible": self.is_visible,
            "component_type": self.component_type,
            "gx": self.gx,
            "gy": self.gy,
            "x": self.x,
            "y": self.y,
            "snapped_x": self.x,
            "snapped_y": self.y,
            "orthogonal_axis": {"x_axis": self.x, "y_axis": self.y},
            "width": self.width,
            "height": self.height,
            "specification": self.specification,
        }

    def __repr__(self) -> str:
        return (
            f"<GhostPreview visible={self.is_visible} type='{self.component_type}' "
            f"grid=({self.gx},{self.gy}) pos=({self.x},{self.y}) size={self.width}x{self.height}>"
        )


class SchematicCanvas:
    """SchematicCanvas (符号图) handling drag-and-drop, 20px orthogonal grid snapping,

    100x100 ghost preview rendering, component placement & auto-selection,
    and pin coordinate deduplication.
    """

    GRID_SIZE: int = 20
    SYMBOL_WIDTH: int = 100
    SYMBOL_HEIGHT: int = 100

    def __init__(self, circuit_store: Optional[CircuitStore] = None, grid_size: int = 20):
        self.grid_size: int = grid_size or self.GRID_SIZE
        self.circuit_store: CircuitStore = circuit_store or CircuitStore()
        self.ghost_preview_obj: GhostPreview = GhostPreview(
            width=self.SYMBOL_WIDTH, height=self.SYMBOL_HEIGHT
        )

    @property
    def components(self) -> List[Component]:
        return self.circuit_store.components

    @property
    def ghost_preview(self) -> Optional[Dict[str, Any]]:
        if self.ghost_preview_obj.is_visible:
            return self.ghost_preview_obj.to_dict()
        return None

    @property
    def circuitStore(self) -> CircuitStore:
        """Alias property matching camelCase specification."""
        return self.circuit_store

    def snap_to_orthogonal_grid(self, x: float, y: float) -> Tuple[float, float]:
        """Calculates 20px orthogonal grid snapped coordinates."""
        gx, gy = self.pixel_to_grid(x, y)
        return self.grid_to_pixel(gx, gy)

    def pixel_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Converts pixel coordinates (x, y) to 20px Manhattan grid integer coordinates (gx, gy)."""
        g_size = float(self.grid_size if self.grid_size > 0 else 20)
        gx = int(round(x / g_size))
        gy = int(round(y / g_size))
        return gx, gy

    def grid_to_pixel(self, gx: int, gy: int) -> Tuple[float, float]:
        """Converts integer grid coordinates (gx, gy) to snapped pixel coordinates (snap_x, snap_y)."""
        g_size = float(self.grid_size if self.grid_size > 0 else 20)
        snap_x = float(gx * g_size)
        snap_y = float(gy * g_size)
        return snap_x, snap_y

    def _extract_drag_args(
        self, x_or_event: Union[float, int, dict, Any], y: Optional[Union[float, int]] = None, component_type: Optional[str] = None
    ) -> Tuple[float, float, str, Dict[str, Any]]:
        """Helper to extract x, y, component_type, and payload dict from positional args or event dict/object."""
        payload: Dict[str, Any] = {}
        if isinstance(x_or_event, dict):
            payload = x_or_event
            if y is not None and isinstance(y, (int, float)) and component_type is not None and isinstance(component_type, (int, float)):
                px = float(y)
                py = float(component_type)
                ctype = str(payload.get("component_type") or payload.get("type") or "symbol")
            else:
                px = float(payload.get("x", payload.get("mouse_x", 0.0)))
                py = float(payload.get("y", payload.get("mouse_y", 0.0)))
                ctype = str(payload.get("component_type") or payload.get("type") or "symbol")
        elif hasattr(x_or_event, "x") and hasattr(x_or_event, "y"):
            obj = x_or_event
            if y is not None and isinstance(y, (int, float)) and component_type is not None and isinstance(component_type, (int, float)):
                px = float(y)
                py = float(component_type)
            else:
                px = float(getattr(obj, "x", getattr(obj, "mouse_x", 0.0)))
                py = float(getattr(obj, "y", getattr(obj, "mouse_y", 0.0)))
            ctype = str(getattr(obj, "component_type", None) or getattr(obj, "type", None) or "symbol")
        else:
            px = float(x_or_event)
            py = float(y) if y is not None else 0.0
            ctype = str(component_type) if component_type is not None else "symbol"

        return px, py, ctype, payload

    def on_drag_enter(
        self, x_or_event: Union[float, int, dict, Any], y: Optional[Union[float, int]] = None, component_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if isinstance(x_or_event, dict) and not x_or_event and y is None:
            self.ghost_preview_obj.clear()
            return None

        px, py, ctype, payload = self._extract_drag_args(x_or_event, y, component_type)
        gx, gy = self.pixel_to_grid(px, py)
        snap_x, snap_y = self.grid_to_pixel(gx, gy)

        self.ghost_preview_obj.update(
            component_type=ctype,
            gx=gx,
            gy=gy,
            x=snap_x,
            y=snap_y,
        )
        return self.render_ghost_preview()

    onDragEnter = on_drag_enter

    def on_drag_over(
        self, x_or_event: Union[float, int, dict, Any], y: Optional[Union[float, int]] = None, component_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if not self.ghost_preview_obj.is_visible:
            if not (isinstance(x_or_event, (int, float)) or (isinstance(x_or_event, dict) and ("type" in x_or_event or "component_type" in x_or_event))):
                return None

        # Handle on_drag_over(x, y) when preview is active
        if isinstance(x_or_event, (int, float)) and y is not None and isinstance(y, (int, float)) and self.ghost_preview_obj.is_visible:
            gx, gy = self.pixel_to_grid(float(x_or_event), float(y))
            snap_x, snap_y = self.grid_to_pixel(gx, gy)
            self.ghost_preview_obj.update(
                component_type=self.ghost_preview_obj.component_type,
                gx=gx,
                gy=gy,
                x=snap_x,
                y=snap_y,
            )
            return self.render_ghost_preview()

        px, py, ctype, payload = self._extract_drag_args(x_or_event, y, component_type)
        gx, gy = self.pixel_to_grid(px, py)
        snap_x, snap_y = self.grid_to_pixel(gx, gy)

        self.ghost_preview_obj.update(
            component_type=ctype,
            gx=gx,
            gy=gy,
            x=snap_x,
            y=snap_y,
        )
        return self.render_ghost_preview()

    onDragOver = on_drag_over

    def on_drag_leave(self) -> None:
        """Handles onDragLeave event: clears and deactivates ghost preview frame."""
        self.ghost_preview_obj.clear()

    onDragLeave = on_drag_leave

    def on_drop(
        self, x_or_event: Union[float, int, dict, Any], y: Optional[Union[float, int]] = None, component_type: Optional[str] = None
    ) -> Optional[Component]:
        if isinstance(x_or_event, dict) and not x_or_event and y is None:
            self.ghost_preview_obj.clear()
            return None

        px, py, ctype, payload = self._extract_drag_args(x_or_event, y, component_type)
        gx, gy = self.pixel_to_grid(px, py)
        snap_x, snap_y = self.grid_to_pixel(gx, gy)

        sym = payload.get("properties", {}).get("symbol") or payload.get("symbol") or ctype.upper()
        props = payload.get("properties") or payload.get("props") or {}

        component = self.circuit_store.addComponent(
            component_type=ctype,
            x=snap_x,
            y=snap_y,
            gx=gx,
            gy=gy,
            width=self.SYMBOL_WIDTH,
            height=self.SYMBOL_HEIGHT,
            symbol=sym,
            props=props,
        )

        self.ghost_preview_obj.clear()
        return component

    onDrop = on_drop

    def render_ghost_preview(self) -> Dict[str, Any]:
        """Renders/returns the 100x100 symbol ghost preview box configuration."""
        return self.ghost_preview_obj.to_dict()

    def deduplicate_pins(self, pins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicates overlapping schematic pins by their local coordinates (localX, localY),

        ensuring only a single interactive dot is rendered per unique coordinate position.
        """
        seen: Dict[Tuple[float, float], Dict[str, Any]] = {}
        unique_pins: List[Dict[str, Any]] = []

        for pin in pins:
            if "localX" in pin and "localY" in pin:
                lx = float(pin["localX"])
                ly = float(pin["localY"])
            elif "gxOffset" in pin and "gyOffset" in pin:
                lx = float(pin["gxOffset"]) + 50.0
                ly = float(pin["gyOffset"]) + 50.0
            else:
                lx = 0.0
                ly = 0.0

            coord_key = (round(lx, 4), round(ly, 4))

            if coord_key not in seen:
                pin_data = dict(pin)
                pin_data["localX"] = lx
                pin_data["localY"] = ly
                pin_data["merged_pin_ids"] = [pin.get("id")]
                if "logicalPort" in pin:
                    pin_data["merged_ports"] = [pin.get("logicalPort")]
                seen[coord_key] = pin_data
                unique_pins.append(pin_data)
            else:
                existing = seen[coord_key]
                if pin.get("id") and pin.get("id") not in existing.get("merged_pin_ids", []):
                    existing.setdefault("merged_pin_ids", []).append(pin.get("id"))
                if "logicalPort" in pin:
                    if "merged_ports" not in existing:
                        existing["merged_ports"] = []
                    if pin.get("logicalPort") not in existing["merged_ports"]:
                        existing["merged_ports"].append(pin.get("logicalPort"))

        return unique_pins

    def get_component_pins(
        self, component_or_type: Union[Component, str, Dict[str, Any]], deduplicate: bool = True
    ) -> List[Dict[str, Any]]:
        """Returns the schematic pins for a component or component type.

        If deduplicate is True (default), overlapping pins sharing identical coordinates
        are merged into a single pin definition.
        """
        if isinstance(component_or_type, Component):
            ctype = component_or_type.component_type
        elif isinstance(component_or_type, dict):
            ctype = component_or_type.get("component_type") or component_or_type.get("type", "")
        else:
            ctype = str(component_or_type)

        grid_def = get_schematic_grid(ctype)
        raw_pins = grid_def.get("pins", [])

        if deduplicate:
            return self.deduplicate_pins(raw_pins)
        return raw_pins

    getComponentPins = get_component_pins

    def render_interactive_dots(
        self, component: Component, deduplicate: bool = True
    ) -> List[Dict[str, Any]]:
        """Renders interactive dots for a component on the schematic canvas.

        Each dot includes localX, localY, absolute x, absolute y, normalAngleDeg,
        and merged pin IDs. Deduplicates overlapping pins at the same coordinates.
        """
        pins = self.get_component_pins(component, deduplicate=deduplicate)
        dots: List[Dict[str, Any]] = []

        for pin in pins:
            lx = float(pin.get("localX", 0.0))
            ly = float(pin.get("localY", 0.0))
            dot = {
                "id": pin.get("id"),
                "localX": lx,
                "localY": ly,
                "absX": component.x + lx,
                "absY": component.y + ly,
                "normalAngleDeg": pin.get("normalAngleDeg", 0),
                "logicalPort": pin.get("logicalPort"),
                "merged_pin_ids": pin.get("merged_pin_ids", [pin.get("id")]),
            }
            dots.append(dot)

        return dots

    renderInteractiveDots = render_interactive_dots
