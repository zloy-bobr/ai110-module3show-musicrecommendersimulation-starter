"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile: an upbeat pop listener who prefers produced (non-acoustic) sound
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
        "target_valence": 0.8,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print(f"User profile: {profile}")
    print("\nTop recommendations")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   {song['genre']} / {song['mood']}   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print("-" * 60)


if __name__ == "__main__":
    main()
