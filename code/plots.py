"""The actual charts. Each helper draws on an axes we already created for a question."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D

from config import GOLD, INK, MUTED, NAVY, NON_SPOILER, SPOILER, TEAL


def rating_hist(ax, analysis) -> None:
    # Integer stars, so this is a bar-style histogram, not a smooth density.
    counts = analysis.rating_counts
    xs = counts.index.to_numpy()
    ys = counts.to_numpy()
    colors = [GOLD if int(x) == analysis.rating_mode else NAVY for x in xs]
    ax.bar(xs, ys, color=colors, edgecolor="white", width=0.72, zorder=3)
    ax.set_xticks(range(0, 6))
    ax.set_xlabel("rating")
    ax.set_ylabel("number of reviews")
    ax.set_title("Rating distribution (discrete histogram)")
    for x, y in zip(xs, ys):
        ax.text(x, y, f"{y:,}", ha="center", va="bottom", fontsize=8, color=MUTED)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def length_box(ax, analysis, emphasize_outliers: bool = False) -> None:
    # Two groups side by side. The line in the box is the median, not the mean.
    df = analysis.df
    data_non = df.loc[~df["has_spoiler"], "review_length"].to_numpy()
    data_sp = df.loc[df["has_spoiler"], "review_length"].to_numpy()
    bp = ax.boxplot(
        [data_non, data_sp],
        tick_labels=["has_spoiler = False", "has_spoiler = True"],
        patch_artist=True,
        showfliers=True,
        flierprops=dict(
            marker="o",
            markersize=4 if emphasize_outliers else 3,
            markerfacecolor=SPOILER if emphasize_outliers else "#ABB2B9",
            markeredgecolor="none",
            alpha=0.55 if emphasize_outliers else 0.25,
        ),
        medianprops=dict(color="#1A5276", linewidth=2.4),
        whiskerprops=dict(color=NAVY, linewidth=1.2),
        capprops=dict(color=NAVY, linewidth=1.2),
    )
    fills = [NON_SPOILER, SPOILER]
    for patch, c in zip(bp["boxes"], fills):
        patch.set_facecolor(c)
        patch.set_alpha(0.55)
        patch.set_edgecolor(NAVY)
    ax.set_ylabel("review_length (characters)")
    ax.set_title("Review length by spoiler flag")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    medians = [analysis.median_len_non, analysis.median_len_spoiler]
    for i, m in enumerate(medians, start=1):
        ax.annotate(
            f"median = {m:,.0f}",
            xy=(i, m),
            xytext=(i + 0.28, m),
            fontsize=8,
            color=NAVY,
            va="center",
        )


def length_rating_scatter(ax, analysis, color_by_spoiler: bool, n_sample: int) -> None:
    # Draw a sample so the plot stays readable. Correlation still uses every loaded row.
    df = analysis.df
    if len(df) > n_sample:
        sample = df.sample(n_sample, random_state=42)
    else:
        sample = df
    if color_by_spoiler:
        non = sample[~sample["has_spoiler"]]
        spo = sample[sample["has_spoiler"]]
        ax.scatter(
            non["rating"] + np.random.default_rng(0).uniform(-0.12, 0.12, len(non)),
            non["review_length"],
            s=12,
            alpha=0.22,
            c=NON_SPOILER,
            linewidths=0,
            label="no spoiler",
        )
        ax.scatter(
            spo["rating"] + np.random.default_rng(1).uniform(-0.12, 0.12, len(spo)),
            spo["review_length"],
            s=14,
            alpha=0.35,
            c=SPOILER,
            linewidths=0,
            label="has spoiler",
        )
        ax.legend(frameon=False, loc="upper left")
    else:
        ax.scatter(
            sample["rating"] + np.random.default_rng(0).uniform(-0.12, 0.12, len(sample)),
            sample["review_length"],
            s=12,
            alpha=0.18,
            c=NAVY,
            linewidths=0,
        )
    ax.set_xticks(range(0, 6))
    ax.set_xlabel("rating")
    ax.set_ylabel("review_length (characters)")
    ax.set_title("Review length vs rating")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def corr_heatmap(ax, analysis, highlight: bool) -> None:
    corr = analysis.corr
    labels = list(corr.columns)
    mat = corr.to_numpy()
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_yticklabels(labels)
    ax.set_title("Pearson correlation")
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = mat[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=INK, fontsize=9)
    if highlight:
        a, b = analysis.strongest_pair
        ia, ib = labels.index(a), labels.index(b)
        for (x, y) in ((ib, ia), (ia, ib)):
            ax.add_patch(
                __import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle(
                    (x - 0.5, y - 0.5),
                    1,
                    1,
                    fill=False,
                    edgecolor=GOLD,
                    lw=2.4,
                )
            )
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="r")


def top_books_barh(ax, table: pd.DataFrame, color_by_rating: bool = False) -> None:
    t = table.sort_values("n_reviews", ascending=True)
    labels = [f"book {b}" for b in t["book_id"]]
    if color_by_rating:
        ratings = t["mean_rating"].to_numpy()
        # 0-5 mapped from muted blue to gold
        norm = (ratings - 0) / 5.0
        colors = [(0.12, 0.35 + 0.4 * v, 0.55, 0.9) for v in norm]
        ax.barh(labels, t["n_reviews"], color=colors, edgecolor="white")
        for y, (n, r) in enumerate(zip(t["n_reviews"], t["mean_rating"])):
            ax.text(n, y, f"  {int(n)} reviews | mean rating {r:.2f}", va="center", fontsize=8, color=INK)
    else:
        ax.barh(labels, t["n_reviews"], color=TEAL, edgecolor="white")
        for y, n in enumerate(t["n_reviews"]):
            ax.text(n, y, f"  {int(n)}", va="center", fontsize=8, color=MUTED)
    ax.set_xlabel("number of reviews in this sample")
    ax.set_title("Top 10 most-reviewed books")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def minmax(series: pd.Series) -> pd.Series:
    # Same idea as Q5: if max equals min we cannot divide, so we park everyone at 0.5.
    lo, hi = float(series.min()), float(series.max())
    if hi == lo:
        return pd.Series(np.full(len(series), 0.5), index=series.index)
    return (series - lo) / (hi - lo)


def radar_polygon(ax, table: pd.DataFrame, highlight_idx: int | None = None) -> list[str]:
    metrics = [
        ("n_reviews", "review count"),
        ("mean_rating", "avg rating"),
        ("mean_length", "avg length"),
        ("mean_spoiler_ratio", "spoiler ratio"),
    ]
    keys = [k for k, _ in metrics]
    names = [n for _, n in metrics]
    scaled = table.copy()
    for k in keys:
        scaled[k] = minmax(table[k])
    angles = np.linspace(0, 2 * np.pi, len(keys), endpoint=False)
    angles = np.concatenate([angles, angles[:1]])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(names)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1"], color=MUTED, fontsize=8)
    ax.set_ylim(0, 1.05)
    palette = [NAVY, SPOILER, TEAL, GOLD]
    labels = []
    for i, row in scaled.iterrows():
        vals = [float(row[k]) for k in keys] + [float(row[keys[0]])]
        lw = 2.8 if highlight_idx is not None and i == highlight_idx else 1.6
        alpha = 0.28 if highlight_idx is None or i == highlight_idx else 0.08
        lab = f"book {table.loc[i, 'book_id']}"
        labels.append(lab)
        ax.plot(angles, vals, color=palette[i % 4], lw=lw, label=lab)
        ax.fill(angles, vals, color=palette[i % 4], alpha=alpha)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.12), frameon=False, fontsize=8)
    return labels


def tsne_scatter(ax, blob: dict, title: str) -> None:
    x, y, flag = blob["x"], blob["y"], blob["has_spoiler"]
    ax.scatter(x[~flag], y[~flag], s=14, alpha=0.35, c=NON_SPOILER, linewidths=0, label="no spoiler")
    ax.scatter(x[flag], y[flag], s=16, alpha=0.55, c=SPOILER, linewidths=0, label="has spoiler")
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    ax.set_title(title)
    ax.legend(frameon=False)
    ax.set_xticks([])
    ax.set_yticks([])


def spoiler_prone_barh(ax, table: pd.DataFrame) -> None:
    t = table.sort_values("mean_spoiler_ratio", ascending=True)
    labels = [f"book {b}" for b in t["book_id"]]
    ax.barh(labels, t["mean_spoiler_ratio"], color=SPOILER, alpha=0.8, edgecolor="white")
    ax.set_xlabel("mean spoiler_ratio")
    ax.set_title("Most spoiler-prone books in this sample")
    ax.set_xlim(0, 1.05)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def arrow(ax, x1, y1, x2, y2, color=NAVY):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            color=color,
            lw=1.4,
            transform=ax.transAxes,
        )
    )


def draw_digraph(ax, nodes: dict, edges: list, title: str = "") -> None:
    """Draw a real node-and-edge graph (not a slide of unconnected boxes).

    nodes[id] = (x, y, width, height, label, facecolor, textcolor)
    Coordinates are in data space on a 0–10 board.
    """
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_facecolor("white")
    if title:
        ax.set_title(title, color=NAVY, fontweight="bold", pad=10)
    for src, dst in edges:
        x1, y1 = nodes[src][0], nodes[src][1]
        x2, y2 = nodes[dst][0], nodes[dst][1]
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#7F8C8D",
                lw=1.7,
                shrinkA=22,
                shrinkB=22,
            ),
            zorder=1,
        )
    for x, y, w, h, label, fc, tc in nodes.values():
        ax.add_patch(
            FancyBboxPatch(
                (x - w / 2, y - h / 2),
                w,
                h,
                boxstyle="round,pad=0.04,rounding_size=0.15",
                facecolor=fc,
                edgecolor="#1B3A4B",
                lw=1.3,
                zorder=2,
            )
        )
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            color=tc,
            fontsize=8,
            fontweight="bold",
            zorder=3,
        )


def concept_axes(ax) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("#FBFCFC")


def legend_spoiler() -> list:
    return [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=NON_SPOILER, markersize=8, label="no spoiler"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=SPOILER, markersize=8, label="has spoiler"),
    ]
