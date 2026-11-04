#!/usr/bin/env python3
"""Two charts from the results/ CSVs."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import *
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
SAT, ELN, CTL, GRY = '#e8a317', '#1d9bf0', '#6b7280', '#c4c9d0'

# ------------------------------------------------ chart 1: double spaces
d = pd.read_csv(f'{RESULTS}/double_space_summary.csv').set_index('label')
la = pd.read_csv(f'{RESULTS}/double_space_by_list_author.csv'); la = la[la.boundaries >= 50]
fa = pd.read_csv(f'{RESULTS}/double_space_by_forum_author.csv'); fa = fa[fa.boundaries >= 50]
rows = [
 ('Satoshi: BitcoinTalk/P2P forum', 'Satoshi - BitcoinTalk/P2P Foundation forum posts', SAT),
 ('Satoshi: public emails', 'Satoshi - mailing-list emails (SNI/metzdowd/SourceForge)', SAT),
 ('Satoshi: private emails', 'Satoshi - private emails (Back/Dai/Finney)', SAT),
 ('Elon: X posts, raw API text', 'Elon - X API sample (raw text)', ELN),
 ('Hal Finney: crypto-list emails', 'Hal Finney - cryptography list emails', CTL),
 ('Adam Back: crypto-list emails', 'Adam Back - cryptography list emails', CTL),
 ('Adam Back: X posts (raw)', 'adam3us - X API sample', CTL),
 ('Nick Szabo: X posts (raw)', 'NickSzabo4 - X API sample', CTL),
 ('Vitalik Buterin: X posts (raw)', 'VitalikButerin - X API sample', CTL),
]
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={'width_ratios': [1.55, 1]})
for i, (lab, key, c) in enumerate(rows[::-1]):
    r = d.loc[key]; y = i
    ax.errorbar(r.rate * 100, y, xerr=[[ (r.rate - r.ci_lo) * 100], [(r.ci_hi - r.rate) * 100]], fmt='o', color=c, ms=8, capsize=4, lw=2)
    ax.text(103, y, f'{int(r.double)}/{int(r.boundaries)}', va='center', fontsize=9, color='#333')
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]])
ax.set_xlim(-3, 112); ax.set_xlabel('% of sentence ends followed by TWO spaces (95% Wilson CI)  -  label = doubles / boundaries')
ax.axvline(0, color='#999', lw=.6); ax.set_title('Double space after a full stop, inline boundaries only', loc='left', fontweight='bold')
ax.text(0.5, -0.19, 'Elon\'s 18k-post scraped CSV and the HTML blog copies collapse whitespace, so they cannot be tested; the raw-API sample can.\nPhones auto-convert double-space to ". " (iOS), so a 0% on a phone-typed account is weak evidence either way.', transform=ax.transAxes, fontsize=8, color='#555', ha='center')
ax2.hist(la.rate * 100, bins=np.linspace(0, 100, 11), color=GRY, edgecolor='white', label=f'{len(la)} crypto-list authors, 2006-09')
ax2.hist(fa.rate * 100, bins=np.linspace(0, 100, 11), color='#f3d9a0', edgecolor='white', alpha=.9, label=f'{len(fa)} BitcoinTalk posters')
ax2.axvline(95.3, color=SAT, lw=2.5); ax2.set_ylim(0, 48); ax2.text(93, 30, 'Satoshi\n95%', color=SAT, ha='right', fontweight='bold')
ax2.set_xlabel("Author's double-space rate (%)"); ax2.set_ylabel('number of authors'); ax2.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, 1.0))
ax2.set_title('...but it was common in Satoshi\'s world', loc='left', fontweight='bold')
fig.tight_layout(); fig.savefig(f'{CHARTS}/chart1_double_space.png', dpi=160); plt.close(fig)

# ------------------------------------------------ chart 2: spelling + Delta
sp = pd.read_csv(f'{RESULTS}/spelling_summary.csv').set_index('corpus')
items = [('Satoshi: emails + forum', 'Satoshi - informal (emails+forum)', SAT),
         ('Elon: X posts 2010-26 (own words)', 'Elon - X posts (cmj CSV, non-RT, 2010-2026)', ELN),
         ('Elon: Tesla blog prose', 'Elon - Tesla blog prose', ELN),
         ('Hal Finney', 'Hal Finney (list+emails+essays)', CTL),
         ('Nick Szabo (essays)', 'Nick Szabo (essays)', CTL),
         ('Crypto-list others (2006-09)', 'Cryptography-list others (2006-09)', GRY),
         ('BitcoinTalk others', 'BitcoinTalk others (same threads as Satoshi)', GRY)]
from common import wilson
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={'width_ratios': [1, 1.25]})
for i, (lab, key, c) in enumerate(items[::-1]):
    r = sp.loc[key]; n = r.british + r.american; lo, hi = wilson(int(r.british), int(n)); p = r.british / n
    a.errorbar(p * 100, i, xerr=[[(p - lo) * 100], [(hi - p) * 100]], fmt='o', color=c, ms=8, capsize=4, lw=2)
    a.text(56, i, f'{int(r.british)} UK / {int(r.american)} US', va='center', fontsize=9)
a.set_yticks(range(len(items))); a.set_yticklabels([x[0] for x in items[::-1]]); a.set_xlim(-2, 80)
a.set_xlabel('% of spelling-variant words that are British (95% CI)'); a.set_title('British vs American spellings', loc='left', fontweight='bold')
rk = pd.read_csv(f'{RESULTS}/delta_rank_vs_satoshi.csv'); ex = pd.read_csv(f'{RESULTS}/delta_extra_slices_vs_satoshi.csv').set_index('slice')
bl = pd.read_csv(f'{RESULTS}/delta_genre_baselines.csv').set_index('pair')
b.scatter(range(len(rk)), rk.delta, s=22, color=GRY, zorder=2, label=f'{len(rk)} other writers (crypto lists / forums / essays)')
def mark(name, val, c, dy):
    b.axhline(val, color=c, lw=1.4, ls='--', zorder=1); b.text(len(rk) - .5, val + dy, name, color=c, ha='right', fontsize=8.5, fontweight='bold')
mark(f"Elon X posts {ex.loc['Elon - X posts (all)', 'delta']:.2f}", ex.loc['Elon - X posts (all)', 'delta'], ELN, .012)
for nm in ['Hal Finney (writing)', 'Nick Szabo (writing)']:
    r = rk[rk.candidate == nm].iloc[0]; b.scatter(r.name, r.delta, s=70, color=CTL, zorder=3); b.annotate(nm.split(' (')[0], (r.name, r.delta), textcoords='offset points', xytext=(-6, 8), fontsize=8, ha='right')
bv = bl.loc['Satoshi forum vs Satoshi emails (same author, 2 channels)', 'delta']
b.axhspan(bv - .0, bv, color=SAT); b.axhline(bv, color=SAT, lw=2, label=f'Satoshi vs himself, forum vs email = {bv:.2f}')
ev = bl.loc['Elon X posts vs Elon blog prose (same author, 2 genres)', 'delta']
b.axhline(ev, color=ELN, lw=1.2, ls=':', label=f'Elon vs himself, X posts vs blog = {ev:.2f}')
b.set_xlabel('candidates, ranked by closeness to Satoshi'); b.set_ylabel("Burrows' Delta to Satoshi (lower = more similar)")
b.set_title("Function-word style distance to Satoshi", loc='left', fontweight='bold'); b.legend(fontsize=8, loc='upper left')
fig.tight_layout(); fig.savefig(f'{CHARTS}/chart2_spelling_and_delta.png', dpi=160); plt.close(fig)
print('ok')

# ------------------------------------------------ chart 3: era shift
er = pd.read_csv(f'{RESULTS}/era_shift_elon.csv'); er = er[er.genre == 'ALL']
wr = pd.read_csv(f'{RESULTS}/era_claim_words.csv')
sp = pd.read_csv(f'{RESULTS}/spelling_summary.csv').set_index('corpus')
s_all = sp.loc['Satoshi - ALL']; s_lo, s_hi = wilson(int(s_all.british), int(s_all.british + s_all.american)); s_p = s_all.british / (s_all.british + s_all.american) * 100
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={'width_ratios': [1.3, 1]})
a.axhspan(s_lo * 100, s_hi * 100, color=SAT, alpha=.18); a.axhline(s_p, color=SAT, lw=2)
a.text(5.45, s_p + 1.2, f'Satoshi (2008-10): {s_p:.0f}% British\n({int(s_all.british)} UK vs {int(s_all.american)} US forms)', color='#a06c00', ha='right', va='bottom', fontweight='bold', fontsize=9)
cl = sp.loc['Cryptography-list others (2006-09)']; a.axhline(cl.british / (cl.british + cl.american) * 100, color=GRY, lw=1.5, ls='--')
a.text(-0.4, cl.british / (cl.british + cl.american) * 100 + 1, "2006-09 crypto-list average: 13%", color='#555', fontsize=8)
for i, r in enumerate(er.itertuples()):
    n = r.british + r.american
    a.bar(i, r.pct_british, color=ELN, width=.6, alpha=.9)
    a.errorbar(i, r.pct_british, yerr=[[r.pct_british - r.ci_lo], [r.ci_hi - r.pct_british]], color='#0b4f7a', capsize=4, lw=1.5)
    a.text(i, max(r.ci_hi, 0) + 1.5, f'{int(r.british)} UK / {int(r.american)} US\n{r.words/1000:.1f}k words', ha='center', fontsize=8)
    if n < 10: a.text(i, 25, 'too few\nspelling\nwords to\ntell', ha='center', va='center', fontsize=8, color='#555', bbox=dict(fc='white', ec='none', alpha=.85))
a.set_xticks(range(len(er))); a.set_xticklabels(er.era, fontsize=9); a.set_ylim(0, 60)
a.set_ylabel('% of spelling-variant words that are British (95% CI)'); a.set_title("Elon's own writing, by era (posts, blog, emails/texts)", loc='left', fontweight='bold')
a.text(0.5, -0.17, 'No Elon writing before 2006 is available to test, so 1971-2005 (incl. the 1989 move to Canada) is unmeasured.', transform=a.transAxes, ha='center', fontsize=8, color='#555')
labels = {'colour/color': 'colour / color', 'centre/center': 'centre / center', 'organise/organize': 'organise / organize', 'realise/realize': 'realise / realize', 'optimise/optimize': 'optimise / optimize'}
elon_w = wr[wr.corpus.str.startswith('Elon')].groupby('word')[['british', 'american']].sum()
sat_w = wr[wr.corpus == 'Satoshi (all)'].set_index('word')
yy = 0
for k, lab in list(labels.items())[::-1]:
    for who, df_, c, off in [('Satoshi', sat_w, SAT, .18), ('Elon', elon_w, ELN, -.18)]:
        u, am = int(df_.loc[k, 'british']), int(df_.loc[k, 'american']); n = u + am
        if n == 0: b.text(1, yy + off, 'not used', va='center', fontsize=8, color='#888')
        else: b.barh(yy + off, 100 * u / n, height=.32, color=c)
        b.text(104, yy + off, f'{u}/{n}', va='center', fontsize=8, color='#333')
    yy += 1
b.set_yticks(range(len(labels))); b.set_yticklabels(list(labels.values())[::-1]); b.set_xlim(0, 118); b.set_xlabel('% British spelling   (label = British / total uses)')
b.set_title('The claim\'s example words', loc='left', fontweight='bold')
from matplotlib.patches import Patch
b.legend(handles=[Patch(color=SAT, label='Satoshi'), Patch(color=ELN, label='Elon (all own writing)')], loc='lower right', fontsize=8)
fig.tight_layout(); fig.savefig(f'{CHARTS}/chart3_era_shift.png', dpi=160); plt.close(fig)
print('ok3')
