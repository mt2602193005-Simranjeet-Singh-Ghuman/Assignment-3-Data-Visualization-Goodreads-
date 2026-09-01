"""Load the Goodreads JSONL file without swallowing the whole 1.75 GB at once."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from config import DATA_PATH, MAX_ROWS, RANDOM_SEED, TSNE_PERPLEXITY_SAMPLE, TSNE_SAMPLE


def n_sentences(review_sentences) -> int:
    # One pair in review_sentences = one sentence. Empty list → 0, not None.
    if not review_sentences:
        return 0
    return len(review_sentences)


def sentence_texts(review_sentences) -> list[str]:
    texts = []
    if not review_sentences:
        return texts
    for item in review_sentences:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            texts.append(str(item[1]))
        elif isinstance(item, str):
            texts.append(item)
    return texts


def spoiler_sentence_count(review_sentences) -> int:
    # k in the ratio formula: how many sentences carry flag 1.
    if not review_sentences:
        return 0
    k = 0
    for item in review_sentences:
        if isinstance(item, (list, tuple)) and len(item) >= 1:
            try:
                k += int(item[0]) == 1
            except (TypeError, ValueError):
                continue
    return k


def review_length(review_sentences) -> int:
    """Count characters in the sentence texts. We ignore the 0/1 flags here."""
    texts = sentence_texts(review_sentences)
    if not texts:
        return 0
    return sum(len(t) for t in texts)


def spoiler_ratio(review_sentences) -> float:
    """k / n. If there are no sentences, return 0.0 instead of dividing."""
    n = n_sentences(review_sentences)
    if n == 0:
        return 0.0  # this is the Q5 safeguard — never hit ZeroDivisionError
    return spoiler_sentence_count(review_sentences) / n


def joined_text(review_sentences) -> str:
    return " ".join(sentence_texts(review_sentences))


def load_reviews(max_rows: int | None = None) -> tuple[list[dict], float]:
    """Read one JSON object per line until MAX_ROWS. The rest of the file stays unread."""
    cap = MAX_ROWS if max_rows is None else max_rows
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    rows: list[dict] = []
    t0 = time.perf_counter()
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        for i, line in enumerate(handle, start=1):
            # We have enough. Do not parse the remaining ~1.3 million lines.
            if len(rows) >= cap:
                break
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if len(rows) % 10_000 == 0:
                print(f"  loaded {len(rows):,} reviews ...")
    elapsed = time.perf_counter() - t0
    print(f"  finished {len(rows):,} reviews in {elapsed:.1f}s")
    return rows, elapsed


def reviews_to_frame(reviews: list[dict]) -> pd.DataFrame:
    # Flatten each JSON review into numbers we can plot. Text is kept for t-SNE only.
    records = []
    for r in reviews:
        sents = r.get("review_sentences") or []
        n = n_sentences(sents)
        k = spoiler_sentence_count(sents)
        length = review_length(sents)
        records.append(
            {
                "user_id": r.get("user_id"),
                "book_id": str(r.get("book_id")),
                "review_id": r.get("review_id"),
                "timestamp": r.get("timestamp"),
                "rating": int(r.get("rating") or 0),
                "has_spoiler": bool(r.get("has_spoiler")),
                "n_sentences": n,
                "n_spoiler_sents": k,
                "review_length": length,
                "spoiler_ratio": (k / n) if n else 0.0,
                "text": joined_text(sents),
            }
        )
    return pd.DataFrame.from_records(records)


def pick_worked_example(reviews: list[dict]) -> dict:
    """Prefer a mixed-flag review so the formula card has a real k and n."""
    fallback = reviews[0] if reviews else {}
    for r in reviews:
        sents = r.get("review_sentences") or []
        flags = []
        for item in sents:
            if isinstance(item, (list, tuple)) and item:
                try:
                    flags.append(int(item[0]))
                except (TypeError, ValueError):
                    continue
        if 0 in flags and 1 in flags and 5 <= len(flags) <= 24:
            k = sum(1 for f in flags if f == 1)
            return {
                "review": r,
                "n": len(flags),
                "k": k,
                "flags": flags,
                "length": review_length(sents),
                "ratio": k / len(flags),
            }
    sents = fallback.get("review_sentences") or []
    n = n_sentences(sents)
    k = spoiler_sentence_count(sents)
    return {
        "review": fallback,
        "n": n,
        "k": k,
        "flags": [int(x[0]) for x in sents if isinstance(x, (list, tuple)) and x],
        "length": review_length(sents),
        "ratio": (k / n) if n else 0.0,
    }


@dataclass
class Analysis:
    df: pd.DataFrame
    reviews: list[dict]
    max_rows: int
    load_seconds: float
    example: dict = field(default_factory=dict)
    _tsne_main: dict | None = field(default=None, repr=False)
    _tsne_perp: dict | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        df = self.df
        self.n = len(df)
        self.n_spoiler = int(df["has_spoiler"].sum())
        self.n_non = self.n - self.n_spoiler
        self.n_books = int(df["book_id"].nunique())
        self.n_users = int(df["user_id"].nunique())
        self.n_zero_sentence = int((df["n_sentences"] == 0).sum())
        self.rating_counts = df["rating"].value_counts().sort_index()
        self.rating_mode = int(self.rating_counts.idxmax()) if len(self.rating_counts) else 0
        self.median_len_spoiler = float(df.loc[df["has_spoiler"], "review_length"].median()) if self.n_spoiler else 0.0
        self.median_len_non = float(df.loc[~df["has_spoiler"], "review_length"].median()) if self.n_non else 0.0
        self.mean_ratio_spoiler = float(df.loc[df["has_spoiler"], "spoiler_ratio"].mean()) if self.n_spoiler else 0.0
        self.mean_ratio_non = float(df.loc[~df["has_spoiler"], "spoiler_ratio"].mean()) if self.n_non else 0.0

        expected_true = df["has_spoiler"] & (df["n_spoiler_sents"] == 0)
        expected_false = (~df["has_spoiler"]) & (df["n_spoiler_sents"] > 0)
        self.n_mismatch = int((expected_true | expected_false).sum())
        self.n_agree = self.n - self.n_mismatch

        cols = ["rating", "n_sentences", "review_length", "spoiler_ratio"]
        self.corr = df[cols].corr()
        pair = ("n_sentences", "review_length")
        best = -2.0
        for i, a in enumerate(cols):
            for b in cols[i + 1 :]:
                val = float(self.corr.loc[a, b])
                if val > best:
                    best = val
                    pair = (a, b)
        self.strongest_pair = pair
        self.strongest_r = best

        self.file_bytes = DATA_PATH.stat().st_size if DATA_PATH.exists() else 0
        if not self.example:
            self.example = pick_worked_example(self.reviews)

    def book_stats(self, min_reviews: int = 8) -> pd.DataFrame:
        g = (
            self.df.groupby("book_id", sort=False)
            .agg(
                n_reviews=("review_id", "count"),
                mean_rating=("rating", "mean"),
                mean_length=("review_length", "mean"),
                mean_spoiler_ratio=("spoiler_ratio", "mean"),
                spoiler_share=("has_spoiler", "mean"),
                mean_sentences=("n_sentences", "mean"),
            )
            .reset_index()
        )
        return g[g["n_reviews"] >= min_reviews].copy()

    def top_books(self, n: int = 10) -> pd.DataFrame:
        g = self.book_stats(min_reviews=1)
        return g.sort_values("n_reviews", ascending=False).head(n).reset_index(drop=True)

    def spoiler_prone_books(self, n: int = 8, min_reviews: int = 12) -> pd.DataFrame:
        g = self.book_stats(min_reviews=min_reviews)
        if g.empty:
            g = self.book_stats(min_reviews=3)
        return g.sort_values("mean_spoiler_ratio", ascending=False).head(n).reset_index(drop=True)

    def radar_books(self, n: int = 4) -> pd.DataFrame:
        g = self.book_stats(min_reviews=10)
        if len(g) < n:
            g = self.book_stats(min_reviews=3)
        popular = g.sort_values("n_reviews", ascending=False).head(max(n * 3, n))
        return popular.head(n).reset_index(drop=True)

    def _text_sample(self, n: int, balanced: bool) -> pd.DataFrame:
        df = self.df[self.df["text"].str.len() > 20].copy()
        rng = np.random.default_rng(RANDOM_SEED)
        if balanced:
            spo = df[df["has_spoiler"]]
            non = df[~df["has_spoiler"]]
            k = min(len(spo), len(non), n // 2)
            if k < 50:
                take = min(n, len(df))
                idx = rng.choice(df.index.to_numpy(), size=take, replace=False)
                return df.loc[idx]
            spo_idx = rng.choice(spo.index.to_numpy(), size=k, replace=False)
            non_idx = rng.choice(non.index.to_numpy(), size=k, replace=False)
            return df.loc[np.concatenate([spo_idx, non_idx])]
        take = min(n, len(df))
        idx = rng.choice(df.index.to_numpy(), size=take, replace=False)
        return df.loc[idx]

    def tsne_main(self) -> dict:
        if self._tsne_main is None:
            print("  computing TF-IDF + t-SNE (perplexity=30) ...")
            self._tsne_main = compute_tsne(self._text_sample(TSNE_SAMPLE, balanced=True), perplexity=30)
        return self._tsne_main

    def tsne_perplexity_panel(self) -> dict:
        if self._tsne_perp is None:
            print("  computing t-SNE perplexity comparison ...")
            sample = self._text_sample(TSNE_PERPLEXITY_SAMPLE, balanced=True)
            self._tsne_perp = {
                5: compute_tsne(sample, perplexity=5),
                30: compute_tsne(sample, perplexity=30),
                100: compute_tsne(sample, perplexity=min(100, max(5, len(sample) // 4))),
            }
        return self._tsne_perp


def compute_tsne(sample: pd.DataFrame, perplexity: int) -> dict:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.manifold import TSNE

    vectorizer = TfidfVectorizer(
        max_features=300,
        stop_words="english",
        min_df=1,
        max_df=0.95,
    )
    X = vectorizer.fit_transform(sample["text"].tolist())
    n = X.shape[0]
    perp = max(5, min(perplexity, max(5, n // 4)))
    dense = X.toarray()
    kwargs = dict(
        n_components=2,
        perplexity=perp,
        random_state=RANDOM_SEED,
        init="pca",
        learning_rate="auto",
    )
    try:
        model = TSNE(max_iter=500, **kwargs)
    except TypeError:
        model = TSNE(n_iter=500, **kwargs)
    coords = model.fit_transform(dense)
    return {
        "x": coords[:, 0],
        "y": coords[:, 1],
        "has_spoiler": sample["has_spoiler"].to_numpy(),
        "perplexity": perp,
        "n": n,
        "n_features": X.shape[1],
    }


def build_analysis(max_rows: int | None = None) -> Analysis:
    cap = MAX_ROWS if max_rows is None else max_rows
    print(f"Streaming at most {cap:,} reviews from:\n  {DATA_PATH}")
    reviews, elapsed = load_reviews(cap)
    print("  computing features ...")
    df = reviews_to_frame(reviews)
    example = pick_worked_example(reviews)
    return Analysis(df=df, reviews=reviews, max_rows=cap, load_seconds=elapsed, example=example)
