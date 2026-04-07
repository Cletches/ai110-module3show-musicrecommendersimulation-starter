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

    # Taste profile — target values for every scored feature.
    # Numeric targets use proximity scoring: songs closer to these values rank higher.
    # Secondary genres/moods receive partial credit (0.5) instead of a full match (1.0).
    user_prefs = {
        "genre":             "hip-hop",                      # primary — full credit (weight 0.25)
        "secondary_genres":  ["funk", "r&b", "electronic"],  # partial credit (0.5 × weight)
        "mood":              "confident",                    # primary — full credit (weight 0.20)
        "secondary_moods":   ["uplifting", "groovy"],        # partial credit (0.5 × weight)
        "energy":            0.78,        # 0.0–1.0: high energy but not overwhelming (weight 0.20)
        "valence":           0.65,        # 0.0–1.0: mostly positive, some edge (weight 0.15)
        "danceability":      0.85,        # 0.0–1.0: very danceable (weight 0.10)
        "acousticness":      0.10,        # 0.0–1.0: prefers produced/electronic sound (weight 0.05)
        "tempo_bpm":         95.0,        # beats per minute: mid-tempo hip-hop range (weight 0.05)
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
