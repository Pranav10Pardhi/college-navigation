import streamlit as st
import folium
import networkx as nx
from geopy.distance import geodesic
import os
from streamlit_folium import folium_static
import qrcode
import cv2

# Set page configuration
st.set_page_config(
    page_title="College Navigation Assistant",
    page_icon="🎓",
    layout="wide"
)

# College locations with coordinates remain the same
COLLEGE_LOCATIONS = {
    "Main Gate": {"lat":  23.520872, "lon": 77.819182, "type": "entrance"},
    "Library": {"lat": 23.521052, "lon": 77.820847, "type": "academic"},
    "Ksh": {"lat":  23.517608, "lon":  77.820086, "type": "facility"},
    "Cricket Ground": {"lat": 23.517186, "lon": 77.818474, "type": "academic"},
    "Computer Science Block": {"lat": 23.520910, "lon": 77.820373, "type": "academic"},
    "Polytechnic": {"lat": 23.519144, "lon": 77.820320, "type": "residence"},
    "Canteen": {"lat": 23.519005, "lon": 77.819553, "type": "facility"}
}

# Video paths remain the same    "videos/main.mp4"
ROUTE_VIDEOS = {
    ("Main Gate", "Library"): "videos/main.mp4",
    ("Main Gate", "KSH"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos",
    ("Main Gate", "Cricket Ground"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos",
    ("Main Gate", "Computer Science Block"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos",
    ("Main Gate", "Polytechnic"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos",
    ("Main Gate", "Canteen"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos",
    ("Library", "Cafeteria"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos",
    ("Library", "Auditorium"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos",
    ("Cafeteria", "Hostel A"): "https://github.com/Pranav10Pardhi/college-navigation/tree/main/videos"
}

# Keep all other functions the same except remove speech-related ones
def create_navigation_graph():
    G = nx.Graph()
    for location, coords in COLLEGE_LOCATIONS.items():
        G.add_node(location, pos=(coords["lat"], coords["lon"]))
    
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
    lats = [loc["lat"] for loc in COLLEGE_LOCATIONS.values()]
    lons = [loc["lon"] for loc in COLLEGE_LOCATIONS.values()]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=18)
    
    for name, coords in COLLEGE_LOCATIONS.items():
        folium.Marker(
            [coords["lat"], coords["lon"]],
            popup=name,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    return m

try:
    import speech_recognition as sr
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

def get_route_video(start, end):
    if (start, end) in ROUTE_VIDEOS:
        return ROUTE_VIDEOS[(start, end)]
    elif (end, start) in ROUTE_VIDEOS:
        return ROUTE_VIDEOS[(end, start)]
    return None

def test_video(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        ret = cap.isOpened()
        cap.release()
        return ret
    except:
        return False
def generate_qr_code():
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    # Use current app URL or default to your college website
    website_url = "https://www.satiengg.in/"  #actual website
    qr.add_data(website_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(os.path.dirname(__file__), "app_qr.png")
    img.save(qr_path)
    return qr_path
    if st.sidebar.button("Generate QR Code"):
        qr_image = generate_qr_code()
        st.sidebar.image(qr_image, caption="Scan to access website")
        st.sidebar.markdown("[Visit Website](https://www.satiengg.in/)")  # Replace URL here too    

def main():
    st.title("🎓 College Navigation Assistant")
    
    G = create_navigation_graph()
    
    st.sidebar.title("Navigation Options")
    start_point = st.sidebar.selectbox("Select Start Point", list(COLLEGE_LOCATIONS.keys()))
    end_point = st.sidebar.selectbox("Select Destination", list(COLLEGE_LOCATIONS.keys()))
    
    if st.sidebar.button("Find Route"):
        try:
            path = nx.shortest_path(G, start_point, end_point, weight='weight')
            
            m = create_map()
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
                directions = f"Route from {start_point} to {end_point}: " + " → ".join(path)
                st.write(directions)
            
            with col2:
                video_path = get_route_video(start_point, end_point)
                if video_path and test_video(video_path):
                    st.subheader("Route Video Guide")
                    st.video(video_path)
                else:
                    st.info("Video guide not available for this route")
            
        except nx.NetworkXNoPath:
            st.error("No path found between selected locations.")
    
    if st.sidebar.button("Generate QR Code"):
        qr_image = generate_qr_code()
        st.sidebar.image(qr_image, caption="Scan to open app")

if __name__ == "__main__":
    main()
