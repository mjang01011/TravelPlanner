TODO:
1) Refactor Mapper
2) Fix googlemaps search from coords to id
3) Add UI for streamlit
4) Add DB for user (id, password, prev_plans)

# TravelPlanner

TravelPlanner is a travel itinerary plan suggestion application that leverages LangChain, OpenAI for AI-powered suggestions, and Google APIs for map routing and directions. The application provides a simple user interface generated with Streamlit, making it easy for users to input their travel plans and receive suggested itineraries and routes.

## Features

- **Itinerary Suggestion:** Based on user input, the application suggests optimized travel itineraries including stops and transportation modes.
- **Integration with APIs:** Utilizes LangChain for natural language understanding, OpenAI for generating travel suggestions, and Google APIs for route planning and map display.
- **User Interface with Streamlit:** Offers a straightforward web-based interface for users to interact with the application and view their travel plans visually.

## Installation

1. **Clone the repository:**

2. **Install dependencies:**

## Configuration

1. **Set up API Keys:**
- Create a `.env` file in the root directory.
- Add your API keys for OpenAI, Google Gemini, and Google Maps in the following format:
  ```
  OPENAI_API_KEY=your_openai_api_key
  GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
  GOOGLE_MAPS_API_KEY=your_google_maps_api_key
  ```
