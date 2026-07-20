import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Scoring recipe (see README, "The Algorithm Recipe"): the score is a weighted
# sum of four rules. Genre is the strongest signal, then mood; energy and
# acoustic fit are continuous 0-1 "how close" terms that act as tie-breakers.
# Max score ≈ 6.5.
#
#   genre match ...... 1 if song.genre == favorite_genre else 0     × 3.0
#   mood match ....... 1 if song.mood  == favorite_mood  else 0     × 1.5
#   energy fit ....... 1 - abs(target_energy - song.energy)         × 1.0
#   acoustic fit ..... acousticness (or 1 - acousticness)           × 1.0
#
# Every rule also emits a reason string that names the points it awarded, e.g.
# "genre match (+3.0)", so a recommendation can explain itself.
# ---------------------------------------------------------------------------

W_GENRE = 3.0
W_MOOD = 1.5
W_ENERGY = 1.0
W_ACOUSTIC = 1.0

# ---------------------------------------------------------------------------
# Diversity penalty: a good-taste match alone can flood the top list with the
# same artist (or genre) over and over. To keep the results varied, a song is
# penalized *while the list is being built* for every song already chosen that
# shares its artist or genre. The first appearance of an artist/genre is free;
# each repeat costs more. Because this depends on what is already in the list,
# it lives in the ranking pass (recommend_songs / Recommender.recommend), not
# in the per-song score.
#
#   artist repeat .... W_ARTIST_PENALTY x (# already-chosen songs, same artist)
#   genre repeat ..... W_GENRE_PENALTY  x (# already-chosen songs, same genre)
#
# The artist penalty is the stronger lever (artist is otherwise unscored); the
# genre penalty is deliberately smaller than W_GENRE so one repeat nudges the
# list toward variety without fully cancelling a genuine genre match.
# ---------------------------------------------------------------------------
W_ARTIST_PENALTY = 2.0
W_GENRE_PENALTY = 1.0


def _closeness(target: float, actual: float) -> float:
    """Proximity on a 0-1 scale: 1.0 == identical, floored at 0 (no penalty)."""
    return max(0.0, 1.0 - abs(target - actual))


def _diversity_penalty(
    artist: str,
    genre: str,
    chosen_artists: List[str],
    chosen_genres: List[str],
) -> Tuple[float, List[str]]:
    """
    Points to subtract from a candidate given the artists/genres already chosen.

    chosen_artists / chosen_genres list the artist and genre of every song
    already placed in the top results. Returns (penalty, reasons); reasons is
    empty when the candidate adds a fresh artist and genre.
    """
    penalty = 0.0
    reasons: List[str] = []

    artist_repeats = chosen_artists.count(artist)
    if artist_repeats:
        points = W_ARTIST_PENALTY * artist_repeats
        penalty += points
        reasons.append(f"artist repeat (-{points:.1f})")

    genre_repeats = chosen_genres.count(genre)
    if genre_repeats:
        points = W_GENRE_PENALTY * genre_repeats
        penalty += points
        reasons.append(f"genre repeat (-{points:.1f})")

    return penalty, reasons


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

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """
        Score a Song against a UserProfile using the README recipe.

        Returns (score, reasons); each reason names the points its rule awarded,
        e.g. "genre match (+3.0)".
        """
        score = 0.0
        reasons: List[str] = []

        # Rule 1 + 2: categorical matches award full weight or nothing.
        if song.genre == user.favorite_genre:
            score += W_GENRE
            reasons.append(f"genre match (+{W_GENRE:.1f})")

        if song.mood == user.favorite_mood:
            score += W_MOOD
            reasons.append(f"mood match (+{W_MOOD:.1f})")

        # Rule 3: energy fit — closer to the target energy earns more.
        energy_points = W_ENERGY * _closeness(user.target_energy, song.energy)
        score += energy_points
        reasons.append(f"energy fit (+{energy_points:.2f})")

        # Rule 4: acoustic fit — likes_acoustic is a direction, not a target:
        # reward high acousticness when they like acoustic, low when they don't.
        acoustic_fit = song.acousticness if user.likes_acoustic else 1.0 - song.acousticness
        acoustic_points = W_ACOUSTIC * acoustic_fit
        score += acoustic_points
        reasons.append(f"acoustic fit (+{acoustic_points:.2f})")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Return the top-k Songs for a user, highest score first.

        Selection is greedy so the diversity penalty can apply: songs are ranked
        by base score, then chosen one at a time, each time re-ranking the
        remaining songs by (base score - diversity penalty) so an artist or
        genre already in the list is discouraged from repeating.
        """
        remaining = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)

        results: List[Song] = []
        chosen_artists: List[str] = []
        chosen_genres: List[str] = []
        while remaining and len(results) < k:
            best_i = max(
                range(len(remaining)),
                key=lambda i: self._score(user, remaining[i])[0]
                - _diversity_penalty(
                    remaining[i].artist, remaining[i].genre, chosen_artists, chosen_genres
                )[0],
            )
            song = remaining.pop(best_i)
            results.append(song)
            chosen_artists.append(song.artist)
            chosen_genres.append(song.genre)
        return results

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string naming why this song scored as it did."""
        _, reasons = self._score(user, song)
        return "Because: " + ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
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
    Score a single song against user preferences using the README recipe.
    Required by recommend_songs() and src/main.py

    Returns (score, reasons). Each reason names the rule and the points it
    awarded, e.g. "genre match (+3.0)", so the recommendation can explain
    itself. Categorical misses award zero and stay silent; the energy and
    acoustic terms always contribute partial "how close" credit.
    """
    score = 0.0
    reasons: List[str] = []

    # Rule 1: genre match (categorical, strongest weight).
    if song["genre"] == user_prefs.get("favorite_genre"):
        score += W_GENRE
        reasons.append(f"genre match (+{W_GENRE:.1f})")

    # Rule 2: mood match (categorical).
    if song["mood"] == user_prefs.get("favorite_mood"):
        score += W_MOOD
        reasons.append(f"mood match (+{W_MOOD:.1f})")

    # Rule 3: energy fit — closer to the target energy earns more (0-1 scale).
    energy_points = W_ENERGY * _closeness(user_prefs["target_energy"], song["energy"])
    score += energy_points
    reasons.append(f"energy fit (+{energy_points:.2f})")

    # Rule 4: acoustic fit — reward acousticness when the user likes acoustic,
    # otherwise reward electronic (low acousticness).
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acoustic_fit = song["acousticness"] if likes_acoustic else 1.0 - song["acousticness"]
    acoustic_points = W_ACOUSTIC * acoustic_fit
    score += acoustic_points
    reasons.append(f"acoustic fit (+{acoustic_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns up to k (song_dict, score, explanation) tuples. Selection is greedy
    so the diversity penalty (see _diversity_penalty) can apply: the returned
    score is the base score minus any penalty, and the explanation names the
    "artist repeat"/"genre repeat" deductions when a song is chosen despite
    sharing an artist or genre already in the list.
    """
    # Base score + reasons once per song; highest base score first so the greedy
    # pass below considers the strongest candidates early.
    remaining = [
        (song, base, reasons)
        for song in songs
        for base, reasons in [score_song(user_prefs, song)]
    ]
    remaining.sort(key=lambda item: item[1], reverse=True)

    results: List[Tuple[Dict, float, str]] = []
    chosen_artists: List[str] = []
    chosen_genres: List[str] = []
    while remaining and len(results) < k:
        # Re-rank what is left by score-after-penalty and take the current best.
        # remaining is already ordered by base score, so max() keeps the first
        # (strongest) candidate on ties.
        best_i = max(
            range(len(remaining)),
            key=lambda i: remaining[i][1]
            - _diversity_penalty(
                remaining[i][0]["artist"], remaining[i][0]["genre"], chosen_artists, chosen_genres
            )[0],
        )
        song, base, reasons = remaining.pop(best_i)

        penalty, penalty_reasons = _diversity_penalty(
            song["artist"], song["genre"], chosen_artists, chosen_genres
        )
        explanation = ", ".join(reasons + penalty_reasons)
        results.append((song, base - penalty, explanation))
        chosen_artists.append(song["artist"])
        chosen_genres.append(song["genre"])
    return results
