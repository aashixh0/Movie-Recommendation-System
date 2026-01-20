import pickle
import streamlit as st
import requests
from functools import lru_cache

# Page configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
        .movie-card { text-align: center; }
        .movie-title { font-weight: bold; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load movies and similarity data with caching"""
    movies = pickle.load(open('model/movies_improved.pkl','rb'))
    similarity = pickle.load(open('model/similarity_improved.pkl','rb'))
    return movies, similarity

@lru_cache(maxsize=100)
def fetch_poster_and_imdb(movie_id):
    """Fetch movie poster and IMDb ID with error handling"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url, timeout=5)
        data = data.json()
        poster_path = data.get('poster_path')
        imdb_id = data.get('imdb_id')
        poster_url = None
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return poster_url, imdb_id
    except Exception as e:
        return None, None

def recommend(movie):
    """Get 5 movie recommendations based on similarity"""
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_imdb_ids = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster, imdb_id = fetch_poster_and_imdb(movie_id)
        if poster:
            recommended_movie_posters.append(poster)
            recommended_movie_names.append(movies.iloc[i[0]].title)
            recommended_imdb_ids.append(imdb_id)
    
    return recommended_movie_names, recommended_movie_posters, recommended_imdb_ids

# Load data
movies, similarity = load_data()

# Header
st.title("🎬 Movie Recommender System")
st.markdown("Find movies similar to your favorites!")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info("This app recommends movies based on content similarity using machine learning.")

# Main section
col1, col2 = st.columns([2, 1])

with col1:
    selected_movie = st.selectbox(
        "Select a movie you like",
        sorted(movies['title'].values),
        help="Choose a movie to get similar recommendations"
    )

with col2:
    st.write("")
    search_button = st.button("🔍 Get Recommendations", use_container_width=True)

# Display recommendations
if search_button:
    with st.spinner("Finding recommendations..."):
        recommended_movie_names, recommended_movie_posters, recommended_imdb_ids = recommend(selected_movie)
        
        if recommended_movie_names:
            st.markdown("### ⭐ Recommended Movies")
            cols = st.columns(5)
            
            for idx, col in enumerate(cols):
                with col:
                    if idx < len(recommended_movie_posters):
                        st.image(recommended_movie_posters[idx], use_container_width=True)
                        title = recommended_movie_names[idx]
                        imdb_id = recommended_imdb_ids[idx]
                        
                        if imdb_id:
                            imdb_link = f"https://www.imdb.com/title/{imdb_id}/"
                            st.markdown(f"**[{title}]({imdb_link})**", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**{title}**")
        else:
            st.error("Could not fetch recommendations. Please try another movie.")