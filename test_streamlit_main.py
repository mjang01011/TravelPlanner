from utils import load_keys, create_travel_agent, increment_progress_bar, get_itinerary, get_directions, decode_route, create_map
from Router.Router import Router
import streamlit as st
from streamlit_folium import st_folium
import time

def updateMap(list_of_places):
    router = Router(google_maps_key=keys["google_maps_key"])
    directions_result, marker_points = get_directions(router, list_of_places)
    route_coords = decode_route(directions_result)
    map_start_loc = [route_coords[0][0], route_coords[0][1]]
    map = create_map(route_coords, marker_points, map_start_loc)
    return map

keys = load_keys()
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("Travel Planner")
if 'auth' not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    if st.button("Login to Log your Plans!"):
        st.switch_page("pages/test_streamlit_login.py")
with st.form("travel_form"):
    input_query = st.text_input("Type your travel plan:")
    submitted = st.form_submit_button("Submit")
map_col, itinerary_col = st.columns([1,1], gap="small")

# if 'initial_list_of_places' in st.session_state:
#     itinerary_col.text(st.session_state.itinerary)
#     with map_col:
#         st_folium(updateMap(st.session_state.list_of_places), width="100%", returned_objects=[])
        
if submitted:
    try:
        map_col.subheader("Route Map")
        itinerary_col.subheader("Itinerary Details")
        progress_bar = map_col.progress(0,"Validating your travel plan...")
        travel_agent = create_travel_agent(keys["open_ai_key"])
        itinerary, list_of_places, validation = get_itinerary(travel_agent, input_query)
        st.session_state.itinerary = itinerary
        st.session_state.list_of_places = list_of_places
        print(list_of_places)
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

if 'list_of_places' in st.session_state:        
    boxes = []
    with itinerary_col:
        itinerary_col.text(st.session_state.itinerary)
        for i, place in enumerate(st.session_state.initial_list_of_places['stops']):
            boxes.append(st.checkbox(place, value=True))
        st.session_state.list_of_places['stops'] = [stop for stop, keep in zip(st.session_state.initial_list_of_places['stops'], boxes) if keep]
    with map_col:
        st_folium(updateMap(st.session_state.list_of_places), width="100%", returned_objects=[], key="map_folium_updated")