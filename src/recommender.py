from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv


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

    def _score(self, user: UserProfile, song: Song) -> float:
        genre_match = 1.0 if song.genre == user.favorite_genre else 0.0
        mood_match = 1.0 if song.mood == user.favorite_mood else 0.0
        energy_score = 1.0 - abs(song.energy - user.target_energy)
        acoustic_score = song.acousticness if user.likes_acoustic else (1.0 - song.acousticness)

        return (3.0 * genre_match
                + 2.0 * mood_match
                + 1.5 * energy_score
                + 0.7 * acoustic_score)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches ({song.mood})")
        if abs(song.energy - user.target_energy) < 0.15:
            reasons.append(f"energy is close to your target ({song.energy:.2f} vs {user.target_energy:.2f})")
        if user.likes_acoustic and song.acousticness > 0.6:
            reasons.append(f"has acoustic feel ({song.acousticness:.2f})")
        elif not user.likes_acoustic and song.acousticness < 0.4:
            reasons.append(f"has electronic/produced sound ({song.acousticness:.2f})")

        if not reasons:
            return f"Closest available match (score: {self._score(user, song):.2f})"
        return "Recommended because: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    return []

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    user_genre = user_prefs.get("genre", "")
    user_mood = user_prefs.get("mood", "")
    user_energy = float(user_prefs.get("energy", 0.5))
    user_likes_acoustic = user_prefs.get("likes_acoustic", False)

    def score(song: Dict) -> float:
        genre_match = 1.0 if song["genre"] == user_genre else 0.0
        mood_match = 1.0 if song["mood"] == user_mood else 0.0
        energy_score = 1.0 - abs(song["energy"] - user_energy)
        acoustic_score = song["acousticness"] if user_likes_acoustic else (1.0 - song["acousticness"])
        return 3.0 * genre_match + 2.0 * mood_match + 1.5 * energy_score + 0.7 * acoustic_score

    def explain(song: Dict) -> str:
        reasons = []
        if song["genre"] == user_genre:
            reasons.append(f"genre matches ({song['genre']})")
        if song["mood"] == user_mood:
            reasons.append(f"mood matches ({song['mood']})")
        if abs(song["energy"] - user_energy) < 0.15:
            reasons.append(f"energy is close to your target ({song['energy']:.2f})")
        if not reasons:
            return "Closest available match"
        return "Recommended because: " + ", ".join(reasons)

    ranked = sorted(songs, key=score, reverse=True)[:k]
    return [(song, score(song), explain(song)) for song in ranked]
