# TravelPlanner

TravelPlanner is a travel itinerary suggestion application designed to leverage large language models, Google Maps, LangChain, and MongoDB to provide users with AI-powered travel plans. This application offers a sleek, user-friendly interface powered by Streamlit, making it easy for users to input their travel queries and receive tailored itineraries and routes. The platform supports GPT-3.5, GPT-4, and Gemini 1.5 for generating travel plans and includes robust features for user authentication, data storage, and dynamic map interactions.

## Features

- **Itinerary Suggestion:** Provides optimized travel itineraries based on user input, including stops, transportation modes, and additional suggestions to enhance travel plans.
- **Dynamic Map Visualization:** Utilizes Folium and Google Maps to dynamically display the recommended itinerary and travel plans, allowing users to see changes in their schedules interactively.
- **User Authentication:** Implements login/signup functionality using MongoDB, enabling users to archive and view past travel plans.
- **Travel Query Validation:** Validates user travel queries using LangChain to ensure they are feasible and provides additional suggestions for improvement.
- **Interactive Itinerary Updates:** Allows users to select on additional suggested places to dynamically update the travel plan and map.
- **Language Model Integration:** Supports multiple LLM models (GPT-3.5, GPT-4, Gemini 1.5) for generating travel plans, allowing users to choose their preferred model.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/TravelPlanner.git
    cd TravelPlanner
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **Set up API Keys:**
    - Create a `.env` file in the root directory.
    - Add your API keys for OpenAI, Google Maps, and MongoDB in the following format:

    ```dotenv
    OPENAI_API_KEY=your_openai_api_key
    GEMINI_API_KEY=your_gemini_api_key
    GOOGLE_MAPS_API_KEY=your_google_maps_api_key
    MONGO_URI=your_mongo_uri
    ```

## Usage

1. **Run the application:**

    ```bash
    streamlit run main.py
    ```

2. **Interact with the application:**
    - Login or sign up to access your personalized travel plans.
    - Input your travel query and select your preferred language model.
    - View and interact with the dynamically generated itinerary and map.
    - Archive and review past travel plans.

## TODO

1. Code commenting and logic cleanup.