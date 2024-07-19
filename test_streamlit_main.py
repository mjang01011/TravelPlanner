from utils import load_keys, create_travel_agent, increment_progress_bar, get_itinerary, get_directions, decode_route, create_map, updateMap
from Router.Router import Router
import streamlit as st
from streamlit_folium import st_folium
import time

def updateMap(list_of_places, google_maps_key):
    router = Router(google_maps_key=google_maps_key)
    directions_result, marker_points = get_directions(router, list_of_places)
    route_coords = decode_route(directions_result)
    map_start_loc = [route_coords[0][0], route_coords[0][1]]
    map = create_map(route_coords, marker_points, map_start_loc)
    return map

keys = load_keys()
keys = keys
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
title, login = st.columns([0.9, 0.1])
title.title("Travel Planner")
if 'auth' not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    if login.button("Login"):
        st.switch_page("pages/test_streamlit_login.py")
else:
    if login.button("Logout"):
        st.session_state.auth = False
        st.rerun()
    if st.button("View your past plans!"):
        st.switch_page("pages/past_records.py")
with st.form("travel_form"):
    input_query = st.text_input("Type your travel plan:")
    query_submitted = st.form_submit_button("Submit")
map_col, itinerary_col = st.columns([1,1], gap="small")
        
if query_submitted:
    try:
        map_col.empty()
        map_col.subheader("Route Map")
        itinerary_col.subheader("Itinerary Details")
        progress_bar = map_col.progress(0,"Validating your travel plan...")
        travel_agent = create_travel_agent(keys["open_ai_key"])
        itinerary, list_of_places, validation = get_itinerary(travel_agent, input_query)
        st.session_state.itinerary = itinerary
        print("Itinerary: ", itinerary)
        print("Places: ",list_of_places)
        print("Validation: ",validation)
        st.session_state.list_of_places = list_of_places
        st.session_state.initial_list_of_places = list_of_places.copy()
        st.session_state.validation = validation
        if validation:
            increment_progress_bar(progress_bar, 0, 30, '\nRoute map is loading...')
            router = Router(google_maps_key=keys["google_maps_key"])
            directions_result, marker_points = get_directions(router, list_of_places)
            increment_progress_bar(progress_bar, 30, 70, '\nRoute map is loading...')
            route_coords = decode_route(directions_result)
            map_start_loc = [route_coords[0][0], route_coords[0][1]]
            increment_progress_bar(progress_bar, 70, 100, '\nRoute map is loading...')
            time.sleep(0.5)
            progress_bar.empty()
            map = create_map(route_coords, marker_points, map_start_loc)
            st.session_state.map = map
            with map_col:
                st_folium(map, width="100%", returned_objects=[])
            
        else:
            progress_bar.empty()
            map_col.text("Error has occured with google maps api and wasn't able to generate a map.")
        
    except Exception as e:
        map_col.error(f"An error occurred: {e}")

if 'initial_list_of_places' in st.session_state:        
    suggestions = []
    with itinerary_col:
        itinerary_col.text(st.session_state.itinerary)
        st.text("Currently suggested places to visit:")
        for i, place in enumerate(st.session_state.initial_list_of_places['stops']):
            suggestions.append(st.checkbox(place, value=True))
        st.divider()
        st.text("Extra places you may want to consider:")
        for i, place in enumerate(st.session_state.initial_list_of_places['extra_stops']):
            suggestions.append(st.checkbox(place, value=False))
        st.session_state.list_of_places['stops'] = [stop for stop, keep in zip(st.session_state.initial_list_of_places['stops'], suggestions) if keep]
    if not query_submitted:
        with map_col:
            st_folium(updateMap(st.session_state.list_of_places, keys["google_maps_key"]), width="100%", returned_objects=[], key="map_folium_updated")