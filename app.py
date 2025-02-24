from flask import Flask, request, render_template
import pickle
import requests
import pandas as pd

app = Flask(__name__)

# Load your trained model
with open("movies.pkl", "rb") as file:
    movies_df = pickle.load(file)

with open("similarity.pkl", "rb") as file:
    similarity = pickle.load(file)

# TMDB API Key
API_KEY = "0e1758306547d1bae948030700d9537f"

def get_poster(movie_title):
    """Fetch the poster URL from TMDB API."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    response = requests.get(url).json()
    
    if response["results"]:
        poster_path = response["results"][0]["poster_path"]
        full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        return full_poster_url
    else:
        return "https://via.placeholder.com/500x750.png?text=No+Image"

def get_recommendations(movie_name):
    """Fetch top 5 recommended movies with posters."""
    movie_name = movie_name.lower().strip()  # Normalize input

    # Convert all movie titles to lowercase for case-insensitive search
    movies_df["lower_title"] = movies_df["title"].str.lower()

    if movie_name not in movies_df["lower_title"].values:
        return [], []  # No recommendations found

    # Get movie index
    idx = movies_df[movies_df["lower_title"] == movie_name].index[0]

    # Get similarity scores
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]  # Top 5

    recommended_movies = []
    recommended_posters = []

    for i in scores:
        title = movies_df.iloc[i[0]]["title"]
        poster = get_poster(title)
        
        recommended_movies.append(title)
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters

@app.route("/")
def home():
    return render_template("index.html", movie_titles=movies_df["title"].tolist())

@app.route("/recommend", methods=["POST"])
def recommend():
    movie_name = request.form.get("movie")

    # Get recommendations and posters
    recommendations, posters = get_recommendations(movie_name)

    return render_template("index.html", recommendations=zip(recommendations, posters),  movie=movie_name, movie_titles=movies_df["title"].tolist())

if __name__ == "__main__":
    app.run(debug=True)