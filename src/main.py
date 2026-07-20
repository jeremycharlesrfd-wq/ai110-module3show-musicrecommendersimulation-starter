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

    # Taste profile for the four scored rules (see README, "The Algorithm
    # Recipe"). This example models a "chill lofi listener". Swap the values to
    # model other tastes (e.g. an "intense rock" fan would flip genre/mood,
    # raise target_energy, and set likes_acoustic=False).
    user_prefs = {
        "favorite_genre": "lofi",       # categorical match       (x 3.0)
        "favorite_mood": "chill",       # categorical match       (x 1.5)
        "target_energy": 0.40,          # 0.0 (calm) -> 1.0 (high) (x 1.0)
        "likes_acoustic": True,         # prefer acoustic texture (x 1.0)
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    header = "Top recommendations"
    print(f"\n{header}")
    print("=" * len(header) + "\n")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Title + final score on the headline; artist as a subtle subtitle.
        print(f"{rank}. {song['title']} — {song['artist']}   (score: {score:.2f})")

        # The explanation is a comma-joined string of the reasons the scoring
        # function awarded; split it back out into an indented bullet list.
        for reason in explanation.split(", "):
            print(f"     • {reason}")
        print()


if __name__ == "__main__":
    main()
