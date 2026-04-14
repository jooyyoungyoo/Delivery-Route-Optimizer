import heapq
import math
from data.shortest_route import route_between_coordinates
from data.coord_verification import validate_coordinate, snap_to_node


def euclidean_distance(coord1, coord2):
    """
    Calculate Euclidean distance between two coordinates.
    Sufficient for small local areas like Abington Township.
    Much faster than haversine for local optimization.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)


def astar_route_optimizer(G, start_coord, destinations, weight="length"):
    """
    A* algorithm for multi-stop route optimization.
    Uses Euclidean distance as heuristic to find near-optimal delivery routes.
    
    Args:
        G: NetworkX graph of road network
        start_coord: Starting coordinate (lat, lon)
        destinations: List of destination coordinates [(lat, lon), ...]
        weight: 'length' for distance or 'travel_time' for time-based optimization
    
    Returns:
        Dictionary with optimized route information
    """
    
    # Validate all coordinates
    validate_coordinate(start_coord[0], start_coord[1], label="Start")
    for i, dest in enumerate(destinations):
        validate_coordinate(dest[0], dest[1], label=f"Destination {i+1}")
    
    # Convert coordinates to nodes
    start_node = snap_to_node(G, start_coord[0], start_coord[1])
    dest_nodes = [snap_to_node(G, dest[0], dest[1]) for dest in destinations]
    
    # Initialize
    visited = set()
    current = start_coord
    visit_order = [start_coord]
    full_route_nodes = []
    total_distance = 0
    total_time = 0
    
    remaining_indices = set(range(len(destinations)))
    
    while remaining_indices:
        # Priority queue: (f_score, index, result)
        # f_score = g_score (actual distance traveled so far) + h_score (heuristic to destination)
        open_set = []
        
        for idx in remaining_indices:
            dest = destinations[idx]
            
            # Get actual route cost from current to destination
            result = route_between_coordinates(G, current, dest, weight)
            
            if weight == "length":
                g_score = result["distance_m"]
            else:
                g_score = result["time_seconds"]
            
            # Heuristic: Euclidean distance to destination (straight line)
            h_score = euclidean_distance(current, dest)
            
            # f_score combines actual cost with heuristic estimate
            f_score = g_score + h_score
            
            heapq.heappush(open_set, (f_score, idx, result, dest))
        
        # Select best destination according to A* heuristic
        _, best_idx, best_result, best_dest = heapq.heappop(open_set)
        
        # Update totals
        total_distance += best_result["distance_m"]
        total_time += best_result["time_seconds"]
        
        # Append route nodes
        if not full_route_nodes:
            full_route_nodes.extend(best_result["route_nodes"])
        else:
            full_route_nodes.extend(best_result["route_nodes"][1:])
        
        visit_order.append(best_dest)
        
        # Move to next location
        current = best_dest
        remaining_indices.remove(best_idx)
    
    return {
        "algorithm": "A*",
        "visit_order": visit_order,
        "route_nodes": full_route_nodes,
        "total_distance_km": round(total_distance / 1000, 3),
        "total_time_minutes": round(total_time / 60, 2),
        "num_stops": len(destinations)
    }


# Example usage
if __name__ == "__main__":
    from data.map_loader import G
    
    start_coord = (40.1165, -75.1150)
    destinations = [
        (40.1200, -75.1100),
        (40.1180, -75.1200),
        (40.1140, -75.1050),
        (40.1125, -75.1180),
        (40.1175, -75.1120),
        (40.1155, -75.1085),
    ]
    
    result = astar_route_optimizer(G, start_coord, destinations)
    print("A* Algorithm Results:")
    print(f"Visit order: {result['visit_order']}")
    print(f"Total distance: {result['total_distance_km']} km")
    print(f"Total time: {result['total_time_minutes']} minutes")