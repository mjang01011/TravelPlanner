import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import connect_db
import streamlit as st
import time


def main():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    if "auth" in st.session_state and st.session_state.auth:
        st.markdown("<h1 style='text-align: center;'>You are already logged in. Redirecting to main page.</h1>", unsafe_allow_html=True)
        time.sleep(2)
        st.switch_page("main.py")
    users_collection = connect_db()
    
    def authenticate_user(username, password):
        user = users_collection.find_one({"username": username})
        if user and password == user["password"]:
            return user["uid"]
        return None

    st.title("Login to TravelPlanner")
    redirect_main = st.button("Main Page")
    if redirect_main:
        st.switch_page("main.py")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            uid = authenticate_user(username, password)
            if uid:
                st.session_state.auth = True
                st.session_state.uid = uid
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter username and password")
    
    if "auth" in st.session_state and st.session_state.auth:
        st.switch_page("main.py")
    st.text("Do not have an account yet?")
    if st.button("Signup"):
        st.switch_page("pages/signup.py")
        
if __name__ == "__main__":
    main()