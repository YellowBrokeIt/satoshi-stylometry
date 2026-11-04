## 4b. The science: does the writing fit?

The prose "fingerprints" in section 4 are easy to repeat and rarely checked, so we checked them. We built a corpus of everything Satoshi Nakamoto wrote (61 emails and 543 forum posts, about 62,000 words, plus the white paper) and set it against Elon Musk's X posts (89,485 original posts, about 646,000 words), his Tesla blog posts, and 48 of his published emails and text messages. As controls we added 2006-09 cryptography-list writers, BitcoinTalk posters, Hal Finney, Nick Szabo and Adam Back. Every number below comes from code in the [open repo]([REPO LINK]), and you can rerun it. Here is what fits the theory, and what doesn't.

### 1. "Bloody": the one phrase both men share

Satoshi on BitcoinTalk: *"Writing a description for this thing for general audiences is bloody hard."* Elon, in 2017: *"Bloody hell, I'm going to have to write a blog."* The word is a classic Commonwealth-English intensifier. It shows up in Satoshi's writing, and it shows up in Elon's own posts too (3 times in 646,000 words). It sits alongside the other shared phrase from section 4, "order of magnitude".

### 2. Satoshi's two habits were unusual, and they point to a Commonwealth-educated writer

![Double space after a full stop, Satoshi vs Elon vs peers](stylometry/charts/chart1_double_space.png)

- **Double space after a full stop: 1,824 of 1,913 sentence boundaries, 95.3%** (95% CI 94.3-96.2%). It holds across forum posts (95.2%), public emails (97.7%) and private emails (92.6%). It is a deep habit, not an accident.
- **Spelling: 33% British** (32 British forms vs 66 American). Among 2006-09 cryptography-list writers the figure was 13%, and among other BitcoinTalk posters 10%. Satoshi leans British roughly two and a half to three times more than the people around him. He wrote *favour* in the white paper, and across his posts *neighbour* (5 vs 0), *optimise* (12 vs 11) and *colour* (2 vs 4).

The theory's reading is that this is a writer educated in a Commonwealth country, such as South Africa, who types in mostly American spelling after years in the US. That is a hypothesis, and this analysis did not prove it, but the pattern is the one it predicts. Satoshi's spelling is a mix of both, which is the kind of mix a writer who switched would produce. Satoshi's own mix also varies by year (2008: 8 British vs 4 American; 2009: 1 vs 13; 2010: 23 vs 40).

![Spelling and function-word similarity](stylometry/charts/chart2_spelling_and_delta.png)

### 3. The era question cannot be settled by data

![Elon's British-spelling share by era](stylometry/charts/chart3_era_shift.png)

Elon grew up in South Africa and moved to Canada in 1989 and the US a few years later. **We found no Elon writing from before 2006**, and the 2006-2012 writing we did find contains only 8 spelling-variant words (all American). So whether he wrote British spellings as a young man, and when he changed, is untestable with what's public. The "he Americanised later" theory can't be ruled out by the data, and it also can't be confirmed. The earliest era with enough words to measure (2013-16) is 3.6% British (3 of 83), well below Satoshi's 33%, but by then he had lived in North America for over two decades. There is no Elon writing with enough spelling words from Satoshi's own 2008-10 window, so a like-for-like comparison doesn't exist.

### 4. The fingerprint matches nobody, so stylometry can't clear Elon or anyone else

We compared how often each writer uses the 150 most common function words (the, of, but, which, however...), using Burrows' Delta (lower is closer). Against 65 other writers:

- **No candidate comes close.** The best match to Satoshi is Peter Gutmann at 0.80. Satoshi's own forum posts vs his own emails score 0.72. Even the nearest known writers are further from Satoshi than Satoshi is from himself across two channels. So nobody's writing is a close match.
- **Elon's X posts score 1.04.** That is closer to Satoshi than **Nick Szabo's writing (1.32)**, **Adam Back's writing (1.13)** or **Elon's own Tesla blog posts (1.29)**. Szabo and Back are two of the best-known candidates for Satoshi, and each scores further away than Elon's tweets do. Elon's tweets also rank 30th of 66, slightly better than the median writer (1.06).
- **This is a cross-genre comparison.** Tweets and mailing-list posts are different kinds of writing, so these gaps are inflated for everyone. The same author scores far apart across genres: Elon's tweets vs his own blog 1.15, Adam Back's emails vs his tweets 1.25, Szabo's essays vs his tweets 1.58. So the numbers say "inconclusive", not "match".
- **A pseudonymous author may have disguised his style.** If Satoshi was deliberately hiding, such as writing in a different register, mixing spellings or imitating a different background, a fingerprint that matches no known writer is exactly what you'd expect. A disguise would blunt every stylometric test, for Elon and for Back, Szabo, Finney and Dai alike.

### What the skeptics will say

Elon's own posts are 0.65% British (13 of 2,006 spelling words, and several of those are words American English also accepts). The raw-text posts show 0 double spaces out of 231 sentence boundaries, although an iPhone automatically turns a double space into a full stop plus one space, so that test is weak. The 2013-16 Elon writing is already American. "Bloody" is common among Commonwealth writers. And the function-word method is inconclusive across genres: Elon is middle of the pack and the single best match to Satoshi is a mailing-list writer, not a candidate in the theory.

### Bottom line

| Evidence | Satoshi | Elon | Reading |
|---|---|---|---|
| Double space | 95.3% | 0 / 231 (iPhone caveat) | Distinctive for Satoshi; Elon's test is weak |
| British spelling | 33% (peers 10-13%) | 0.65% | Satoshi is mixed and unusual; Elon is American in every era with data |
| Before 2006 | n/a | no writing available | An early British-to-American shift cannot be tested |
| "Bloody" | 1 | 3 (including "Bloody hell...") | Shared British intensifier |
| Function words (Delta to Satoshi) | n/a | 1.04, closer than Szabo 1.32, Back 1.13 and Elon's blog 1.29 | No candidate matches; cross-genre, so inconclusive |

Stylometry can't name Satoshi. It can say Satoshi's habits were unusual, and that nobody's writing matches closely enough to rule anyone in or out. **Full method, caveats, data and charts:** [REPO LINK].
