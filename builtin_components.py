"""Builtin components definitions with schematic pins and logical ports."""

from typing import Dict, List, Any

BUILTIN_COMPONENTS: Dict[str, Dict[str, Any]] = {
    "rheostat": {
        "type": "rheostat",
        "name": "滑动变阻器",
        "schematicPins": [
            {
                "id": "pin_a",
                "logicalPort": "A",
                "gxOffset": -50,
                "gyOffset": 0,
                "normalAngleDeg": 180,
                "localX": 0,
                "localY": 50,
            },
            {
                "id": "pin_b",
                "logicalPort": "B",
                "gxOffset": 50,
                "gyOffset": 0,
                "normalAngleDeg": 0,
                "localX": 100,
                "localY": 50,
            },
            {
                "id": "pin_c",
                "logicalPort": "P",
                "gxOffset": 50,
                "gyOffset": 0,
                "normalAngleDeg": 0,
                "localX": 100,
                "localY": 50,
            },
            {
                "id": "pin_d",
                "logicalPort": "P",
                "gxOffset": 50,
                "gyOffset": 0,
                "normalAngleDeg": 0,
                "localX": 100,
                "localY": 50,
            },
        ],
    },
    "resistor": {
        "type": "resistor",
        "name": "电阻",
        "schematicPins": [
            {
                "id": "pin_a",
                "logicalPort": "A",
                "gxOffset": -50,
                "gyOffset": 0,
                "normalAngleDeg": 180,
                "localX": 0,
                "localY": 50,
            },
            {
                "id": "pin_b",
                "logicalPort": "B",
                "gxOffset": 50,
                "gyOffset": 0,
                "normalAngleDeg": 0,
                "localX": 100,
                "localY": 50,
            },
        ],
    },
    "battery": {
        "type": "battery",
        "name": "电源",
        "schematicPins": [
            {
                "id": "pin_a",
                "logicalPort": "A",
                "gxOffset": -50,
                "gyOffset": 0,
                "normalAngleDeg": 180,
                "localX": 0,
                "localY": 50,
            },
            {
                "id": "pin_b",
                "logicalPort": "B",
                "gxOffset": 50,
                "gyOffset": 0,
                "normalAngleDeg": 0,
                "localX": 100,
                "localY": 50,
            },
        ],
    },
    "bulb": {
        "type": "bulb",
        "name": "小灯泡",
        "schematicPins": [
            {
                "id": "pin_a",
                "logicalPort": "A",
                "gxOffset": -50,
                "gyOffset": 0,
                "normalAngleDeg": 180,
                "localX": 0,
                "localY": 50,
            },
            {
                "id": "pin_b",
                "logicalPort": "B",
                "gxOffset": 50,
                "gyOffset": 0,
                "normalAngleDeg": 0,
                "localX": 100,
                "localY": 50,
            },
        ],
    },
    "switch": {
        "type": "switch",
        "name": "开关",
        "schematicPins": [
            {
                "id": "pin_a",
                "logicalPort": "A",
                "gxOffset": -50,
                "gyOffset": 0,
                "normalAngleDeg": 180,
                "localX": 0,
                "localY": 50,
            },
            {
                "id": "pin_b",
                "logicalPort": "B",
                "gxOffset": 50,
                "gyOffset": 0,
                "normalAngleDeg": 0,
                "localX": 100,
                "localY": 50,
            },
        ],
    },
}


def get_builtin_component(component_type: str) -> Dict[str, Any]:
    """Returns builtin component definition for a component type."""
    return BUILTIN_COMPONENTS.get(
        component_type,
        {
            "type": component_type,
            "name": component_type,
            "schematicPins": [
                {
                    "id": "pin_a",
                    "logicalPort": "A",
                    "gxOffset": -50,
                    "gyOffset": 0,
                    "normalAngleDeg": 180,
                    "localX": 0,
                    "localY": 50,
                },
                {
                    "id": "pin_b",
                    "logicalPort": "B",
                    "gxOffset": 50,
                    "gyOffset": 0,
                    "normalAngleDeg": 0,
                    "localX": 100,
                    "localY": 50,
                },
            ],
        },
    )
