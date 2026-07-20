# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders turn users and items into data, score how well each item fits the
user, and rank the best ones first — learning preferences from behavior. My version is a
transparent stand-in: it uses a hand-written scoring rule instead of learning, and
**prioritizes genre first**, then mood, with energy and acoustic closeness as tie-breakers.

**Features used:**

- **`Song`:** `genre`, `mood`, `energy`, `acousticness` (scored) + `id`, `title`, `artist`.
- **`UserProfile`:** `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

---

### My Design

#### Song features used

Each `Song` carries 7 attributes, but my recipe scores on the **core 4** that map
directly to a user preference:

- **genre** (categorical, e.g. `pop`, `lofi`)
- **mood** (categorical, e.g. `happy`, `chill`)
- **energy** (0.0–1.0, how driving/intense the track feels)
- **acousticness** (0.0–1.0, how acoustic vs. electronic it sounds)

The remaining features (`tempo_bpm`, `valence`, `danceability`) are kept in the data
for later experiments but are not scored.

#### What the `UserProfile` stores

- **favorite_genre** — the genre they want most
- **favorite_mood** — the mood they want most
- **target_energy** — their ideal energy level (0.0–1.0)
- **likes_acoustic** — whether they prefer acoustic (`True`) or electronic (`False`) tracks

#### The Algorithm Recipe (scoring rules)

The score is a **weighted sum** of four rules. Each rule also produces a short
*reason* used to explain the recommendation.

| # | Rule | How it scores | Weight |
|---|------|---------------|--------|
| 1 | **Genre match** | `1` if `song.genre == favorite_genre`, else `0` | × 3.0 |
| 2 | **Mood match** | `1` if `song.mood == favorite_mood`, else `0` | × 1.5 |
| 3 | **Energy fit** | `1 - abs(target_energy - song.energy)` (closer = higher) | × 1.0 |
| 4 | **Acoustic fit** | if `likes_acoustic`: `song.acousticness`; else `1 - song.acousticness` | × 1.0 |

```
score = 3.0 * genre_match
      + 1.5 * mood_match
      + 1.0 * energy_fit
      + 1.0 * acoustic_fit        # max ≈ 6.5
```

**Why these weights:** genre and mood are categorical (hit-or-miss) and carry the most
weight, so a same-genre song almost always outranks a different-genre one. Genre is
weighted **twice** as high as mood (3.0 vs 1.5) so it clearly dominates: a genre match
plus *any one* other matching rule beats a song that matches everything *except* genre.
The only way a wrong-genre song can win is by being a near-perfect match on mood, energy,
and acoustic all at once (max 1.5 + 1.0 + 1.0 = 3.5). Energy and acoustic fit are
continuous 0–1 measures of "how close," so they give partial credit and act as
tie-breakers.

#### Choosing what to recommend

1. Score every song in the catalog with the rules above.
2. Sort by total score, highest first.
3. Return the top `k` songs, each with its score and the reasons that earned points.

#### Worked example

```
User: genre=pop, mood=happy, target_energy=0.8, likes_acoustic=False

"Sunrise City"  (pop,  happy, energy=0.82, acoustic=0.18)
  3.0*1 + 1.5*1 + 1.0*(1-0.02) + 1.0*(1-0.18) = 6.30  → ranked #1
"Midnight Coding" (lofi, chill, energy=0.42, acoustic=0.71)
  3.0*0 + 1.5*0 + 1.0*(1-0.38) + 1.0*(1-0.71) = 0.91
```

#### Design visualization

Input — load_songs() reads data/songs.csv into a list; user_prefs holds the taste profile (main.py:29).
Process — recommend_songs() loops every song through score_song(): genre × 3.0, mood × 1.5, energy fit × 1.0, acoustic fit × 1.0, summed into one score.
Output — sort by score descending, slice [:k], print each Top-K pick with its "Because" reasons (recommender.py).

#### Expected biases

Because the recipe is a hand-tuned weighted sum, its blind spots are baked into the weights:

- **Over-prioritizes genre.** Genre carries the largest weight (3.0) and is hit-or-miss, so a
  song in the "wrong" genre almost never surfaces — even if it's a perfect match on mood, energy,
  and acoustic feel (those max out at 3.5 combined, and only in a near-perfect case). Great
  cross-genre songs the user would love are effectively invisible.
- **Popularity/echo-chamber effect.** By always rewarding the favorite genre and mood, the system
  keeps recommending more of the same and never introduces variety or discovery — the same
  filter-bubble dynamic real recommenders are criticized for.
- **Under-weights nuance.** `tempo_bpm`, `valence`, and `danceability` aren't scored at all, so two
  songs that feel very different (a frantic vs. a mellow track at the same energy) can tie. Mood is
  also treated as a single exact-match label, so near-miss moods ("calm" vs. "chill") score zero.
- **Catalog and cold-start limits.** Scores are only meaningful relative to this tiny catalog, and a
  user with an unusual profile (no matching genre) gets weak, near-random rankings.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output


```
Top recommendations for: Chill Lofi
===================================

1. Library Rain — Paper Lanterns   (score: 6.31)
     • genre match (+3.0)
     • mood match (+1.5)
     • energy fit (+0.95)
     • acoustic fit (+0.86)

2. Midnight Coding — LoRoom   (score: 6.19)
     • genre match (+3.0)
     • mood match (+1.5)
     • energy fit (+0.98)
     • acoustic fit (+0.71)

3. Focus Flow — LoRoom   (score: 4.78)
     • genre match (+3.0)
     • energy fit (+1.00)
     • acoustic fit (+0.78)

4. Spacewalk Thoughts — Orbit Bloom   (score: 3.30)
     • mood match (+1.5)
     • energy fit (+0.88)
     • acoustic fit (+0.92)

5. Requiem for Dawn — String Theory Ensemble   (score: 1.88)
     • energy fit (+0.93)
     • acoustic fit (+0.95)

```

```
Top recommendations for: High-Energy Pop
========================================

1. Sunrise City — Neon Echo   (score: 6.24)
     • genre match (+3.0)
     • mood match (+1.5)
     • energy fit (+0.92)
     • acoustic fit (+0.82)

2. Gym Hero — Max Pulse   (score: 4.92)
     • genre match (+3.0)
     • energy fit (+0.97)
     • acoustic fit (+0.95)

3. Rooftop Lights — Indigo Parade   (score: 3.01)
     • mood match (+1.5)
     • energy fit (+0.86)
     • acoustic fit (+0.65)

4. Basslight — Deep Circuit   (score: 1.91)
     • energy fit (+0.95)
     • acoustic fit (+0.96)

5. Iron Verdict — Grave Meridian   (score: 1.91)
     • energy fit (+0.93)
     • acoustic fit (+0.98)

```


```
Top recommendations for: Deep Intense Rock
==========================================

1. Storm Runner — Voltline   (score: 6.39)
     • genre match (+3.0)
     • mood match (+1.5)
     • energy fit (+0.99)
     • acoustic fit (+0.90)

2. Gym Hero — Max Pulse   (score: 3.44)
     • mood match (+1.5)
     • energy fit (+0.99)
     • acoustic fit (+0.95)

3. Basslight — Deep Circuit   (score: 1.93)
     • energy fit (+0.97)
     • acoustic fit (+0.96)

4. Iron Verdict — Grave Meridian   (score: 1.93)
     • energy fit (+0.95)
     • acoustic fit (+0.98)

5. Concrete Jungle — Ill Cadence   (score: 1.85)
     • energy fit (+0.93)
     • acoustic fit (+0.92)

```



```
Top recommendations for: Late-Night Jazz
========================================

1. Coffee Shop Stories — Slow Stereo   (score: 6.37)
     • genre match (+3.0)
     • mood match (+1.5)
     • energy fit (+0.98)
     • acoustic fit (+0.89)

2. Requiem for Dawn — String Theory Ensemble   (score: 1.93)
     • energy fit (+0.98)
     • acoustic fit (+0.95)

3. Library Rain — Paper Lanterns   (score: 1.86)
     • energy fit (+1.00)
     • acoustic fit (+0.86)

4. Spacewalk Thoughts — Orbit Bloom   (score: 1.85)
     • energy fit (+0.93)
     • acoustic fit (+0.92)

5. Focus Flow — LoRoom   (score: 1.73)
     • energy fit (+0.95)
     • acoustic fit (+0.78)

```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



