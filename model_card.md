# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**TuneJudge 1.0**: a small recommender that "judges" every song with a points scorecard.

---

## 2. Intended Use  

**Goal:** TuneJudge suggests 5 songs a user will probably enjoy. It does this by comparing each song's features to the user's taste profile. It doesn't learn from listening history. It only uses what the user says they like.

**Assumptions about the user:**
- They have one favorite genre and one favorite mood.
- They can describe their taste as numbers (energy and positivity from 0 to 1).
- They type genre and mood names exactly as the catalog spells them.

**Intended use:**
- Classroom exploration of how recommenders work.
- Experimenting with weights and seeing how rankings change.
- Learning where bias can come from in simple scoring systems.

**Not intended for:**
- Real users or a real music app. The catalog is tiny and made up.
- Judging the quality of real artists or songs.
- Any decision that matters to someone, like what music a business plays or promotes.
- Users with mixed or changing tastes. The profile only holds one genre and one mood.

---

## 3. How the Model Works  

Think of the recommender as a judge holding a scorecard. You tell it what you like: a favorite genre, a favorite mood, how energetic you want the music to be, whether you like acoustic or more electronic, produced sounds, and (optionally) how upbeat or positive you want songs to feel. The judge then goes through every song in the catalog one at a time and gives it points.

- **Genre is worth the most.** A song in your exact genre gets 2 points. A closely related genre (like "indie pop" when you said "pop") gets 1 point.
- **Mood is worth 1 point** if it matches exactly. It counts less than genre because mood changes from moment to moment, while genre is a steadier part of someone's taste.
- **Energy is about closeness, not loudness.** A song whose energy is right at your target gets the full 1.5 points, and it gets fewer the further away it is. Someone who wants calm music isn't pushed toward the loudest tracks.
- **Acoustic preference adds up to half a point**, in favor of either acoustic or produced sound, depending on what you said you like.
- **Positivity adds up to 1 point** for songs that feel as upbeat (or as gloomy) as you asked for. This helps tell apart songs that are equally energetic but feel very different, like a euphoric dance track and an angry metal song.

Once every song has a score, the judge sorts them from highest to lowest and shows you the top five. If two songs tie, they are ordered alphabetically by title. Every recommendation comes with its scorecard, a list of exactly which rules earned points and how many, so you can always see *why* a song was picked.

**Changes from the starter logic:** the starter returned the first few songs in the file with a placeholder explanation. I replaced it with the point system above, added partial credit for related genres, added the optional positivity preference, and made every recommendation list the reasons behind its score.

---

## 4. Data  

**Size:** 18 songs in `data/songs.csv`. The starter file had 10. I added 8 more to cover new genres and moods.

**Features per song:** title, artist, genre, mood, energy, tempo, valence (positivity), danceability, and acousticness. Later I added 5 advanced features: popularity (0–100), release decade, detailed mood tags (like "nostalgic" or "late-night"), instrumentalness (how much of the song has no vocals), and language. The scoring uses everything except tempo and danceability. The advanced features only count when a user's profile asks for them.

**What's covered:** 15 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, classical, metal, country, r&b, edm, folk, reggae) and 14 moods (happy, chill, intense, relaxed, moody, focused, confident, peaceful, angry, nostalgic, romantic, euphoric, sad, uplifting).

**Limits:**
- It's tiny. Real apps have millions of songs.
- It's uneven. Lofi has 3 songs, pop has 2, and the other 13 genres have only 1 each.
- Some combinations are missing. No song is both loud and acoustic. Only one song is quiet and sad.
- The songs and numbers are made up, not measured from real audio.
- Each song has only one genre and one mood. Real songs often mix several.
- It leaves out lyrics, language, culture, release year and popularity.

---

## 5. Strengths  

- **Clear, consistent tastes work well.** The pop, lofi and rock profiles all got the "obvious" best song at #1.
- **It works best when the catalog has depth.** The lofi fan got three lofi songs in a row, then other calm, acoustic music. It felt like a real playlist.
- **Energy closeness works as planned.** A calm listener isn't pushed toward loud songs, and a loud listener isn't pushed toward quiet ones.
- **Positivity separates songs that feel different.** It ranks dark metal above euphoric EDM for a darker listener.
- **Every pick explains itself.** Each song lists exactly which rules gave it points. That made it easy to spot when something went wrong.

---

## 6. Limitations and Bias 

The system quietly ignores listeners whose taste combines traits the catalog never puts together, such as someone who wants energetic *and* acoustic music (think unplugged rock or bluegrass). In `data/songs.csv`, every song with energy above 0.7 has an acousticness of 0.35 or lower, so when I tested an "acoustic rocker" profile (rock, intense, energy 0.9, likes acoustic), all five recommendations were electric or electronic tracks with acousticness between 0.02 and 0.18. The scoring makes this worse: closeness in energy is worth up to 1.5 points (3.0 in my weight-shift experiment), while the acoustic preference is worth at most 0.5, so being the right loudness always beats being the right sound, and the explanation only shows a tiny "acoustic sound (+0.05)" without telling the user their preference couldn't be met. The same pattern hurt the "Sad Banger" profile, where the only sad song in the catalog (Paper Boats) was pushed down, or out of the top 5 entirely, because its energy was too low. In effect, users whose taste matches one of the catalog's two main clusters (loud and produced, or quiet and acoustic) are served well, while everyone else gets a filter bubble of whatever matches their energy level.

**Other patterns I noticed:**
- **Genre outweighs feeling.** A genre match (2 points) is worth as much as a perfect mood match and perfect positivity combined.
- **Popular genres get more.** A lofi fan gets 3 genre matches. A folk or metal fan gets 1, then filler.
- **No variety rule.** Two of the lofi fan's top 3 songs are by the same artist.
- **Moods must match exactly.** "happy" gets no credit for "euphoric" or "uplifting." (Capital letters and extra spaces used to break matching too. That's now fixed.)
- **Input checks were missing.** An energy target of 1.5 used to give songs negative points. Targets are now clamped to 0–1.

---

## 7. Evaluation  

I ran the recommender (`python -m src.main`) on seven user profiles. For each one I checked whether the top 5 made sense for that listener, and whether the listed reasons actually explained the ranking. All outputs below use the main weights (genre 2.0, mood 1.0, energy 1.5, acoustic 0.5, valence 1.0). Two edge cases exposed bugs that I then fixed, so for those I show the output both before and after the fix.

**Profiles tested:**

| Profile | What it tests |
|---|---|
| High-Energy Pop | A mainstream listener: pop, happy, loud, produced, upbeat |
| Chill Lofi | The opposite end: quiet, acoustic, calm |
| Deep Intense Rock | A genre with only one song in the catalog |
| Sad Banger *(edge case)* | Conflicting wishes: sad and gloomy, but also loud and energetic |
| Capitalized Genre *(edge case)* | The same taste as High-Energy Pop, but typed "Pop" and "Happy" with capital letters |
| Out-of-Range Energy *(edge case)* | An impossible energy target of 1.5 on a 0–1 scale |
| Empty Profile *(edge case)* | A user who gives no preferences at all |

**What surprised me:**

- **Gym Hero, a pop workout song, appeared in 5 of the 7 lists**, including for the rock fan. (Explained below.)
- **The "Sad Banger" user's #1 pick was the happiest-sounding song in the catalog.** Lightspeed Rave is euphoric (positivity 0.88), but it's the only EDM song, and the genre bonus outweighed the fact that it feels completely wrong.
- **A capital letter was enough to break matching.** Typing "Pop" instead of "pop" made the system act as if the user had no favorite genre or mood at all. (Fixed. See below.)
- **My weight-shift experiment (less genre, more energy) made things worse, not better.** The one sad song dropped out of the sad listener's list entirely (see the README, Experiment 1).

### High-Energy Pop

```
User profile: favorite_genre=pop, favorite_mood=happy, target_energy=0.8, likes_acoustic=False, target_valence=0.8
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

Works as expected. The only pop + happy song is first, followed by the two partial matches. Once the pop and happy songs run out, places 4–5 go to upbeat, high-energy songs.

### Chill Lofi

```
User profile: favorite_genre=lofi, favorite_mood=chill, target_energy=0.35, likes_acoustic=True, target_valence=0.6
============================================================
1. Library Rain by Paper Lanterns
   lofi / chill   Score: 5.93
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.35 vs target 0.35 (+1.50)
     - acoustic sound (+0.43)
     - positivity 0.60 vs target 0.60 (+1.00)
------------------------------------------------------------
2. Midnight Coding by LoRoom
   lofi / chill   Score: 5.71
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.42 vs target 0.35 (+1.40)
     - acoustic sound (+0.35)
     - positivity 0.56 vs target 0.60 (+0.96)
------------------------------------------------------------
3. Focus Flow by LoRoom
   lofi / focused   Score: 4.80
     - genre match (+2.0)
     - energy 0.40 vs target 0.35 (+1.42)
     - acoustic sound (+0.39)
     - positivity 0.59 vs target 0.60 (+0.99)
------------------------------------------------------------
4. Spacewalk Thoughts by Orbit Bloom
   ambient / chill   Score: 3.80
     - mood match (+1.0)
     - energy 0.28 vs target 0.35 (+1.40)
     - acoustic sound (+0.46)
     - positivity 0.65 vs target 0.60 (+0.95)
------------------------------------------------------------
5. Coffee Shop Stories by Slow Stereo
   jazz / relaxed   Score: 2.81
     - energy 0.37 vs target 0.35 (+1.47)
     - acoustic sound (+0.45)
     - positivity 0.71 vs target 0.60 (+0.89)
------------------------------------------------------------
```

Works well. All three lofi songs fill the top 3. Library Rain scores almost perfectly because its energy and positivity hit the targets exactly. The next places go to other calm, acoustic songs (ambient, jazz), which a lofi listener would likely enjoy.

### Deep Intense Rock

```
User profile: favorite_genre=rock, favorite_mood=intense, target_energy=0.9, likes_acoustic=False, target_valence=0.45
============================================================
1. Storm Runner by Voltline
   rock / intense   Score: 5.90
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.91 vs target 0.90 (+1.48)
     - produced, non-acoustic sound (+0.45)
     - positivity 0.48 vs target 0.45 (+0.97)
------------------------------------------------------------
2. Gym Hero by Max Pulse
   pop / intense   Score: 3.61
     - mood match (+1.0)
     - energy 0.93 vs target 0.90 (+1.46)
     - produced, non-acoustic sound (+0.47)
     - positivity 0.77 vs target 0.45 (+0.68)
------------------------------------------------------------
3. Iron Cathedral by Grave Signal
   metal / angry   Score: 2.67
     - energy 0.97 vs target 0.90 (+1.40)
     - produced, non-acoustic sound (+0.48)
     - positivity 0.24 vs target 0.45 (+0.79)
------------------------------------------------------------
4. Night Drive Loop by Neon Echo
   synthwave / moody   Score: 2.62
     - energy 0.75 vs target 0.90 (+1.27)
     - produced, non-acoustic sound (+0.39)
     - positivity 0.49 vs target 0.45 (+0.96)
------------------------------------------------------------
5. Lightspeed Rave by Pulse Theory
   edm / euphoric   Score: 2.49
     - energy 0.95 vs target 0.90 (+1.43)
     - produced, non-acoustic sound (+0.49)
     - positivity 0.88 vs target 0.45 (+0.57)
------------------------------------------------------------
```

Shows that the catalog is uneven. There's only one rock song, so after Storm Runner the list falls back to mood (Gym Hero, an intense *pop* song) and then to energy alone. Iron Cathedral (metal) at #3 makes sense, but Lightspeed Rave (euphoric EDM) at #5 doesn't really fit an "intense rock" listener.

### Edge: Sad Banger (conflicting mood vs. energy)

```
User profile: favorite_genre=edm, favorite_mood=sad, target_energy=0.9, likes_acoustic=False, target_valence=0.2
============================================================
1. Lightspeed Rave by Pulse Theory
   edm / euphoric   Score: 4.24
     - genre match (+2.0)
     - energy 0.95 vs target 0.90 (+1.43)
     - produced, non-acoustic sound (+0.49)
     - positivity 0.88 vs target 0.20 (+0.32)
------------------------------------------------------------
2. Iron Cathedral by Grave Signal
   metal / angry   Score: 2.84
     - energy 0.97 vs target 0.90 (+1.40)
     - produced, non-acoustic sound (+0.48)
     - positivity 0.24 vs target 0.20 (+0.96)
------------------------------------------------------------
3. Storm Runner by Voltline
   rock / intense   Score: 2.65
     - energy 0.91 vs target 0.90 (+1.48)
     - produced, non-acoustic sound (+0.45)
     - positivity 0.48 vs target 0.20 (+0.72)
------------------------------------------------------------
4. Paper Boats by Hollow Pines
   folk / sad   Score: 2.63
     - mood match (+1.0)
     - energy 0.30 vs target 0.90 (+0.60)
     - produced, non-acoustic sound (+0.05)
     - positivity 0.22 vs target 0.20 (+0.98)
------------------------------------------------------------
5. Night Drive Loop by Neon Echo
   synthwave / moody   Score: 2.38
     - energy 0.75 vs target 0.90 (+1.27)
     - produced, non-acoustic sound (+0.39)
     - positivity 0.49 vs target 0.20 (+0.71)
------------------------------------------------------------
```

**The genre match overpowers what the user actually asked for.** The user wants sad, gloomy music (valence 0.2), but the top pick is a *euphoric* EDM song (valence 0.88), only because the genre label matches (+2.0). The only sad song in the catalog, Paper Boats, comes 4th, because its low energy costs it more than the mood match earns.

### Edge: Capitalized Genre ('Pop' vs. 'pop')

```
User profile: favorite_genre=Pop, favorite_mood=Happy, target_energy=0.8, likes_acoustic=False
============================================================
1. Sunrise City by Neon Echo
   pop / happy   Score: 1.88
     - energy 0.82 vs target 0.80 (+1.47)
     - produced, non-acoustic sound (+0.41)
------------------------------------------------------------
2. Night Drive Loop by Neon Echo
   synthwave / moody   Score: 1.81
     - energy 0.75 vs target 0.80 (+1.42)
     - produced, non-acoustic sound (+0.39)
------------------------------------------------------------
3. Storm Runner by Voltline
   rock / intense   Score: 1.78
     - energy 0.91 vs target 0.80 (+1.33)
     - produced, non-acoustic sound (+0.45)
------------------------------------------------------------
4. Gym Hero by Max Pulse
   pop / intense   Score: 1.78
     - energy 0.93 vs target 0.80 (+1.30)
     - produced, non-acoustic sound (+0.47)
------------------------------------------------------------
5. Lightspeed Rave by Pulse Theory
   edm / euphoric   Score: 1.77
     - energy 0.95 vs target 0.80 (+1.28)
     - produced, non-acoustic sound (+0.49)
------------------------------------------------------------
```

**Text matching is case-sensitive, so a capital letter breaks it.** "Pop" ≠ "pop" and "Happy" ≠ "happy", so no genre or mood points are awarded at all. The list falls back to energy only: Gym Hero, a pop song, drops below a rock song, and the top five are separated by just 0.11 points.

**After the fix** (labels are now lowercased and trimmed before comparing):

```
User profile: favorite_genre=Pop, favorite_mood=Happy, target_energy=0.8, likes_acoustic=False
============================================================
1. Sunrise City by Neon Echo
   pop / happy   Score: 4.88
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
     - produced, non-acoustic sound (+0.41)
------------------------------------------------------------
2. Gym Hero by Max Pulse
   pop / intense   Score: 3.78
     - genre match (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
     - produced, non-acoustic sound (+0.47)
------------------------------------------------------------
3. Rooftop Lights by Indigo Parade
   indie pop / happy   Score: 3.77
     - related genre: indie pop (+1.0)
     - mood match (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
     - produced, non-acoustic sound (+0.33)
------------------------------------------------------------
4. Night Drive Loop by Neon Echo
   synthwave / moody   Score: 1.81
     - energy 0.75 vs target 0.80 (+1.42)
     - produced, non-acoustic sound (+0.39)
------------------------------------------------------------
5. Storm Runner by Voltline
   rock / intense   Score: 1.78
     - energy 0.91 vs target 0.80 (+1.33)
     - produced, non-acoustic sound (+0.45)
------------------------------------------------------------
```

Sunrise City is back on top with its genre and mood points, and the pop songs return to the top 3. The scores are lower than in High-Energy Pop only because this profile doesn't set a positivity target.

### Edge: Out-of-Range Energy (1.5)

```
User profile: favorite_genre=classical, target_energy=1.5
============================================================
1. Moonlit Sonata Redux by Clara Vey
   classical / peaceful   Score: 1.52
     - genre match (+2.0)
     - energy 0.18 vs target 1.50 (+-0.48)
------------------------------------------------------------
2. Iron Cathedral by Grave Signal
   metal / angry   Score: 0.70
     - energy 0.97 vs target 1.50 (+0.70)
------------------------------------------------------------
3. Lightspeed Rave by Pulse Theory
   edm / euphoric   Score: 0.67
     - energy 0.95 vs target 1.50 (+0.67)
------------------------------------------------------------
4. Gym Hero by Max Pulse
   pop / intense   Score: 0.65
     - energy 0.93 vs target 1.50 (+0.65)
------------------------------------------------------------
5. Storm Runner by Voltline
   rock / intense   Score: 0.61
     - energy 0.91 vs target 1.50 (+0.61)
------------------------------------------------------------
```

**There's no input check, so scores go negative.** A target outside the 0–1 range makes the energy formula subtract points: Moonlit Sonata gets "+-0.48" and stays first only because of its genre bonus. Every other song is ranked purely by "loudest wins," which is exactly what closeness scoring was meant to prevent.

**After the fix** (targets are now clamped to the 0–1 range):

```
User profile: favorite_genre=classical, target_energy=1.5
============================================================
1. Moonlit Sonata Redux by Clara Vey
   classical / peaceful   Score: 2.27
     - genre match (+2.0)
     - energy 0.18 vs target 1.00 (+0.27)
------------------------------------------------------------
2. Iron Cathedral by Grave Signal
   metal / angry   Score: 1.46
     - energy 0.97 vs target 1.00 (+1.46)
------------------------------------------------------------
3. Lightspeed Rave by Pulse Theory
   edm / euphoric   Score: 1.42
     - energy 0.95 vs target 1.00 (+1.42)
------------------------------------------------------------
4. Gym Hero by Max Pulse
   pop / intense   Score: 1.40
     - energy 0.93 vs target 1.00 (+1.40)
------------------------------------------------------------
5. Storm Runner by Voltline
   rock / intense   Score: 1.36
     - energy 0.91 vs target 1.00 (+1.36)
------------------------------------------------------------
```

No song gets negative points anymore. The target of 1.5 is treated as 1.0, the loudest possible, and the reasons show the clamped target. The list is still mostly loud songs, but now that's because the user really asked for maximum energy, not because of a math error.

### Edge: Empty Profile

```
User profile: (none)
============================================================
1. Coffee Shop Stories by Slow Stereo
   jazz / relaxed   Score: 0.00
     - (no preferences matched)
------------------------------------------------------------
2. Dusty Porch Swing by Willow Creek Band
   country / nostalgic   Score: 0.00
     - (no preferences matched)
------------------------------------------------------------
3. Focus Flow by LoRoom
   lofi / focused   Score: 0.00
     - (no preferences matched)
------------------------------------------------------------
4. Golden Hour Bars by Kilo Static
   hip hop / confident   Score: 0.00
     - (no preferences matched)
------------------------------------------------------------
5. Gym Hero by Max Pulse
   pop / intense   Score: 0.00
     - (no preferences matched)
------------------------------------------------------------
```

**With no preferences, the tie-break decides everything.** Every song scores 0.00, so the "recommendations" are just the first five titles alphabetically. A real system should say it doesn't know enough yet, or fall back to popular or varied picks, instead of pretending to recommend.

### Comparing profiles side by side

**High-Energy Pop vs. Chill Lofi:** these two lists don't share a single song. The pop list is all loud, produced tracks (energy 0.68–0.95, acousticness 0.35 or lower), while the lofi list is all quiet, acoustic ones (energy 0.28–0.42, acousticness 0.71–0.92). That makes sense: the two users ask for opposite energy levels *and* opposite sounds, so they land on opposite sides of the catalog.

**High-Energy Pop vs. Deep Intense Rock:** both users want loud, non-acoustic music, so they share two songs (Gym Hero and Lightspeed Rave). The difference is *feel*. The pop fan wants bright music (positivity 0.8) and gets cheerful picks like Rooftop Lights, while the rock fan wants something darker (positivity 0.45) and gets Iron Cathedral and Night Drive Loop instead. Gym Hero moves *up* from #3 to #2 for the rock fan because its mood label, "intense," matches the rock fan's mood exactly.

**Chill Lofi vs. Deep Intense Rock:** again no overlap, as expected for opposite tastes. What's different is the *shape* of the scores. The lofi fan's top three are all close together (5.93, 5.71, 4.80) because the catalog has three lofi songs. The rock fan's list drops sharply after #1 (5.90, then 3.61) because there is only one rock song. So the lofi fan gets three good matches, and the rock fan gets one good match followed by stand-ins.

**Deep Intense Rock vs. Sad Banger:** these users want the same loudness and the same produced sound, so 4 of their 5 songs are the same. Only the *order* changes. Lightspeed Rave jumps from #5 to #1 because its "edm" label matches the Sad Banger's genre. Iron Cathedral moves up from #3 to #2 because its dark sound (positivity 0.24) fits a sad listener better. The positivity setting did its job on Iron Cathedral, but the genre bonus was stronger.

**High-Energy Pop vs. Capitalized Genre:** these are meant to be the *same person*. The only difference is capital letters (and no positivity setting). A human would expect the same list, but the top score fell from 5.84 to 1.88. Rooftop Lights disappeared, and a rock song (Storm Runner) ranked above Gym Hero, a pop song. This result is *not* valid. It shows the system compared text exactly, letter for letter, instead of understanding it. After the case fix, the two lists line up again.

**Deep Intense Rock vs. Out-of-Range Energy:** these lists look surprisingly alike (Iron Cathedral, Lightspeed Rave, Gym Hero and Storm Runner appear in both), even though one user asked for rock and the other for classical. An energy target of 1.5 can never be reached, so the system just rewards whatever is loudest, much like a high-energy rock fan. Before the fix, the classical song only stayed at #1 because of its genre bonus, despite getting *negative* energy points.

**Empty Profile vs. everyone else:** every song scores 0, so the list is just the first five titles in alphabetical order. It's the only list that doesn't respond to the user at all, which shows that without preferences, the tie-break rule silently becomes the whole recommender.

### Why does "Gym Hero" keep showing up for people who want happy pop?

Think of the recommender as a judge scoring each song for a "happy pop" listener. Gym Hero is labeled **pop**, so it immediately gets the biggest bonus available (2 points). It's also **loud** like the listener asked for, **polished rather than acoustic**, and fairly **cheerful-sounding** (0.77 on a 0–1 positivity scale, close to the 0.8 the listener wanted). So it collects points on almost every rule.

The only thing "wrong" with it is its mood label, "intense" instead of "happy," and a mood match is worth just 1 point, half as much as genre. So the judge effectively says: *"Right genre, right energy, right sound, nearly the right feeling. Just the wrong mood label."* It loses only one point and still finishes #3.

The catalog makes this worse. There are only two songs labeled pop, so Gym Hero is one of only two options that can earn the genre bonus at all. It also shows up for the rock fan, for a different reason: it's one of the loudest songs in the catalog *and* its mood is "intense." For someone who wants upbeat dance-pop, Gym Hero is a reasonable suggestion. For someone who specifically wants *happy* music, it shows that a mood match doesn't count for enough.

### Unit tests

The starter tests passed from the start, but only by luck. The `Recommender` class still returned the first songs in the list without scoring them, and the test's pop song just happened to be listed first. When I reversed the song order, a pop fan got the lofi song as #1. I connected the class to the real scoring function and added two tests: one checks that ranking doesn't depend on list order, and one checks messy input (capital letters, out-of-range targets, "False" as text). All 4 tests pass.

**Summary:** the three normal profiles get sensible results, especially when the catalog has several songs in the user's genre (lofi). The edge cases found four weaknesses: genre outweighs mood and feel, text matching was case-sensitive (fixed), targets outside 0–1 weren't checked (fixed), and an empty profile produces alphabetical "recommendations."

---

## 8. Future Work  

1. **Make matching smarter.** Give partial credit to related genres (rock ↔ metal) and similar moods (happy ↔ euphoric ↔ uplifting).
2. **Balance the weights.** Raise mood and positivity so they can beat a genre label when they disagree. The weight-shift experiment showed that energy is the wrong thing to boost.
3. **Add variety and honesty to the list.** Allow at most one song per artist in the top 5. Warn the user when a preference couldn't be met, for example "No loud acoustic songs found."

Smaller fix: show a "tell me more about your taste" message for an empty profile instead of an alphabetical list.

---

## 9. Personal Reflection  

**Biggest learning moment.** My weight-shift experiment was the big one. I was sure genre was the problem, so I cut its weight in half and doubled energy. The results got worse. The only sad song dropped out of the sad listener's list completely. That taught me to test a change before trusting my guess about it. Fixing one weight can break something else.

**How AI tools helped, and when I double-checked.** AI helped me brainstorm the scoring recipe, add new songs to the dataset, write the Python functions, and format the output. It saved a lot of time. But I still had to check its work:
- It once told me two songs were tied at 4.75. When the code ran, the scores were really 4.755 and 4.750, so there was no tie.
- The run command in the README (`python -m src.main`) didn't work until the import was fixed.
- The extra songs it made are invented. I had to remember they aren't real data.

Running the code and reading the actual numbers was always the final check.

**What surprised me.** Five simple rules and some addition felt like real recommendations. The lofi list looked like a playlist a friend would make. The "reasons" made it feel even smarter, because each song explained itself. But the edge cases showed it doesn't understand music at all. One capital letter was enough to break it. It just follows rules, and those rules work only when the user fits the catalog.

**What I'd try next.** I'd use a bigger, real dataset with measured audio features. I'd let users pick more than one genre. I'd add likes and skips so the profile can learn over time. I'd also add a variety rule so the top 5 doesn't repeat the same artist.  
