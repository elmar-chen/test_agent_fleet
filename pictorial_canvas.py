"""
PictorialCanvas (实物图) Drag-and-Drop, Ghost Preview & Grid Snapping Module.
Fulfills requirements for Issue #121 (Epic #119).
"""

import uuid
from typing import Dict, List, Optional, Tuple, Union, Any
from circuit_store import CircuitStore, Component


class Terminal:
    """Represents a connection terminal point on a physical component."""

    def __init__(
        self,
        rel_x: float,
        rel_y: float,
        terminal_id: Optional[str] = None,
        label: str = "",
    ):
        self.id = terminal_id or f"term-{uuid.uuid4().hex[:6]}"
        self.rel_x = float(rel_x)
        self.rel_y = float(rel_y)
        self.label = label

    @classmethod
    def from_data(cls, data: Union[Dict[str, Any], Tuple[float, float], List[float], "Terminal"]) -> "Terminal":
        if isinstance(data, Terminal):
            return data
        elif isinstance(data, (list, tuple)) and len(data) >= 2:
            return cls(rel_x=data[0], rel_y=data[1])
        elif isinstance(data, dict):
            return cls(
                rel_x=data.get("rel_x", data.get("x", 0.0)),
                rel_y=data.get("rel_y", data.get("y", 0.0)),
                terminal_id=data.get("id"),
                label=data.get("label", ""),
            )
        else:
            raise ValueError(f"Invalid terminal data format: {data}")

    def get_absolute_position(self, comp_x: float, comp_y: float) -> Tuple[float, float]:
        """Calculates absolute canvas position of terminal given component top-left (comp_x, comp_y)."""
        return (comp_x + self.rel_x, comp_y + self.rel_y)

    def to_dict(self, comp_x: float = 0.0, comp_y: float = 0.0) -> Dict[str, Any]:
        abs_x, abs_y = self.get_absolute_position(comp_x, comp_y)
        return {
            "id": self.id,
            "rel_x": self.rel_x,
            "rel_y": self.rel_y,
            "abs_x": abs_x,
            "abs_y": abs_y,
            "label": self.label,
        }


class PictorialComponent(Component):
    """Represents an instantiated pictorial physical component."""

    def __init__(
        self,
        component_type: str,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 60.0,
        height: float = 40.0,
        component_id: Optional[str] = None,
        selected: bool = True,
        properties: Optional[Dict[str, Any]] = None,
        terminals: Optional[List[Union[Terminal, Dict[str, Any], Tuple[float, float]]]] = None,
        name: str = "",
    ):
        gx = int(round(x / 20.0))
        gy = int(round(y / 20.0))
        super().__init__(
            component_type=component_type,
            x=x,
            y=y,
            gx=gx,
            gy=gy,
            width=width,
            height=height,
            component_id=component_id,
            selected=selected,
            properties=properties or {},
        )
        self.name: str = name or component_type
        self.terminals: List[Terminal] = []
        if terminals:
            for t in terminals:
                self.terminals.append(Terminal.from_data(t))

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["name"] = self.name
        res["terminals"] = [t.to_dict(self.x, self.y) for t in self.terminals]
        return res


class GhostPreview:
    """Represents semi-transparent blue dashed ghost preview box and terminal indicator points."""

    def __init__(
        self,
        component_type: str = "",
        snapped_x: float = 0.0,
        snapped_y: float = 0.0,
        width: float = 60.0,
        height: float = 40.0,
        terminals: Optional[List[Terminal]] = None,
        grid_size: float = 20.0,
        is_visible: bool = True,
    ):
        self.component_type = component_type
        self.snapped_x = float(snapped_x)
        self.snapped_y = float(snapped_y)
        self.x = self.snapped_x
        self.y = self.snapped_y
        self.width = float(width)
        self.height = float(height)
        self.grid_size = float(grid_size)
        self.is_visible = is_visible
        self.terminals: List[Terminal] = terminals or []

        # Default Ghost Styling: Semi-transparent blue dashed box
        self.style = {
            "stroke": "#1890ff",  # Blue dashed border
            "stroke_dasharray": "4 4",  # Dashed line pattern
            "fill": "rgba(24, 144, 255, 0.15)",  # Semi-transparent blue fill
            "opacity": 0.6,
            "border_width": 2,
        }

    @property
    def position(self) -> Tuple[float, float]:
        return (self.snapped_x, self.snapped_y)

    @property
    def size(self) -> Tuple[float, float]:
        return (self.width, self.height)

    @property
    def center_position(self) -> Tuple[float, float]:
        return (self.snapped_x + self.width / 2.0, self.snapped_y + self.height / 2.0)

    def render(self) -> Dict[str, Any]:
        """Renders Ghost preview frame box and terminal indicator points."""
        if not self.is_visible:
            return {"visible": False}

        terminal_indicators = []
        for t in self.terminals:
            abs_x, abs_y = t.get_absolute_position(self.snapped_x, self.snapped_y)
            terminal_indicators.append({
                "id": t.id,
                "label": t.label,
                "x": abs_x,
                "y": abs_y,
                "radius": 4,
                "color": "#1890ff",
                "stroke": "#0050b3",
                "fill": "#e6f7ff",
            })

        return {
            "visible": True,
            "is_visible": True,
            "component_type": self.component_type,
            "snapped_x": self.snapped_x,
            "snapped_y": self.snapped_y,
            "x": self.snapped_x,
            "y": self.snapped_y,
            "position": self.position,
            "size": self.size,
            "width": self.width,
            "height": self.height,
            "center": self.center_position,
            "grid_size": self.grid_size,
            "box": {
                "x": self.snapped_x,
                "y": self.snapped_y,
                "width": self.width,
                "height": self.height,
                "style": self.style,
            },
            "terminals": terminal_indicators,
        }

    def __getitem__(self, item: str) -> Any:
        return self.render()[item]


class PictorialCanvas:
    """PictorialCanvas (实物图) handling drag & drop events, coordinate conversion,

    center alignment calculation, 20px/10px grid snapping, ghost preview rendering,
    and component instantiation/selection into CircuitStore.
    """

    def __init__(
        self,
        grid_size: float = 20.0,
        circuit_store: Optional[CircuitStore] = None,
        canvas_offset: Tuple[float, float] = (0.0, 0.0),
    ):
        self.grid_size = float(grid_size)
        self.circuit_store = circuit_store or CircuitStore()
        self.canvas_offset = (float(canvas_offset[0]), float(canvas_offset[1]))
        self.components: List[PictorialComponent] = []
        self.ghost_preview: Optional[GhostPreview] = None
        self._current_payload: Optional[Dict[str, Any]] = None

    @property
    def circuitStore(self) -> CircuitStore:
        return self.circuit_store

    def snap_to_grid(self, x: float, y: float, grid_size: Optional[float] = None) -> Tuple[float, float]:
        """Snaps coordinate (x, y) to closest multiple of grid_size (e.g. 20px or 10px)."""
        g_size = float(grid_size) if grid_size is not None else self.grid_size
        if g_size <= 0:
            return (float(x), float(y))
        snapped_x = round(float(x) / g_size) * g_size
        snapped_y = round(float(y) / g_size) * g_size
        return (float(snapped_x), float(snapped_y))

    def calculate_centered_position(
        self,
        mouse_x: float,
        mouse_y: float,
        width: float,
        height: float,
        canvas_offset: Optional[Tuple[float, float]] = None,
    ) -> Tuple[float, float]:
        """Converts cursor position to canvas-relative coordinates and calculates top-left position

        such that component center aligns with cursor position.
        """
        offset_x, offset_y = canvas_offset if canvas_offset is not None else self.canvas_offset
        canvas_x = mouse_x - offset_x
        canvas_y = mouse_y - offset_y

        top_left_x = canvas_x - (width / 2.0)
        top_left_y = canvas_y - (height / 2.0)
        return (top_left_x, top_left_y)

    def _parse_drag_input(
        self,
        arg1: Any,
        arg2: Optional[Any] = None,
        arg3: Optional[Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Parses drag enter/over/drop arguments across multiple call patterns."""
        payload = {}

        if isinstance(arg1, dict):
            payload = dict(arg1)
            mx = arg2 if arg2 is not None else payload.get("mouse_x", payload.get("x", 0.0))
            my = arg3 if arg3 is not None else payload.get("mouse_y", payload.get("y", 0.0))
        elif hasattr(arg1, "component_id") or hasattr(arg1, "type"):
            payload = {
                "component_id": getattr(arg1, "component_id", getattr(arg1, "id", None)),
                "type": getattr(arg1, "component_type", getattr(arg1, "type", "unknown")),
                "name": getattr(arg1, "name", ""),
                "width": getattr(arg1, "width", 60.0),
                "height": getattr(arg1, "height", 40.0),
                "properties": getattr(arg1, "properties", getattr(arg1, "props", {})),
                "terminals": getattr(arg1, "terminals", []),
            }
            mx = arg2 if arg2 is not None else 0.0
            my = arg3 if arg3 is not None else 0.0
        elif isinstance(arg1, (int, float)):
            mx = arg1
            my = arg2 if arg2 is not None else 0.0
            if isinstance(arg3, str):
                payload["type"] = arg3
            elif self._current_payload:
                payload = dict(self._current_payload)
        else:
            mx = 0.0
            my = 0.0

        if self._current_payload and not payload.get("type"):
            payload.update({k: v for k, v in self._current_payload.items() if k not in payload or not payload[k]})

        c_type = payload.get("type") or payload.get("component_type") or kwargs.get("component_type", "unknown")
        c_id = payload.get("component_id") or payload.get("id") or kwargs.get("component_id")
        c_name = payload.get("name") or kwargs.get("name", c_type)
        c_size = kwargs.get("size")
        if not c_size:
            w = payload.get("width", kwargs.get("width", 60.0))
            h = payload.get("height", kwargs.get("height", 40.0))
            c_size = (float(w), float(h))

        c_props = payload.get("properties") or payload.get("props") or kwargs.get("properties", kwargs.get("props", {}))
        c_terminals = payload.get("terminals") or kwargs.get("terminals", [])
        g_size = kwargs.get("grid_size", payload.get("grid_size", self.grid_size))
        center_align = kwargs.get("center_align", False)

        return {
            "payload": payload,
            "mouse_x": float(mx),
            "mouse_y": float(my),
            "component_id": c_id,
            "component_type": c_type,
            "name": c_name,
            "width": float(c_size[0]),
            "height": float(c_size[1]),
            "properties": c_props,
            "terminals": [Terminal.from_data(t) for t in c_terminals],
            "grid_size": float(g_size),
            "center_align": center_align,
        }

    def on_drag_enter(self, payload: Dict[str, Any], x: float = 0.0, y: float = 0.0) -> Dict[str, Any]:
        """Handles onDragEnter event: initializes ghost preview frame."""
        self._current_payload = dict(payload) if isinstance(payload, dict) else payload
        return self.on_drag_over(payload, x, y)

    onDragEnter = on_drag_enter

    def on_drag_over(
        self,
        arg1: Any,
        arg2: Optional[Any] = None,
        arg3: Optional[Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Handles onDragOver event: calculates coordinate conversion, center alignment (if requested),

        grid snapping (20px/10px), updates GhostPreview state, and returns preview render dictionary.
        """
        parsed = self._parse_drag_input(arg1, arg2, arg3, **kwargs)

        mx, my = parsed["mouse_x"], parsed["mouse_y"]
        w, h = parsed["width"], parsed["height"]
        g_size = parsed["grid_size"]

        if parsed["center_align"]:
            raw_x, raw_y = self.calculate_centered_position(mx, my, w, h)
        else:
            offset_x, offset_y = self.canvas_offset
            raw_x = mx - offset_x
            raw_y = my - offset_y

        snapped_x, snapped_y = self.snap_to_grid(raw_x, raw_y, g_size)

        self.ghost_preview = GhostPreview(
            component_type=parsed["component_type"],
            snapped_x=snapped_x,
            snapped_y=snapped_y,
            width=w,
            height=h,
            terminals=parsed["terminals"],
            grid_size=g_size,
            is_visible=True,
        )

        return self.ghost_preview.render()

    onDragOver = on_drag_over

    def on_drag_leave(self, event: Any = None) -> None:
        """Handles onDragLeave event: hides and clears ghost preview frame."""
        if self.ghost_preview:
            self.ghost_preview.is_visible = False
        self.ghost_preview = None
        self._current_payload = None

    onDragLeave = on_drag_leave

    def on_drop(
        self,
        arg1: Any,
        arg2: Optional[Any] = None,
        arg3: Optional[Any] = None,
        **kwargs: Any,
    ) -> Optional[PictorialComponent]:
        """Handles onDrop event: calculates coordinate conversion, center alignment (if requested),

        grid snapping (20px/10px), instantiates PictorialComponent into circuitStore via addComponent,
        automatically selects it, clears ghost preview, and returns the created component.
        Returns None if drop payload is empty/invalid.
        """
        if isinstance(arg1, dict) and not arg1:
            return None

        parsed = self._parse_drag_input(arg1, arg2, arg3, **kwargs)
        if not parsed["component_type"] or parsed["component_type"] == "unknown":
            if isinstance(arg1, dict) and not arg1.get("type") and not arg1.get("component_type"):
                return None

        mx, my = parsed["mouse_x"], parsed["mouse_y"]
        w, h = parsed["width"], parsed["height"]
        g_size = parsed["grid_size"]

        if parsed["center_align"]:
            raw_x, raw_y = self.calculate_centered_position(mx, my, w, h)
        else:
            offset_x, offset_y = self.canvas_offset
            raw_x = mx - offset_x
            raw_y = my - offset_y

        snapped_x, snapped_y = self.snap_to_grid(raw_x, raw_y, g_size)

        # Create PictorialComponent instance
        comp = PictorialComponent(
            component_type=parsed["component_type"],
            x=snapped_x,
            y=snapped_y,
            width=w,
            height=h,
            component_id=parsed["component_id"],
            selected=True,
            properties=parsed["properties"],
            terminals=parsed["terminals"],
            name=parsed["name"],
        )

        # Store in canvas components list
        self.components.append(comp)

        # Register in circuitStore and set auto selection
        if self.circuit_store:
            self.circuit_store.addComponent(comp)

        # Clear ghost preview after drop
        self.on_drag_leave()

        return comp

    onDrop = on_drop

    def render_ghost_preview(self) -> Dict[str, Any]:
        """Returns rendered ghost preview structure or invisible state."""
        if self.ghost_preview and self.ghost_preview.is_visible:
            return self.ghost_preview.render()
        return {"visible": False}
