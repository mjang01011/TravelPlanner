import os
from dotenv import load_dotenv, find_dotenv
from Agent.Agent import Agent
from Router.Router import Router
import folium
from googlemaps.convert import decode_polyline
import time
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
from streamlit_modal import Modal

def load_keys():
    load_dotenv(find_dotenv(), override=True)
    return {
        "open_ai_key": os.environ.get("OPENAI_API_KEY"),
        "google_gemini_key": os.environ.get("GEMINI_API_KEY"),
        "google_maps_key": os.environ.get("GOOGLE_MAPS_API_KEY"),
        "mongo_uri": os.environ.get("MONGO_URI")
    }

def connect_db():
    keys = load_keys()
    client = MongoClient(keys["mongo_uri"], server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = client["TravelPlanner"]
    users_collection = db["users"]
    return users_collection

def display_message(title, message):
    modal = Modal(key=title, title=title)
    with modal.container():
        st.text(message)
    return modal

def create_travel_agent(api_key, model="gpt-3.5-turbo"):
    return Agent(api_key=api_key, model=model)

def increment_progress_bar(progress_bar, prev, final, text):
    for i in range(prev, final):
        progress_bar.progress(i, text)
        time.sleep(0.01)
        
def get_itinerary(travel_agent, query):
    return travel_agent.suggest_travel(query)

def get_updated_itinerary(travel_agent, query, mapping_list):
    return travel_agent.update_itinerary(query, mapping_list)

def get_directions(router, list_of_places):
    directions_result, marker_points = router.make_markers(list_of_places)
    return directions_result, marker_points

def decode_route(directions_result):
    if not directions_result or not directions_result[0].get("overview_polyline"):
        return None
    
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

def update_map(list_of_places, google_maps_key):
    router = Router(google_maps_key=google_maps_key)
    directions_result, marker_points = get_directions(router, list_of_places)
    route_coords = decode_route(directions_result)
    if route_coords == None:
        return st.warning("Error has occured with google maps API. Please try again.")
    map_start_loc = [route_coords[0][0], route_coords[0][1]]
    map = create_map(route_coords, marker_points, map_start_loc)
    return map