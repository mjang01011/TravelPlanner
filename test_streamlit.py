import os
from dotenv import load_dotenv, find_dotenv
from Agent.Agent import Agent
import folium
from branca.element import Figure
from googlemaps.convert import decode_polyline
from Router.Router import Router
import streamlit as st
from streamlit_folium import st_folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

def run_test(query):

    # Load API Keys
    load_dotenv(find_dotenv(), override=True)

    open_ai_key = os.environ.get("OPENAI_API_KEY")
    google_gemini_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
    google_maps_key = os.environ.get("GOOGLE_MAPS_API_KEY")

    travel_agent = Agent(
        open_ai_api_key=open_ai_key,
    )
    
    itinerary, list_of_places, validation = travel_agent.suggest_travel(query)
        
    # Create a Figure
    figure = Figure(height=500, width=1000)

    router = Router(google_maps_key=google_maps_key)
    directions_result, marker_points = router.make_markers(list_of_places)

    # Decode the polyline from the directions result to get the overall route
    # List contains lat and lng coordinates for each stops {'lat': xx, 'lng': yy}
    overall_route = decode_polyline(directions_result[0]["overview_polyline"]["points"])

    # Create a list of tuples containing latitude and longitude coordinates for each point in the overall route
    route_coords = [(float(p["lat"]), float(p["lng"])) for p in overall_route]

    # Set the map center to be at the start location of the route
    map_start_loc = [overall_route[0]["lat"], overall_route[0]["lng"]]

    def create_map():
        if "map" not in st.session_state or st.session_state.map is None:
            map = folium.Map(
                location=map_start_loc, tiles="openstreetmap", zoom_start=9
            )
            figure.add_child(map)

            # Add the waypoints as red markers
            for location, address in marker_points:
                folium.Marker(
                    location=location,
                    popup=address,
                    tooltip="<strong>Click for address</strong>",
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(map)

            # Add the route as a blue line
            f_group = folium.FeatureGroup("Route overview")
            folium.vector_layers.PolyLine(
                route_coords,
                popup="<b>Overall route</b>",
                tooltip="This is a tooltip where we can add distance and duration",
                color="blue",
                weight=2,
            ).add_to(f_group)
            f_group.add_to(map)
            st.session_state.map = map
        return st.session_state.map

    def show_map():
        map = create_map()
        folium_static(map)

    show_map()


with st.form("travel_form"):
    input_query = st.text_input("Type your travel plan:")
    submitted = st.form_submit_button("Submit")
    if submitted:
        run_test(input_query)