from utils import load_keys, create_travel_agent, increment_progress_bar, decode_route, update_map, connect_db, display_message, verification_spinner
from Router.Router import Router
import streamlit as st
from streamlit_folium import st_folium
import time
from datetime import datetime, timezone
import uuid
from bson.binary import Binary
import json


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
title, login = st.columns([0.9, 0.1])
title.title("Travel Planner")
validation_result = verification_spinner()
if not validation_result:
    time.sleep(9999)
keys = load_keys()
    
if 'auth' not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    if login.button("Login"):
        st.switch_page("pages/login.py")
else:
    if login.button("Logout"):
        st.session_state.auth = False
        st.rerun()
    if st.button("View your past plans!"):
        st.switch_page("pages/past_records.py")
with st.form("travel_form"):
    input_query = st.text_input("Type your travel plan:")
    query_submitted = st.form_submit_button("Submit")
select_llm_model = st.radio("Choose language model:", ["gpt-3.5-turbo", "gemini-1.5-pro"])
st.session_state.llm_model = select_llm_model
llm_model_names = ["gpt-3.5-turbo", "gemini-1.5-pro"]
llm_model_keys = ["open_ai_key", "google_gemini_key"]
map_col, itinerary_col, update_buttons = st.columns([0.45,0.45,0.1], gap="small")

if query_submitted:
    if input_query == "":
        st.warning("Please enter your travel plan.")
    else:
        try:
            map_col.empty()
            map_col.subheader("Route Map")
            itinerary_col.subheader("Itinerary Details")
            progress_bar = map_col.progress(0,"Validating your travel plan...")
            travel_agent = create_travel_agent(keys[llm_model_keys[llm_model_names.index(st.session_state.llm_model)]], model=select_llm_model)
            itinerary, list_of_places, validation = travel_agent.suggest_travel(input_query)
            st.session_state.input_query = input_query
            st.session_state.itinerary = itinerary
            st.session_state.list_of_places = list_of_places
            st.session_state.initial_list_of_places = list_of_places.copy()
            st.session_state.validation = validation
            if validation:
                increment_progress_bar(progress_bar, 0, 30, '\nRoute map is loading...')
                router = Router(google_maps_key=keys["google_maps_key"])
                directions_result, marker_points = router.make_markers(list_of_places)
                increment_progress_bar(progress_bar, 30, 70, '\nRoute map is loading...')
                route_coords = decode_route(directions_result)
                if route_coords == None:
                    st.warning("Error has occured with google maps API. Please try again.")
                map_start_loc = [route_coords[0][0], route_coords[0][1]]
                increment_progress_bar(progress_bar, 70, 100, '\nRoute map is loading...')
                time.sleep(0.5)
                progress_bar.empty()
            else:
                progress_bar.empty()
                map_col.text("Error has occured with google maps api and wasn't able to generate a map.")
        
        except Exception as e:
            map_col.error(f"An error occurred: {e}")

def update_itinerary():
    travel_agent = create_travel_agent(keys[llm_model_keys[llm_model_names.index(st.session_state.llm_model)]], model=st.session_state.llm_model)
    st.session_state.itinerary = travel_agent.update_itinerary(st.session_state.input_query, json.dumps(st.session_state.list_of_places))
    
if 'initial_list_of_places' in st.session_state:        
    suggestions = []
    update_itinerary_button = update_buttons.button("Update Itinerary", on_click=update_itinerary)
    add_to_past_records_button = update_buttons.button("Add to past records")
    with itinerary_col:
        itinerary_text = itinerary_col.text(st.session_state.itinerary)
        st.text("Currently suggested places to visit:")
        for i, place in enumerate(st.session_state.initial_list_of_places['stops']):
            suggestions.append(st.checkbox(place, value=True))
        st.divider()
        st.text("Extra places you may want to consider:")
        for i, place in enumerate(st.session_state.initial_list_of_places['extra_stops']):
            suggestions.append(st.checkbox(place, value=False))
        new_stops = []
        new_extra_stops = []
        for stop, keep in zip(st.session_state.initial_list_of_places['stops'] + st.session_state.initial_list_of_places['extra_stops'], suggestions):
            if keep:
                new_stops.append(stop)
            else:
                new_extra_stops.append(stop)
        st.session_state.list_of_places['stops'] = new_stops
        st.session_state.list_of_places['extra_stops'] = new_extra_stops
        with map_col:
            st_folium(update_map(st.session_state.list_of_places, keys["google_maps_key"]), width="100%", returned_objects=[], key="map_folium_updated")
    if add_to_past_records_button:
        if not st.session_state.auth:
            update_buttons.warning("You are not logged in. Please log in to add your travel plan.")
            time.sleep(2)
            st.switch_page("pages/login.py")
        else:
            users_collection = connect_db()
            new_query = {
                "qid": Binary(uuid.uuid4().bytes, 4),
                "query": st.session_state.input_query,
                "timestamp": datetime.now(timezone.utc),
                "itinerary": f"""{st.session_state.itinerary}""",
                'list_of_places': st.session_state.list_of_places
            }
            result = users_collection.update_one(
                {"uid": st.session_state.uid},
                {"$push": {"queries": new_query}}
            )
            if result.matched_count > 0:
                display_message("Success!", "Your travel plan has been added.")
            else:
                display_message("Failed!", "An error occurred with adding your travel plan. Please try again.")
        