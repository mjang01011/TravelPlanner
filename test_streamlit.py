from utils import load_api_keys, create_travel_agent, increment_progress_bar, get_itinerary, get_directions, decode_route, create_map
from Router.Router import Router
import streamlit as st
from streamlit_folium import st_folium
import time


def main():
    st.set_page_config(layout="wide")
    st.title("Travel Planner")
    with st.form("travel_form"):
        input_query = st.text_input("Type your travel plan:")
        submitted = st.form_submit_button("Submit")
    if submitted:
        map_col, itinerary_col = st.columns([1,1], gap="small")
        map_col.subheader("Route Map")
        itinerary_col.subheader("Itinerary Details")
        progress_bar = map_col.progress(0,"Validating your travel plan...")
        try:
            api_keys = load_api_keys()
            travel_agent = create_travel_agent(api_keys["open_ai_key"])
            itinerary, list_of_places, validation = get_itinerary(travel_agent, input_query)
            if validation:
                increment_progress_bar(progress_bar, 0, 30, '\nRoute map is loading...')
                itinerary_col.text(itinerary)
                increment_progress_bar(progress_bar, 30, 50, '\nRoute map is loading...')
                router = Router(google_maps_key=api_keys["google_maps_key"])
                directions_result, marker_points = get_directions(router, list_of_places)
                increment_progress_bar(progress_bar, 50, 70, '\nRoute map is loading...')
                route_coords = decode_route(directions_result)
                map_start_loc = [route_coords[0][0], route_coords[0][1]]
                increment_progress_bar(progress_bar, 70, 100, '\nRoute map is loading...')
                time.sleep(0.5)
                progress_bar.empty()
                map = create_map(route_coords, marker_points, map_start_loc)
                with map_col:
                        st_folium(map, width="100%", returned_objects=[])
            else:
                progress_bar.empty()
                map_col.text("Error has occured with google maps api and wasn't able to generate a map.")
        
        except Exception as e:
            map_col.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()