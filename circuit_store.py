import uuid
from typing import Dict, List, Optional, Tuple, Union, Any


class Component:
    """Represents a component in the circuit."""

    def __init__(
        self,
        component_type: str,
        x: float = 0.0,
        y: float = 0.0,
        gx: int = 0,
        gy: int = 0,
        width: float = 100.0,
        height: float = 100.0,
        component_id: Optional[str] = None,
        selected: bool = False,
        properties: Optional[Dict[str, Any]] = None,
    ):
        self.id: str = component_id or str(uuid.uuid4())
        self.type: str = component_type
        self.component_type: str = component_type
        self.x: float = float(x)
        self.y: float = float(y)
        self.gx: int = int(gx)
        self.gy: int = int(gy)
        self.width: float = float(width)
        self.height: float = float(height)
        self.selected: bool = selected
        self.properties: Dict[str, Any] = properties or {}

    @property
    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @position.setter
    def position(self, pos: Tuple[float, float]) -> None:
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.gx = int(round(self.x / 20.0))
        self.gy = int(round(self.y / 20.0))

    @property
    def size(self) -> Tuple[float, float]:
        return (self.width, self.height)

    @property
    def props(self) -> Dict[str, Any]:
        return self.properties

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "component_type": self.component_type,
            "x": self.x,
            "y": self.y,
            "gx": self.gx,
            "gy": self.gy,
            "width": self.width,
            "height": self.height,
            "selected": self.selected,
            "properties": self.properties,
        }

    def __repr__(self) -> str:
        return f"<Component {self.type} id={self.id} grid=({self.gx},{self.gy}) pos=({self.x},{self.y}) selected={self.selected}>"


class CircuitStore:
    """Store managing circuit components and selection state."""

    def __init__(self):
        self.components: List[Component] = []
        self.selected_component_id: Optional[str] = None

    @property
    def selected_component(self) -> Optional[Component]:
        return self.get_selected_component()

    def add_component(
        self,
        component_type: Union[str, Component],
        x: Optional[float] = None,
        y: Optional[float] = None,
        gx: Optional[int] = None,
        gy: Optional[int] = None,
        width: float = 100.0,
        height: float = 100.0,
        position: Optional[Tuple[float, float]] = None,
        size: Optional[Tuple[float, float]] = None,
        component_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        auto_select: bool = True,
        **kwargs: Any,
    ) -> Component:
        """Instantiates a component, adds it to store, and automatically selects it."""
        if isinstance(component_type, Component):
            comp = component_type
        else:
            if position is not None:
                comp_x = float(position[0])
                comp_y = float(position[1])
            else:
                comp_x = float(x if x is not None else 0.0)
                comp_y = float(y if y is not None else 0.0)

            if size is not None:
                w = float(size[0])
                h = float(size[1])
            else:
                w = float(width)
                h = float(height)

            if gx is None:
                gx = int(round(comp_x / 20.0))
            if gy is None:
                gy = int(round(comp_y / 20.0))

            comp_props = properties or kwargs.get("props", {})

            comp = Component(
                component_type=component_type,
                x=comp_x,
                y=comp_y,
                gx=gx,
                gy=gy,
                width=w,
                height=h,
                component_id=component_id,
                selected=False,
                properties=comp_props,
            )

        self.components.append(comp)

        if auto_select:
            self.select_component(comp.id)
        else:
            comp.selected = False

        return comp

    # camelCase alias for JS/TS spec alignment
    addComponent = add_component

    def select_component(self, component_id: Optional[str]) -> None:
        """Selects the component with the given ID and unselects others."""
        self.selected_component_id = component_id
        for comp in self.components:
            comp.selected = (comp.id == component_id)

    selectComponent = select_component

    def get_selected_component(self) -> Optional[Component]:
        """Returns the currently selected component."""
        for comp in self.components:
            if comp.id == self.selected_component_id:
                return comp
        return None

    getSelectedComponent = get_selected_component

    def get_components(self) -> List[Component]:
        """Returns list of all components."""
        return list(self.components)

    getComponents = get_components

    def get_component_by_id(self, component_id: str) -> Optional[Component]:
        """Finds a component by its ID."""
        for comp in self.components:
            if comp.id == component_id:
                return comp
        return None

    getComponent = get_component_by_id

    def clear(self) -> None:
        self.components.clear()
        self.selected_component_id = None
