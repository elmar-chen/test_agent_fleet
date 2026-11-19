from typing import Dict, List, Optional, Tuple, Union, Any
from circuit_store import CircuitStore, Component, SchematicComponent


class GhostPreview:
    """Represents the 100x100 GB/中考 standard symbol ghost preview frame during drag."""

    DEFAULT_WIDTH: float = 100.0
    DEFAULT_HEIGHT: float = 100.0

    def __init__(
        self,
        component_type: str = "",
        gx: int = 0,
        gy: int = 0,
        x: float = 0.0,
        y: float = 0.0,
        width: float = DEFAULT_WIDTH,
        height: float = DEFAULT_HEIGHT,
        is_visible: bool = False,
    ):
        self.component_type: str = component_type
        self.gx: int = gx
        self.gy: int = gy
        self.x: float = float(x)
        self.y: float = float(y)
        self.width: float = float(width)
        self.height: float = float(height)
        self.is_visible: bool = is_visible
        self.specification: str = "GB/中考 100x100 Standard"

    def update(self, component_type: str, gx: int, gy: int, x: float, y: float) -> None:
        self.component_type = component_type
        self.gx = gx
        self.gy = gy
        self.x = x
        self.y = y
        self.is_visible = True

    def clear(self) -> None:
        self.is_visible = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "visible": self.is_visible,
            "is_visible": self.is_visible,
            "component_type": self.component_type,
            "type": self.component_type,
            "gx": self.gx,
            "gy": self.gy,
            "snapped_x": self.x,
            "snapped_y": self.y,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "orthogonal_axis": {"x_axis": self.x, "y_axis": self.y},
            "specification": self.specification,
        }

    def __getitem__(self, item: str) -> Any:
        return self.to_dict()[item]

    def __contains__(self, item: str) -> bool:
        return item in self.to_dict()

    def get(self, item: str, default: Any = None) -> Any:
        return self.to_dict().get(item, default)

    def __repr__(self) -> str:
        return (
            f"<GhostPreview visible={self.is_visible} type='{self.component_type}' "
            f"grid=({self.gx},{self.gy}) pos=({self.x},{self.y}) size={self.width}x{self.height}>"
        )


class SchematicCanvas:
    """SchematicCanvas (符号图) handling drag-and-drop, 20px orthogonal grid snapping,

    100x100 ghost preview rendering, and component placement & auto-selection.
    """

    GRID_SIZE: float = 20.0
    SYMBOL_WIDTH: float = 100.0
    SYMBOL_HEIGHT: float = 100.0

    def __init__(self, circuit_store: Optional[CircuitStore] = None, grid_size: float = 20.0):
        self.grid_size: float = float(grid_size)
        self.circuit_store: CircuitStore = circuit_store or CircuitStore()
        self._ghost_preview_active: bool = False
        self.ghost_preview_data: GhostPreview = GhostPreview(
            width=self.SYMBOL_WIDTH, height=self.SYMBOL_HEIGHT
        )
        self.current_drag_payload: Dict[str, Any] = {}

    @property
    def circuitStore(self) -> CircuitStore:
        return self.circuit_store

    @property
    def components(self) -> List[Component]:
        return self.circuit_store.components

    @property
    def ghost_preview(self) -> Optional[Dict[str, Any]]:
        """Returns current ghost preview dict if active, or None if inactive."""
        if self._ghost_preview_active and self.ghost_preview_data.is_visible:
            return self.ghost_preview_data.to_dict()
        return None

    def pixel_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Converts pixel coordinates (x, y) to 20px Manhattan grid integer coordinates (gx, gy)."""
        gx = int(round(float(x) / float(self.grid_size)))
        gy = int(round(float(y) / float(self.grid_size)))
        return gx, gy

    def grid_to_pixel(self, gx: int, gy: int) -> Tuple[float, float]:
        """Converts integer grid coordinates (gx, gy) to snapped pixel coordinates (snap_x, snap_y)."""
        snap_x = float(gx * self.grid_size)
        snap_y = float(gy * self.grid_size)
        return snap_x, snap_y

    def snap_to_orthogonal_grid(self, x: float, y: float) -> Tuple[float, float]:
        """Snaps continuous pixel position (x, y) to 20px orthogonal grid integer position."""
        gx, gy = self.pixel_to_grid(x, y)
        return self.grid_to_pixel(gx, gy)

    def _parse_drag_args(
        self,
        arg1: Any,
        arg2: Any = None,
        arg3: Any = None,
        component_type: Optional[str] = None,
    ) -> Tuple[float, float, str, Dict[str, Any]]:
        """Flexibly parses drag arguments from positional parameters, event objects, or payload dicts."""
        payload: Dict[str, Any] = {}
        ctype = "symbol"
        px = 0.0
        py = 0.0

        if isinstance(arg1, dict):
            payload = arg1
            if arg2 is not None and arg3 is not None:
                px = float(arg2)
                py = float(arg3)
            else:
                px = float(payload.get("x", 0.0))
                py = float(payload.get("y", 0.0))
            ctype = (
                payload.get("type")
                or payload.get("component_type")
                or payload.get("name")
                or "symbol"
            )
        elif hasattr(arg1, "x") and hasattr(arg1, "y"):
            px = float(getattr(arg1, "x", 0.0))
            py = float(getattr(arg1, "y", 0.0))
            ctype = (
                getattr(arg1, "component_type", None)
                or getattr(arg1, "type", None)
                or "symbol"
            )
        else:
            px = float(arg1) if arg1 is not None else 0.0
            if arg2 is not None:
                py = float(arg2)
                ctype = component_type or (str(arg3) if isinstance(arg3, str) else "symbol")
            else:
                py = 0.0
                ctype = component_type or "symbol"

        if payload:
            self.current_drag_payload = payload

        return px, py, ctype, payload

    def on_drag_enter(
        self,
        arg1: Any,
        arg2: Any = None,
        arg3: Any = None,
    ) -> Dict[str, Any]:
        """Handles onDragEnter event: initializes ghost preview frame."""
        px, py, ctype, payload = self._parse_drag_args(arg1, arg2, arg3)
        gx, gy = self.pixel_to_grid(px, py)
        snap_x, snap_y = self.grid_to_pixel(gx, gy)

        self._ghost_preview_active = True
        self.ghost_preview_data.update(
            component_type=ctype,
            gx=gx,
            gy=gy,
            x=snap_x,
            y=snap_y,
        )
        return self.render_ghost_preview()

    onDragEnter = on_drag_enter

    def on_drag_over(
        self,
        arg1: Any,
        arg2: Any = None,
        arg3: Any = None,
        component_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handles onDragOver event: calculates 20px Manhattan grid (gx, gy)

        and updates 100x100 ghost preview rendering state.
        """
        px, py, ctype, payload = self._parse_drag_args(arg1, arg2, arg3, component_type)
        if not ctype or ctype == "symbol":
            ctype = self.ghost_preview_data.component_type or "symbol"

        gx, gy = self.pixel_to_grid(px, py)
        snap_x, snap_y = self.grid_to_pixel(gx, gy)

        self._ghost_preview_active = True
        self.ghost_preview_data.update(
            component_type=ctype,
            gx=gx,
            gy=gy,
            x=snap_x,
            y=snap_y,
        )
        return self.render_ghost_preview()

    onDragOver = on_drag_over

    def on_drag_leave(self, event: Any = None) -> None:
        """Handles onDragLeave event: clears and deactivates ghost preview frame."""
        self._ghost_preview_active = False
        self.ghost_preview_data.clear()

    onDragLeave = on_drag_leave

    def on_drop(
        self,
        arg1: Any,
        arg2: Any = None,
        arg3: Any = None,
        component_type: Optional[str] = None,
    ) -> Optional[Component]:
        """Handles onDrop event: converts target to 20px Manhattan grid (gx, gy),

        snaps pixel coordinates, instantiates component via circuitStore.addComponent,
        automatically selects it, and clears ghost preview.
        """
        if isinstance(arg1, dict) and not arg1:
            # Empty payload drop is invalid
            self.on_drag_leave()
            return None

        px, py, ctype, payload = self._parse_drag_args(arg1, arg2, arg3, component_type)
        if not ctype or ctype == "symbol":
            ctype = self.ghost_preview_data.component_type or payload.get("type") or "symbol"

        gx, gy = self.pixel_to_grid(px, py)
        snap_x, snap_y = self.grid_to_pixel(gx, gy)

        name = payload.get("name", "")
        props = payload.get("properties", {})
        sym = props.get("symbol") or payload.get("symbol", "")
        comp_id = payload.get("component_id")

        width = payload.get("width", self.SYMBOL_WIDTH)
        height = payload.get("height", self.SYMBOL_HEIGHT)

        # Instantiate component via circuitStore.addComponent
        component = self.circuit_store.addComponent(
            component_type=ctype,
            x=snap_x,
            y=snap_y,
            gx=gx,
            gy=gy,
            width=width,
            height=height,
            name=name,
            symbol=sym,
            properties=props,
            component_id=comp_id,
        )

        # Clear ghost preview after dropping
        self.on_drag_leave()

        return component

    onDrop = on_drop

    def render_ghost_preview(self) -> Dict[str, Any]:
        """Renders/returns the 100x100 symbol ghost preview box configuration."""
        return self.ghost_preview_data.to_dict()
