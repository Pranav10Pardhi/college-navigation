import streamlit as st
import os

st.set_page_config(page_title="Video Player", layout="wide")

st.title("College Navigation Video Guide")

video_path = r"c:\Users\HP\Desktop\py\mejor Project_directory\videos\main_to_library.mp4"

if os.path.exists(video_path):
    # Display file info
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # Convert to MB
    st.info(f" file size: {file_size:.2f} MB")
    
    # Create a container for the video
    with st.container():
        st.subheader("Route: Main Gate to Library")
        st.video(video_path)
        st.success("Video loaded successfully!")
else:
    st.error(f"map location: {video_path}")
    st.info("Please make sure you have created the file first.")