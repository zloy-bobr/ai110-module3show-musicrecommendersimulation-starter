import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field

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
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    language: str = "english"

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
    # Optional preferences: None means "no preference", so the rule is skipped
    target_valence: Optional[float] = None
    desired_mood_tags: Optional[List[str]] = None
    favorite_decade: Optional[int] = None
    target_popularity: Optional[int] = None
    target_instrumentalness: Optional[float] = None
    preferred_language: Optional[str] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Rank songs with score_song (highest first, ties by title) and return the top k."""
        prefs = asdict(user)
        ranked = sorted(self.songs, key=lambda song: (-score_song(prefs, asdict(song))[0], song.title))
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return the scoring reasons for one song as a single readable string."""
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons) if reasons else "No preferences matched this song."

def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV into a list of dicts, converting numeric columns to int/float."""
    int_fields = ["id", "popularity", "release_decade"]
    float_fields = ["energy", "tempo_bpm", "valence", "danceability", "acousticness", "instrumentalness"]

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for name in int_fields:
                row[name] = int(row[name])
            for name in float_fields:
                row[name] = float(row[name])
            row["mood_tags"] = _tags(row["mood_tags"])
            songs.append(row)
    return songs

def _normalize(text) -> str:
    """Lowercase and trim a label so "Pop " and "pop" compare equal."""
    return str(text or "").strip().lower()

def _target(value) -> float:
    """Convert a 0-1 target to float and clamp it into range."""
    return min(1.0, max(0.0, float(value)))

def _to_bool(value) -> bool:
    """Read a yes/no preference, treating strings like "False" or "no" as False."""
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1")
    return bool(value)

def _tags(value) -> List[str]:
    """Turn "a;b" or ["A", " b"] into a clean list of lowercase tags."""
    items = value.split(";") if isinstance(value, str) else (value or [])
    return [_normalize(tag) for tag in items if _normalize(tag)]

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences and return (score, list of reasons)."""
    score = 0.0
    reasons = []

    # Genre: exact match beats a partial match on whole words ("pop" <-> "indie pop")
    genre = _normalize(user_prefs.get("favorite_genre"))
    song_genre = _normalize(song["genre"])
    if genre and song_genre == genre:
        score += 2.0
        reasons.append("genre match (+2.0)")
    elif genre and set(genre.split()) & set(song_genre.split()):
        score += 1.0
        reasons.append(f"related genre: {song['genre']} (+1.0)")

    mood = _normalize(user_prefs.get("favorite_mood"))
    if mood and _normalize(song["mood"]) == mood:
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Numeric features earn points for being close to the target, not for being high
    if user_prefs.get("target_energy") is not None:
        target = _target(user_prefs["target_energy"])
        points = 1.5 * (1 - abs(song["energy"] - target))
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {target:.2f} (+{points:.2f})")

    if user_prefs.get("likes_acoustic") is not None:
        if _to_bool(user_prefs["likes_acoustic"]):
            points = 0.5 * song["acousticness"]
            reasons.append(f"acoustic sound (+{points:.2f})")
        else:
            points = 0.5 * (1 - song["acousticness"])
            reasons.append(f"produced, non-acoustic sound (+{points:.2f})")
        score += points

    if user_prefs.get("target_valence") is not None:
        target = _target(user_prefs["target_valence"])
        points = 1.0 * (1 - abs(song["valence"] - target))
        score += points
        reasons.append(f"positivity {song['valence']:.2f} vs target {target:.2f} (+{points:.2f})")

    # Advanced features: each rule only runs if the profile sets it

    # Detailed mood tags give partial credit for close moods ("happy" vs. "euphoric")
    wanted = _tags(user_prefs.get("desired_mood_tags"))
    shared = [tag for tag in wanted if tag in _tags(song.get("mood_tags"))]
    if shared:
        points = min(1.0, 0.5 * len(shared))
        score += points
        reasons.append(f"mood tags: {', '.join(shared)} (+{points:.2f})")

    if user_prefs.get("favorite_decade") is not None and song.get("release_decade") is not None:
        gap = abs(int(song["release_decade"]) - int(user_prefs["favorite_decade"]))
        if gap == 0:
            score += 0.75
            reasons.append(f"from the {song['release_decade']}s (+0.75)")
        elif gap == 10:
            score += 0.35
            reasons.append(f"neighboring decade: {song['release_decade']}s (+0.35)")

    if user_prefs.get("target_popularity") is not None and song.get("popularity") is not None:
        target = min(100, max(0, float(user_prefs["target_popularity"])))
        points = 0.5 * (1 - abs(song["popularity"] - target) / 100)
        score += points
        reasons.append(f"popularity {song['popularity']} vs target {target:.0f} (+{points:.2f})")

    if user_prefs.get("target_instrumentalness") is not None and song.get("instrumentalness") is not None:
        target = _target(user_prefs["target_instrumentalness"])
        points = 0.5 * (1 - abs(song["instrumentalness"] - target))
        score += points
        reasons.append(f"instrumental {song['instrumentalness']:.2f} vs target {target:.2f} (+{points:.2f})")

    # Songs without lyrics get half credit, since language doesn't get in the way
    language = _normalize(user_prefs.get("preferred_language"))
    song_language = _normalize(song.get("language"))
    if language and song_language == language:
        score += 0.5
        reasons.append(f"sung in {song_language} (+0.5)")
    elif language and song_language == "instrumental":
        score += 0.25
        reasons.append("instrumental, no language barrier (+0.25)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest first (ties by title), and return the top k as (song, score, explanation)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Highest score first; ties broken alphabetically by title
    ranked = sorted(scored, key=lambda item: (-item[1], item[0]["title"]))

    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
