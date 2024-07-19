import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import connect_db, display_message
import streamlit as st
import time
from datetime import datetime, timezone

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
        username_exists = users_collection.find_one({"user_id": username})
        if username_exists:
            st.error("Username already exists.")
        else:
            user_data = {
                "user_id": username,
                "password": password,
                "email": email,
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
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