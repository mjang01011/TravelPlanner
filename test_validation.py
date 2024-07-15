import os
from dotenv import load_dotenv, find_dotenv
from Agent.Agent import Agent

# Load API Keys
load_dotenv(find_dotenv(), override=True)

open_ai_key = os.environ.get("OPENAI_API_KEY")
google_gemini_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
google_maps_key = os.environ.get("GOOGLE_MAPS_API_KEY")

# Testing validation
travel_agent = Agent(open_ai_api_key=open_ai_key, verbose=True)

query_valid = """
  I want to do a 7 day roadtrip from Berlin to Paris.
  I want to visit the famous attractions along the route.
  """
query_invalid = """
  I want to bike from Seoul, South Korea to Tokyo, Japan.
  After I arrive in Tokyo, I want to go to the moon.
    """

travel_agent.validate_travel(query_valid)

# travel_agent.validate_travel(query_invalid)