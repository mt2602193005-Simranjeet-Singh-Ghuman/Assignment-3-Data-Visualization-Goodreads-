"""
Assignment 3 knobs — keep this folder separate from Assignment 2.

The Goodreads file is huge (~1.75 GB, about 1.38 million reviews). We only
read the first MAX_ROWS lines so a normal laptop survives. The rest of the
file is left unread on disk; we do not delete anything.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "code"
OUTPUT_DIR = ROOT / "output"
DATA_PATH = ROOT / "goodreads_reviews_spoiler.json" / "goodreads_reviews_spoiler.json"

# Cap how many reviews we actually parse. Raise this only if the machine can take it.
MAX_ROWS = 50_000
# 50k dots would hide the scatter; we still compute stats on every loaded row.
SCATTER_SAMPLE = 8_000
# t-SNE is slow. A couple of thousand reviews is enough to show the idea.
TSNE_SAMPLE = 2_000
TSNE_PERPLEXITY_SAMPLE = 800
RANDOM_SEED = 42

SPOILER = "#C0392B"
NON_SPOILER = "#1F6AA5"
NAVY = "#1B3A4B"
TEAL = "#148F77"
GOLD = "#B7950B"
INK = "#1C2833"
MUTED = "#5D6D7E"
CARD_BG = "#F4F6F7"
PANEL_BG = "#FFFFFF"
BOX_FILL = "#EAF2F8"
BOX_EDGE = "#1B3A4B"

SECTIONS = {
    "A": ("section_A_data_understanding", "Data Understanding", (1, 2, 3)),
    "B": ("section_B_feature_engineering", "Feature Engineering", (4, 5)),
    "C": ("section_C_distribution", "Distribution Plots", (6, 7, 8)),
    "D": ("section_D_scatter", "Scatter Plot", (9, 10)),
    "E": ("section_E_heatmap", "Correlation Heatmap", (11, 12)),
    "F": ("section_F_leaderboard", "Leaderboard (Bar Chart)", (13, 14)),
    "G": ("section_G_radar", "Radar Chart", (15, 16)),
    "H": ("section_H_tsne", "t-SNE Plot", (17, 18, 19)),
    "I": ("section_I_critical", "Analysis & Critical Thinking", (20, 21)),
}

QUESTIONS = {
    1: {
        "folder": "Q01_schema",
        "title": "Schema of a single review record",
        "pdf": (
            "Describe the schema of a single review record in the Goodreads spoiler "
            "dataset. In what format does the review_sentences field store spoiler information?"
        ),
    },
    2: {
        "folder": "Q02_spoiler_flags",
        "title": "has_spoiler vs sentence spoiler flags",
        "pdf": (
            "What is the difference between the has_spoiler field (per-review boolean) "
            "and the individual spoiler flags (0/1) inside review_sentences (per-sentence)? "
            "Based on how the two fields are related, would you expect has_spoiler=True "
            "whenever at least one sentence is flagged 1?"
        ),
    },
    3: {
        "folder": "Q03_safe_loading",
        "title": "Why MAX_ROWS streaming is required",
        "pdf": (
            "The real dataset contains ~1.38 million reviews across ~25,000 books and "
            "~19,000 users, totaling ~17.6 million sentences. Why would loading a file "
            "this large directly into memory as a Python list be risky on a typical laptop? "
            "What strategy did we use to load it safely (see the MAX_ROWS variable)?"
        ),
    },
    4: {
        "folder": "Q04_formulas",
        "title": "Review length and spoiler ratio formulas",
        "pdf": (
            "How are the review_length and spoiler_ratio features computed? "
            "Write down the formula for each."
        ),
    },
    5: {
        "folder": "Q05_zero_sentences",
        "title": "Zero-sentence safeguard",
        "pdf": (
            "If a review has 0 sentences, why does the spoiler ratio function not crash? "
            "Which safeguard in the code prevents this?"
        ),
    },
    6: {
        "folder": "Q06_rating_histogram",
        "title": "Rating histogram: shape and mode",
        "pdf": (
            "Looking at the rating histogram, is the distribution of ratings normal or "
            "skewed? Which rating value has the highest frequency?"
        ),
    },
    7: {
        "folder": "Q07_length_boxplot",
        "title": "Median review length by spoiler group",
        "pdf": (
            "Compare the median review length between has_spoiler=True and "
            "has_spoiler=False groups in the boxplot. Which group has longer reviews, "
            "and why might that be the case?"
        ),
    },
    8: {
        "folder": "Q08_outliers",
        "title": "What boxplot outliers are",
        "pdf": "What do the individual dots (outliers) in the boxplot represent?",
    },
    9: {
        "folder": "Q09_length_vs_rating",
        "title": "Scatter: review length vs rating",
        "pdf": (
            "Does the scatter plot of review length vs rating show a clear linear "
            "relationship? Justify your answer."
        ),
    },
    10: {
        "folder": "Q10_color_encoding",
        "title": "Color encoding on the scatter plot",
        "pdf": (
            "What additional insight does the color encoding (has_spoiler) provide "
            "that could not be seen from the x-y position alone?"
        ),
    },
    11: {
        "folder": "Q11_strongest_pair",
        "title": "Strongest positive correlation",
        "pdf": (
            "Among rating, n_sentences, review_length, and spoiler_ratio, which pair "
            "shows the strongest positive correlation?"
        ),
    },
    12: {
        "folder": "Q12_correlation_range",
        "title": "Why r is always between -1 and +1",
        "pdf": (
            "Why does the correlation coefficient always lie between -1 and +1? "
            "What does a value close to 0 indicate?"
        ),
    },
    13: {
        "folder": "Q13_barh",
        "title": "Why a horizontal bar chart",
        "pdf": (
            "Why was the top-10 most-reviewed-books chart drawn as a horizontal bar "
            "chart (barh) instead of a vertical one?"
        ),
    },
    14: {
        "folder": "Q14_reviews_vs_quality",
        "title": "Most reviewed is not necessarily best",
        "pdf": (
            "Is the book with the most reviews necessarily the \"best\" book? "
            "What additional metric should be considered (hint: rating)?"
        ),
    },
    15: {
        "folder": "Q15_normalization",
        "title": "Why radar metrics are min-max scaled",
        "pdf": (
            "Why were the metrics normalized to a 0-1 range before plotting on the "
            "radar chart, instead of using their original scales "
            "(e.g. review count 50-500 vs. average rating 0-5)?"
        ),
    },
    16: {
        "folder": "Q16_polygon_shape",
        "title": "Radar polygon: balanced vs extreme",
        "pdf": (
            "How does the shape of a book's radar polygon indicate whether it is "
            "\"balanced\" across metrics or extreme in just one?"
        ),
    },
    17: {
        "folder": "Q17_what_tsne_does",
        "title": "What t-SNE does to TF-IDF vectors",
        "pdf": (
            "What does the t-SNE algorithm do – how does it convert high-dimensional "
            "TF-IDF vectors (300 dimensions) into a 2D plot?"
        ),
    },
    18: {
        "folder": "Q18_cluster_caution",
        "title": "Are spoiler clusters this clean on real data?",
        "pdf": (
            "In this notebook's plot, spoiler and non-spoiler reviews appear as fairly "
            "separate clusters. Given the note on data above, is this separation likely "
            "to be as clean on the real dataset (where spoilers are only ~3.22% of "
            "sentences and wording overlaps more)? Explain your reasoning."
        ),
    },
    19: {
        "folder": "Q19_perplexity",
        "title": "Role of perplexity=30",
        "pdf": (
            "What role does the perplexity=30 parameter play in t-SNE? How might "
            "changing it affect the resulting plot?"
        ),
    },
    20: {
        "folder": "Q20_publisher_choice",
        "title": "Two visualizations for spoiler-prone books",
        "pdf": (
            "If you were a publisher trying to determine which book is most "
            "\"spoiler-prone,\" which two visualizations from this assignment would "
            "be most useful, and why?"
        ),
    },
    21: {
        "folder": "Q21_synthetic_vs_real",
        "title": "Sample conclusions vs the full UCSD file",
        "pdf": (
            "This assignment uses synthetic sample data with the same schema as the "
            "real dataset. How might your conclusions change if you re-ran the "
            "notebook on the real UCSD dataset?"
        ),
    },
}


def question_dir(qid: int) -> Path:
    section_key = None
    for key, (folder, _name, qids) in SECTIONS.items():
        if qid in qids:
            section_key = key
            break
    if section_key is None:
        raise KeyError(qid)
    section_folder = SECTIONS[section_key][0]
    return OUTPUT_DIR / section_folder / QUESTIONS[qid]["folder"]


def section_of(qid: int) -> str:
    for key, (_folder, _name, qids) in SECTIONS.items():
        if qid in qids:
            return key
    raise KeyError(qid)
