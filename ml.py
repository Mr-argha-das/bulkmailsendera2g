import pandas as pd
import spacy
import random

# Load the song data (replace with the correct path)
data = pd.read_csv('/content/ex.csv', encoding='ISO-8859-1')

# Load pre-trained NLP model
nlp = spacy.load('en_core_web_sm')

# Function to classify prompts into categories like 'specific song', 'movie song', or 'emotion'
def classify_prompt(prompt):
    prompt = prompt.lower()
    if "from" in prompt:
        return "movie_song"
    elif any(emotion in prompt for emotion in ["sad", "happy", "romantic", "party"]):
        return "emotion"
    elif "play" in prompt:
        return "specific_song"
    else:
        return "generic"

# Function to extract song and movie names from the prompt
def extract_song_and_movie(prompt):
    song_name = ""
    movie_name = ""
    if "from" in prompt.lower():
        # Extract song name before "from" and movie name after "from"
        parts = prompt.split("from")
        song_name = parts[0].replace("play", "").strip()
        movie_name = parts[1].strip()
    else:
        # Extract song name only
        song_name = prompt.replace("play", "").strip()
    return song_name, movie_name

# Function to extract the emotion from the prompt
def extract_emotion(prompt):
    emotions = ["sad", "happy", "romantic", "party"]
    for emotion in emotions:
        if emotion in prompt.lower():
            return emotion
    return None

# Function to suggest songs based on prompt classification
def suggest_song(prompt):
    # Classify the prompt type
    prompt_type = classify_prompt(prompt)
    
    # Extract song name, movie name, and emotion from the prompt
    song_name, movie_name = extract_song_and_movie(prompt)
    emotion = extract_emotion(prompt)
    
    # Check if the 'Emotion' column exists in the dataset
    if 'Emotion' not in data.columns:
        print("'Emotion' column not found in the dataset. Proceeding without emotion-based classification.")
        emotion = None  # Set emotion to None
    
    if prompt_type == "specific_song":
        # Search for the song in the dataset
        song_match = data[data['Song-Name'].str.contains(song_name, case=False, na=False)]
        if not song_match.empty:
            return random.choice(song_match['Song-Name'].values)
        else:
            return f"Song '{song_name}' not found."
    
    elif prompt_type == "movie_song":
        # Search for the song from the specific movie
        song_match = data[
            (data['Song-Name'].str.contains(song_name, case=False, na=False)) &
            (data['Album/Movie'].str.contains(movie_name, case=False, na=False))
        ]
        if not song_match.empty:
            return random.choice(song_match['Song-Name'].values)
        else:
            return f"Song '{song_name}' from movie '{movie_name}' not found."
    
    elif prompt_type == "emotion" and emotion:
        # Only search for songs based on emotion if the 'Emotion' column exists
        emotion_match = data[data['Emotion'].str.contains(emotion, case=False, na=False)]
        if not emotion_match.empty:
            return random.choice(emotion_match['Song-Name'].values)
        else:
            return f"No songs found for emotion '{emotion}'."
    
    else:
        # Suggest a random song if no specific match is found
        return random.choice(data['Song-Name'].values)