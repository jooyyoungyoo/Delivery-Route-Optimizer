from data.map_loader import G
from data.shortest_route import route_between_coordinates


def greedy_delivery_route(G, start_coord, destinations, weight="length"):
    remaining = destinations.copy()
    current = start_coord

    visit_order = [start_coord]
    full_route_nodes = []

    total_distance = 0
    total_time = 0

    while remaining:

        best_destination = None
        best_result = None
        best_cost = float("inf")

        # Evaluate all remaining destinations
        for dest in remaining:

            result = route_between_coordinates(G, current, dest, weight)

            if weight == "length":
                cost = result["distance_m"]
            else:
                cost = result["time_seconds"]

            # Greedy heuristic: choose closest node
            if cost < best_cost:
                best_cost = cost
                best_destination = dest
                best_result = result

        # Update totals
        total_distance += best_result["distance_m"]
        total_time += best_result["time_seconds"]

        # Append route nodes
        if not full_route_nodes:
            full_route_nodes.extend(best_result["route_nodes"])
        else:
            full_route_nodes.extend(best_result["route_nodes"][1:])

        visit_order.append(best_destination)

        # Move to next location
        current = best_destination
        remaining.remove(best_destination)

    return {
        "visit_order": visit_order,
        "route_nodes": full_route_nodes,
        "total_distance_km": round(total_distance / 1000, 3),
        "total_time_minutes": round(total_time / 60, 2)
    }


# Starting coordinate (warehouse / origin)
start_coord = (40.1165, -75.1150)  # Central Abington Township

# Example destination coordinates (6 delivery points)
destinations = [
    (40.1200, -75.1100),  # Northeast Abington
    (40.1180, -75.1200),  # West side
    (40.1140, -75.1050),  # Southeast corner
    (40.1125, -75.1180),  # South-central
    (40.1175, -75.1120),  # Near central park / community area
    (40.1155, -75.1085),  # East side residential
]

# Example usage:
result = greedy_delivery_route(G, start_coord, destinations)
print(result["visit_order"])
print(result["total_distance_km"])
