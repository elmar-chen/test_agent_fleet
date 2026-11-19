import uuid
from typing import Dict, List, Optional, Any


class Component:
    """Represents a component in the circuit canvas."""

    def __init__(
        self,
        component_type: str = "",
        x: float = 0.0,
        y: float = 0.0,
        gx: Optional[int] = None,
        gy: Optional[int] = None,
        width: float = 100.0,
        height: float = 100.0,
        component_id: Optional[str] = None,
        name: str = "",
        symbol: str = "",
        properties: Optional[Dict[str, Any]] = None,
        selected: bool = False,
    ):
        self.id: str = component_id or str(uuid.uuid4())
        self.component_id: str = self.id
        self.type: str = component_type
        self.component_type: str = component_type
        self.name: str = name or component_type
        self.x: float = float(x)
        self.y: float = float(y)
        self.gx: int = gx if gx is not None else int(round(self.x / 20.0))
        self.gy: int = gy if gy is not None else int(round(self.y / 20.0))
        self.width: float = float(width)
        self.height: float = float(height)
        self.properties: Dict[str, Any] = properties or {}
        self.symbol: str = symbol or self.properties.get("symbol", component_type)
        self.selected: bool = selected

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "component_id": self.component_id,
            "type": self.type,
            "component_type": self.component_type,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "gx": self.gx,
            "gy": self.gy,
            "width": self.width,
            "height": self.height,
            "symbol": self.symbol,
            "properties": self.properties,
            "selected": self.selected,
        }

    def __repr__(self) -> str:
        return f"<Component {self.type} id={self.id} grid=({self.gx},{self.gy}) pos=({self.x},{self.y}) selected={self.selected}>"


SchematicComponent = Component


class CircuitStore:
    """Store managing circuit components and selection state."""

    def __init__(self):
        self.components: List[Component] = []
        self.selected_component_id: Optional[str] = None

    def add_component(
        self,
        component_type: str = "",
        x: float = 0.0,
        y: float = 0.0,
        gx: Optional[int] = None,
        gy: Optional[int] = None,
        width: float = 100.0,
        height: float = 100.0,
        name: str = "",
        symbol: str = "",
        properties: Optional[Dict[str, Any]] = None,
        component_id: Optional[str] = None,
    ) -> Component:
        """Instantiates a component, adds it to store, and automatically selects it."""
        if gx is None:
            gx = int(round(x / 20.0))
        if gy is None:
            gy = int(round(y / 20.0))

        comp = Component(
            component_type=component_type,
            x=x,
            y=y,
            gx=gx,
            gy=gy,
            width=width,
            height=height,
            name=name,
            symbol=symbol,
            properties=properties,
            component_id=component_id,
            selected=False,
        )
        self.components.append(comp)
        self.select_component(comp.id)
        return comp

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

    get_component = get_component_by_id
