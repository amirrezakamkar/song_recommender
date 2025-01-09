import streamlit as st
import pandas as pd
import joblib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load the KMeans model and the scaler
kmeans_model = joblib.load('../Model/kmeans_model.pkl')
scaler = joblib.load('../Scaler/scaler.pkl')

# Load your song dataset
df = pd.read_csv('../data/names_genres_clustered.csv')

# Function to prepare song data for prediction
def prepare_song_data(song_info):
    genre_columns = ['is_rock', 'is_pop', 'is_jazz', 'is_electronic', 'is_classical', 'is_blues', 'is_indie']
    for genre in genre_columns:
        if genre not in song_info:
            song_info[genre] = 0
    
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
        'is_rock', 'is_pop', 'is_jazz', 'is_electronic', 'is_classical', 'is_blues', 'is_indie'
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
    genre_columns = ['is_rock', 'is_pop', 'is_jazz', 'is_electronic', 'is_classical', 'is_blues', 'is_indie']
    for genre in genre_columns:
        if genre not in song_info:
            song_info[genre] = 0

    # Prepare song data
    song_data = prepare_song_data(song_info)
    cluster = kmeans_model.predict(song_data)[0]

    # Get similar songs from the same cluster
    similar_songs = df[df['cluster'] == cluster]
    similar_songs = similar_songs.sort_values(by='popularity', ascending=False)
    similar_songs = similar_songs[similar_songs['spotify_title'] != song_info['spotify_title']]
    top_similar_songs = similar_songs.head(num_suggestions)

    return top_similar_songs

# Streamlit App
st.title("Music Recommendation App")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Search", "Song Selection", "Recommendations"])

if page == "Search":
    st.header("Search for a Song")
    song_title = st.text_input("Enter the song title you like:")
    artist_name = st.text_input("Enter the artist name of the song:")

    if st.button("Search"):
        if song_title and artist_name:
            search_results = search_song_on_spotify(song_title, artist_name)
            if search_results:
                st.session_state['search_results'] = search_results
                st.success("Songs found! Go to 'Song Selection' page to choose.")
            else:
                st.error("No songs found. Try again.")
        else:
            st.error("Please enter both song title and artist name.")

if page == "Song Selection":
    st.header("Select Your Desired Song")
    if 'search_results' in st.session_state:
        for i, result in enumerate(st.session_state['search_results']):
            st.image(result['image_url'], width=200)
            st.write(f"**{result['title']}** by **{result['artist']}**")
            if st.button(f"Select Song {i+1}", key=f"select_{i}"):
                st.session_state['selected_song'] = result
                st.success("Song selected! Go to 'Recommendations' page.")
    else:
        st.warning("No search results found. Go to 'Search' page to search for songs.")

if page == "Recommendations":
    st.header("Recommended Songs")
    if 'selected_song' in st.session_state:
        selected_song = st.session_state['selected_song']
        st.image(selected_song['image_url'], width=200)
        st.write(f"**Selected Song:** {selected_song['title']} by {selected_song['artist']}")

        # Prepare song info
        track_data = selected_song['track_data']
        song_info = {
            'spotify_title': track_data['name'],
            'spotify_artist': track_data['artists'][0]['name'],
            'release_date': track_data['album']['release_date'][:4],  # Only the year
            'popularity': track_data['popularity'],
            'duration_ms': track_data['duration_ms'],
            'explicit': track_data['explicit'],
            'is_rock': 0,
            'is_pop': 0,
            'is_jazz': 0,
            'is_electronic': 0,
            'is_classical': 0,
            'is_blues': 0,
            'is_indie': 0
        }

        # Get genres for the selected song
        artist_id = track_data['artists'][0]['id']
        artist_info = sp.artist(artist_id)
        genres = artist_info.get('genres', [])
        genre_keywords = ['rock', 'pop', 'jazz', 'electronic', 'classical', 'blues', 'indie']
        for genre in genres:
            for keyword in genre_keywords:
                if keyword.lower() in genre.lower():
                    song_info[f'is_{keyword}'] = 1

        # Get recommendations
        recommended_songs = suggest_similar_songs(song_info, df, num_suggestions=10)
        for _, row in recommended_songs.iterrows():
            st.write(f"**{row['spotify_title']}** by **{row['spotify_artist']}** (Popularity: {row['popularity']})")
            track_search = sp.search(q=f"track:{row['spotify_title']} artist:{row['spotify_artist']}", type='track', limit=1)
            if track_search['tracks']['items']:
                track = track_search['tracks']['items'][0]
                st.image(track['album']['images'][0]['url'], width=100)
                st.markdown(f"[Listen on Spotify]({track['external_urls']['spotify']})")
    else:
        st.warning("No song selected. Go to 'Song Selection' page to choose a song.")
