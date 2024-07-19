import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import load_keys, connect_db, update_map
import streamlit as st
from streamlit_folium import st_folium
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
    def fetch_records(uid):
        user = users_collection.find_one({"uid": uid})
        queries = user["queries"]
        if queries is None:
            st.text("You do not have any logged travel plans.")
            return
        query_record = []
        query_qid = []
        for query in queries:
           query_record.append(query["query"]) 
           query_qid.append(query["qid"])
        selected_index = st.selectbox(
            "Select your past travel plan",
            range(len(query_record)),
            format_func=lambda x: query_record[x]
        )
        print(selected_index)
        if st.button("Delete"):
            @st.experimental_dialog("Are you sure you want to delete?")
            def confirm_deletion():
                if st.button("Yes"):
                    users_collection.update_one({"uid": uid}, { "$pull": {"queries": {"qid": query_qid[selected_index]}} })
                    st.success("Successfully deleted your plan.")
                    time.sleep(2)
                    st.rerun()
            confirm_deletion()
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
    fetch_records(st.session_state.uid)

if __name__ == "__main__":
    main()