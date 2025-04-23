import streamlit as st
import folium
from folium import plugins
import networkx as nx
from geopy.distance import geodesic
import speech_recognition as sr
from gtts import gTTS
import json
import os
from streamlit_folium import folium_static
import qrcode
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="College Navigation Assistant",
    page_icon="🎓",
    layout="wide"
)

# Sample college locations (replace with your college's coordinates)
COLLEGE_LOCATIONS = {
    "Main Gate": {"lat": 28.7041, "lon": 77.1025, "type": "entrance"},
    "Library": {"lat": 28.7043, "lon": 77.1027, "type": "academic"},
    "Cafeteria": {"lat": 28.7044, "lon": 77.1026, "type": "facility"},
    "Auditorium": {"lat": 28.7042, "lon": 77.1028, "type": "facility"},
    "Hostel A": {"lat": 28.7045, "lon": 77.1029, "type": "residence"}
}
ROUTE_VIDEOS = {
    ("Main Gate", "Library"): r"c:\Users\HP\Desktop\py\mejor Project_directory\videos\main_to_library.mp4",
    ("Main Gate", "Cafeteria"): r"c:\Users\HP\Desktop\py\mejor Project_directory\videos\main_to_cafeteria.mp4",
    ("Library", "Cafeteria"): r"c:\Users\HP\Desktop\py\mejor Project_directory\videos\library_to_cafeteria.mp4",
    ("Library", "Auditorium"): r"c:\Users\HP\Desktop\py\mejor Project_directory\videos\library_to_auditorium.mp4",
    ("Cafeteria", "Hostel A"): r"c:\Users\HP\Desktop\py\mejor Project_directory\videos\cafeteria_to_hostel.mp4",
}

def create_navigation_graph():
    G = nx.Graph()
    
    # Add nodes
    for location, coords in COLLEGE_LOCATIONS.items():
        G.add_node(location, pos=(coords["lat"], coords["lon"]))
    
    # Add edges (connections between locations)
    for loc1 in COLLEGE_LOCATIONS:
        for loc2 in COLLEGE_LOCATIONS:
            if loc1 != loc2:
                dist = geodesic(
                    (COLLEGE_LOCATIONS[loc1]["lat"], COLLEGE_LOCATIONS[loc1]["lon"]),
                    (COLLEGE_LOCATIONS[loc2]["lat"], COLLEGE_LOCATIONS[loc2]["lon"])
                ).meters
                G.add_edge(loc1, loc2, weight=dist)
    
    return G

def create_map():
    # Calculate center of the map
    lats = [loc["lat"] for loc in COLLEGE_LOCATIONS.values()]
    lons = [loc["lon"] for loc in COLLEGE_LOCATIONS.values()]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=18)
    
    # Add markers for each location
    for name, coords in COLLEGE_LOCATIONS.items():
        folium.Marker(
            [coords["lat"], coords["lon"]],
            popup=name,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    return m
def get_route_video(start, end):
    video_path = None
    if (start, end) in ROUTE_VIDEOS:
        video_path = ROUTE_VIDEOS[(start, end)]
    elif (end, start) in ROUTE_VIDEOS:
        video_path = ROUTE_VIDEOS[(end, start)]
    
    if video_path and os.path.exists(video_path):
        return video_path
    return None

def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return text
        except:
            return None

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    return "response.mp3"

def generate_qr_code():
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(st.experimental_get_query_params().get("url", [""])[0])
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("app_qr.png")
    return "app_qr.png"

def main():
    st.title("🎓 College Navigation Assistant")
    
    # Initialize navigation graph
    G = create_navigation_graph()
    
    # Create sidebar for navigation options
    st.sidebar.title("Navigation Options")
    start_point = st.sidebar.selectbox("Select Start Point", list(COLLEGE_LOCATIONS.keys()))
    end_point = st.sidebar.selectbox("Select Destination", list(COLLEGE_LOCATIONS.keys()))
    
    # Voice input button
    if st.sidebar.button("🎤 Use Voice Input"):
        voice_text = get_voice_input()
        if voice_text:
            st.sidebar.write(f"You said: {voice_text}")
    
    # Calculate and display route
    if st.sidebar.button("Find Route"):
        try:
            path = nx.shortest_path(G, start_point, end_point, weight='weight')
            
            # Create map with route
            m = create_map()
            
            # Add path to map
            path_coords = [[COLLEGE_LOCATIONS[loc]["lat"], COLLEGE_LOCATIONS[loc]["lon"]] 
                         for loc in path]
            folium.PolyLine(
                path_coords,
                weight=2,
                color='blue',
                opacity=0.8
            ).add_to(m)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Route Map")
                folium_static(m)
                
                # Generate directions
                directions = f"Route from {start_point} to {end_point}: " + " → ".join(path)
                st.write(directions)
                
                # Convert directions to speech
                audio_file = text_to_speech(directions)
                st.audio(audio_file)
            
            with col2:
                # Display route video if available
                video_path = get_route_video(start_point, end_point)
                if video_path and os.path.exists(video_path):
                    st.subheader("Route Video Guide")
                    st.video(video_path)
                else:
                    st.info("Video guide not available for this route")
            
        except nx.NetworkXNoPath:
            st.error("No path found between selected locations.")

if __name__ == "__main__":
    main()                                                                 
                                                                          
