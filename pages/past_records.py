import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import load_keys, connect_db, update_map
import streamlit as st
from streamlit_folium import st_folium
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import time

def main():
    if 'auth' not in st.session_state or not st.session_state.auth:
        st.markdown("<h1 style='text-align: center;'>You do not have access to this page. Please login to view your past plans. Redirecting to main page.</h1>", unsafe_allow_html=True)
        time.sleep(2)
        st.switch_page("main.py")
    keys = load_keys()
    users_collection = connect_db()
    redirect_main = st.button("Main Page")
    if redirect_main:
        st.switch_page("main.py")
    def fetch_records(username):
        user = users_collection.find_one({"user_id": username})
        queries = user["queries"]
        query_record = []
        for i, query in enumerate(queries):
           query_record.append(query["query"]) 
        selected_query = st.selectbox(
            "Select your past travel plan",
            query_record
        )
        selected_index = query_record.index(selected_query)
        map_col, itinerary_col = st.columns([1,1], gap="small")
        map_col.subheader("Route Map")
        itinerary_col.subheader("Itinerary Details")
        itinerary_col.write(queries[selected_index]["itinerary"])
        with map_col:
            st_folium(update_map(queries[selected_index]["list_of_places"], keys["google_maps_key"]), width="100%", returned_objects=[], key=f"map_folium_{selected_index}")
        ## For 'view all', need to reduce gap between groups
        # for i, query in enumerate(queries):
        #     map_col, itinerary_col = st.columns([1,1], gap="small")
        #     map_col.subheader("Route Map")
        #     itinerary_col.subheader("Itinerary Details")
        #     itinerary_col.write(query["itinerary"])
        #     with map_col:
        #         st_folium(update_map(query["list_of_places"], keys["google_maps_key"]), width="100%", returned_objects=[], key=f"map_folium_{i}")
        #     st.divider()

    fetch_records(st.session_state.username)

if __name__ == "__main__":
    main()