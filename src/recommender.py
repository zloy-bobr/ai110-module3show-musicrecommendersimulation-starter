import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV into a list of dicts, converting numeric columns to int/float."""
    int_fields = ["id"]
    float_fields = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences and return (score, list of reasons)."""
    score = 0.0
    reasons = []

    # Genre: exact match beats a partial match like "pop" in "indie pop"
    genre = user_prefs.get("favorite_genre")
    if genre and song["genre"] == genre:
        score += 2.0
        reasons.append("genre match (+2.0)")
    elif genre and genre in song["genre"]:
        score += 1.0
        reasons.append(f"related genre: {song['genre']} (+1.0)")

    if user_prefs.get("favorite_mood") and song["mood"] == user_prefs["favorite_mood"]:
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Numeric features earn points for being close to the target, not for being high
    if "target_energy" in user_prefs:
        points = 1.5 * (1 - abs(song["energy"] - user_prefs["target_energy"]))
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{points:.2f})")

    if "likes_acoustic" in user_prefs:
        if user_prefs["likes_acoustic"]:
            points = 0.5 * song["acousticness"]
            reasons.append(f"acoustic sound (+{points:.2f})")
        else:
            points = 0.5 * (1 - song["acousticness"])
            reasons.append(f"produced, non-acoustic sound (+{points:.2f})")
        score += points

    if "target_valence" in user_prefs:
        points = 1.0 * (1 - abs(song["valence"] - user_prefs["target_valence"]))
        score += points
        reasons.append(f"positivity {song['valence']:.2f} vs target {user_prefs['target_valence']:.2f} (+{points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest first (ties by title), and return the top k as (song, score, explanation)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Highest score first; ties broken alphabetically by title
    ranked = sorted(scored, key=lambda item: (-item[1], item[0]["title"]))

    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
