## 4b. The science: what the numbers say

The prose "fingerprints" in section 4 are easy to repeat and rarely checked. So we checked them. We built a corpus of everything Satoshi Nakamoto wrote (61 emails and 543 forum posts, about 62,000 words, plus the white paper) and set it against Elon Musk's X posts (89,485 original posts, about 646,000 words), his Tesla blog posts, and 48 of his published emails and text messages. We also added 2006-09 cryptography-list writers, BitcoinTalk posters, Hal Finney, Nick Szabo and Adam Back as controls. Every number below comes from code in the [open repo]([REPO LINK]). You can rerun it.

![Double space after a full stop, Satoshi vs Elon vs peers](stylometry/charts/chart1_double_space.png)

### The double space: Satoshi yes, Elon no (and it's less special than it sounds)

We counted every sentence boundary *inside a line* (a period, then a capital letter) and asked how often two spaces followed.

- **Satoshi: 1,824 of 1,913 boundaries, 95.3%** (95% CI 94.3-96.2%). Forum posts 95.2%, public emails 97.7%, private emails 92.6%. The habit is real, strong and consistent across 2008-2010.
- **Elon: 0 of 231** in the raw-text posts we could test (CI 0-1.6%), and 0 in each period (2012-17: 0/77, 2018-22: 0/88, 2023-26: 0/66). The big scrape and the blog copies strip extra spaces, so they cannot be tested.
- **The habit was common in Satoshi's world.** Among 87 writers on the 2006-09 cryptography list, 43% double-spaced at least half the time, and Adam Back did it 79 times out of 79. Hal Finney: 44%. It was a standard habit for people who learned to type on typewriters.

**What this means:** a double space fits Satoshi's generation and fits many cypherpunks. It does not point to Elon. The caveat in his favor is that an iPhone silently turns double-space into ". ", so a phone poster can't easily show the habit. Not matching is therefore weak evidence against, not proof. Matching would have been interesting; it didn't match.

### British vs American spelling: Satoshi mixed, Elon American

![Spelling and function-word similarity](stylometry/charts/chart2_spelling_and_delta.png)

We counted 833 British/American word pairs (colour/color, realise/realize, centre/center, and so on).

- **Satoshi: 32 British forms vs 66 American, so 33% British.** It's not "consistently British". He wrote *favour* in the white paper but also *realizes* and *characterized*. Across his posts, *optimise/optimize* was 12 vs 11, *decentralise/decentralize* 2 vs 7, *colour/color* 2 vs 4, *neighbour* 5 vs 0, *minimize* 0 vs 9, *realize* 0 vs 6. He used "while" 47 times and "whilst" never (Elon: 1 "whilst" against 332 "while"). Only 29 of his 605 documents contain a British spelling at all.
- **Elon: 13 British vs 1,993 American in his own posts, 0.65%.** And those 13 are a ceiling: 6 are "cancelled" or "acknowledgement" (also accepted in American English), and 2 are the Labour Party. The "South African" words are all American: colour 0 of 45 uses, centre 0 of 130, organise 0 of 150, realise 0 of 157, and *optimise*, the word Satoshi spelled British more than half the time (12 of 23), 0 of 73.
- **Other people on the same 2006-09 lists** were 13% British, and BitcoinTalk posters 10%. So Satoshi's ~33% is higher than his peers (mildly distinctive: maybe an American-trained writer from the Commonwealth, maybe a deliberate mix). Elon's 0.65% is far from it.

**What this means:** the mixture does fit "someone who learned British spelling and writes mostly American". It does not fit Elon's recorded writing, which is American at every point we can measure.

### Did Elon "switch" from British to American?

![Elon's British-spelling share by era](stylometry/charts/chart3_era_shift.png)

A popular claim says Elon grew up writing South African English and went American after leaving for Canada (1989) and the US. We split his writing by era and treated that claim as unproven.

| Era | British / American spelling words | % British (95% CI) |
|---|---|---|
| 2006 Tesla blog | 0 / 4 | too few to tell |
| 2010-12 | 0 / 4 | too few to tell |
| 2013-16 | 3 / 80 | 3.6% (1.2-10%) |
| 2017-20 | 2 / 368 | 0.5% |
| 2021-24 | 4 / 1,037 | 0.4% |
| 2025-26 | 4 / 528 | 0.8% |

- **No shift is visible.** The earliest Elon writing we can reach is a 2006 blog post, and it is already American (0 British words out of 4). Satoshi in 2008-10 was ~33% British. The earliest era where Elon has enough spelling words to test (2013-16) is 3.6% British, with a CI that tops out at 10%, below Satoshi's 24-42% band (CI for 32 of 98). The two don't overlap.
- **The 1989 move is out of reach.** We could find no writing by Elon before 2006, so we can't test what he wrote as a teenager in South Africa. If he wrote British then, there's no data showing it; if he switched, it happened before our data starts.
- **Satoshi never "switched".** His British share bounces around (2008: 8 vs 4; 2009: 1 vs 13; 2010: 23 vs 40) with small counts and no clean trend, and private emails (0 vs 9) look American. That reads more like a mixed writer than a time-shifting one.

### Writing style by function words: nobody lines up

We compared how often each writer uses the 150 most common function words (the, of, but, which, however...), using Burrows' Delta (lower is closer). Against 65 other writers:

- Elon's X posts: **Delta 1.04**, **30th of 66**, about the middle (typical writer: 1.06). Cosine similarity 0.03, essentially zero.
- Hal Finney is closer (0.94, 14th); Szabo is further (1.32). Peter Gutmann and Jerry Leichter, two list writers, top the ranking at 0.80.
- The method works: it attributes a held-out 2,000-word chunk to the right author 84.5% of the time. It never put an Elon chunk with Satoshi or a Satoshi chunk with Elon.

**The genre problem, stated plainly.** Satoshi wrote emails and forum posts about code. Elon writes tweets. Even the same person scores far apart across genres: Elon's tweets vs his own blog posts, 1.15; Adam Back's emails vs his tweets, 1.25; Szabo's essays vs his tweets, 1.58. Satoshi's forum vs his emails is 0.72. Elon vs Satoshi (1.04) sits inside that cross-genre noise. So function words don't *rule Elon out*, and they don't *show a match*.

### The other quirks

Satoshi wrote "e-mail" 17 times and "email" 3; Elon has never written "e-mail" (0 vs 65). Elon uses "lol" (4 per 10,000 words) and emoji (397 per 10,000); Satoshi used neither. Satoshi wrote "bloody" once; Elon three times ("Bloody hell, I'm going to have to write a blog"). That's the one supporting cue the data does show: both use a British interjection, though so do a lot of people.

### Bottom line

| Section 4 claim | What the data shows |
|---|---|
| Both double-space | Satoshi: yes, 95%. Elon: 0 of 231 (weak test; iPhone caveat). Common among 2000s cypherpunks. |
| British spelling | Satoshi: mixed (33% British), not consistent. Elon: 0.65%, American in every era we can measure. |
| South African to American switch | Unsupported: no Elon writing before 2006; earliest writing is already American. |
| "Bloody", "order of magnitude" | Both use them; each is a common phrase (bloody: Satoshi 1, Elon 3). |
| Function-word style | Elon is average-distance from Satoshi; genre mismatch makes this inconclusive. |

Stylometry is a weak lens on a 18-year-old pseudonym, and this isn't forensic linguistics. The honest reading: the two best-known "tells" in the theory are weaker than they look, and one (double space) points *away* from Elon in the evidence we can reach. It doesn't settle who Satoshi is, and it doesn't touch the non-stylistic case (timing, skills, silence). **Full method, caveats, data and charts:** [REPO LINK].
