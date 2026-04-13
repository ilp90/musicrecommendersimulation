"""
Command line runner for the Music Recommender Simulation.
Runs five user profiles (including two adversarial edge cases) and one
weight-shift experiment to evaluate scoring sensitivity.
"""

import os
from src.recommender import load_songs, recommend_songs

W = 64  # output width


def print_profile(label: str, user_prefs: dict, songs: list, k: int = 5,
                  weights: dict = None) -> None:
    """Prints a formatted recommendation table for one user profile."""
    tag = " [EXPERIMENT]" if weights else ""
    print(f"\n{'=' * W}")
    print(f"  {label}{tag}")
    print(f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}  acoustic={user_prefs.get('likes_acoustic', False)}")
    if weights:
        print(f"  weights: genre={weights['genre']} mood={weights['mood']} "
              f"energy={weights['energy']} acoustic={weights['acoustic']}")
    print(f"{'=' * W}")
    print(f"{'#':<3} {'Title':<26} {'Score':>5}  Reasons")
    print(f"{'-' * W}")
    for rank, (song, score, reasons) in enumerate(
        recommend_songs(user_prefs, songs, k, weights), start=1
    ):
        print(f"{rank:<3} {song['title']:<26} {score:>5.2f}  {', '.join(reasons)}")
    print(f"{'-' * W}")


def main() -> None:
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(csv_path)
    print(f"Loaded songs: {len(songs)}")

    # ── Standard profiles ──────────────────────────────────────────────────
    profiles = [
        ("Profile A · High-Energy Pop",
         {"genre": "pop",      "mood": "happy",   "energy": 0.80, "likes_acoustic": False}),
        ("Profile B · Chill Lofi Study",
         {"genre": "lofi",     "mood": "focused", "energy": 0.40, "likes_acoustic": True}),
        ("Profile C · Deep Intense Rock",
         {"genre": "rock",     "mood": "intense", "energy": 0.90, "likes_acoustic": False}),
        # Adversarial: genre exists but energy conflicts with the mood
        ("Profile D · Adversarial — High-Energy Blues (conflicting prefs)",
         {"genre": "blues",    "mood": "sad",     "energy": 0.90, "likes_acoustic": False}),
        # Edge case: genre not present in the catalog at all
        ("Profile E · Edge Case — Country (genre missing from catalog)",
         {"genre": "country",  "mood": "happy",   "energy": 0.60, "likes_acoustic": True}),
    ]

    for label, prefs in profiles:
        print_profile(label, prefs, songs)

    # ── Step 3 Experiment: double energy weight, halve genre weight ─────────
    print(f"\n\n{'#' * W}")
    print("  EXPERIMENT: genre weight 3.0→1.5 · energy weight 1.5→3.0")
    print("  Hypothesis: high-energy non-pop songs enter the top 5 for Profile A")
    print(f"{'#' * W}")

    exp_weights = {"genre": 1.5, "mood": 2.0, "energy": 3.0, "acoustic": 0.7}
    label_a, prefs_a = profiles[0]
    print_profile(label_a + " — baseline", prefs_a, songs)
    print_profile(label_a + " — energy-first", prefs_a, songs, weights=exp_weights)


if __name__ == "__main__":
    main()
