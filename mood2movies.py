import requests
from bs4 import BeautifulSoup
import re
import time
import streamlit as st

# Emotion keyword dictionary
EMOTION_KEYWORDS = {
    "happy": ["joy", "excited", "glad", "cheerful", "delighted", "content", "thrilled"],
    "sad": ["unhappy", "down", "depressed", "melancholy", "heartbroken", "gloomy"],
    "angry": ["mad", "furious", "annoyed", "frustrated", "outraged"],
    "scared": ["afraid", "fearful", "nervous", "anxious", "terrified"],
    "excited": ["thrilled", "eager", "enthusiastic", "ecstatic"],
}

# Map emotions to IMDb genres
EMOTION_TO_GENRE = {
    "happy": "Comedy",
    "sad": "Drama",
    "angry": "Action",
    "scared": "Horror",
    "excited": "Adventure",
}

# IMDb URL mapping
BASE_URL = "https://www.imdb.com/search/title/?title_type=feature&genres="


def detect_emotion(text):
    """Detects emotion from input text using regex-based keyword matching."""
    text = text.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(re.search(rf'\b{re.escape(word)}\b', text) for word in keywords):
            return emotion
    return None


def fetch_movie_titles(genre):
    """Fetches movie titles from IMDb based on the genre."""
    url = BASE_URL + genre.lower()

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        time.sleep(1.5)  # Respect IMDb's servers
    except requests.RequestException as e:
        return [f"⚠️ Error fetching data: {e}"]

    soup = BeautifulSoup(response.text, "lxml")

    # Extract movie titles
    titles = [h3.a.get_text(strip=True) for h3 in soup.find_all('h3', class_='lister-item-header')]

    if not titles:
        # Alternative extraction if IMDb structure changes
        titles = [
            a.get_text(strip=True) for a in soup.find_all('a', href=re.compile(r'/title/tt\d+/'))
            if len(a.get_text(strip=True)) > 1
        ]

    return titles[:10] if titles else ["⚠️ No recommendations found. IMDb may be blocking requests."]


# Streamlit UI
st.title("🎬 Movie Recommender Based on Your Mood")
st.write("Enter how you're feeling, and we'll recommend movies for you!")

user_input = st.text_input("How are you feeling today?", "")

if st.button("Get Movies"):
    if not user_input:
        st.warning("❌ Please enter how you feel!")
    else:
        detected_emotion = detect_emotion(user_input)

        if not detected_emotion:
            st.error("❌ I couldn't detect your emotion. Try using words like 'happy', 'sad', 'angry', etc.")
        else:
            genre = EMOTION_TO_GENRE.get(detected_emotion)
            st.success(
                f"😊 I detected that you're feeling **{detected_emotion.capitalize()}**. You might enjoy **{genre}** movies!")

            movie_titles = fetch_movie_titles(genre)

            if not movie_titles or "Error" in movie_titles[0]:
                st.error("⚠️ No movie recommendations found. IMDb may be blocking requests.")
            else:
                st.subheader("🎬 Recommended Movies for You:")
                for title in movie_titles:
                    st.write(f"- {title}")
