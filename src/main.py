"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# Four distinct taste profiles for the four scored rules (see README, "The
# Algorithm Recipe"). Each dict is a listener persona; swap which one is passed
# to recommend_songs() in main() to model a different taste. Keys:
#   favorite_genre  categorical match        (x 3.0)
#   favorite_mood   categorical match        (x 1.5)
#   target_energy   0.0 (calm) -> 1.0 (high) (x 1.0)
#   likes_acoustic  prefer acoustic texture  (x 1.0)
USER_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.92,
        "likes_acoustic": False,
    },
    "Late-Night Jazz": {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Pick which persona to model by name; try the others from USER_PROFILES.
    profile_name = "Late-Night Jazz"
    user_prefs = USER_PROFILES[profile_name]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # Wrap the whole render in a markdown fence so it can be pasted as-is.
    print("\n```")

    header = f"Top recommendations for: {profile_name}"
    print(header)
    print("=" * len(header) + "\n")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Title + final score on the headline; artist as a subtle subtitle.
        print(f"{rank}. {song['title']} — {song['artist']}   (score: {score:.2f})")

        # The explanation is a comma-joined string of the reasons the scoring
        # function awarded; split it back out into an indented bullet list.
        for reason in explanation.split(", "):
            print(f"     • {reason}")
        print()

    print("```")


if __name__ == "__main__":
    main()
