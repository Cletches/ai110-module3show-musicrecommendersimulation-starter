from src.recommender import Song, UserProfile, Recommender, score_song

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


# --- Edge case song used across multiple tests ---
AMBIENT_SONG = {
    "genre": "ambient", "mood": "chill",
    "energy": 0.28, "tempo_bpm": 60.0,
    "valence": 0.65, "danceability": 0.41, "acousticness": 0.92,
}
POP_SONG = {
    "genre": "pop", "mood": "happy",
    "energy": 0.93, "tempo_bpm": 132.0,
    "valence": 0.77, "danceability": 0.88, "acousticness": 0.05,
}


# Edge case 1: empty profile — all songs should score the same
def test_empty_profile_produces_equal_scores():
    user_prefs = {}
    score_ambient, _ = score_song(AMBIENT_SONG, user_prefs)
    score_pop, _     = score_song(POP_SONG, user_prefs)
    assert score_ambient == score_pop, (
        "Empty profile should give every song the same neutral score"
    )


# Edge case 2: genre/energy conflict — ambient genre but high energy target
def test_genre_energy_conflict():
    user_prefs = {"genre": "ambient", "energy": 0.95}
    score_ambient, _ = score_song(AMBIENT_SONG, user_prefs)
    score_pop, _     = score_song(POP_SONG, user_prefs)
    # Ambient song gets +2.0 genre but near-zero energy; pop gets 0 genre but high energy bonus
    # Ambient should still win because genre outweighs energy
    assert score_ambient > score_pop, (
        "Genre match (+2.0) should outweigh energy mismatch even with conflicting targets"
    )


# Edge case 3: likes_acoustic ignored when explicit acousticness is also set
def test_explicit_acousticness_overrides_likes_acoustic():
    prefs_explicit  = {"acousticness": 0.9, "likes_acoustic": False}
    prefs_bool_only = {"likes_acoustic": True}
    score_explicit, _ = score_song(AMBIENT_SONG, prefs_explicit)   # acousticness=0.92 ≈ target 0.9
    score_bool, _     = score_song(AMBIENT_SONG, prefs_bool_only)  # target mapped to 0.8
    # Both should favour the high-acousticness ambient song, but explicit target is closer
    assert score_explicit >= score_bool, (
        "Explicit acousticness value should score at least as well as likes_acoustic=True"
    )


# Edge case 4: extreme tempo target beyond catalog range
def test_extreme_tempo_target_clamps_to_zero():
    user_prefs = {"tempo_bpm": 200.0}
    # Song at 60 BPM: proximity = 1 - |60-200|/140 = 0.0 (clamped)
    slow_song = {**AMBIENT_SONG, "tempo_bpm": 60.0}
    score, _ = score_song(slow_song, user_prefs)
    # tempo contributes 0.0 pts (0.0 × 0.1 cap); other unspecified features get neutral 0.5×
    assert score >= 0.0, "Score must never go negative with extreme tempo target"


# Edge case 5: secondary genre same as primary — no double counting
def test_secondary_genre_duplicate_of_primary():
    prefs_with_dup    = {"genre": "pop", "secondary_genres": ["pop", "lofi"]}
    prefs_without_dup = {"genre": "pop", "secondary_genres": ["lofi"]}
    score_dup, _    = score_song(POP_SONG, prefs_with_dup)
    score_no_dup, _ = score_song(POP_SONG, prefs_without_dup)
    assert score_dup == score_no_dup, (
        "Listing primary genre in secondary_genres should not change the score"
    )


# Edge case 6: energy target at 0.0 — only songs near zero score well
def test_zero_energy_target():
    user_prefs = {"energy": 0.0}
    score_ambient, _ = score_song(AMBIENT_SONG, user_prefs)  # energy=0.28, closer to 0
    score_pop, _     = score_song(POP_SONG, user_prefs)      # energy=0.93, far from 0
    assert score_ambient > score_pop, (
        "Low-energy song should score higher than high-energy song when target is 0.0"
    )


# Edge case 7: genre not in catalog — winner decided by numeric features alone
def test_unknown_genre_falls_back_to_numeric():
    user_prefs = {"genre": "bossa nova", "energy": 0.28}
    score_ambient, _ = score_song(AMBIENT_SONG, user_prefs)  # energy close to 0.28
    score_pop, _     = score_song(POP_SONG, user_prefs)      # energy far from 0.28
    assert score_ambient > score_pop, (
        "When genre is unknown, numeric proximity should determine the winner"
    )
