import streamlit as st
import requests

# --- Page Configuration & Styling ---
st.set_page_config(
    page_title="SonicFetch | YouTube to MP3",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stTextInput > div > div > input {
        border-radius: 8px;
        background-color: #1E222D;
        color: #FFFFFF;
        border: 1px solid #363B4E;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #FF0000;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #CC0000; }
    </style>
""", unsafe_allow_html=True)

# --- UI Header ---
st.title("🎵 SonicFetch MP3 Studio")
st.caption("100% Cloud-Bypass YouTube to MP3 converter")
st.divider()

url_input = st.text_input("Paste YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🚀 Process & Prepare MP3"):
    if not url_input:
        st.warning("Please enter a URL first.")
    else:
        with st.spinner("Bypassing YouTube blocks & fetching audio..."):
            try:
                # We use the open-source Cobalt API to bypass Streamlit Cloud IP blocks
                api_url = "https://api.cobalt.tools/"
                
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                
                # Cobalt v7 API Payload for MP3
                payload = {
                    "url": url_input,
                    "downloadMode": "audio",
                    "audioFormat": "mp3",
                    "filenamePattern": "pretty"
                }
                
                # 1. Ask the API to extract the direct MP3 link
                api_res = requests.post(api_url, json=payload, headers=headers)
                
                if api_res.status_code == 200:
                    data = api_res.json()
                    direct_mp3_url = data.get("url")
                    
                    if direct_mp3_url:
                        st.success("Extraction successful! Preparing your download...")
                        
                        # 2. Download the MP3 file bytes directly into Streamlit
                        audio_res = requests.get(direct_mp3_url)
                        
                        if audio_res.status_code == 200:
                            st.audio(audio_res.content, format="audio/mp3")
                            
                            st.download_button(
                                label="💾 Save MP3 File to Device",
                                data=audio_res.content,
                                file_name="SonicFetch_Audio.mp3",
                                mime="audio/mpeg"
                            )
                        else:
                            st.error("Failed to retrieve the final MP3 file from the server.")
                    else:
                        st.error("The API couldn't generate a download link. Try another video.")
                else:
                    st.error(f"YouTube blocked the proxy server (Error {api_res.status_code}). Please try again later.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
