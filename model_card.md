# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
