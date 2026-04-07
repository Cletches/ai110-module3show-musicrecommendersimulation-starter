# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

Give your model a short, descriptive name.  
6 Example: **VibeFinder 1.0**

**Moodsetter**

---

## 2. Intended Use

Describe what your recommender is designed to do and who it is for.

Prompts:

- What kind of recommendations does it generate
- What assumptions does it make about the user
- Is this for real users or classroom exploration

Moodsetter is a CLI-first simulation that recommends songs from a small catalog based on a user's preferred genre, mood, and energy level. It is built for classroom exploration — not real users. It assumes the user can describe their taste as a set of labeled preferences (e.g. favorite genre, target energy as a number between 0 and 1). It is not designed to handle ambiguous input, adapt over time, or serve listeners with tastes outside the catalog.

---

## 3. How the Model Works

Explain your scoring approach in simple language.
Prompts:

- What features of each song are used (genre, energy, mood, etc.)
- What user preferences are considered
- How does the model turn those into a score
- What changes did you make from the starter logic

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Every song in the catalog is given a score based on how closely it matches what the user said they like. The scoring works like a point system:

- A song gets +1.0 points if its genre matches the user's favorite genre, or +0.25 if it's a secondary genre the user also likes.
- A song gets +1.0 points if its mood matches, or +0.5 for a secondary mood.
- A song gets up to +2.0 points based on how close its energy level is to the user's target — the closer, the more points.
- Smaller bonuses are added for valence (positivity), danceability, acousticness, and tempo.

All points are added up. The five songs with the highest total score are returned as recommendations. The original starter used percentage-based weights that had to sum to 100%. This version switched to an additive point system, which is easier to reason about and adjust. Energy was also doubled in importance after testing showed it had the most impact on which songs felt right for different user types.

---

## 4. Data

Describe the dataset the model uses.

Prompts:

- How many songs are in the catalog
- What genres or moods are represented
- Did you add or remove data
- Are there parts of musical taste missing in the dataset

The catalog contains 20 songs stored in `data/songs.csv`. Each song has 10 attributes: id, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. The genres represented include pop, lofi, rock, hip-hop, jazz, synthwave, indie pop, classical, metal, country, r&b, funk, electronic, indie folk, dream pop, and ambient. Moods include happy, chill, intense, focused, moody, confident, melancholic, nostalgic, romantic, groovy, uplifting, and angry. The catalog was expanded from 10 to 20 songs during development. Missing from the dataset: Latin music, Afrobeats, K-pop, gospel, blues, and non-English language music — meaning users with those tastes will always receive poor genre matches.

---

## 5. Strengths

Where does your system seem to work well

Prompts:

- User types for which it gives reasonable results
- Any patterns you think your scoring captures correctly
- Cases where the recommendations matched your intuition

The system works best for users whose taste aligns with common catalog genres. In testing, three user types produced results that matched intuition well:

- **Gym goers** (high energy, electronic/intense) consistently received Pulse Grid and Storm Runner at the top — both high-BPM, high-energy tracks.
- **Late-night studiers** (lofi, focused, low energy) reliably received Focus Flow and Midnight Coding — both quiet, acoustic lofi tracks.
- **Romantic dinner listeners** (r&b, romantic) received Velvet Hours with a near-perfect score of 4.90 out of 5.0.

The additive point system is transparent — it is easy to look at a score and understand exactly why a song ranked where it did. The explanation string returned alongside each score also makes the reasoning visible to the user.

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly.

**Features it does not consider**

The system has no awareness of lyrics, language, cultural context, or listening history. It cannot tell the difference between two songs in the same genre that feel completely different, or adapt to what a user has already heard.

**Genres or moods that are underrepresented**

The 20-song catalog skews toward Western pop, rock, and hip-hop. Genres like Afrobeats, Latin, K-pop, gospel, and blues are entirely absent. Users whose taste falls outside the catalog always score 0 for genre — meaning their primary preference is effectively ignored every time.

**Cases where the system overfits to one preference**

Because genre match alone is worth +1.0 pts, a user with a strong genre preference will always see that genre dominate the top results, even when energy or mood are a poor fit. A hip-hop fan asking for calm, low-energy music will still get high-energy hip-hop ranked first.

**Ways the scoring might unintentionally favor some users**

Users whose preferred genre, mood, and energy level happen to align with the most common songs in the catalog get far better recommendations than users with niche tastes. The system also assumes users can express preferences as exact numbers (e.g. energy = 0.78), which favors technically literate users over casual listeners who just want something that "feels right."

---

## 7. Evaluation

Seven edge case profiles were tested using automated pytest tests, plus three representative user types run manually:

- **Empty profile** — confirmed all songs score equally when no preferences are given.
- **Genre/energy conflict** (ambient genre + high energy target) — genre match still won, confirming the point hierarchy works as intended.
- **Gym goer, late-night studier, romantic dinner** — all three returned top results that matched the expected song intuitively.
- **Unknown genre** (bossa nova) — confirmed the system falls back gracefully to numeric scoring rather than crashing.

What was surprising: Concrete Jungle ranked #1 across all four energy targets tested (0.2, 0.5, 0.78, 0.95) because its genre and mood match combined (+2.0 pts) was strong enough to override a poor energy fit. This revealed that the genre lock-in effect persists even after doubling energy's importance.

---

## 8. Future Work

- **Diversity penalty** — prevent the top 5 from all being the same genre by adding a small score deduction for repeated genres in the results.
- **Context-aware profiles** — allow different profiles for different situations (studying, working out, commuting) rather than a single static preference set.
- **Mood proximity** — treat moods as related rather than exact strings (e.g. "happy" and "uplifting" should be closer than "happy" and "angry").
- **Expand the catalog** — add songs from underrepresented genres (Afrobeats, Latin, K-pop) so the system works fairly for more user types.
- **User feedback loop** — let users thumbs-up or thumbs-down a recommendation and adjust weights accordingly.

---

## 9. Personal Reflection

Building Moodsetter made it clear that even a simple scoring system encodes assumptions about what matters, and those assumptions shape who the system works well for. Doubling energy's weight changed the rankings for users 2–5 but not user 1, which showed how a single weight change can have uneven effects depending on how well a user's profile matches the catalog. The most interesting discovery was how genre lock-in persists even when energy dominates: once a song earns the top genre bonus, numeric features alone rarely overcome it. Real music apps like Spotify likely face the same tension at scale, which is probably why they inject randomness and diversity mechanisms that this system lacks entirely. Using the AI tool was very helpful as it created certain edge cases that I overlooked, it helped to improve my algorithm. If the project was extended, I would like to design it to be close to a real world recommender system
