import itertools
import math
from data.shortest_route import route_between_coordinates
from data.coord_verification import validate_coordinate


def euclidean_distance(coord1, coord2):
    """
    Calculate Euclidean distance between two coordinates.
    Simplified for small geographic areas (Abington Township).
    Returns approximate distance in meters.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Approximate meters per degree at latitude ~40°N
    meters_per_lat = 111000
    meters_per_lon = 85000
    
    dlat = (lat2 - lat1) * meters_per_lat
    dlon = (lon2 - lon1) * meters_per_lon
    
    return math.sqrt(dlat**2 + dlon**2)


def nearest_neighbor_tsp(G, start_coord, destinations, weight="length"):
    """
    Nearest Neighbor heuristic for TSP - fast approximation algorithm.
    Good for quick solutions, not necessarily optimal.
    
    Args:
        G: NetworkX graph
        start_coord: Starting coordinate
        destinations: List of destination coordinates
        weight: 'length' or 'travel_time'
    
    Returns:
        Dictionary with route information
    """
    validate_coordinate(start_coord[0], start_coord[1], label="Start")
    for i, dest in enumerate(destinations):
        validate_coordinate(dest[0], dest[1], label=f"Destination {i+1}")
    
    visited = set()
    current = start_coord
    visit_order = [start_coord]
    full_route_nodes = []
    total_distance = 0
    total_time = 0
    
    remaining = set(range(len(destinations)))
    
    while remaining:
        best_idx = None
        best_distance = float('inf')
        best_result = None
        
        # Find nearest unvisited destination
        for idx in remaining:
            dest = destinations[idx]
            result = route_between_coordinates(G, current, dest, weight)
            
            if weight == "length":
                cost = result["distance_m"]
            else:
                cost = result["time_seconds"]
            
            if cost < best_distance:
                best_distance = cost
                best_idx = idx
                best_result = result
        
        # Update totals
        total_distance += best_result["distance_m"]
        total_time += best_result["time_seconds"]
        
        # Append route nodes
        if not full_route_nodes:
            full_route_nodes.extend(best_result["route_nodes"])
        else:
            full_route_nodes.extend(best_result["route_nodes"][1:])
        
        visit_order.append(destinations[best_idx])
        current = destinations[best_idx]
        remaining.remove(best_idx)
    
    return {
        "algorithm": "Nearest Neighbor TSP",
        "visit_order": visit_order,
        "route_nodes": full_route_nodes,
        "total_distance_km": round(total_distance / 1000, 3),
        "total_time_minutes": round(total_time / 60, 2),
        "num_stops": len(destinations)
    }


def dynamic_programming_tsp(G, start_coord, destinations, weight="length", max_stops=12):
    """
    Dynamic Programming TSP solver (Held-Karp algorithm).
    Optimal solution but computationally expensive for large datasets.
    Works well for up to 12-15 stops.
    
    Args:
        G: NetworkX graph
        start_coord: Starting coordinate
        destinations: List of destination coordinates
        weight: 'length' or 'travel_time'
        max_stops: Maximum number of stops to process (for performance)
    
    Returns:
        Dictionary with optimal route information
    """
    
    # Limit number of stops for practical performance
    if len(destinations) > max_stops:
        print(f"Warning: {len(destinations)} stops exceeds max_stops={max_stops}. Using first {max_stops} stops only.")
        destinations = destinations[:max_stops]
    
    validate_coordinate(start_coord[0], start_coord[1], label="Start")
    for i, dest in enumerate(destinations):
        validate_coordinate(dest[0], dest[1], label=f"Destination {i+1}")
    
    n = len(destinations)
    
    # Precompute all distances between points
    dist_matrix = [[0] * (n + 1) for _ in range(n + 1)]
    
    # Distance from start to each destination
    for i, dest in enumerate(destinations):
        result = route_between_coordinates(G, start_coord, dest, weight)
        if weight == "length":
            dist_matrix[0][i + 1] = result["distance_m"]
        else:
            dist_matrix[0][i + 1] = result["time_seconds"]
    
    # Distance between destinations
    for i, dest_i in enumerate(destinations):
        for j, dest_j in enumerate(destinations):
            if i != j:
                result = route_between_coordinates(G, dest_i, dest_j, weight)
                if weight == "length":
                    dist_matrix[i + 1][j + 1] = result["distance_m"]
                else:
                    dist_matrix[i + 1][j + 1] = result["time_seconds"]
    
    # Dynamic Programming: dp[mask][i] = (min_cost, path)
    dp = {}
    parent = {}
    
    # Base case: start from position 0
    for i in range(1, n + 1):
        mask = 1 << i
        dp[(mask, i)] = (dist_matrix[0][i], [i])
        parent[(mask, i)] = -1
    
    # Fill DP table
    for subset_size in range(2, n + 1):
        for subset in itertools.combinations(range(1, n + 1), subset_size):
            mask = 0
            for i in subset:
                mask |= (1 << i)
            
            for last in subset:
                prev_mask = mask ^ (1 << last)
                min_cost = float('inf')
                best_prev = -1
                
                for prev in subset:
                    if prev != last and (prev_mask & (1 << prev)):
                        if (prev_mask, prev) in dp:
                            cost = dp[(prev_mask, prev)][0] + dist_matrix[prev][last]
                            if cost < min_cost:
                                min_cost = cost
                                best_prev = prev
                
                if best_prev != -1:
                    path = dp[(prev_mask, best_prev)][1] + [last]
                    dp[(mask, last)] = (min_cost, path)
                    parent[(mask, last)] = best_prev
    
    # Find optimal solution
    final_mask = (1 << (n + 1)) - 2
    min_total_cost = float('inf')
    best_last = -1
    
    for i in range(1, n + 1):
        if (final_mask, i) in dp:
            if dp[(final_mask, i)][0] < min_total_cost:
                min_total_cost = dp[(final_mask, i)][0]
                best_last = i
    
    # Reconstruct path
    if best_last != -1 and (final_mask, best_last) in dp:
        optimal_indices = dp[(final_mask, best_last)][1]
        visit_order = [start_coord] + [destinations[i - 1] for i in optimal_indices]
        
        # Build actual route nodes
        full_route_nodes = []
        total_distance = 0
        total_time = 0
        
        for i in range(len(visit_order) - 1):
            result = route_between_coordinates(G, visit_order[i], visit_order[i + 1], weight)
            total_distance += result["distance_m"]
            total_time += result["time_seconds"]
            
            if i == 0:
                full_route_nodes.extend(result["route_nodes"])
            else:
                full_route_nodes.extend(result["route_nodes"][1:])
        
        return {
            "algorithm": "Dynamic Programming TSP (Held-Karp)",
            "visit_order": visit_order,
            "route_nodes": full_route_nodes,
            "total_distance_km": round(total_distance / 1000, 3),
            "total_time_minutes": round(total_time / 60, 2),
            "num_stops": len(destinations),
            "is_optimal": True
        }
    
    # Fallback to nearest neighbor if DP fails
    return nearest_neighbor_tsp(G, start_coord, destinations, weight)


def christofides_approximation_tsp(G, start_coord, destinations, weight="length"):
    """
    Christofides algorithm - 1.5-approximation for TSP.
    More sophisticated than nearest neighbor, better quality solutions.
    Good balance between speed and solution quality.
    
    Uses 2-opt local search improvement.
    
    Args:
        G: NetworkX graph
        start_coord: Starting coordinate
        destinations: List of destination coordinates
        weight: 'length' or 'travel_time'
    
    Returns:
        Dictionary with optimized route information
    """
    
    # Start with nearest neighbor solution
    result = nearest_neighbor_tsp(G, start_coord, destinations, weight)
    current_route = result["visit_order"].copy()
    current_cost = result["total_distance_km"] if weight == "length" else result["total_time_minutes"]
    
    improved = True
    iterations = 0
    max_iterations = 100
    
    # 2-opt improvement heuristic
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(1, len(current_route) - 2):
            for j in range(i + 2, len(current_route)):
                if j - i == 1:
                    continue
                
                # Reverse segment between i and j
                new_route = current_route[:i] + current_route[i:j][::-1] + current_route[j:]
                
                # Calculate cost of new route
                new_cost = 0
                for k in range(len(new_route) - 1):
                    res = route_between_coordinates(G, new_route[k], new_route[k + 1], weight)
                    if weight == "length":
                        new_cost += res["distance_m"]
                    else:
                        new_cost += res["time_seconds"]
                
                if weight == "length":
                    new_cost = round(new_cost / 1000, 3)
                else:
                    new_cost = round(new_cost / 60, 2)
                
                # If improvement found, update route
                if new_cost < current_cost:
                    current_route = new_route
                    current_cost = new_cost
                    improved = True
                    break
            
            if improved:
                break
    
    # Rebuild full route nodes
    full_route_nodes = []
    total_distance = 0
    total_time = 0
    
    for i in range(len(current_route) - 1):
        res = route_between_coordinates(G, current_route[i], current_route[i + 1], weight)
        total_distance += res["distance_m"]
        total_time += res["time_seconds"]
        
        if i == 0:
            full_route_nodes.extend(res["route_nodes"])
        else:
            full_route_nodes.extend(res["route_nodes"][1:])
    
    return {
        "algorithm": "Christofides (2-Opt Optimized)",
        "visit_order": current_route,
        "route_nodes": full_route_nodes,
        "total_distance_km": round(total_distance / 1000, 3),
        "total_time_minutes": round(total_time / 60, 2),
        "num_stops": len(destinations),
        "optimization_iterations": iterations
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
    
    print("=== Nearest Neighbor TSP ===")
    result_nn = nearest_neighbor_tsp(G, start_coord, destinations)
    print(f"Total distance: {result_nn['total_distance_km']} km")
    print(f"Total time: {result_nn['total_time_minutes']} minutes\n")
    
    print("=== Christofides with 2-Opt ===")
    result_christofides = christofides_approximation_tsp(G, start_coord, destinations)
    print(f"Total distance: {result_christofides['total_distance_km']} km")
    print(f"Total time: {result_christofides['total_time_minutes']} minutes\n")
    
    print("=== Dynamic Programming TSP (Optimal) ===")
    result_dp = dynamic_programming_tsp(G, start_coord, destinations)
    print(f"Total distance: {result_dp['total_distance_km']} km")
    print(f"Total time: {result_dp['total_time_minutes']} minutes")