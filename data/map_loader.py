import osmnx as ox
import os

MapCachePath = "abington_graph.graphml"

# Abington Township Boundary Coordinates w/ Small Buffer
AbingtonBounds = {
    "north": 40.145,
    "south": 40.085,
    "east": -75.075,
    "west": -75.175
}

def download_graph():
    # Download Abington Road Network
    G = ox.graph_from_place(
        "Abington Township, Montgomery County, Pennsylvania, USA",
        network_type="drive",
        retain_all=False
    )
    # Add Speed and Travel Time Data to Edges
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    ox.save_graphml(G, MapCachePath) # Save Road Network.
    print(f"Graph Saved at {MapCachePath}")
    return G

def load_graph():
    # Load Graph From Cache. If not in Cache, download then load.
    if os.path.exists(MapCachePath):
        return ox.load_graphml(MapCachePath)
    return download_graph()

G = load_graph()