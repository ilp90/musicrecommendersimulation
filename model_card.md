# Model Card: VibeFinder 1.0

---

## Model Name

**VibeFinder 1.0** — a content-based music recommender simulation built for classroom exploration of how scoring and ranking algorithms work.

---

## Goal / Task

VibeFinder tries to answer one question: *given what a user says they want right now, which songs in the catalog fit best?* It does not predict long-term taste or learn from listening history. It takes four stated preferences — genre, mood, target energy, and acoustic texture — and returns the five songs that most closely match all four at once. Each recommendation comes with a plain-language explanation of the points awarded.

---

## Data Used

- **Size:** 18 songs (10 starter + 8 added in Phase 2)
- **Features per song:** id, title, artist, genre, mood, energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1)
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, metal, classical, reggae, folk, edm, blues (14 total)
- **Moods represented:** happy, chill, intense, relaxed, focused, moody, hype, romantic, angry, melancholic, uplifting, nostalgic, euphoric, sad (14 total)
- **Limits:** Most rare genres have exactly one song. Non-Western genres (K-pop, Afrobeats, cumbia, etc.) are entirely absent. The dataset reflects a narrow slice of global music and would not serve diverse real-world users fairly. Feature values (energy, valence, etc.) were assigned by the developer, not measured from audio — they are estimates, not ground truth.

---

## Algorithm Summary

Each song is assigned a score by comparing it to the user's preferences across four features. Higher score = better match.

1. **Genre match (up to +3.0 pts):** If the song's genre equals the user's favorite genre, it gets 3 full points. Otherwise zero. Genre carries the highest weight because it defines the broadest sonic category — rock and lofi are incompatible even if they share a mood.

2. **Mood match (up to +2.0 pts):** If the song's mood label matches, it earns 2 points. Mood sets the emotional tone within a genre — a user who wants "focused" music is looking for something different than "happy," even within the same genre.

3. **Energy proximity (up to +1.5 pts):** The closer a song's energy is to the user's target, the more points it earns. The formula is `1.5 × (1 − |song_energy − target_energy|)`. This means a perfect match earns 1.5 pts; a song that is 0.5 away earns only 0.75 pts. This rewards closeness, not just "high energy."

4. **Acoustic fit (up to +0.7 pts):** If the user likes acoustic music, songs with high acousticness scores earn more. If the user prefers electronic/produced sound, low acousticness earns more. Maximum 0.7 pts.

All songs are scored independently, sorted from highest to lowest, and the top five are returned with their point breakdown as reasons.

---

## Observed Behavior / Biases

**Genre dominance overrides everything else.**
The genre+mood bonus combined can reach 5.0 points, while the maximum energy penalty for a completely wrong song is about 0.86 points. This means the system will always rank a genre-matching song first, even if its energy is the exact opposite of what the user wants. In testing, a "high-energy blues" user (energy target: 0.90) got Empty Porch Blues (energy: 0.33) as their #1 result — because the 5.0-point genre+mood bonus swamped the 0.86-point energy mismatch penalty.

**Single-song genre trap.**
For 8 of the 14 genres (blues, reggae, metal, classical, folk, r&b, hip-hop, edm), only one song exists. The system will always recommend that song first for users of those genres, no matter how poor the energy or mood fit. There is no alternative to offer.

**Binary mood matching ignores near-synonyms.**
"Chill" and "relaxed" earn zero shared points even though most listeners treat them as interchangeable. A jazz fan who wants "chill" music gets 0 mood points from Coffee Shop Stories (mood: "relaxed"), penalizing an otherwise excellent match.

**Silent acoustic default.**
If a user does not specify `likes_acoustic`, it defaults to `False` — silently biasing every score toward electronic-sounding songs without the user knowing.

**No artist diversity.**
The same artist can appear multiple times in the top five (e.g., Neon Echo's Sunrise City and Night Drive Loop). Real recommenders penalize this to avoid a monotonous feed.

---

## Evaluation Process

Five user profiles were tested:

| Profile | Genre / Mood / Energy | Top result | Score | Finding |
|---|---|---|---|---|
| A — High-Energy Pop | pop / happy / 0.8 | Sunrise City | 7.04 | Correct and intuitive — 3 of 4 features matched |
| B — Chill Lofi Study | lofi / focused / 0.4 | Focus Flow | 7.05 | Correct — energy was a near-perfect match (0.40 vs 0.40) |
| C — Deep Intense Rock | rock / intense / 0.9 | Storm Runner | 7.11 | Correct — only rock/intense song in catalog |
| D — Adversarial: Blues + high energy | blues / sad / 0.9 | Empty Porch Blues | 5.76 | Surprising — genre+mood overrode a 0.57 energy mismatch |
| E — Edge case: missing genre (country) | country / happy / 0.6 | Rooftop Lights | 3.50 | Fallback worked; low scores (all < 4.0) signal low confidence |

One weight-shift experiment was run: genre weight lowered from 3.0 to 1.5, energy weight raised from 1.5 to 3.0. For Profile A, Rooftop Lights leapfrogged Gym Hero because its energy (0.76) was closer to the target (0.80) than Gym Hero's (0.93). This confirmed that the default system is genre-first — not vibe-first — and that doubling the energy weight makes it cross-genre more willingly.

---

## Intended Use and Non-Intended Use

**Intended use:**
- Classroom exploration of content-based filtering concepts
- Learning how scoring functions, weights, and ranking interact
- Demonstrating that "AI recommendations" can be built from simple math and explained fully in plain language

**Not intended for:**
- Real users making real music decisions — the catalog is too small and too narrow
- Any production environment — there is no error handling for malformed input, no authentication, and no privacy controls
- Representing musical diversity — the dataset reflects a specific cultural viewpoint and would produce unfair or irrelevant results for users whose genres are not represented
- Learning or personalization — the system has no memory of past sessions and cannot improve over time

---

## Ideas for Improvement

1. **Soft categorical matching.** Build a mood similarity map (e.g., "chill" ≈ "relaxed" ≈ "focused" at 0.7 similarity) so near-synonym moods earn partial credit instead of zero. This alone would fix the biggest source of bad recommendations within a genre.

2. **Multi-value preferences.** Let users specify `"genre": ["lofi", "ambient"]` to express overlapping taste. The genre score would be the max match across all listed genres. This removes the single-genre lock-in without requiring a full collaborative filter.

3. **Confidence-aware output.** When no genre match exists in the catalog, report a warning alongside the results (e.g., "No country songs found — showing closest matches by mood and energy"). This makes the fallback behavior visible instead of silent.

---

## Personal Reflection

**Biggest learning moment:**
The adversarial Profile D test was the clearest "aha" moment of the project. I expected the system to degrade gracefully — recommending songs that are at least medium-energy when the user asked for high energy. Instead, the genre+mood match of 5.0 points completely overwhelmed the energy signal, and a song with nearly the opposite energy ended up ranked first. That revealed something important: the weights don't just balance features against each other — they determine *which features can ever be overruled*. With genre at 3.0, genre is essentially un-overrulable by any combination of other features. Spotify's real system likely has the opposite problem: collaborative filtering can discover that two users share taste across genres, so genre becomes less of a hard wall.

**On using AI tools:**
AI tools were most useful for drafting the boilerplate structure (CSV loading, dataclass fields, output formatting) and for pressure-testing the logic by suggesting adversarial profiles I wouldn't have thought to try. The moment I needed to double-check the AI was when it proposed the scoring formula — the proximity formula `1 − |Δ|` is correct, but it was worth manually computing a few examples to confirm that the range is actually 0 to 1 and that the weights add up to a meaningful maximum score. AI tools are fast at structure; humans still need to verify the math and ask "does this output make sense for a real person?"

**What surprised me about simple algorithms feeling like recommendations:**
The output genuinely *looks* personalized even though the logic is five lines of arithmetic. The reason is the explanation — "genre match (+3.0), mood match (+2.0), energy proximity (+1.47)" reads like a justification a human music curator would give. Real recommendation systems at Spotify or YouTube likely feel authoritative for the same reason: they surface a confident ranked list with no visible uncertainty, even when the underlying model is uncertain. The presentation of a ranked list creates a feeling of precision that the algorithm does not actually earn.

**What I would try next:**
The most interesting extension would be replacing the fixed genre weight with a *learned* weight. After 10 or 20 listening events (skips and completions), you could estimate whether a specific user cares more about genre or energy and adjust the weights per-user. That would turn VibeFinder from a static calculator into a simple adaptive system — and it would also expose whether the "right" weights differ between users, which I suspect they do significantly.
