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

Real-world platforms like Spotify and YouTube combine two main approaches. Collaborative filtering looks at what similar users listened to. Content-based filtering compares the attributes of the songs themselves. Behind both is a two-step design: a model scores how well each item fits the user, and a separate ranking step builds the final list, handling things like variety and freshness. My version is a small content-based recommender that follows the same two steps. A scoring rule rates one song against the user's taste profile, and a ranking rule scores every song in the catalog, sorts them, and returns the top `k`. It prioritizes **genre** first, then **mood** and **energy**, with **acousticness** as a smaller tie-breaker. Each part of the score also produces a short reason, so every recommendation can be explained.

### Features used

**`Song`**

| Feature | Used in scoring? | How |
|---|---|---|
| `genre` | Yes | +2.0 for an exact match, +1.0 for a partial match (e.g. "pop" in "indie pop") |
| `mood` | Yes | +1.0 if it matches the user's favorite mood |
| `energy` | Yes | Up to +1.5 for closeness: `1.5 × (1 − abs(energy − target_energy))` |
| `acousticness` | Yes | Up to +0.5: rewards high acousticness if the user likes acoustic, low otherwise |
| `tempo_bpm` | No | Closely follows energy in this dataset, so it would count the same signal twice |
| `valence` | Yes (optional) | Up to +1.0 for closeness to `target_valence`, only if the profile sets it |
| `danceability` | No | Possible future addition; the profile has no matching preference yet |
| `id`, `title`, `artist` | No | Used only to identify and display songs |

**`UserProfile`**

- `favorite_genre`: the genre to match exactly
- `favorite_mood`: the mood to match exactly
- `target_energy`: the preferred energy level (0–1)
- `likes_acoustic`: whether the user prefers acoustic-sounding songs
- `target_valence` *(optional)*: how positive the user wants songs to sound (0–1)

### Algorithm recipe

**Scoring rule (one song):** start at 0 and add points:

| Rule | Points | Why this weight |
|---|---|---|
| Genre exact match | +2.0 | Genre is the most stable part of a person's taste, so it carries the most weight |
| Genre partial match | +1.0 | Related genres ("indie pop" for a pop fan) deserve some credit, not zero |
| Mood match | +1.0 | Mood changes with the moment, and the labels are sparse and exact, so it counts half as much as genre |
| Energy closeness | 0 to +1.5 | `1.5 × (1 − abs(energy − target_energy))`. Rewards being *close* to the target, not just high or low |
| Acoustic preference | 0 to +0.5 | `acousticness` if `likes_acoustic`, else `1 − acousticness`. Small because it mostly repeats energy |
| Valence closeness | 0 to +1.0 | `1 − abs(valence − target_valence)`, skipped if not set. Breaks ties between high-energy songs with different feelings (euphoric EDM vs. angry metal) |

The maximum score is 6.0. Genre beats mood by design: a genre match with average energy (2.0 + ~0.75) still outscores a mood-only match with perfect energy (1.0 + 1.5). Energy is the strongest numeric signal because every song gets a score for it, while genre and mood points only go to the few songs that match.

**Ranking rule (whole list):** score every song, sort from highest to lowest, break ties by title, and return the top `k` (default 5) together with each song's reasons.

### Data flow

```mermaid
flowchart LR
    A["<b>Input</b><br/>User prefs dict<br/>genre, mood, target_energy,<br/>likes_acoustic, target_valence"] --> C
    B["data/songs.csv<br/>→ load_songs()<br/>list of song dicts"] --> C
    C["<b>Process: the loop</b><br/>for each song:<br/>score_song(prefs, song)<br/>→ (score, reasons)"] --> D
    D["<b>Output: the ranking</b><br/>sort by score (ties by title)<br/>keep top k<br/>→ (song, score, explanation)"]
```

1. **Input:** `main.py` builds the user prefs dictionary, and `load_songs()` reads `data/songs.csv` into a list of song dictionaries (converting numeric columns to floats).
2. **Process:** `recommend_songs()` loops over *every* song and calls `score_song()` on it. Each song is judged on its own against the same profile, producing a score and a list of reasons such as `"genre match (+2.0)"`.
3. **Output:** the scored songs are sorted from highest to lowest, ties are broken by title, and the top `k` are returned as `(song, score, explanation)` for `main.py` to print.

### Expected biases

- **Genre dominates.** A genre match (+2.0) is worth as much as a perfect mood match and a perfect valence match combined. A happy pop fan will see an *intense* pop song (Gym Hero) above *Island Time*, an uplifting reggae song with almost the same positivity, simply because of the genre label.
- **Exact mood labels miss close matches.** "euphoric" and "uplifting" earn no mood points for a user who wants "happy," even though they mean nearly the same thing. Valence partly makes up for this, but only when the profile sets it.
- **Uneven catalog.** Lofi has 3 songs, while most genres have just 1. A lofi fan gets a full list of genre matches; a metal or folk fan gets one match and then songs picked mostly by energy.
- **Energy counts twice.** Acousticness closely follows energy in this data, so loud, produced songs and quiet, acoustic songs get a double reward or penalty. Mid-energy acoustic songs (e.g. Dusty Porch Swing) fall in between and can be overlooked.
- **The tie-break isn't neutral.** Breaking ties alphabetically always favors titles earlier in the alphabet, which is arbitrary from the listener's point of view.

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

Output of `python -m src.main` with the default pop/happy profile:

```
Loaded songs: 18
User profile: favorite_genre=pop, favorite_mood=happy, target_energy=0.8, likes_acoustic=False, target_valence=0.8

Top recommendations
============================================================
1. Sunrise City by Neon Echo
   pop / happy   Score: 5.84
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
     - produced, non-acoustic sound (+0.41)
     - positivity 0.84 vs target 0.80 (+0.96)
------------------------------------------------------------
2. Rooftop Lights by Indigo Parade
   indie pop / happy   Score: 4.75
     - related genre: indie pop (+1.0)
     - mood match (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
     - produced, non-acoustic sound (+0.33)
     - positivity 0.81 vs target 0.80 (+0.99)
------------------------------------------------------------
3. Gym Hero by Max Pulse
   pop / intense   Score: 4.75
     - genre match (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
     - produced, non-acoustic sound (+0.47)
     - positivity 0.77 vs target 0.80 (+0.97)
------------------------------------------------------------
4. Lightspeed Rave by Pulse Theory
   edm / euphoric   Score: 2.69
     - energy 0.95 vs target 0.80 (+1.28)
     - produced, non-acoustic sound (+0.49)
     - positivity 0.88 vs target 0.80 (+0.92)
------------------------------------------------------------
5. Golden Hour Bars by Kilo Static
   hip hop / confident   Score: 2.58
     - energy 0.68 vs target 0.80 (+1.32)
     - produced, non-acoustic sound (+0.44)
     - positivity 0.62 vs target 0.80 (+0.82)
------------------------------------------------------------
```

These results match what the recipe should produce. The only song that matches both genre and mood (Sunrise City) is clearly first. The two partial matches come next: Rooftop Lights (related genre + mood) and Gym Hero (genre only). Rooftop Lights edges ahead, 4.755 to 4.750, which both round to 4.75. After that there are no pop or happy songs left, so places 4–5 are decided only by energy, acousticness and positivity. Lightspeed Rave's upbeat, euphoric sound puts it ahead of darker high-energy songs like Iron Cathedral.

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



