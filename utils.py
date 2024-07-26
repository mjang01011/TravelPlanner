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
import openai
import requests
import google.generativeai as genai

def load_keys():
    load_dotenv(find_dotenv(), override=True)
    return {
        "open_ai_key": os.environ.get("OPENAI_API_KEY"),
        "google_gemini_key": os.environ.get("GEMINI_API_KEY"),
        "google_maps_key": os.environ.get("GOOGLE_MAPS_API_KEY"),
        "mongo_uri": os.environ.get("MONGO_URI")
    }


def validate_openai_api_key(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True
    
def validate_gemini_api_key(api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")
    try:
        model.generate_content("Hello World")
    except:
        return False
    else:
        return True
    
def validate_google_maps_key(api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address=New+York&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'OK':
            return True
        else:
            return False
    else:
        return False

def validate_mongo_uri(mongo_uri):
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
    except Exception as e:
        return False
    return client

def verification_spinner():
    with st.spinner('Verifying keys...'):
        keys = load_keys()
        openai_message = st.empty()
        gemini_message = st.empty()
        google_maps_message = st.empty()
        mongo_message = st.empty()
        validation_results = {"openai": True, "gemini": True, "google_maps": True, "mongo_uri": True}

        if validate_openai_api_key(keys["open_ai_key"]):
            openai_message.success("OpenAI API Key is valid.")
        else:
            openai_message.warning("OpenAI API Key is not valid.")
            validation_results["openai"] = False

        if validate_gemini_api_key(keys["google_gemini_key"]):
            gemini_message.success("Gemini API Key is valid.")
        else:
            gemini_message.warning("Gemini API Key is not valid.")
            validation_results["gemini"] = False

        if validate_google_maps_key(keys["google_maps_key"]):
            google_maps_message.success("Google Maps API Key is valid.")
        else:
            google_maps_message.warning("Google Maps API Key is not valid.")
            validation_results["google_maps"] = False

        if validate_mongo_uri(keys["mongo_uri"]):
            mongo_message.success("Mongo URI is valid.")
        else:
            mongo_message.warning("Mongo URI is not valid.")
            validation_results["mongo_uri"] = False
        time.sleep(1)

    openai_message.empty()
    gemini_message.empty()
    google_maps_message.empty()
    mongo_message.empty()
    if (validation_results["openai"] or validation_results["gemini"]) and validation_results["google_maps"] and validation_results["mongo_uri"]:
        return True
    if not validation_results["openai"] and not validation_results["gemini"]:
        st.warning("You must provide at least one valid API key for either OpenAI or Gemini.")
    if not validation_results["google_maps"]:
        st.warning("You must provide a valid API key for Google Maps.")
    if not validation_results["mongo_uri"]:
        st.warning("You must provide a valid key for mongo_uri.")
    return False

def connect_db():
    client = validate_mongo_uri(load_keys()["mongo_uri"])
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
    directions_result, marker_points = router.make_markers(list_of_places)
    route_coords = decode_route(directions_result)
    if route_coords == None:
        return st.warning("Error has occured with google maps API. Please try again.")
    map_start_loc = [route_coords[0][0], route_coords[0][1]]
    map = create_map(route_coords, marker_points, map_start_loc)
    return map