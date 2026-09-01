# Assignment 3 — Data Visualization (Goodreads Spoiler Reviews)

UCSD Goodreads spoiler dataset (McAuley Lab / Wan et al., ACL’19).

This repository has **code**, **output graphs**, and the assignment PDF.  
It does **not** include the review JSON (about 1.75 GB / 1.38 million reviews).

## Dataset (metadata) — download this yourself

**File:** `goodreads_reviews_spoiler.json.gz`

**Link:**  
https://mcauleylab.ucsd.edu/public_datasets/gdrive/goodreads/goodreads_reviews_spoiler.json.gz

After download:

1. Unzip the `.gz` so you get `goodreads_reviews_spoiler.json`.
2. Place it here (this is the path the code already uses):

```text
Assignment 3/
  goodreads_reviews_spoiler.json/
    goodreads_reviews_spoiler.json
```

The loader only reads the first `MAX_ROWS` lines (default 50,000). The rest of the file stays unread on disk.

Source page: [UCSD McAuley Lab Goodreads datasets](https://mcauleylab.ucsd.edu/public_datasets/gdrive/goodreads/).

## What is in this repo

| Path | What it is |
|---|---|
| `code/` | Python CLI that draws every question |
| `output/` | Graphs, viva cards, and `.txt` write-ups per question |
| `PL_Assign3 (1).pdf` | Assignment questions |

## How to run (VS Code terminal)

```text
cd code
python main.py
```

First time type `all` (builds every output folder).

| You type | Meaning |
|---|---|
| `4` | Only question 4 |
| `A` | Section A only (Q1–Q3). **A is not “all”.** |
| `all` | Questions 1–21 plus the viva map |
| `map` | Overview posters only |
| `help` | Option list |
| `q` | Quit |

Or skip the menu:

```text
python main.py all
python main.py 4
python main.py A
```

Needs: Python 3, pandas, numpy, matplotlib, scikit-learn (`pip install -r requirements.txt` from `code/`).

## Viva

Start at `output/00_viva_map/viva_map.png`, then open that question’s `viva_card.png`.
