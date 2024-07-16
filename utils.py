import os
from dotenv import load_dotenv, find_dotenv
from Agent.Agent import Agent
import folium
from branca.element import Figure
from googlemaps.convert import decode_polyline

import time

# Loads api keys
def load_keys():
    load_dotenv(find_dotenv(), override=True)
    return {
        "open_ai_key": os.environ.get("OPENAI_API_KEY"),
        # "google_gemini_key": os.environ.get("GOOGLE_GEMINI_API_KEY"),
        "google_maps_key": os.environ.get("GOOGLE_MAPS_API_KEY"),
        "mongo_uri": os.environ.get("MONGO_URI")
    }

def create_travel_agent(open_ai_key):
    return Agent(open_ai_api_key=open_ai_key)

def increment_progress_bar(progress_bar, prev, final, text):
    for i in range(prev, final):
        progress_bar.progress(i, text)
        time.sleep(0.01)
        
def get_itinerary(travel_agent, query):
    return travel_agent.suggest_travel(query)

def get_directions(router, list_of_places):
    directions_result, marker_points = router.make_markers(list_of_places)
    return directions_result, marker_points

def decode_route(directions_result):
    if not directions_result or not directions_result[0].get("overview_polyline"):
        raise ValueError("Invalid directions result")
    
    overall_route = decode_polyline(directions_result[0]["overview_polyline"]["points"])
    return [(float(p["lat"]), float(p["lng"])) for p in overall_route]

def create_map(route_coords, marker_points, map_start_loc):
    map = folium.Map(location=map_start_loc, tiles="openstreetmap", zoom_start=9)

    for location, address in marker_points:
        folium.Marker(
            location=location,
            popup=address,
            tooltip="<strong>Click for address</strong>",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(map)

    f_group = folium.FeatureGroup("Route overview")
    folium.vector_layers.PolyLine(
        route_coords,
        popup="<b>Overall route</b>",
        tooltip="This is a tooltip where we can add distance and duration",
        color="blue",
        weight=2,
    ).add_to(f_group)
    f_group.add_to(map)
    
    return map