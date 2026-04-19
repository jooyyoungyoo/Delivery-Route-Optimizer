import osmnx as ox
from data.map_loader import AbingtonBounds


def is_in_abington(lat, lon):
    # Return True if coordinate falls within Abington boundaries
    return (
        AbingtonBounds["south"] <= lat <= AbingtonBounds["north"] and
        AbingtonBounds["west"] <= lon <= AbingtonBounds["east"]
    )


def validate_coordinate(lat, lon, label="Coordinate"):
    # Raise an error if a coordinate is out of bounds
    if not is_in_abington(lat, lon):
        raise ValueError(
            f"{label} ({lat}, {lon}) is outside the Abington Township working area.\n"
            f"Valid range: lat {AbingtonBounds['south']}–{AbingtonBounds['north']}, "
            f"lon {AbingtonBounds['west']}–{AbingtonBounds['east']}"
        )


def snap_to_node(G, lat, lon):
    # Snap coordinate to the nearest road node so entered coordinates don't need to be directly on the road
    return ox.nearest_nodes(G, lon, lat)  # OSMnx expects longitude and latitude
