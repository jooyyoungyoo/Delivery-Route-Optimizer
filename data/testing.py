from map_loader import load_graph
from shortest_route import route_between_coordinates

if __name__ == "__main__":
    G = load_graph()

    # Example: two points within Abington Township
    coord1 = (40.115, -75.130)  # near Abington center
    coord2 = (40.098, -75.105)  # toward Jenkintown area

    try:
        result = route_between_coordinates(G, coord1, coord2, weight="travel_time")
        print(f"Distance:  {result['distance_km']} km")
        print(f"Est. time: {result['time_minutes']} minutes")
        print(f"Nodes in route: {len(result['route_nodes'])}")
    except ValueError as e:
        print(f"Error: {e}")

# Can't run with Numpy 2.0.0+ due to sklearn dependency
