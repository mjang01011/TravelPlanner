import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import connect_db, display_message
import streamlit as st
import time
import uuid
from bson.binary import Binary

st.title("Signup to TravelPlanner")
users_collection = connect_db()
redirect_main = st.button("Main Page")
if redirect_main:
    st.switch_page("main.py")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
email = st.text_input("Email")

if st.button("Create Account"):
    if username and password:
        username_exists = users_collection.find_one({"username": username})
        if username_exists:
            st.error("Username already exists.")
        else:
            user_data = {
                "uid": Binary(uuid.uuid4().bytes, 4),
                "username": username,
                "password": password,
                "email": email,
                "queries": []
            }
            try:
                users_collection.insert_one(user_data)
                display_message("Success!", "Your account has been created. Redirecting to login page.")
                time.sleep(2)
                st.switch_page("pages/login.py")
            except Exception as e:
                display_message("Failed!", "An error occurred with creating your account. Please try again.")
    else:
        st.warning("Please enter username and password")