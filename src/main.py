"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
        "target_valence": 0.8,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
        "target_valence": 0.6,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "likes_acoustic": False,
        "target_valence": 0.45,
    },
    # Edge cases: profiles meant to trick or stress the scoring logic
    "Edge: Sad Banger (conflicting mood vs. energy)": {
        "favorite_genre": "edm",
        "favorite_mood": "sad",
        "target_energy": 0.9,
        "likes_acoustic": False,
        "target_valence": 0.2,
    },
    "Edge: Capitalized Genre ('Pop' vs. 'pop')": {
        "favorite_genre": "Pop",
        "favorite_mood": "Happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    },
    "Edge: Out-of-Range Energy (1.5)": {
        "favorite_genre": "classical",
        "target_energy": 1.5,
    },
    "Edge: Empty Profile": {},
    # Advanced features: mood tags, decade, popularity, instrumentalness, language
    "Advanced: High-Energy Pop + Mood Tags": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
        "target_valence": 0.8,
        "desired_mood_tags": ["happy", "sunny", "feel-good"],
    },
    "Advanced: Nostalgic Late-Night Drive": {
        "favorite_genre": "synthwave",
        "favorite_mood": "moody",
        "target_energy": 0.7,
        "likes_acoustic": False,
        "desired_mood_tags": ["nostalgic", "late-night", "dreamy"],
        "favorite_decade": 2010,
        "target_popularity": 60,
    },
    "Advanced: Underground Instrumental Study": {
        "favorite_mood": "focused",
        "target_energy": 0.35,
        "likes_acoustic": True,
        "desired_mood_tags": ["study", "calm", "cozy"],
        "target_instrumentalness": 0.9,
        "target_popularity": 40,
        "preferred_language": "english",
    },
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Print one profile's top recommendations with scores and reasons."""
    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items()) or "(none)"
    print(f"\n### {name}")
    print(f"User profile: {profile}")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   {song['genre']} / {song['mood']}   Score: {score:.2f}")
        for reason in explanation.split("; ") if explanation else ["(no preferences matched)"]:
            print(f"     - {reason}")
        print("-" * 60)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
