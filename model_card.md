# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests up to five songs from an 18-song catalog based on a user's stated genre preference, mood preference, target energy level, and acoustic texture preference. It is designed for classroom exploration of content-based filtering — not for real-world deployment. It assumes the user can describe their taste with a single genre and mood label, and that those labels match exactly what is in the catalog.

---

## 3. How the Model Works

Every song in the catalog is given a score by comparing it to the user's preferences across four features:

- **Genre** — if the song's genre matches what the user asked for, it earns up to 3 points (the biggest single reward). Genre defines the overall sound world — rock and lofi are fundamentally different even if they share a mood.
- **Mood** — if the mood matches (e.g., "happy", "chill", "intense"), the song earns 2 points. Mood sets the emotional context within a genre.
- **Energy** — songs score up to 1.5 points based on how close their energy is to the user's target. A workout user who wants energy 0.9 gets penalized for low-energy songs, and rewarded for close matches — not just "high" ones.
- **Acoustic texture** — if the user likes acoustic-sounding music, songs with high acousticness score higher (up to 0.7 points). If the user prefers electronic/produced sound, the score flips to reward low acousticness.

Once every song has a score, the list is sorted from highest to lowest and the top five are returned with the reasons for each point.

---

## 4. Data

The catalog contains **18 songs** across **14 genres**: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, metal, classical, reggae, folk, edm, and blues. Moods represented include happy, chill, intense, relaxed, focused, moody, hype, romantic, angry, melancholic, uplifting, nostalgic, euphoric, and sad.

Eight songs (ids 1–10) were part of the starter dataset. Eight additional songs (ids 11–18) were added to cover genres and moods missing from the original set. The catalog skews toward electronic and Western genres; non-Western music, classical traditions outside European forms, and genres like K-pop or cumbia are absent. Most rare genres (blues, reggae, metal, classical) are represented by exactly one song.

---

## 5. Strengths

- **Clean genre/mood separation.** The high genre weight (3.0) means profiles with a matching genre in the catalog always surface those songs first. Profile A (pop/happy) correctly led with Sunrise City (7.04) well ahead of the pack.
- **Energy proximity works as intended.** Profile B (lofi/focused, energy 0.4) surfaced Focus Flow at 7.05 — its near-perfect energy match (0.40 vs 0.40) contributed the maximum 1.5 points, confirming the formula distinguishes study music from workout music.
- **Fully transparent.** Every score decomposes into its four components. There are no hidden embeddings or black-box weights — a user can look at the reasons and understand exactly why a song ranked where it did.
- **Graceful fallback.** Profile E (country — genre not in catalog) still returned reasonable results by falling back to mood and energy signals, placing Rooftop Lights (indie pop, happy, energy 0.76) first rather than returning nothing.

---

## 6. Limitations and Bias

**Genre lock-in with small per-genre catalogs.** For genres with only one song (blues, reggae, metal, classical, folk, r&b, hip-hop, edm), the system always places that single song at #1 regardless of how well the other features match. Profile D (blues/sad, energy 0.90) returned Empty Porch Blues at #1 with a score of 5.76 — even though its energy (0.33) is almost the exact opposite of what the user wanted. The genre+mood bonus (5.0 combined points) completely overwhelmed the energy mismatch penalty. A real user wanting high-energy sad music would be poorly served.

**Binary categorical matching misses near-synonyms.** The system treats "chill" and "relaxed" as entirely different moods, even though most listeners experience them as interchangeable. A jazz user with mood "chill" gets 0 mood points from Coffee Shop Stories (mood "relaxed"), which misrepresents human perception.

**Genre weight dominance can erase energy signal.** With the default weights, Profile C (rock/intense, energy 0.90) ranked Gym Hero (#2) — a pop/intense song — ahead of Signal Peak (edm) and Iron Collapse (metal), purely because Gym Hero matched the mood. The energy scores for those three songs were nearly identical. The experiment (halving genre weight to 1.5, doubling energy to 3.0) reshuffled the pop list: Rooftop Lights jumped from #3 to #2 because its energy (0.76) was closer to 0.8 than Gym Hero's (0.93). This confirms that the default weights make the system genre-first, not vibe-first.

**No diversity enforcement.** The system can return the same artist twice (e.g., Neon Echo appears as Sunrise City and Night Drive Loop). A real recommender would penalize repeated artists in a single session.

**No handling of missing preferences.** If a user does not specify `likes_acoustic`, it defaults to `False`, silently biasing every recommendation toward electronic-sounding songs.

---

## 7. Evaluation

Five profiles were tested against the 18-song catalog:

| Profile | Top result | Score | Observation |
|---|---|---|---|
| A — High-Energy Pop | Sunrise City | 7.04 | Intuitive; 3 of 4 features matched |
| B — Chill Lofi Study | Focus Flow | 7.05 | Correct; only lofi/focused song in catalog |
| C — Deep Intense Rock | Storm Runner | 7.11 | Correct; only rock/intense song |
| D — Adversarial (Blues, high energy) | Empty Porch Blues | 5.76 | **Surprising** — genre+mood dominated despite large energy mismatch |
| E — Edge Case (Country, missing genre) | Rooftop Lights | 3.50 | Reasonable fallback; all scores below 4.0 signal low confidence |

**Most surprising finding:** Profile D exposed that a genre+mood bonus of 5.0 points can override an energy gap of 0.57, which translates to a 0.86-point energy penalty — a 6:1 ratio. The system will always prefer a genre-matching song that is completely wrong in energy over a better-fitting song in a different genre.

**Experiment result:** Halving the genre weight from 3.0 to 1.5 and doubling energy from 1.5 to 3.0 caused Rooftop Lights to leapfrog Gym Hero in Profile A, confirming the hypothesis. It also revealed that the top song (Sunrise City) is surprisingly robust: it still ranked #1 even under energy-first weights because it happens to also have good energy alignment.

---

## 8. Future Work

- **Multi-value preferences.** Allow `"genre": ["lofi", "ambient"]` so users can express overlapping taste without being locked into one genre.
- **Learned weights.** Instead of fixed weights, use a small number of listening events to adjust the importance of each feature per user.
- **Diversity enforcement.** Add a penalty for repeated artists in the top-k list.
- **Soft categorical matching.** Build a mood similarity map (e.g., "chill" ≈ "relaxed" ≈ "focused") so near-synonym moods earn partial credit instead of zero.
- **Confidence signal.** When no genre match exists (like Profile E), report a lower-confidence flag so the user knows the recommendations are less reliable.

---

## 9. Personal Reflection

*(Write 2–3 sentences here about what surprised you and how building this changed the way you think about real music apps like Spotify or YouTube Music. For example: what does it mean that a 3-point genre weight can override a half-point energy penalty? How would you design the weights differently if you were building this for real users?)*
