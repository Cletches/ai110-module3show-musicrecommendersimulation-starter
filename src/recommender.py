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


# --- Additive point values for categorical features ---
# Genre: +2.0 primary, +1.0 secondary
# Mood:  +1.0 primary, +0.5 secondary
GENRE_MATCH_POINTS     = 2.0
GENRE_SECONDARY_POINTS = 0.5
MOOD_MATCH_POINTS      = 1.0
MOOD_SECONDARY_POINTS  = 0.5

# --- Bonus point caps for numeric features (proximity 0–1 scaled by these) ---
# Energy is the primary numeric signal; others are smaller bonuses.
NUMERIC_POINTS = {
    "energy":       1.0,   # 0.0 – 1.0 pts
    "valence":      0.5,   # 0.0 – 0.5 pts
    "danceability": 0.3,   # 0.0 – 0.3 pts
    "acousticness": 0.1,   # 0.0 – 0.1 pts
    "tempo_bpm":    0.1,   # 0.0 – 0.1 pts
}
# Max possible score: 2.0 + 1.0 + 1.0 + 0.5 + 0.3 + 0.1 + 0.1 = 5.0

# --- Numeric feature ranges for proximity normalization ---
RANGES = {
    "energy":       1.0,    # 0.0 – 1.0
    "valence":      1.0,    # 0.0 – 1.0
    "danceability": 1.0,    # 0.0 – 1.0
    "acousticness": 1.0,    # 0.0 – 1.0
    "tempo_bpm":    140.0,  # practical range ~60–200 BPM
}


def _proximity(value: float, target: float, feature_range: float) -> float:
    """
    Proximity score for a numeric feature.

    Returns 1.0 when value == target, and decreases linearly
    toward 0.0 as the gap grows to feature_range.

    Formula: 1 - |value - target| / feature_range
    Clamped to [0, 1] to handle values outside the expected range.
    """
    return max(0.0, 1.0 - abs(value - target) / feature_range)


def score_song(song: Dict, user_prefs: Dict) -> Tuple[float, str]:
    """
    Scores a single song against a user preference dict.  

    user_prefs keys:
        genre (str), mood (str), energy (float), valence (float),
        danceability (float), acousticness (float), tempo_bpm (float),
        likes_acoustic (bool, optional)

    Returns (score: float, explanation: str).
    """
    total_score = 0.0
    component_scores: Dict[str, float] = {}

    # --- Categorical features (additive points) ---
    secondary_genres = set(user_prefs.get("secondary_genres", []))
    secondary_moods  = set(user_prefs.get("secondary_moods",  []))

    if song["genre"] == user_prefs.get("genre"):
        component_scores["genre"] = GENRE_MATCH_POINTS
    elif song["genre"] in secondary_genres:
        component_scores["genre"] = GENRE_SECONDARY_POINTS
    else:
        component_scores["genre"] = 0.0

    if song["mood"] == user_prefs.get("mood"):
        component_scores["mood"] = MOOD_MATCH_POINTS
    elif song["mood"] in secondary_moods:
        component_scores["mood"] = MOOD_SECONDARY_POINTS
    else:
        component_scores["mood"] = 0.0

    total_score += component_scores["genre"] + component_scores["mood"]

    # --- Numeric features: proximity scaled by bonus point cap ---
    for feature in ("energy", "valence", "danceability", "acousticness", "tempo_bpm"):
        if feature in user_prefs:
            target = float(user_prefs[feature])
        elif feature == "acousticness" and "likes_acoustic" in user_prefs:
            target = 0.8 if user_prefs["likes_acoustic"] else 0.2
        else:
            # Feature not specified — award half the bonus points (neutral)
            component_scores[feature] = NUMERIC_POINTS[feature] * 0.5
            total_score += component_scores[feature]
            continue

        proximity = _proximity(float(song[feature]), target, RANGES[feature])
        component_scores[feature] = proximity * NUMERIC_POINTS[feature]
        total_score += component_scores[feature]

    # --- Human-readable explanation ---
    reasons = []
    if component_scores["genre"] == GENRE_MATCH_POINTS:
        reasons.append(f"genre matches ({song['genre']})")
    elif component_scores["genre"] == GENRE_SECONDARY_POINTS:
        reasons.append(f"genre is a secondary match ({song['genre']})")
    if component_scores["mood"] == MOOD_MATCH_POINTS:
        reasons.append(f"mood matches ({song['mood']})")
    elif component_scores["mood"] == MOOD_SECONDARY_POINTS:
        reasons.append(f"mood is a secondary match ({song['mood']})")
    for feature in ("energy", "valence", "danceability", "acousticness", "tempo_bpm"):
        proximity = component_scores[feature] / NUMERIC_POINTS[feature]
        if proximity >= 0.85:
            reasons.append(f"{feature} is very close to your preference ({song[feature]})")
        elif proximity <= 0.35:
            reasons.append(f"{feature} differs from your preference ({song[feature]})")

    explanation = "; ".join(reasons) if reasons else "moderate overall match"
    return round(total_score, 4), explanation


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Score a Song dataclass instance against a UserProfile."""
        prefs = {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        song_dict = {
            "genre":        song.genre,
            "mood":         song.mood,
            "energy":       song.energy,
            "valence":      song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "tempo_bpm":    song.tempo_bpm,
        }
        score, _ = score_song(song_dict, prefs)
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        prefs = {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        song_dict = {
            "genre":        song.genre,
            "mood":         song.mood,
            "energy":       song.energy,
            "valence":      song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "tempo_bpm":    song.tempo_bpm,
        }
        _, explanation = score_song(song_dict, prefs)
        return explanation


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]           = int(row["id"])
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [(song, *score_song(song, user_prefs)) for song in songs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
