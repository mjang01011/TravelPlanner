from utils import load_keys, create_travel_agent, increment_progress_bar, get_itinerary, get_directions, decode_route, create_map
from Router.Router import Router
import streamlit as st
from streamlit_folium import st_folium
import time
import pymongo
import hashlib
from pymongo import MongoClient
from pymongo.server_api import ServerApi


def main():
    client = MongoClient(load_keys()["mongo_uri"], server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = client["TravelPlanner"]
    users_collection = db["users"]
    
    def authenticate_user(username, password):
        user = users_collection.find_one({"user_id": username})
        # if user:
        #     hashed_password = hashlib.sha256(password.encode()).hexdigest()
        #     if hashed_password == user["password_hash"]:
        #         return user
        if user and password == user["password"]:
            return user
        return None

    st.set_page_config(layout="wide")
    st.title("Login to TravelPlanner")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = user
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter username and password")
    
    if "user" in st.session_state:
        st.switch_page("pages/test_strealit_main.py")

if __name__ == "__main__":
    main()