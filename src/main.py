"""
Command line runner for the Music Recommender Simulation.
"""

import os
from src.recommender import load_songs, recommend_songs


def main() -> None:
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(csv_path)
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    print(f"User profile: genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
          f"energy={user_prefs['energy']}, likes_acoustic={user_prefs['likes_acoustic']}")
    print("=" * 52)
    print(f"{'#':<3} {'Title':<26} {'Score':>5}  Reasons")
    print("-" * 52)

    recommendations = recommend_songs(user_prefs, songs, k=5)
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        reasons_str = ", ".join(reasons)
        print(f"{rank:<3} {song['title']:<26} {score:>5.2f}  {reasons_str}")

    print("=" * 52)


if __name__ == "__main__":
    main()
