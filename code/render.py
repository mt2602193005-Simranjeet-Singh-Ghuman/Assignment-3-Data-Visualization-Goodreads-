"""Shared viva-card layout and the write-up files in every question folder."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

from config import CARD_BG, INK, MUTED, NAVY, PANEL_BG, QUESTIONS, TEAL, section_of


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "figure.facecolor": CARD_BG,
        "axes.facecolor": PANEL_BG,
        "axes.edgecolor": "#D5D8DC",
        "axes.grid": True,
        "grid.color": "#EAECEE",
        "grid.linewidth": 0.7,
    }
)


def question_banner(qid: int) -> str:
    meta = QUESTIONS[qid]
    return f"Q{qid:02d}  |  Section {section_of(qid)}  |  {meta['title']}"


def new_graph_figure(title: str):
    fig, ax = plt.subplots(figsize=(11.2, 7.2), dpi=140)
    fig.patch.set_facecolor("white")
    ax.set_title(title, color=NAVY, pad=10, fontweight="bold")
    return fig, ax


def new_card_figure(qid: int, chart_class: str):
    fig = plt.figure(figsize=(18.4, 10.4), dpi=140, facecolor=CARD_BG)
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[0.09, 0.91],
        width_ratios=[1.38, 1.0],
        left=0.035,
        right=0.985,
        top=0.97,
        bottom=0.055,
        hspace=0.06,
        wspace=0.055,
    )
    ax_head = fig.add_subplot(gs[0, :])
    ax_plot = fig.add_subplot(gs[1, 0])
    ax_notes = fig.add_subplot(gs[1, 1])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis("off")
    ax_head.set_facecolor(CARD_BG)
    ax_head.add_patch(
        FancyBboxPatch(
            (0.0, 0.08),
            1.0,
            0.84,
            boxstyle="round,pad=0.01,rounding_size=0.08",
            facecolor=NAVY,
            edgecolor="none",
            transform=ax_head.transAxes,
        )
    )
    ax_head.text(
        0.018,
        0.50,
        question_banner(qid),
        color="white",
        fontsize=15,
        fontweight="bold",
        va="center",
        transform=ax_head.transAxes,
    )
    ax_head.text(
        0.982,
        0.50,
        f"class: {chart_class}",
        color="#D5F5E3",
        fontsize=11,
        ha="right",
        va="center",
        transform=ax_head.transAxes,
    )
    ax_plot.set_facecolor(PANEL_BG)
    ax_notes.set_xlim(0, 1)
    ax_notes.set_ylim(0, 1)
    ax_notes.axis("off")
    ax_notes.set_facecolor(CARD_BG)
    ax_notes.add_patch(
        FancyBboxPatch(
            (0.0, 0.0),
            1.0,
            1.0,
            boxstyle="round,pad=0.012,rounding_size=0.04",
            facecolor=PANEL_BG,
            edgecolor="#D5D8DC",
            lw=1.2,
            transform=ax_notes.transAxes,
        )
    )
    return fig, ax_plot, ax_notes


def new_polar_card_figure(qid: int, chart_class: str):
    fig = plt.figure(figsize=(18.4, 10.4), dpi=140, facecolor=CARD_BG)
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[0.09, 0.91],
        width_ratios=[1.38, 1.0],
        left=0.035,
        right=0.985,
        top=0.97,
        bottom=0.055,
        hspace=0.12,
        wspace=0.08,
    )
    ax_head = fig.add_subplot(gs[0, :])
    ax_head.axis("off")
    ax_head.add_patch(
        FancyBboxPatch(
            (0.0, 0.08),
            1.0,
            0.84,
            boxstyle="round,pad=0.01,rounding_size=0.08",
            facecolor=NAVY,
            edgecolor="none",
            transform=ax_head.transAxes,
        )
    )
    ax_head.text(
        0.018,
        0.50,
        question_banner(qid),
        color="white",
        fontsize=15,
        fontweight="bold",
        va="center",
        transform=ax_head.transAxes,
    )
    ax_head.text(
        0.982,
        0.50,
        f"class: {chart_class}",
        color="#D5F5E3",
        fontsize=11,
        ha="right",
        va="center",
        transform=ax_head.transAxes,
    )
    ax_polar = fig.add_subplot(gs[1, 0], polar=True)
    ax_notes = fig.add_subplot(gs[1, 1])
    ax_notes.set_xlim(0, 1)
    ax_notes.set_ylim(0, 1)
    ax_notes.axis("off")
    ax_notes.add_patch(
        FancyBboxPatch(
            (0.0, 0.0),
            1.0,
            1.0,
            boxstyle="round,pad=0.012,rounding_size=0.04",
            facecolor=PANEL_BG,
            edgecolor="#D5D8DC",
            lw=1.2,
            transform=ax_notes.transAxes,
        )
    )
    return fig, ax_polar, ax_notes


def numbered_notes(ax, bullets: list[tuple[str, str]], footer: str) -> None:
    """Right-hand viva script. Point at 1..n in order."""
    n = max(len(bullets), 1)
    top = 0.965
    gap = min(0.155, 0.88 / n)
    for i, (head, body) in enumerate(bullets):
        y = top - i * gap
        circ = Circle((0.07, y - 0.012), 0.038, color=TEAL, transform=ax.transAxes, zorder=3)
        ax.add_patch(circ)
        ax.text(
            0.07,
            y - 0.012,
            str(i + 1),
            ha="center",
            va="center",
            color="white",
            fontsize=11,
            fontweight="bold",
            transform=ax.transAxes,
            zorder=4,
        )
        ax.text(
            0.14,
            y,
            head,
            ha="left",
            va="top",
            fontsize=11,
            fontweight="bold",
            color=NAVY,
            transform=ax.transAxes,
        )
        ax.text(
            0.14,
            y - 0.038,
            fill(body, 46),
            ha="left",
            va="top",
            fontsize=9.2,
            color=INK,
            linespacing=1.28,
            transform=ax.transAxes,
        )
    ax.text(
        0.05,
        0.028,
        fill(footer, 52),
        ha="left",
        va="bottom",
        fontsize=8.2,
        color=MUTED,
        transform=ax.transAxes,
    )


def box(ax, x, y, w, h, text, fc, ec, tc="white", fs=9, weight="bold", pad=0.02):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad={pad},rounding_size=0.06",
            facecolor=fc,
            edgecolor=ec,
            lw=1.5,
            transform=ax.transAxes,
        )
    )
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        color=tc,
        fontsize=fs,
        fontweight=weight,
        transform=ax.transAxes,
        wrap=True,
    )


def save_fig(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


SCHEMA_FIELDS = {
    "user_id": "Who wrote the review. We only use it to count unique users in the footer. It is never an axis.",
    "timestamp": "The review date. None of the PDF questions are about time, so we leave it unused.",
    "review_id": "Unique id for one review. Used to count reviews per book. Not plotted.",
    "book_id": "Which book was reviewed. Needed for leaderboards, radar, and spoiler-prone ranking.",
    "rating": "Integer stars 0–5. Used whenever the question is about scores.",
    "has_spoiler": "True/False for the whole review. Used for colour, boxplot groups, and t-SNE colour.",
    "review_sentences": "List of [flag, text] pairs. This is where length, spoiler flags, ratio, and t-SNE text come from.",
}


def dataset_block(analysis) -> str:
    gb = analysis.file_bytes / (1024 ** 3)
    unread = max(1_380_000 - analysis.n, 0)
    pct = 100 * analysis.n / 1_380_000
    return f"""The file on disk is **{gb:.2f} GB**, about **1.38 million reviews** (UCSD / Wan et al.: ~25,000 books, ~19,000 users, ~17.6 million sentences).

This run **kept the first {analysis.n:,} reviews** (`MAX_ROWS = {analysis.max_rows:,}`), which is about **{pct:.2f}%** of the full set. That gave **{analysis.n_books:,} books** and **{analysis.n_users:,} users** in memory.

**What was not used, and how it was “removed”:**
- The remaining ~{unread:,} reviews were **never loaded**. The reader stops at `MAX_ROWS` and closes the file. Nothing is deleted from disk; we just stop reading.
- Why: a typical laptop cannot hold 1.75 GB of nested Python objects (that is Q3).
- Order: JSONL is read from the top, so this is a **first-N sample**, not a random sample. Early users can be over-represented (this run has only {analysis.n_users:,} users). That is a Q21 talking point, not a bug.
- Blank lines are skipped. Records with 0 sentences are **kept**, with `spoiler_ratio = 0.0` (Q5), not dropped.
- Scatter plots **draw** at most 8,000 points so the figure is readable; medians and correlations still use all {analysis.n:,} loaded rows.
- t-SNE uses a further wording subsample (about 2,000 reviews, and ~800 for the perplexity panel). The other loaded rows still feed histograms, boxplots, and the heatmap.
- There is **no book-title field** in this JSON. We did not remove titles; they were never in the metadata."""


def metadata_use_block(metadata_fields: list[str]) -> str:
    joined = " ".join(metadata_fields)
    lines = ["For this question, each JSON field is treated as follows:"]
    for field, why in SCHEMA_FIELDS.items():
        used = field in metadata_fields or field in joined or "JSONL" in joined or "schema" in joined.lower()
        flag = "**used**" if used else "**not plotted**"
        lines.append(f"- `{field}` — {flag}. {why}")
    extra = [f for f in metadata_fields if f not in SCHEMA_FIELDS]
    if extra:
        lines.append("Question-specific fields/notes: " + ", ".join(f"`{e}`" for e in extra))
    return "\n".join(lines)


def explanation_md(
    qid: int,
    *,
    chart_class: str,
    graph_structure: str,
    features: list[str],
    metadata_fields: list[str],
    formulas: list[str],
    what_represents: str,
    feature_analysis: str,
    explanation: str,
    viva_steps: list[str],
    how_code: str,
    how_graph_made: str,
    dataset: str,
) -> str:
    meta = QUESTIONS[qid]
    formula_block = "\n".join(f"- `{f}`" for f in formulas) if formulas else "- (no numeric formula for this question — it is a concept / pipeline question)"
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(viva_steps, 1))
    feat = ", ".join(f"`{f}`" for f in features) if features else "none derived for this question"
    fields = ", ".join(f"`{f}`" for f in metadata_fields)
    return f"""# Q{qid:02d} — {meta['title']}

## Question (from the PDF)
{meta['pdf']}

## 1. Direct answer
{explanation}

## 2. How long is the dataset, and what was left out?
{dataset}

## 3. Workflow — how the code worked
1. Stream the JSONL file line by line (`json.loads` on one review at a time).
2. Stop at `MAX_ROWS`. The rest of the 1.75 GB file is unread, not deleted.
3. From `review_sentences`, build `n_sentences`, `review_length` (character count), and `spoiler_ratio = k/n` (0.0 if n is 0).
4. Keep the original metadata (`rating`, `has_spoiler`, `book_id`, …) next to those features in a table.
5. This question then does: {how_code}

## 4. How metadata was used
Fields named in this question: {fields}

{metadata_use_block(metadata_fields)}

Derived features on the table: {feat}

## 5. Formula and working
{formula_block}

If the examiner asks you to “work it”, use the numbered boxes on `viva_card.png` and plug the example numbers. Do not only recite the symbol.

## 6. How the graph was made
{how_graph_made}

matplotlib draws two files from the same idea:
- graph.png — the actual graph
- viva_card.png — the same graph plus numbered boxes you can point at
- explanation.txt and how_code_worked.txt — the write-up (plain text, not markdown)

## 7. What the graph represents
{what_represents}

## 8. Graph visualization
Open `viva_card.png` first. Speak boxes 1 → 2 → 3 → 4. That order is formula / working / meaning / edge case. Use `graph.png` only if they want an uncluttered chart.

## 9. Graph structure
{graph_structure}

**Class:** `{chart_class}`

## 10. Feature analysis
{feature_analysis}

## 11. How to say this in viva
{steps}
"""


def how_code_md(
    qid: int,
    how_code: str,
    functions: list[str],
    safeguards: list[str],
    how_graph_made: str,
    dataset: str,
    metadata_fields: list[str],
    formulas: list[str],
) -> str:
    fns = "\n".join(f"- `{f}`" for f in functions)
    safe = "\n".join(f"- {s}" for s in safeguards)
    formula_block = "\n".join(f"- `{f}`" for f in formulas) if formulas else "- no numeric formula"
    fields = ", ".join(f"`{f}`" for f in metadata_fields)
    return f"""# How the code worked — Q{qid:02d}

## Dataset (length, keep, drop)
{dataset}

## Step-by-step workflow
{how_code}

## Metadata used
{fields}

{metadata_use_block(metadata_fields)}

## Formula
{formula_block}

## How the graph was drawn
{how_graph_made}

## Functions / classes
{fns}

## Safeguards
{safe}

## Honest line for viva
We did **not** load 1.38 million reviews. We streamed and stopped at `MAX_ROWS`. The leftover file is unread, still sitting on disk.
"""


def metadata_json(qid: int, payload: dict) -> dict:
    base = {
        "question": qid,
        "section": section_of(qid),
        "title": QUESTIONS[qid]["title"],
        "pdf_question": QUESTIONS[qid]["pdf"],
        "files": [
            "graph.png",
            "viva_card.png",
            "explanation.txt",
            "how_code_worked.txt",
            "metadata.json",
        ],
    }
    base.update(payload)
    return base


def write_pack(
    out_dir: Path,
    qid: int,
    *,
    analysis,
    chart_class: str,
    graph_structure: str,
    features: list[str],
    metadata_fields: list[str],
    formulas: list[str],
    what_represents: str,
    feature_analysis: str,
    explanation: str,
    how_code: str,
    functions: list[str],
    safeguards: list[str],
    viva_steps: list[str],
    extra_meta: dict,
    how_graph_made: str | None = None,
    n_rows: int | None = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset = dataset_block(analysis)
    graph_made = how_graph_made or (
        "After the feature table exists, a matplotlib axes is created and the "
        "drawing function for this question fills it (boxes, bars, points, or a "
        f"pipeline diagram). Chart class: `{chart_class}`. "
        + how_code
    )
    write_text(
        out_dir / "explanation.txt",
        explanation_md(
            qid,
            chart_class=chart_class,
            graph_structure=graph_structure,
            features=features,
            metadata_fields=metadata_fields,
            formulas=formulas,
            what_represents=what_represents,
            feature_analysis=feature_analysis,
            explanation=explanation,
            viva_steps=viva_steps,
            how_code=how_code,
            how_graph_made=graph_made,
            dataset=dataset,
        ),
    )
    write_text(
        out_dir / "how_code_worked.txt",
        how_code_md(
            qid,
            how_code,
            functions,
            safeguards,
            graph_made,
            dataset,
            metadata_fields,
            formulas,
        ),
    )
    payload = metadata_json(
        qid,
        {
            "chart_class": chart_class,
            "graph_structure": graph_structure,
            "features": features,
            "metadata_fields": metadata_fields,
            "formulas": formulas,
            "n_rows": analysis.n if n_rows is None else n_rows,
            "file_gb": round(analysis.file_bytes / (1024 ** 3), 2),
            "full_corpus_reviews_approx": 1_380_000,
            "n_books_in_sample": analysis.n_books,
            "n_users_in_sample": analysis.n_users,
            **extra_meta,
        },
    )
    (out_dir / "metadata.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    for stale in ("explanation.md", "how_code_worked.md"):
        old = out_dir / stale
        if old.exists():
            old.unlink()
