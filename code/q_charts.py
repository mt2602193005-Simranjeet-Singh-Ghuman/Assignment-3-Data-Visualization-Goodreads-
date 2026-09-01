"""Chart questions. Each function draws a clean graph.png and a bettergraph_viva.png with notes."""

from __future__ import annotations

import matplotlib.pyplot as plt

from config import MUTED, NAVY, SCATTER_SAMPLE
from plots import (
    corr_heatmap,
    length_box,
    length_rating_scatter,
    radar_polygon,
    rating_hist,
    spoiler_prone_barh,
    top_books_barh,
    tsne_scatter,
)
from q_concept import _finish, _footer
from render import new_card_figure, new_graph_figure, new_polar_card_figure, numbered_notes


def run_q06(analysis):
    mode = analysis.rating_mode
    counts = analysis.rating_counts
    peak = int(counts.loc[mode])
    # Goodreads stars usually pile at 4–5: peak on the right = left-skewed / negatively skewed.
    skew_word = "left-skewed (peak at high ratings), not a normal bell curve"

    fig_g, ax_g = new_graph_figure("Rating histogram")
    rating_hist(ax_g, analysis)
    fig_c, ax_p, ax_n = new_card_figure(6, "histogram (discrete)")
    rating_hist(ax_p, analysis)
    numbered_notes(
        ax_n,
        [
            ("Shape", f"Not normal. It is {skew_word}."),
            ("Mode", f"Highest bar is rating {mode} with {peak:,} reviews. That gold bar is the mode."),
            ("Why", "People who finish and review books tend to like them. 1-star is rare."),
            ("Class", "This is a discrete histogram / bar of integer ratings 0–5, not a continuous density."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 6, fig_g, fig_c,
        chart_class="histogram (discrete bar)",
        graph_structure="x = rating 0–5, y = count, one bar per integer; mode bar highlighted gold",
        features=["rating frequency"],
        metadata_fields=["rating"],
        formulas=["mode = argmax count(rating)", "this sample mode = " + str(mode)],
        what_represents="How often each star rating appears in the loaded sample.",
        feature_analysis=(
            f"Counts: {', '.join(f'{int(k)}★={int(v):,}' for k, v in counts.items())}. "
            "A bell curve would peak in the middle (around 2–3). This does not."
        ),
        explanation=(
            f"The rating distribution is not normal; it is {skew_word}. "
            f"The rating with highest frequency (mode) is {mode} ({peak:,} reviews)."
        ),
        how_code=(
            "value_counts on df['rating'], then ax.bar. The mode bar is coloured gold. "
            "Ratings stay integers; we do not treat them as a continuous histogram of floats."
        ),
        functions=["Analysis.rating_counts", "plots.rating_hist"],
        safeguards=["xticks fixed at 0–5"],
        viva_steps=[
            "Say 'not normal, peak at the high end'.",
            f"Point at the tallest bar: mode = {mode}.",
            "If they say 'skew': peak on the right is left/negative skew.",
        ],
        extra_meta={"mode": mode, "counts": {int(k): int(v) for k, v in counts.items()}},
    )


def run_q07(analysis):
    ms, mn = analysis.median_len_spoiler, analysis.median_len_non
    longer = "has_spoiler=True" if ms >= mn else "has_spoiler=False"
    fig_g, ax_g = new_graph_figure("Review length boxplot by spoiler")
    length_box(ax_g, analysis, emphasize_outliers=False)
    fig_c, ax_p, ax_n = new_card_figure(7, "boxplot")
    length_box(ax_p, analysis, emphasize_outliers=False)
    numbered_notes(
        ax_n,
        [
            ("Median (the line)", f"False group median = {mn:,.0f} chars. True group median = {ms:,.0f} chars."),
            ("Which is longer", f"{longer} has the longer median in this sample."),
            ("Why", "Spoiler reviews usually retell plot. Retelling needs more sentences, so more characters."),
            ("Not the mean", "The box line is the median, 50th percentile, not the average. Outliers do not move it much."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 7, fig_g, fig_c,
        chart_class="boxplot",
        graph_structure="Two boxes: has_spoiler False vs True; y = review_length characters; inner line = median",
        features=["review_length", "has_spoiler"],
        metadata_fields=["has_spoiler", "review_sentences"],
        formulas=["median = middle value after sorting review_length in that group"],
        what_represents="How typical review length differs for spoiler vs non-spoiler reviews.",
        feature_analysis=(
            f"Median length True={ms:,.0f}, False={mn:,.0f}. "
            f"Mean spoiler_ratio True={analysis.mean_ratio_spoiler:.3f}, False={analysis.mean_ratio_non:.3f}."
        ),
        explanation=(
            f"The has_spoiler=True group has median length {ms:,.0f} characters versus {mn:,.0f} "
            f"for False. {longer} is longer. Spoiler reviews tend to explain plot, so they run longer."
        ),
        how_code=(
            "review_length is computed per review, then matplotlib boxplot of the two groups. "
            "Median is the orange/navy line inside each box, also annotated."
        ),
        functions=["review_length", "plots.length_box"],
        safeguards=["Empty reviews have length 0 and still sit in a group"],
        viva_steps=[
            "Point at the two median labels.",
            f"Say True={ms:,.0f}, False={mn:,.0f}.",
            "Give the plot-retelling reason.",
        ],
        extra_meta={"median_spoiler": ms, "median_non": mn},
    )


def run_q08(analysis):
    fig_g, ax_g = new_graph_figure("Boxplot outliers are unusual reviews, not errors")
    length_box(ax_g, analysis, emphasize_outliers=True)
    fig_c, ax_p, ax_n = new_card_figure(8, "boxplot (outliers emphasised)")
    length_box(ax_p, analysis, emphasize_outliers=True)
    numbered_notes(
        ax_n,
        [
            ("What a dot is", "One review whose length sits outside the 1.5×IQR fence. It is still a real review."),
            ("Fence formula", "IQR = Q3−Q1. Outlier if length < Q1−1.5 IQR or > Q3+1.5 IQR."),
            ("Not a bug", "Do not delete them as 'bad data' unless you have another reason. Long essays happen."),
            ("Median stays", "Those dots barely move the median line. That is why we used a boxplot, not only a mean."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 8, fig_g, fig_c,
        chart_class="boxplot with outliers",
        graph_structure="Same two-group boxplot; fliers drawn as dots beyond the whiskers",
        features=["review_length"],
        metadata_fields=["has_spoiler", "review_sentences"],
        formulas=["IQR = Q3 - Q1", "outlier if x < Q1 - 1.5 IQR or x > Q3 + 1.5 IQR"],
        what_represents="Reviews with unusually short or (usually) long character counts.",
        feature_analysis=(
            "Whiskers stop at the last point inside the fence. Everything beyond is a flier. "
            "They stretch the y-axis; they do not redefine the median."
        ),
        explanation=(
            "The individual dots are outliers: reviews whose length is more than 1.5×IQR beyond "
            "the quartiles. They represent unusually long (or short) reviews, not plotting errors."
        ),
        how_code="boxplot(..., showfliers=True). Q8 reuses Q7's figure with stronger flier styling.",
        functions=["plots.length_box"],
        safeguards=["Outliers kept in the dataset"],
        viva_steps=[
            "Point at a dot: 'that is one review'.",
            "Write the 1.5 IQR rule.",
            "Say they are unusual lengths, not mistakes.",
        ],
        extra_meta={"fence": "Tukey 1.5 IQR"},
    )


def run_q09(analysis):
    r = float(analysis.corr.loc["review_length", "rating"])
    fig_g, ax_g = new_graph_figure("Length vs rating (no spoiler colour yet)")
    length_rating_scatter(ax_g, analysis, color_by_spoiler=False, n_sample=SCATTER_SAMPLE)
    ax_g.axhline(analysis.df["review_length"].median(), color=MUTED, ls="--", lw=1, alpha=0.8)
    fig_c, ax_p, ax_n = new_card_figure(9, "scatter plot")
    length_rating_scatter(ax_p, analysis, color_by_spoiler=False, n_sample=SCATTER_SAMPLE)
    numbered_notes(
        ax_n,
        [
            ("Look at the cloud", "Points form vertical stripes at 0–5, not a diagonal line. No clear linear relationship."),
            ("Number", f"Pearson r(length, rating) = {r:.3f}, close to 0 on the Q12 number line."),
            ("Why stripes", "Rating is discrete. Jitter was added on x only so points do not hide on top of each other."),
            ("Viva word", "If they ask 'correlation': weak linear association. That is not 'no relationship of any kind'."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 9, fig_g, fig_c,
        chart_class="scatter plot",
        graph_structure="x = rating (jittered), y = review_length, one point ≈ one review (subsampled)",
        features=["review_length", "rating"],
        metadata_fields=["rating", "review_sentences"],
        formulas=[f"r(review_length, rating) = {r:.3f}"],
        what_represents="Whether longer reviews give higher (or lower) stars. They do not, as a straight line.",
        feature_analysis=(
            f"r={r:.3f}. Long reviews appear at every star. Short reviews appear at every star. "
            f"Scatter draws {min(SCATTER_SAMPLE, analysis.n):,} of {analysis.n:,} points for readability."
        ),
        explanation=(
            f"No. The scatter is a cloud / vertical stripes, not a line. "
            f"r(review_length, rating) = {r:.3f}, which is near 0, so there is no clear linear relationship."
        ),
        how_code=(
            "Sample up to SCATTER_SAMPLE rows, jitter rating by ±0.12, scatter against review_length. "
            "Colour is withheld on purpose so Q10 can add it."
        ),
        functions=["plots.length_rating_scatter"],
        safeguards=["Subsample so 50k points do not black out the figure"],
        viva_steps=[
            "Say 'no diagonal'.",
            f"Quote r={r:.3f}.",
            "Mention discrete ratings cause stripes.",
        ],
        extra_meta={"r_length_rating": round(r, 4), "scatter_n": min(SCATTER_SAMPLE, analysis.n)},
    )


def run_q10(analysis):
    fig_g, ax_g = new_graph_figure("Same scatter, colour = has_spoiler")
    length_rating_scatter(ax_g, analysis, color_by_spoiler=True, n_sample=SCATTER_SAMPLE)
    fig_c, ax_p, ax_n = new_card_figure(10, "scatter with colour encoding")
    length_rating_scatter(ax_p, analysis, color_by_spoiler=True, n_sample=SCATTER_SAMPLE)
    numbered_notes(
        ax_n,
        [
            ("What colour adds", "x-y only showed length vs stars. Colour splits spoiler vs not without a third axis."),
            ("Insight", "Red spoiler points sit higher on length at the same rating. Spoilers are the long band."),
            ("Channel name", "This is a visual encoding: position = two numbers, hue = a category."),
            ("Link back", "This is the same story as the Q7 boxplot, now inside the Q9 cloud."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 10, fig_g, fig_c,
        chart_class="scatter with categorical colour",
        graph_structure="Same x=rating, y=length; hue = has_spoiler (blue vs red)",
        features=["review_length", "rating", "has_spoiler"],
        metadata_fields=["rating", "has_spoiler", "review_sentences"],
        formulas=["colour(has_spoiler=True) = red", "colour(False) = blue"],
        what_represents="An extra variable (spoiler) that position alone could not show.",
        feature_analysis=(
            f"Spoiler reviews = {analysis.n_spoiler:,}. Non-spoiler = {analysis.n_non:,}. "
            "Without colour they occupy the same x-y space and hide each other."
        ),
        explanation=(
            "Colour shows which points are spoiler reviews. Position alone cannot. "
            "The extra insight is that spoiler reviews cluster toward longer lengths at the same ratings."
        ),
        how_code="Same scatter helper with color_by_spoiler=True, plotting two groups with different colours and a legend.",
        functions=["plots.length_rating_scatter"],
        safeguards=["Legend on the figure so colour is not left implicit"],
        viva_steps=[
            "Say 'third variable via hue'.",
            "Point at the high red band: longer spoilers.",
            "Tie it to Q7 medians.",
        ],
        extra_meta={"encoding": "hue=has_spoiler"},
    )


def run_q11(analysis):
    a, b = analysis.strongest_pair
    r = analysis.strongest_r
    fig_g, ax_g = new_graph_figure("Correlation heatmap")
    corr_heatmap(ax_g, analysis, highlight=True)
    fig_c, ax_p, ax_n = new_card_figure(11, "correlation heatmap")
    corr_heatmap(ax_p, analysis, highlight=True)
    numbered_notes(
        ax_n,
        [
            ("Winner", f"Strongest positive pair: {a}  and  {b}.  r = {r:.3f} (gold boxes)."),
            ("Why that pair", "More sentences usually means more characters. They measure size two ways."),
            ("Read the grid", "Each cell is Pearson r for that row vs column. Diagonal is 1.00 with itself."),
            ("Trap", "spoiler_ratio vs rating is usually weak. Do not point at the wrong cell."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 11, fig_g, fig_c,
        chart_class="correlation heatmap",
        graph_structure="4×4 matrix, colour = r from -1 to +1, text = r to 2 decimals, strongest off-diagonal pair outlined",
        features=["rating", "n_sentences", "review_length", "spoiler_ratio"],
        metadata_fields=["rating", "review_sentences", "has_spoiler"],
        formulas=[f"argmax r(i,j) for i<j  →  {a}, {b} = {r:.3f}"],
        what_represents="Linear association between every pair of the four numeric features.",
        feature_analysis="\n".join(
            f"- {i} vs {j}: r={float(analysis.corr.loc[i, j]):.3f}"
            for i in analysis.corr.columns
            for j in analysis.corr.columns
            if i < j
        ),
        explanation=(
            f"The strongest positive correlation is between {a} and {b} (r = {r:.3f}). "
            "That is expected because both are size measures of the same review."
        ),
        how_code="df[['rating','n_sentences','review_length','spoiler_ratio']].corr(); imshow with RdBu_r and vmin/vmax ±1.",
        functions=["DataFrame.corr", "plots.corr_heatmap"],
        safeguards=["Colour scale locked to [-1,1]"],
        viva_steps=[
            f"Name the pair {a}–{b}.",
            f"Quote r={r:.3f}.",
            "Explain they are two size measures.",
        ],
        extra_meta={
            "strongest_pair": list(analysis.strongest_pair),
            "strongest_r": round(r, 4),
            "matrix": {c: {k: round(float(analysis.corr.loc[c, k]), 4) for k in analysis.corr.columns} for c in analysis.corr.columns},
        },
    )


def run_q13(analysis):
    top = analysis.top_books(10)
    fig_g, ax_g = new_graph_figure("Top-10 books as barh")
    top_books_barh(ax_g, top, color_by_rating=False)
    fig_c, ax_p, ax_n = new_card_figure(13, "horizontal bar chart")
    top_books_barh(ax_p, top, color_by_rating=False)
    numbered_notes(
        ax_n,
        [
            ("Why barh", "Book ids (and titles, if we had them) are long text. Vertical bars force rotated, unreadable labels."),
            ("Reading order", "Category names sit on the y-axis in a full horizontal line. Magnitudes run along x, easy to compare."),
            ("Ranking", "Sorting smallest-at-bottom makes the longest bar sit at the top like a leaderboard."),
            ("What it is not", "This is volume of reviews, not quality. That is Q14."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 13, fig_g, fig_c,
        chart_class="horizontal bar chart (barh)",
        graph_structure="y = book_id labels, x = review count, 10 bars sorted ascending so the winner is on top",
        features=["n_reviews per book_id"],
        metadata_fields=["book_id", "review_id"],
        formulas=["n_reviews(book) = count(reviews with that book_id)"],
        what_represents="Which books attracted the most reviews in this sample.",
        feature_analysis=(
            "This dataset has book_id, not titles, so labels are ids. "
            f"Top book {top.iloc[0]['book_id']} has {int(top.iloc[0]['n_reviews'])} reviews here."
        ),
        explanation=(
            "barh is used because book identifiers are long categorical labels. Horizontal bars keep "
            "those labels readable and make a ranking easy to scan. A vertical bar chart would rotate "
            "or overlap the names."
        ),
        how_code="groupby('book_id').size(), take top 10, sort ascending, ax.barh(labels, counts).",
        functions=["Analysis.top_books", "plots.top_books_barh"],
        safeguards=["Labels from book_id because title is not in this JSON schema"],
        viva_steps=[
            "Say 'long labels → barh'.",
            "Point at the top bar: most reviews.",
            "Refuse to call it the best book (Q14).",
        ],
        extra_meta={"top_book_id": str(top.iloc[0]["book_id"]), "top_n": int(top.iloc[0]["n_reviews"])},
    )


def run_q14(analysis):
    top = analysis.top_books(10)
    best_vol = top.iloc[0]
    best_rate = top.sort_values("mean_rating", ascending=False).iloc[0]
    same = str(best_vol["book_id"]) == str(best_rate["book_id"])
    fig_g, ax_g = new_graph_figure("Review volume vs mean rating")
    top_books_barh(ax_g, top, color_by_rating=True)
    fig_c, ax_p, ax_n = new_card_figure(14, "barh + rating overlay")
    top_books_barh(ax_p, top, color_by_rating=True)
    numbered_notes(
        ax_n,
        [
            ("No", "Most reviews ≠ best book. Volume is popularity / discussion, not quality."),
            ("Extra metric", "Mean rating (hint from the PDF). Colour and the text at the bar end show it."),
            ("This sample", f"Most reviewed: book {best_vol['book_id']} ({int(best_vol['n_reviews'])} reviews, mean {best_vol['mean_rating']:.2f})."),
            ("Compare", f"Highest mean rating among these 10: book {best_rate['book_id']} ({best_rate['mean_rating']:.2f}). "
             + ("They happen to match." if same else "They are different books.")),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 14, fig_g, fig_c,
        chart_class="barh with rating annotation",
        graph_structure="Same top-10 volume bars; each bar labelled with mean rating; darker/gold-ish colour encodes rating",
        features=["n_reviews", "mean_rating"],
        metadata_fields=["book_id", "rating", "review_id"],
        formulas=["mean_rating(book) = average of rating over that book's reviews"],
        what_represents="Why a publisher cannot treat the longest bar as the best book.",
        feature_analysis=(
            f"Volume winner mean rating = {best_vol['mean_rating']:.2f}. "
            f"Rating winner among top-10 volume = {best_rate['mean_rating']:.2f}."
        ),
        explanation=(
            "No. The most-reviewed book is the most discussed in the sample, not necessarily the best. "
            "You should also look at mean rating (and, if asked, rating count vs variance). "
            f"Here the volume leader has mean rating {best_vol['mean_rating']:.2f}."
        ),
        how_code="Same top-10 table, but each bar is annotated with n_reviews and mean_rating together.",
        functions=["Analysis.top_books", "plots.top_books_barh"],
        safeguards=["Mean rating is only over reviews present in MAX_ROWS, not the whole Goodreads site"],
        viva_steps=[
            "Answer 'no' immediately.",
            "Name mean rating.",
            "Point at the number on the top bar.",
        ],
        extra_meta={
            "volume_leader": str(best_vol["book_id"]),
            "volume_mean_rating": round(float(best_vol["mean_rating"]), 3),
            "rating_leader_in_top10": str(best_rate["book_id"]),
        },
    )


def run_q15(analysis):
    table = analysis.radar_books(4)
    # Worked min-max example from first radar book
    row = table.iloc[min(1, len(table) - 1)]
    rc_min, rc_max = float(table["n_reviews"].min()), float(table["n_reviews"].max())
    rt_min, rt_max = float(table["mean_rating"].min()), float(table["mean_rating"].max())
    for _, cand in table.iterrows():
        c = float(cand["n_reviews"])
        t = float(cand["mean_rating"])
        if (rc_min < c < rc_max) or (rt_min < t < rt_max):
            row = cand
            break
    rc = float(row["n_reviews"])
    rt = float(row["mean_rating"])
    rc_n = 0.5 if rc_max == rc_min else (rc - rc_min) / (rc_max - rc_min)
    rt_n = 0.5 if rt_max == rt_min else (rt - rt_min) / (rt_max - rt_min)

    fig_g = plt.figure(figsize=(11.2, 7.2), dpi=140, facecolor="white")
    ax = fig_g.add_subplot(111, polar=True)
    radar_polygon(ax, table)
    ax.set_title("Radar after min–max 0–1 scaling", color=NAVY, pad=18)

    fig_c, ax_polar, ax_n = new_polar_card_figure(15, "radar chart (normalised)")
    radar_polygon(ax_polar, table)
    numbered_notes(
        ax_n,
        [
            ("Formula", "x_norm = (x − min) / (max − min). Result always in [0, 1] for that axis."),
            ("Worked numbers", f"review_count {rc:.0f} → ({rc:.0f}−{rc_min:.0f})/({rc_max:.0f}−{rc_min:.0f}) = {rc_n:.2f}.  rating {rt:.2f} → {rt_n:.2f}."),
            ("Why", "Raw 50–500 vs 0–5: the count spoke would eat the chart and rating would look tiny."),
            ("Edge", "If max=min, we set 0.5 so we never divide by zero (same idea as Q5)."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 15, fig_g, fig_c,
        chart_class="radar / spider chart",
        graph_structure="4 axes (count, rating, length, spoiler ratio), each min–max scaled to [0,1], one polygon per book",
        features=["n_reviews", "mean_rating", "mean_length", "mean_spoiler_ratio"],
        metadata_fields=["book_id", "rating", "review_sentences", "has_spoiler"],
        formulas=[
            "x_norm = (x - min) / (max - min)   if max != min else 0.5",
            f"example count {rc:.0f} -> {rc_n:.3f}",
            f"example rating {rt:.2f} -> {rt_n:.3f}",
        ],
        what_represents="Several book-level metrics on one shape, which is only fair after 0–1 scaling.",
        feature_analysis=(
            "Each spoke is a different unit. Normalisation makes spoke length comparable. "
            "It is a relative scale among the books on this radar, not a universal 0–1 for all Goodreads."
        ),
        explanation=(
            "Radar axes share one radius. Review counts (tens–hundreds) and ratings (0–5) are different "
            "units. Min–max scaling puts every metric on [0,1] so one spoke cannot dominate. "
            f"Worked example: count {rc:.0f} becomes {rc_n:.2f}; rating {rt:.2f} becomes {rt_n:.2f}."
        ),
        how_code="plots.minmax on each metric column of the radar table, then polar plot of the 0–1 values.",
        functions=["plots.minmax", "plots.radar_polygon"],
        safeguards=["max==min → 0.5", "only books with enough reviews in the sample"],
        viva_steps=[
            "Write (x-min)/(max-min).",
            "Plug the two example numbers.",
            "Say raw scales cannot share a radius.",
        ],
        extra_meta={"example_count_norm": round(rc_n, 4), "example_rating_norm": round(rt_n, 4)},
    )


def run_q16(analysis):
    table = analysis.radar_books(4)
    from plots import minmax
    keys = ["n_reviews", "mean_rating", "mean_length", "mean_spoiler_ratio"]
    tmp = table.copy()
    for k in keys:
        tmp[k] = minmax(table[k])
    tmp["spread"] = tmp[keys].std(axis=1)
    balanced_i = int(tmp["spread"].idxmin())
    extreme_i = int(tmp["spread"].idxmax())

    fig_g = plt.figure(figsize=(11.2, 7.2), dpi=140, facecolor="white")
    ax = fig_g.add_subplot(111, polar=True)
    radar_polygon(ax, table, highlight_idx=balanced_i)
    ax.set_title("Round polygon ≈ balanced; spike ≈ one extreme metric", color=NAVY, pad=18)

    fig_c, ax_polar, ax_n = new_polar_card_figure(16, "radar / spider chart")
    radar_polygon(ax_polar, table, highlight_idx=balanced_i)
    numbered_notes(
        ax_n,
        [
            ("Balanced", f"Book {table.loc[balanced_i, 'book_id']} has the roundest shape (similar 0–1 scores on every spoke)."),
            ("Extreme", f"Book {table.loc[extreme_i, 'book_id']} has the largest spread — a spike on one metric, a dent on others."),
            ("How to read", "Look at symmetry, not area. A huge lopsided kite is 'extreme in one', not 'best overall'."),
            ("Link to Q15", "This reading only works because every spoke is 0–1. Raw scales would fake a spike on review count."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 16, fig_g, fig_c,
        chart_class="radar / spider chart",
        graph_structure="Overlaid polygons; the most even polygon is highlighted",
        features=["n_reviews", "mean_rating", "mean_length", "mean_spoiler_ratio"],
        metadata_fields=["book_id", "rating", "review_sentences"],
        formulas=["balanced ≈ small std of the 4 normalised scores", "spike ≈ one normalised score near 1, others near 0"],
        what_represents="Whether a book is even across metrics or dominated by a single spoke.",
        feature_analysis=(
            f"Highlight book {table.loc[balanced_i, 'book_id']} (lowest spread of scaled metrics). "
            f"Most lopsided: book {table.loc[extreme_i, 'book_id']}."
        ),
        explanation=(
            "A nearly regular polygon means the book is balanced: similar normalised scores on every metric. "
            "A long spike with a collapsed opposite spoke means it is extreme in just one metric "
            "(for example huge review volume but average rating / low spoiler ratio)."
        ),
        how_code="Same radar helper; highlight_idx picks the book with smallest std of min-max scores.",
        functions=["plots.radar_polygon", "plots.minmax"],
        safeguards=["Compare shape, not raw area"],
        viva_steps=[
            "Point at the round polygon: balanced.",
            "Point at a spike: extreme in one.",
            "Remind them this requires Q15 normalisation.",
        ],
        extra_meta={"balanced_book": str(table.loc[balanced_i, "book_id"]), "extreme_book": str(table.loc[extreme_i, "book_id"])},
    )


def run_q18(analysis):
    blob = analysis.tsne_main()
    n_sp = int(blob["has_spoiler"].sum())
    n_non = int((~blob["has_spoiler"]).sum())
    fig_g, ax_g = new_graph_figure("t-SNE of TF-IDF (coloured by has_spoiler)")
    tsne_scatter(ax_g, blob, f"perplexity={blob['perplexity']}  n={blob['n']}")
    fig_c, ax_p, ax_n = new_card_figure(18, "t-SNE scatter")
    tsne_scatter(ax_p, blob, f"perplexity={blob['perplexity']}  n={blob['n']}")
    numbered_notes(
        ax_n,
        [
            ("What you see", f"This plot used {blob['n']:,} reviews ({n_sp:,} spoiler / {n_non:,} not), 300-D TF-IDF → 2-D."),
            ("Likely too clean", "If red and blue look well separated, that is partly because we balanced the sample. Real spoilers are ~3.22% of sentences."),
            ("Why overlap should exist", "Spoiler and non-spoiler reviews of the same book share names, style, and vocabulary. t-SNE sees wording, not a spoiler bit."),
            ("Viva verdict", "Do not claim the full UCSD set has two neat islands. Expect more mixing. Q21 says the same."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 18, fig_g, fig_c,
        chart_class="t-SNE scatter",
        graph_structure="2D points from TF-IDF; colour = has_spoiler; axes unlabelled on purpose",
        features=["TF-IDF (300)", "t-SNE x,y", "has_spoiler (colour only)"],
        metadata_fields=["review_sentences", "has_spoiler"],
        formulas=["embedding: R^300 → R^2", "colour is NOT an input to t-SNE"],
        what_represents="Wording similarity. It does not represent rating or a guaranteed spoiler classifier.",
        feature_analysis=(
            "A balanced subsample makes clusters look cleaner than the true 3.22% sentence-spoiler rate. "
            "First-N JSONL rows can also bias users and books."
        ),
        explanation=(
            "Not likely. On the full dataset spoilers are rare (~3.22% of sentences) and spoilers/non-spoilers "
            "share book vocabulary, so t-SNE should overlap more. A small or class-balanced plot can look "
            "artificially separated."
        ),
        how_code=(
            "Analysis.tsne_main() takes a balanced text sample, TfidfVectorizer(max_features=300), "
            "TSNE(perplexity=30). Colour is applied after the embedding."
        ),
        functions=["compute_tsne", "Analysis.tsne_main"],
        safeguards=["Subsample", "Do not feed has_spoiler into TF-IDF"],
        viva_steps=[
            "Describe the plot honestly (separate or mixed).",
            "Say balanced sample ≠ 3.22% population.",
            "Conclude: full data should be messier.",
        ],
        extra_meta={"tsne_n": blob["n"], "n_spoiler_points": n_sp, "n_non_points": n_non},
    )


def run_q20(analysis):
    prone = analysis.spoiler_prone_books(8)
    radar_src = analysis.spoiler_prone_books(4, min_reviews=8)
    if radar_src.empty:
        radar_src = analysis.radar_books(4)

    fig_g, axes = plt.subplots(1, 2, figsize=(14.8, 6.6), dpi=140)
    fig_g.patch.set_facecolor("white")
    spoiler_prone_barh(axes[0], prone)
    axes[1].remove()
    ax_r = fig_g.add_subplot(122, polar=True)
    radar_polygon(ax_r, radar_src)
    fig_g.suptitle("Publisher pair: spoiler-ratio leaderboard + radar", color=NAVY, fontweight="bold")
    fig_g.tight_layout()

    fig_c = plt.figure(figsize=(18.4, 10.4), dpi=140, facecolor="#F4F6F7")
    gs = fig_c.add_gridspec(2, 3, height_ratios=[0.10, 0.90], width_ratios=[1.05, 1.05, 0.95],
                            left=0.03, right=0.99, top=0.96, bottom=0.07, hspace=0.12, wspace=0.18)
    ax_head = fig_c.add_subplot(gs[0, :])
    ax_head.axis("off")
    ax_head.text(0.0, 0.25, "Q20  |  Section I  |  Two visualizations for spoiler-prone books",
                 color="white", fontsize=14, fontweight="bold",
                 bbox=dict(facecolor=NAVY, boxstyle="round,pad=0.5"))
    ax_b = fig_c.add_subplot(gs[1, 0])
    spoiler_prone_barh(ax_b, prone)
    ax_r = fig_c.add_subplot(gs[1, 1], polar=True)
    radar_polygon(ax_r, radar_src)
    ax_n = fig_c.add_subplot(gs[1, 2])
    ax_n.set_xlim(0, 1)
    ax_n.set_ylim(0, 1)
    ax_n.axis("off")
    numbered_notes(
        ax_n,
        [
            ("Pick 1: spoiler-ratio bars", "Ranks books by mean spoiler_ratio (k/n averaged). That is the 'spoiler-prone' score."),
            ("Pick 2: radar (Q15–16)", "Shows whether that book is also long, popular, and highly rated — or only spoiler-heavy."),
            ("Why not t-SNE", "t-SNE is wording geometry, not a book ranking. Histogram has no book identity."),
            ("Publisher sentence", "High spoiler_ratio + high volume is a warning. High ratio on a tiny sample of reviews is noise."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 20, fig_g, fig_c,
        chart_class="paired barh + radar",
        graph_structure="Left: books ranked by mean spoiler_ratio. Right: radar of count/rating/length/ratio",
        features=["mean_spoiler_ratio", "n_reviews", "mean_rating", "mean_length"],
        metadata_fields=["book_id", "review_sentences", "rating", "has_spoiler"],
        formulas=["spoiler_prone(book) = mean_i (k_i / n_i)", "require a minimum review count before ranking"],
        what_represents="Which books attract spoiler-heavy reviews, and whether those books are otherwise notable.",
        feature_analysis=(
            f"Top spoiler-prone book in-sample: {prone.iloc[0]['book_id']} "
            f"(mean ratio {prone.iloc[0]['mean_spoiler_ratio']:.3f}, "
            f"{int(prone.iloc[0]['n_reviews'])} reviews). Minimum review filter avoids one-review flukes."
        ),
        explanation=(
            "The two most useful views are (1) a ranking of books by mean spoiler_ratio (barh) and "
            "(2) the radar of that book against review count, mean rating, and length. Together they "
            "answer 'which title is spoiler-prone?' and 'is that signal coming from a widely discussed book?'. "
            "t-SNE and the rating histogram do not identify a book."
        ),
        how_code=(
            "groupby book_id → mean spoiler_ratio with a min-review threshold; barh for the ranking; "
            "radar_polygon for the same books' other metrics after min-max."
        ),
        functions=["Analysis.spoiler_prone_books", "plots.spoiler_prone_barh", "plots.radar_polygon"],
        safeguards=["min_reviews filter", "normalised radar so ratio is not swamped by count"],
        viva_steps=[
            "Name the two plots: spoiler-ratio bars + radar.",
            "Say why: rank + context.",
            "Reject t-SNE and the star histogram.",
        ],
        extra_meta={"top_spoiler_book": str(prone.iloc[0]["book_id"]), "top_ratio": round(float(prone.iloc[0]["mean_spoiler_ratio"]), 4)},
    )
