import os
import glob
import tempfile
import streamlit as st
import yt_dlp

# --- Page Configuration & Styling ---
st.set_page_config(
    page_title="SonicFetch | YouTube to MP3",
    page_icon="🎵",
    layout="centered"
)

# Custom CSS
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


def get_video_info(url):
    """Fetch video metadata bypassing datacenter IP restrictions."""
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'tv', 'android_vr', 'web'],
                'skip': ['dash', 'hls']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def download_mp3(url, target_dir, size_limit_mb=300):
    """Download audio stream using robust cloud-friendly clients."""
    
    ydl_opts = {
        'format': 'ba/ba*', # Best audio fallback
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'mweb', 'android_vr'],
                'player_skip': ['js'],
            }
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(target_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'add_header': [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        filesize = info.get('filesize') or info.get('filesize_approx') or 0
        size_mb = filesize / (1024 * 1024)

        if size_mb > size_limit_mb:
            raise ValueError(f"File size (~{size_mb:.1f} MB) exceeds maximum allowed limit ({size_limit_mb} MB).")

        ydl.download([url])

    # Find created MP3 file path
    downloaded_files = glob.glob(os.path.join(target_dir, "*.mp3"))
    if not downloaded_files:
        raise FileNotFoundError("Conversion failed. Could not locate output MP3.")
    
    return downloaded_files[0]


# --- UI Header ---
st.title("🎵 SonicFetch MP3 Studio")
st.caption("Fast, unrestricted YouTube to MP3 audio converter (Max single file limit: 300 MB)")
st.divider()

# --- Input Area ---
url_input = st.text_input("Paste YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if url_input:
    try:
        with st.spinner("Fetching audio metadata..."):
            info = get_video_info(url_input)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(info.get('thumbnail'), use_container_width=True)
        with col2:
            st.markdown(f"### {info.get('title')}")
            st.text(f"Channel: {info.get('uploader')}")
            
            duration_sec = info.get('duration', 0)
            mins, secs = divmod(duration_sec, 60)
            st.text(f"Duration: {mins:02d}:{secs:02d}")

        st.divider()

        # Download Trigger
        if st.button("🚀 Process & Prepare MP3"):
            with tempfile.TemporaryDirectory() as temp_dir:
                with st.spinner("Extracting high-bitrate audio & encoding to MP3..."):
                    filepath = download_mp3(url_input, temp_dir, size_limit_mb=300)
                    
                    filename = os.path.basename(filepath)
                    with open(filepath, "rb") as f:
                        file_bytes = f.read()

                st.success("Extraction complete!")
                
                # Native browser audio preview
                st.audio(file_bytes, format="audio/mp3")
                
                # Direct Streamlit Download Button
                st.download_button(
                    label="💾 Save MP3 File to Device",
                    data=file_bytes,
                    file_name=filename,
                    mime="audio/mpeg"
                )

    except ValueError as ve:
        st.warning(str(ve))
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
