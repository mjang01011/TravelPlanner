import os
from dotenv import load_dotenv, find_dotenv
from Agent.Agent import Agent
import folium
from branca.element import Figure
from googlemaps.convert import decode_polyline
from Router.Router import Router
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import time

def load_api_keys():
    load_dotenv(find_dotenv(), override=True)
    return {
        "open_ai_key": os.environ.get("OPENAI_API_KEY"),
        "google_gemini_key": os.environ.get("GOOGLE_GEMINI_API_KEY"),
        "google_maps_key": os.environ.get("GOOGLE_MAPS_API_KEY"),
    }

def create_travel_agent(open_ai_key):
    return Agent(open_ai_api_key=open_ai_key)

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
    figure = Figure(height=500, width=1000)
    map = folium.Map(location=map_start_loc, tiles="openstreetmap", zoom_start=9)
    figure.add_child(map)

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

def increment_progress_bar(progress_bar, prev, final, text):
    for i in range(prev, final):
        progress_bar.progress(i, text)
        time.sleep(0.01)

def run_test(query):
    map_col, itinerary_col = st.columns([1,1], gap="small")
    map_col.subheader("Route Map")
    itinerary_col.subheader("Itinerary Details")
    progress_bar = map_col.progress(0,"Validating your travel plan...")
    try:
        api_keys = load_api_keys()
        travel_agent = create_travel_agent(api_keys["open_ai_key"])
        itinerary, list_of_places, validation = get_itinerary(travel_agent, query)
        if validation:
            increment_progress_bar(progress_bar, 0, 30, validation + '\nRoute map is loading...')
        if itinerary:
            itinerary_col.text(itinerary)
            increment_progress_bar(progress_bar, 30, 50, validation + '\nRoute map is loading...')
        router = Router(google_maps_key=api_keys["google_maps_key"])
        directions_result, marker_points = get_directions(router, list_of_places)
        if not directions_result:
            progress_bar.empty()
            map_col.text("Error has occured with google maps api and wasn't able to generate a map.")
        else:
            increment_progress_bar(progress_bar, 50, 70, validation + '\nRoute map is loading...')
            route_coords = decode_route(directions_result)
            map_start_loc = [route_coords[0][0], route_coords[0][1]]
            increment_progress_bar(progress_bar, 70, 100, validation + '\nRoute map is loading...')
            time.sleep(0.5)
            progress_bar.empty()
            map = create_map(route_coords, marker_points, map_start_loc)
            with map_col:
                st_folium(map)
    
    except Exception as e:
        map_col.error(f"An error occurred: {e}")

st.set_page_config(layout="wide")
st.title("Travel Planner")

with st.form("travel_form"):
    input_query = st.text_input("Type your travel plan:")
    submitted = st.form_submit_button("Submit")
    if submitted:
        run_test(input_query)
