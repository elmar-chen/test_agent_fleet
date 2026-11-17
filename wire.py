"""
Wire Management Module for Schematic Editor

Requirement (Issue #78):
CR: 导线选中时拖拽端点移动改变连线，未选中时新增连线
(When a wire is selected, dragging its endpoint moves/reconnects the line; when not selected, dragging creates a new wire.)
"""

from typing import List, Optional, Tuple

Point = Tuple[float, float]


class Wire:
    """
    Represents a schematic wire (lead) between two 2D points.
    """

    def __init__(
        self,
        start_point: Point,
        end_point: Point,
        wire_id: Optional[str] = None,
        selected: bool = False,
    ):
        self.wire_id = wire_id
        self.start_point = (float(start_point[0]), float(start_point[1]))
        self.end_point = (float(end_point[0]), float(end_point[1]))
        self.selected = selected

    def __repr__(self) -> str:
        return f"Wire(id={self.wire_id}, start={self.start_point}, end={self.end_point}, selected={self.selected})"


class WireManager:
    """
    Manages wires in a schematic canvas and handles endpoint drag behavior.
    """

    def __init__(self):
        self.wires: List[Wire] = []
        self._next_id: int = 1

    def create_wire(
        self, start_point: Point, end_point: Point, selected: bool = False
    ) -> Wire:
        wire_id = f"wire_{self._next_id}"
        self._next_id += 1
        wire = Wire(start_point, end_point, wire_id=wire_id, selected=selected)
        self.wires.append(wire)
        return wire

    def select_wire(self, wire_id: str) -> Optional[Wire]:
        for wire in self.wires:
            if wire.wire_id == wire_id:
                wire.selected = True
                return wire
        return None

    def deselect_wire(self, wire_id: str) -> Optional[Wire]:
        for wire in self.wires:
            if wire.wire_id == wire_id:
                wire.selected = False
                return wire
        return None

    def deselect_all(self) -> None:
        for wire in self.wires:
            wire.selected = False

    def get_selected_wires(self) -> List[Wire]:
        return [w for w in self.wires if w.selected]

    def handle_drag_endpoint(
        self,
        start_pos: Point,
        new_pos: Point,
        wire_id: Optional[str] = None,
        tolerance: float = 1e-3,
    ) -> Wire:
        """
        Handles endpoint dragging behavior for Issue #78:
        - If the target wire (or any wire matching start_pos) is selected,
          dragging an endpoint updates that wire's endpoint (reconnects/moves line).
        - If unselected (or no wire matches/is specified), creates and adds a new wire.
        """
        target_wire: Optional[Wire] = None

        if wire_id is not None:
            for w in self.wires:
                if w.wire_id == wire_id:
                    target_wire = w
                    break
        else:
            # Check if any selected wire has an endpoint near start_pos
            for w in self.get_selected_wires():
                if self._is_near(w.start_point, start_pos, tolerance) or self._is_near(
                    w.end_point, start_pos, tolerance
                ):
                    target_wire = w
                    break

        if target_wire and target_wire.selected:
            # Wire is selected -> update existing endpoint (reconnect line)
            dist_to_start = self._distance(target_wire.start_point, start_pos)
            dist_to_end = self._distance(target_wire.end_point, start_pos)

            if dist_to_start <= dist_to_end:
                target_wire.start_point = (float(new_pos[0]), float(new_pos[1]))
            else:
                target_wire.end_point = (float(new_pos[0]), float(new_pos[1]))
            return target_wire
        else:
            # Wire is unselected -> create a new wire
            new_wire = self.create_wire(start_pos, new_pos)
            return new_wire

    @staticmethod
    def _distance(p1: Point, p2: Point) -> float:
        import math

        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _is_near(self, p1: Point, p2: Point, tolerance: float) -> bool:
        return self._distance(p1, p2) <= tolerance
