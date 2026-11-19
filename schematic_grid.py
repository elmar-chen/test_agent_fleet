"""Schematic grid definitions for component symbol pins and physical layout dimensions."""

from typing import Dict, List, Any

SCHEMATIC_GRID_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "rheostat": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 0,
                "localY": 50,
                "normalAngleDeg": 180,
                "name": "Left Terminal A",
                "logicalPort": "A",
            },
            {
                "id": "pin_b",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Right Terminal B",
                "logicalPort": "B",
            },
            {
                "id": "pin_c",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Slider Terminal C",
                "logicalPort": "P",
            },
            {
                "id": "pin_d",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Slider Terminal D",
                "logicalPort": "P",
            },
        ],
    },
    "resistor": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 0,
                "localY": 50,
                "normalAngleDeg": 180,
                "name": "Left Terminal",
                "logicalPort": "A",
            },
            {
                "id": "pin_b",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Right Terminal",
                "logicalPort": "B",
            },
        ],
    },
    "battery": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 0,
                "localY": 50,
                "normalAngleDeg": 180,
                "name": "Positive Terminal",
                "logicalPort": "A",
            },
            {
                "id": "pin_b",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Negative Terminal",
                "logicalPort": "B",
            },
        ],
    },
    "bulb": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 0,
                "localY": 50,
                "normalAngleDeg": 180,
                "name": "Terminal A",
                "logicalPort": "A",
            },
            {
                "id": "pin_b",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Terminal B",
                "logicalPort": "B",
            },
        ],
    },
    "switch": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 0,
                "localY": 50,
                "normalAngleDeg": 180,
                "name": "Terminal A",
                "logicalPort": "A",
            },
            {
                "id": "pin_b",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Terminal B",
                "logicalPort": "B",
            },
        ],
    },
    "ammeter": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 0,
                "localY": 50,
                "normalAngleDeg": 180,
                "name": "Positive Terminal",
                "logicalPort": "A",
            },
            {
                "id": "pin_b",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Negative Terminal",
                "logicalPort": "B",
            },
        ],
    },
    "voltmeter": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 0,
                "localY": 50,
                "normalAngleDeg": 180,
                "name": "Positive Terminal",
                "logicalPort": "A",
            },
            {
                "id": "pin_b",
                "localX": 100,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Negative Terminal",
                "logicalPort": "B",
            },
        ],
    },
    "junction": {
        "width": 100,
        "height": 100,
        "pins": [
            {
                "id": "pin_a",
                "localX": 50,
                "localY": 50,
                "normalAngleDeg": 0,
                "name": "Junction Center",
                "logicalPort": "A",
            },
        ],
    },
}


def get_schematic_grid(component_type: str) -> Dict[str, Any]:
    """Returns schematic grid definition for a component type."""
    return SCHEMATIC_GRID_DEFINITIONS.get(
        component_type,
        {
            "width": 100,
            "height": 100,
            "pins": [
                {"id": "pin_a", "localX": 0, "localY": 50, "normalAngleDeg": 180},
                {"id": "pin_b", "localX": 100, "localY": 50, "normalAngleDeg": 0},
            ],
        },
    )
