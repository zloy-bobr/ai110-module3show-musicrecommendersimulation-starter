from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_recommend_ranks_by_score_not_list_order():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    rec.songs.reverse()  # lofi song first; ranking must not depend on input order

    results = rec.recommend(user, k=2)
    assert results[0].genre == "pop"
    assert "genre match" in rec.explain_recommendation(user, results[0])


def test_score_song_handles_messy_input():
    from src.recommender import score_song

    song = {"genre": "pop", "mood": "happy", "energy": 0.2, "valence": 0.5, "acousticness": 0.9}

    # Case and spaces don't matter
    score, reasons = score_song({"favorite_genre": " Pop", "favorite_mood": "HAPPY"}, song)
    assert score == 3.0

    # Out-of-range targets are clamped, so points never go negative
    score, _ = score_song({"target_energy": 1.5, "target_valence": -1}, song)
    assert score >= 0

    # Partial genre credit needs a whole shared word, in either direction
    assert score_song({"favorite_genre": "indie pop"}, song)[0] == 1.0
    assert score_song({"favorite_genre": "r"}, {**song, "genre": "r&b"})[0] == 0.0

    # A string "False" is read as False
    _, reasons = score_song({"likes_acoustic": "False"}, song)
    assert reasons[0].startswith("produced")


def test_advanced_features_add_points_only_when_requested():
    from src.recommender import score_song

    song = {
        "genre": "edm", "mood": "euphoric", "energy": 0.9, "valence": 0.9, "acousticness": 0.1,
        "popularity": 80, "release_decade": 2010, "mood_tags": ["euphoric", "happy"],
        "instrumentalness": 0.6, "language": "english",
    }
    assert score_song({}, song)[0] == 0.0

    # Close moods earn credit through tags, even when the main mood label differs
    score, reasons = score_song({"favorite_mood": "happy", "desired_mood_tags": ["Happy", "sunny"]}, song)
    assert score == 0.5 and "mood tags: happy" in reasons[0]

    assert score_song({"favorite_decade": 2010}, song)[0] == 0.75
    assert score_song({"favorite_decade": 2000}, song)[0] == 0.35
    assert score_song({"favorite_decade": 1980}, song)[0] == 0.0
    assert score_song({"target_popularity": 80}, song)[0] == 0.5
    assert score_song({"target_instrumentalness": 0.6}, song)[0] == 0.5
    assert score_song({"preferred_language": "English"}, song)[0] == 0.5
    assert score_song({"preferred_language": "spanish"}, {**song, "language": "instrumental"})[0] == 0.25


def test_user_profile_optional_fields_work_with_recommender():
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=True,
        target_instrumentalness=0.9,
    )
    rec = make_small_recommender()
    assert rec.recommend(user, k=1)[0].genre == "lofi"
    assert "instrumental" in rec.explain_recommendation(user, rec.songs[1])
