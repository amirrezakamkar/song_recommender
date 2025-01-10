import streamlit as st
import pandas as pd
import joblib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load the KMeans model and the scaler
kmeans_model = joblib.load('../Model/kmeans_model_9.pkl')
scaler = joblib.load('../Scaler/scaler.pkl')

# Load your song dataset
df = pd.read_csv('../data/names_genres_clustered.csv')

# Initialize session state for smoother navigation
if 'page' not in st.session_state:
    st.session_state['page'] = "Search"
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None
if 'selected_song' not in st.session_state:
    st.session_state['selected_song'] = None
if 'show_sidebar' not in st.session_state:
    st.session_state['show_sidebar'] = False

# Set a background image
def set_background(image_file):
    """
    Set the background image for the Streamlit app.
    :param image_file: Path to the image file
    """
    with open(image_file, "rb") as image:
        b64_image = base64.b64encode(image.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background: url("data:image/jpg;base64,{b64_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Add the background image
set_background("../app/Untitled-1.jpg") 

def get_song_genres(track_data):
    """Get genre information for a song from Spotify"""
    artist_id = track_data['artists'][0]['id']
    artist_info = sp.artist(artist_id)
    genres = artist_info.get('genres', [])
    
    genre_flags = {
        'is_rock': 0, 'is_pop': 0, 'is_jazz': 0, 
        'is_electronic': 0, 'is_classical': 0, 
        'is_blues': 0, 'is_indie': 0
    }
    
    genre_keywords = ['rock', 'pop', 'jazz', 'electronic', 'classical', 'blues', 'indie']
    for genre in genres:
        for keyword in genre_keywords:
            if keyword.lower() in genre.lower():
                genre_flags[f'is_{keyword}'] = 1
    
    return genre_flags

def create_song_info(track_data):
    """Create a standardized song info dictionary with genres"""
    # Basic song info
    song_info = {
        'spotify_title': track_data['name'],
        'spotify_artist': track_data['artists'][0]['name'],
        'release_date': track_data['album']['release_date'][:4],
        'popularity': track_data['popularity'],
        'duration_ms': track_data['duration_ms'],
        'explicit': track_data['explicit']
    }
    
    # Add genre information
    genre_flags = get_song_genres(track_data)
    song_info.update(genre_flags)
    
    return song_info

def prepare_song_data(song_info):
    """Prepare and scale song data for model prediction"""
    song_data = pd.DataFrame([[
        song_info['release_date'],
        song_info['popularity'],
        song_info['duration_ms'],
        song_info['explicit'],
        song_info['is_rock'],
        song_info['is_pop'],
        song_info['is_jazz'],
        song_info['is_electronic'],
        song_info['is_classical'],
        song_info['is_blues'],
        song_info['is_indie']
    ]], columns=[
        'release_date', 'popularity', 'duration_ms', 'explicit', 
        'is_rock', 'is_pop', 'is_jazz', 'is_electronic', 
        'is_classical', 'is_blues', 'is_indie'
    ])
    
    scaled_song_data = scaler.transform(song_data)
    return scaled_song_data

# Function to search for songs using Spotify API
def search_song_on_spotify(song_title, artist_name):
    results = sp.search(q=f"track:{song_title} artist:{artist_name}", type='track', limit=5)
    songs = []
    if results['tracks']['items']:
        for track in results['tracks']['items']:
            song_info = {
                'title': track['name'],
                'artist': track['artists'][0]['name'],
                'image_url': track['album']['images'][0]['url'],
                'spotify_url': track['external_urls']['spotify'],
                'track_data': track
            }
            songs.append(song_info)
    return songs

# Function to suggest similar songs
def suggest_similar_songs(song_info, df, num_suggestions=10):
    """Find similar songs based on song features"""
    # Prepare song data with genres already included
    song_data = prepare_song_data(song_info)
    cluster = kmeans_model.predict(song_data)[0]

    # Get similar songs from the same cluster
    similar_songs = df[df['cluster'] == cluster]
    similar_songs = similar_songs.sort_values(by='popularity', ascending=False)
    similar_songs = similar_songs[similar_songs['spotify_title'] != song_info['spotify_title']]
    return similar_songs.head(num_suggestions)

# Add a toggle button in the main content area
if st.button("☰ Navigate"):
    st.session_state['show_sidebar'] = not st.session_state['show_sidebar']

# Sidebar for manual navigation (only shown when toggled)
if st.session_state['show_sidebar']:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: rgba(0,0,0,0.3);
            backdrop-filter: blur(3px);
        }
        [data-testid="stSidebar"] > div:first-child {
            background-color: transparent;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: white;
        }
        [data-testid="stSidebar"] .stTitle {
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("Navigation")
    menu_page = st.sidebar.radio("Go to", ["Search", "Song Selection", "Recommendations"], 
                                key="navigation", 
                                index=["Search", "Song Selection", "Recommendations"].index(st.session_state['page']))
    if menu_page != st.session_state['page']:
        st.session_state['page'] = menu_page

# Page: Search
if st.session_state['page'] == "Search":
    st.title("Search for a Song")
    song_title = st.text_input("Enter the song title you like:")
    artist_name = st.text_input("Enter the artist name of the song:")

    if st.button("Search"):
        if song_title and artist_name:
            search_results = search_song_on_spotify(song_title, artist_name)
            if search_results:
                st.session_state['search_results'] = search_results
                st.session_state['page'] = "Song Selection"  # Automatically move to next page
            else:
                st.error("No songs found. Try again.")
        else:
            st.error("Please enter both song title and artist name.")

# Page: Song Selection
if st.session_state['page'] == "Song Selection":
    st.title("Select Your Desired Song")
    if st.session_state['search_results']:
        for i, result in enumerate(st.session_state['search_results']):
            st.image(result['image_url'], width=200)
            st.write(f"**{result['title']}** by **{result['artist']}**")
            if st.button(f"Select Song {i+1}", key=f"select_{i}"):
                st.session_state['selected_song'] = result
                st.session_state['page'] = "Recommendations"
                st.rerun()  # Automatically move to next page
    else:
        st.warning("No search results found. Go to 'Search' page to search for songs.")

# Page: Recommendations
if st.session_state['page'] == "Recommendations":
    st.title("Recommended Songs")
    if st.session_state['selected_song']:
        selected_song = st.session_state['selected_song']
        st.image(selected_song['image_url'], width=200)
        st.write(f"**Selected Song:** {selected_song['title']} by {selected_song['artist']}")

        # Create song info with genres included
        track_data = selected_song['track_data']
        song_info = create_song_info(track_data)

        # Get recommendations using the complete song info
        recommended_songs = suggest_similar_songs(song_info, df, num_suggestions=10)
        
        # Display recommendations
        for _, row in recommended_songs.iterrows():
            st.write(f"**{row['spotify_title']}** by **{row['spotify_artist']}** (Popularity: {row['popularity']})")
            track_search = sp.search(q=f"track:{row['spotify_title']} artist:{row['spotify_artist']}", type='track', limit=1)
            if track_search['tracks']['items']:
                track = track_search['tracks']['items'][0]
                st.image(track['album']['images'][0]['url'], width=100)
                st.markdown(f"[Listen on Spotify]({track['external_urls']['spotify']})")
    else:
        st.warning("No song selected. Go to 'Song Selection' page to choose a song.")
