import networkx as nx
from coord_verification import validate_coordinate, snap_to_node
import sklearn  # Needed as optional dependency for traversing graph properly


def route_between_coordinates(G, coord1, coord2, weight="length"):
    # Fine shortest route between two coordinates within working area.
    # Weights: 'length' for shortest distance, 'travel_time' for fastest route

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    validate_coordinate(lat1, lon1, label="Origin")
    validate_coordinate(lat2, lon2, label="Destination")

    orig_node = snap_to_node(G, lat1, lon1)
    dest_node = snap_to_node(G, lat2, lon2)

    route_nodes = nx.shortest_path(G, orig_node, dest_node, weight=weight)
    distance_m = nx.shortest_path_length(G, orig_node, dest_node, weight="length")
    time_s = nx.shortest_path_length(G, orig_node, dest_node, weight="travel_time")

    return {
        "route_nodes": route_nodes,
        "distance_m": distance_m,
        "distance_km": round(distance_m / 1000, 3),
        "time_seconds": round(time_s),
        "time_minutes": round(time_s / 60, 2)
    }
