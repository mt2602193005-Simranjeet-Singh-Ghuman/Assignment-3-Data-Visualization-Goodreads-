"""Concept / formula cards (Q1–Q5, Q12, Q17, Q19, Q21) and the viva map."""

from __future__ import annotations

import matplotlib.pyplot as plt

from config import GOLD, INK, MUTED, NAVY, NON_SPOILER, OUTPUT_DIR, SPOILER, TEAL, question_dir
from plots import arrow, concept_axes, draw_digraph, radar_polygon, tsne_scatter
from render import box, new_card_figure, new_graph_figure, numbered_notes, save_fig, write_pack


def _finish(analysis, qid, fig_graph, fig_card, **kwargs):
    # One question folder always gets the clean graph, the viva card, and the write-up.
    out = question_dir(qid)
    save_fig(fig_graph, out / "graph.png")
    save_fig(fig_card, out / "bettergraph_viva.png")
    kwargs.pop("n_rows", None)
    write_pack(out, qid, analysis=analysis, **kwargs)
    print(f"  saved Q{qid:02d} -> {out}")


def _footer(analysis) -> str:
    gb = analysis.file_bytes / (1024 ** 3)
    return (
        f"metadata: JSONL reviews | n={analysis.n:,} of MAX_ROWS={analysis.max_rows:,} | "
        f"file={gb:.2f} GB | books={analysis.n_books:,} users={analysis.n_users:,}"
    )


def run_q01(analysis):
    def draw(ax):
        # Node-and-edge schema graph: centre = one review, edges = "has field".
        nodes = {
            "rev": (5.0, 8.7, 3.6, 1.15, "REVIEW record\n(one JSONL line)", NAVY, "white"),
            "uid": (1.15, 6.35, 2.0, 0.95, "user_id\nstring", NAVY, "white"),
            "ts": (3.4, 6.35, 2.1, 0.95, "timestamp\nYYYY-MM-DD", TEAL, "white"),
            "rt": (5.6, 6.35, 1.9, 0.95, "rating\n0–5 int", GOLD, NAVY),
            "hs": (7.85, 6.35, 2.1, 0.95, "has_spoiler\nTrue/False", SPOILER, "white"),
            "bid": (2.3, 4.35, 2.2, 0.95, "book_id", MUTED, "white"),
            "rid": (5.0, 4.35, 2.2, 0.95, "review_id", MUTED, "white"),
            "rs": (7.7, 4.35, 2.6, 1.05, "review_sentences\nlist of [flag, text]", TEAL, "white"),
            "f0": (5.5, 1.55, 2.6, 1.15, "[ 0 , text ]\nnon-spoiler sentence", NON_SPOILER, "white"),
            "f1": (8.35, 1.55, 2.6, 1.15, "[ 1 , text ]\nspoiler sentence", SPOILER, "white"),
        }
        edges = [
            ("rev", "uid"), ("rev", "ts"), ("rev", "rt"), ("rev", "hs"),
            ("rev", "bid"), ("rev", "rid"), ("rev", "rs"),
            ("rs", "f0"), ("rs", "f1"),
        ]
        draw_digraph(ax, nodes, edges, "Schema graph of one review (nodes = fields, arrows = contains)")

    fig_g, ax_g = new_graph_figure("Schema of one Goodreads spoiler review")
    draw(ax_g)
    fig_c, ax_p, ax_n = new_card_figure(1, "schema graph (nodes + edges)")
    draw(ax_p)
    numbered_notes(
        ax_n,
        [
            ("Centre node", "One JSON object = one line in the file = one review."),
            ("Spoiler storage", "Follow the arrow into review_sentences. Spoilers live there as [flag, text], not as a paragraph tag."),
            ("Two layers", "has_spoiler is a sibling field (whole review). flag 0/1 is a child of review_sentences."),
            ("How to read this graph", "Nodes are metadata fields. Arrows mean 'this record contains that field'."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 1, fig_g, fig_c,
        chart_class="schema graph (directed tree)",
        graph_structure="Directed tree: REVIEW root → seven field nodes; review_sentences → flag-0 and flag-1 sentence nodes",
        features=[],
        metadata_fields=["user_id", "timestamp", "review_sentences", "rating", "has_spoiler", "book_id", "review_id"],
        formulas=[],
        what_represents="The schema of one JSONL record as a graph. Edges show containment; the two bottom nodes are how spoiler labels are stored.",
        feature_analysis="No derived features yet. You must name every node and say which edge carries per-sentence spoilers (review_sentences → [1, text]).",
        explanation=(
            "A record is one JSON object with user_id, timestamp, rating (0–5), has_spoiler (boolean), "
            "book_id, review_id, and review_sentences. review_sentences stores spoiler information as a "
            "list of two-element arrays: [0-or-1 flag, sentence string]. graph.png is a node-and-edge tree of that schema."
        ),
        how_code=(
            "loader reads JSONL with json.loads(line). It does not flatten review_sentences. "
            "The schema graph is drawn from those field names; nodes are fields, arrows mean contains."
        ),
        functions=["json.loads", "load_reviews", "plots.draw_digraph"],
        safeguards=["Stream line-by-line; never json.load the whole 1.75 GB file."],
        viva_steps=[
            "Point at the centre node: one review = one JSON line.",
            "Follow the arrow to review_sentences, then to [0, text] and [1, text].",
            "Point at has_spoiler as a separate sibling node, not a sentence flag.",
        ],
        extra_meta={"example_review_id": analysis.example.get("review", {}).get("review_id")},
        how_graph_made=(
            "A directed tree is drawn with matplotlib patches: one node per JSON field, arrows for containment. "
            "This is a schema graph, not a histogram."
        ),
    )


def run_q02(analysis):
    agree = analysis.n_agree
    mismatch = analysis.n_mismatch
    pct = 100 * agree / analysis.n if analysis.n else 0

    def draw(ax):
        ax.bar(
            ["agreement\n(has_spoiler matches k≥1)", "mismatches"],
            [agree, mismatch],
            color=[TEAL, GOLD],
            edgecolor="white",
            width=0.55,
        )
        ax.set_ylabel("number of reviews")
        ax.set_title("Do the two spoiler layers agree?")
        for x, v in enumerate([agree, mismatch]):
            ax.text(x, v, f" {v:,}", ha="center", va="bottom", color=NAVY, fontsize=10)
        ax.set_ylim(0, max(agree, mismatch, 1) * 1.12)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig_g, ax_g = new_graph_figure("has_spoiler vs sentence flags")
    draw(ax_g)
    fig_c, ax_p, ax_n = new_card_figure(2, "bar chart")
    draw(ax_p)
    numbered_notes(
        ax_n,
        [
            ("Different grains", "has_spoiler = one True/False for the whole review. Flags = 0/1 on each sentence."),
            ("Expected link", "Yes: you expect True whenever k ≥ 1 spoiler sentences. That is the design, not a law of nature."),
            ("Check, don't assume", f"In this sample, {agree:,} reviews match the rule and {mismatch:,} do not."),
            ("Read the bars", "Left bar = consistent records. Right bar = the two fields disagree."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 2, fig_g, fig_c,
        chart_class="bar chart",
        graph_structure="Two bars: agreement count vs mismatch count",
        features=["n_spoiler_sents"],
        metadata_fields=["has_spoiler", "review_sentences"],
        formulas=["expected: has_spoiler == True  iff  n_spoiler_sents >= 1"],
        what_represents="How often the review-level boolean matches 'at least one sentence flag is 1'.",
        feature_analysis=(
            f"n_spoiler_sents is the count of flag=1 sentences. Agreement {agree:,}/{analysis.n:,}. "
            "A mismatch is rare but possible (label noise). Never say they are the same field."
        ),
        explanation=(
            "has_spoiler is a per-review boolean. The 0/1 values inside review_sentences are per-sentence. "
            "Yes, you would expect has_spoiler=True whenever at least one sentence is flagged 1. "
            f"On this sample that rule holds for {agree:,} reviews ({pct:.2f}%) with {mismatch:,} mismatches."
        ),
        how_code=(
            "After features are built, n_mismatch counts rows where has_spoiler disagrees with "
            "(n_spoiler_sents > 0). The bar chart plots those two counts."
        ),
        functions=["spoiler_sentence_count", "Analysis.__post_init__"],
        safeguards=["Treat mismatches as data, not as a crash."],
        viva_steps=[
            "Name the two grains: review vs sentence.",
            "State the expected iff rule.",
            f"Point at the bars: agree={agree:,}, mismatch={mismatch:,}.",
        ],
        extra_meta={"n_agree": agree, "n_mismatch": mismatch},
        how_graph_made="A two-bar matplotlib bar chart of agreement vs mismatch counts after the iff check.",
    )


def run_q03(analysis):
    gb = analysis.file_bytes / (1024 ** 3)
    unread = max(1_380_000 - analysis.n, 0)

    def draw(ax):
        labels = [f"Kept in this run\nMAX_ROWS = {analysis.max_rows:,}", "Unread (still on disk)\nnever loaded"]
        vals = [analysis.n, unread]
        colors = [TEAL, MUTED]
        bars = ax.barh(labels, vals, color=colors, edgecolor="white", height=0.55)
        ax.set_xlabel("number of reviews")
        ax.set_title("How much of the ~1.38 million-review file we used")
        ax.ticklabel_format(style="plain", axis="x")
        for bar, v in zip(bars, vals):
            ax.text(v, bar.get_y() + bar.get_height() / 2, f"  {v:,.0f}", va="center", color=NAVY, fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig_g, ax_g = new_graph_figure("Safe loading with MAX_ROWS")
    draw(ax_g)
    fig_c, ax_p, ax_n = new_card_figure(3, "horizontal bar chart")
    draw(ax_p)
    numbered_notes(
        ax_n,
        [
            ("Why a list is risky", f"The file is {gb:.2f} GB. A Python list of dicts is larger than the file. A laptop with 8–16 GB RAM can page or die."),
            ("MAX_ROWS formula", "Memory ≈ MAX_ROWS × average review size, not 1.38 million × average size."),
            ("How we load", "Open the file, json.loads one line, append, stop at MAX_ROWS. Never hold the rest."),
            ("Read the bars", f"Teal = {analysis.n:,} kept. Grey = ~{unread:,} unread, not deleted."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 3, fig_g, fig_c,
        chart_class="horizontal bar chart",
        graph_structure="Two horizontal bars: reviews kept vs reviews left unread on disk",
        features=[],
        metadata_fields=["entire JSONL record, streamed"],
        formulas=["memory ≈ MAX_ROWS × avg_review_bytes", f"MAX_ROWS = {analysis.max_rows}"],
        what_represents="The sample we analysed versus the rest of the 1.38 million reviews that were never loaded.",
        feature_analysis="Loading is not a plot feature. It is the reason every later graph is a sample, not the census of 1.38M reviews.",
        explanation=(
            f"Loading ~1.38 million nested reviews (~{gb:.2f} GB) as one list can exhaust laptop RAM because "
            "Python objects add overhead on top of the raw JSON. We stream line-by-line and stop at "
            f"MAX_ROWS={analysis.max_rows:,}, keeping {analysis.n:,} reviews. The grey bar is unread, not deleted."
        ),
        how_code=(
            "load_reviews opens DATA_PATH as text, iterates lines, json.loads each line, breaks when "
            "len(rows) reaches MAX_ROWS. reviews_to_frame then builds the DataFrame only for that cap."
        ),
        functions=["load_reviews", "reviews_to_frame"],
        safeguards=["Hard cap MAX_ROWS", "Line-by-line parse", "UTF-8 text mode, not one huge json.load"],
        viva_steps=[
            "State the file size and 1.38M reviews.",
            "Point at the teal bar: what we kept.",
            "Point at the grey bar: unread, still on disk.",
        ],
        extra_meta={"file_gb": round(gb, 2), "load_seconds": round(analysis.load_seconds, 2), "unread_approx": unread},
        how_graph_made="Horizontal bar chart of kept vs unread review counts. Unread = published 1.38M minus MAX_ROWS.",
    )


def run_q04(analysis):
    ex = analysis.example
    n, k, length, ratio = ex["n"], ex["k"], ex["length"], ex["ratio"]
    flags = ex.get("flags") or []
    show = flags[:8]
    flag_str = "  ".join(str(f) for f in show) + ("  ..." if len(flags) > 8 else "")

    def draw_hists(ax_len, ax_ratio):
        lengths = analysis.df["review_length"]
        cap = float(lengths.quantile(0.95)) if len(lengths) else 1
        ax_len.hist(lengths.clip(upper=cap), bins=40, color=NAVY, edgecolor="white")
        ax_len.axvline(length, color=GOLD, lw=2, label=f"worked example = {length:,}")
        ax_len.set_xlabel("review_length (characters)")
        ax_len.set_ylabel("reviews")
        ax_len.set_title("review_length = sum of character counts")
        ax_len.legend(frameon=False, fontsize=8)
        ax_len.spines["top"].set_visible(False)
        ax_len.spines["right"].set_visible(False)
        ax_ratio.hist(analysis.df["spoiler_ratio"], bins=25, color=TEAL, edgecolor="white")
        ax_ratio.axvline(ratio, color=GOLD, lw=2, label=f"worked example = {ratio:.3f}")
        ax_ratio.set_xlabel("spoiler_ratio = k / n")
        ax_ratio.set_ylabel("reviews")
        ax_ratio.set_title("spoiler_ratio")
        ax_ratio.legend(frameon=False, fontsize=8)
        ax_ratio.spines["top"].set_visible(False)
        ax_ratio.spines["right"].set_visible(False)

    fig_g, axes = plt.subplots(1, 2, figsize=(12.4, 6.2), dpi=140)
    fig_g.patch.set_facecolor("white")
    draw_hists(axes[0], axes[1])
    fig_g.suptitle("The two features these formulas produce", color=NAVY, fontweight="bold")
    fig_g.tight_layout()

    fig_c, ax_p, ax_n = new_card_figure(4, "histograms of derived features")
    ax_p.hist(analysis.df["spoiler_ratio"], bins=25, color=TEAL, edgecolor="white")
    ax_p.axvline(ratio, color=GOLD, lw=2)
    ax_p.set_xlabel("spoiler_ratio = k / n")
    ax_p.set_ylabel("reviews")
    ax_p.set_title(f"spoiler_ratio  |  example k/n = {k}/{n} = {ratio:.3f}")
    ax_p.spines["top"].set_visible(False)
    ax_p.spines["right"].set_visible(False)
    numbered_notes(
        ax_n,
        [
            ("Length formula", f"Join sentence strings, count characters. Example review_length = {length:,}. Gold line on graph.png."),
            ("Ratio formula", f"spoiler_ratio = k / n = {k} / {n} = {ratio:.3f}. Gold line on this histogram."),
            ("Working aloud", f"Flags {flag_str}. Numerator k = flag 1. Denominator n = sentence count. Divide."),
            ("Where it goes", "length → boxplot, scatter, heatmap. ratio → heatmap, radar, spoiler-prone bars."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 4, fig_g, fig_c,
        chart_class="histograms",
        graph_structure="Two histograms: review_length (left) and spoiler_ratio (right); gold line = worked example",
        features=["review_length", "spoiler_ratio", "n_sentences", "n_spoiler_sents"],
        metadata_fields=["review_sentences"],
        formulas=[
            "review_length = sum(len(sentence_text) for sentence in review_sentences)",
            "spoiler_ratio = k / n   if n > 0 else 0.0",
            "n = len(review_sentences)",
            "k = count of sentences whose flag == 1",
        ],
        what_represents="The distribution of the two derived features after applying the formulas to every loaded review.",
        feature_analysis=(
            f"On the example review, n={n}, k={k}, length={length:,}, ratio={ratio:.3f}. "
            "Length is a size feature. Ratio is a spoiler intensity feature. They are not the same as has_spoiler. "
            "Most spoiler_ratio mass sits at 0 (reviews with no spoiler sentences)."
        ),
        explanation=(
            f"review_length is the character count of all sentence texts (example: {length:,}). "
            f"spoiler_ratio is k/n where k is spoiler sentences and n is sentence count "
            f"(example: {k}/{n} = {ratio:.3f}). If n is 0 the ratio is defined as 0.0 (see Q5). "
            "graph.png shows both distributions."
        ),
        how_code=(
            "features.review_length sums len(text) over sentence pairs. features.spoiler_ratio "
            "calls spoiler_sentence_count / n_sentences. reviews_to_frame stores both on the DataFrame. "
            "Then matplotlib hist() plots those columns."
        ),
        functions=["review_length", "spoiler_ratio", "spoiler_sentence_count", "n_sentences"],
        safeguards=["Character count ignores the flag", "Ratio uses n==0 guard from Q5"],
        viva_steps=[
            "Write review_length = sum of character lengths.",
            "Write spoiler_ratio = k/n.",
            f"Plug the example: k={k}, n={n}, ratio={ratio:.3f} (gold line).",
            "Say which plots consume each feature.",
        ],
        extra_meta={"example_n": n, "example_k": k, "example_length": length, "example_ratio": round(ratio, 4)},
        how_graph_made="Two matplotlib histograms of the derived columns. A gold vertical line marks the worked example review.",
    )


def run_q05(analysis):
    z = analysis.n_zero_sentence

    def draw(ax):
        s = analysis.df["n_sentences"]
        cap = float(s.quantile(0.95)) if len(s) else 1
        ax.hist(s.clip(upper=cap), bins=40, color=TEAL, edgecolor="white")
        ax.axvline(0, color=GOLD, lw=2.4, label="n = 0  (would crash without the guard)")
        ax.set_xlabel("n_sentences")
        ax.set_ylabel("reviews")
        ax.set_title(f"Sentence counts  |  empty reviews in sample = {z:,}")
        ax.legend(frameon=False, fontsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig_g, ax_g = new_graph_figure("spoiler_ratio zero-sentence guard")
    draw(ax_g)
    fig_c, ax_p, ax_n = new_card_figure(5, "histogram")
    draw(ax_p)
    numbered_notes(
        ax_n,
        [
            ("Crash source", "k / n with n=0 is ZeroDivisionError in Python."),
            ("Safeguard", "if n == 0: return 0.0  BEFORE the division. That is the whole answer."),
            ("Meaning of 0.0", "An empty review is treated as having no spoiler fraction, not as missing / NaN."),
            ("Evidence", f"{z:,} empty-sentence reviews in this sample. The gold line is n=0."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 5, fig_g, fig_c,
        chart_class="histogram",
        graph_structure="Histogram of n_sentences with a gold line at 0, the crash case",
        features=["spoiler_ratio", "n_sentences"],
        metadata_fields=["review_sentences"],
        formulas=["spoiler_ratio = 0.0 if n == 0 else k / n"],
        what_represents="How many sentences reviews have, and where the divide-by-zero case sits (n=0).",
        feature_analysis=(
            f"{z:,} rows have n_sentences=0. Their spoiler_ratio is 0.0. "
            "They still appear in later plots instead of dropping out as NaN."
        ),
        explanation=(
            "The function does not crash because it checks n == 0 and returns 0.0 before dividing. "
            f"The safeguard is `if n == 0: return 0.0`. This sample contained {z:,} such reviews."
        ),
        how_code=(
            "spoiler_ratio() in data.py: n = n_sentences(sents); if n == 0: return 0.0; "
            "return spoiler_sentence_count(sents) / n. The histogram is df['n_sentences']."
        ),
        functions=["spoiler_ratio"],
        safeguards=["Explicit n == 0 return before division"],
        viva_steps=[
            "Name the crash: division by zero.",
            "Say if n==0 return 0.0, else k/n.",
            "Point at the gold line on the histogram: n=0.",
        ],
        extra_meta={"n_zero_sentence": z},
        how_graph_made="Histogram of n_sentences. Gold vertical line marks the empty-review case the guard handles.",
    )


def run_q12(analysis):
    def draw(ax):
        cols = list(analysis.corr.columns)
        labels, vals, colors = [], [], []
        for i, a in enumerate(cols):
            for b in cols[i + 1 :]:
                r = float(analysis.corr.loc[a, b])
                labels.append(f"{a} vs {b}")
                vals.append(r)
                colors.append(TEAL if r == max(
                    [float(analysis.corr.loc[x, y]) for ii, x in enumerate(cols) for y in cols[ii + 1 :]]
                ) else NAVY)
        order = sorted(zip(vals, labels, colors), key=lambda t: t[0])
        vals, labels, colors = zip(*order)
        ax.barh(list(labels), list(vals), color=list(colors), edgecolor="white")
        ax.set_xlim(-1.05, 1.05)
        ax.axvline(0, color=MUTED, lw=1)
        ax.axvline(-1, color=SPOILER, ls="--", lw=0.8)
        ax.axvline(1, color=TEAL, ls="--", lw=0.8)
        ax.set_xlabel("Pearson r   (always between −1 and +1)")
        ax.set_title("Every pair on the r scale")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig_g, ax_g = new_graph_figure("Why correlation is between -1 and +1")
    draw(ax_g)
    fig_c, ax_p, ax_n = new_card_figure(12, "bar chart of r")
    draw(ax_p)
    numbered_notes(
        ax_n,
        [
            ("Bounds", "Pearson r is covariance divided by (sx sy). After that scaling, r cannot go outside [-1, +1]."),
            ("Near 0", "No linear relationship. There might still be a curve — r only sees straight lines."),
            ("Not percent", "r = 0.82 is not '82% correlated'. It is the linear association strength."),
            ("Not cause", "A high r between n_sentences and review_length does not mean one causes the other."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 12, fig_g, fig_c,
        chart_class="horizontal bar chart",
        graph_structure="One bar per feature pair; x = Pearson r on a locked [-1, +1] axis; dashed lines at the bounds",
        features=["rating", "n_sentences", "review_length", "spoiler_ratio"],
        metadata_fields=["rating", "review_sentences"],
        formulas=["r = cov(x,y) / (s_x s_y)", "-1 <= r <= +1"],
        what_represents="Every pairwise r in this sample, drawn on the only scale r is allowed to use.",
        feature_analysis=(
            f"Strongest pair on this sample is {analysis.strongest_pair[0]}–{analysis.strongest_pair[1]} "
            f"at r={analysis.strongest_r:.3f}, the teal bar near +1."
        ),
        explanation=(
            "Pearson r is a standardized covariance, so it is bounded by -1 and +1. "
            "A value close to 0 means little or no linear association (a non-linear pattern can still exist)."
        ),
        how_code="pandas DataFrame.corr() uses Pearson by default on the four numeric columns. Bars are the off-diagonal values.",
        functions=["DataFrame.corr"],
        safeguards=["x-axis locked to [-1, 1] so a bar cannot wander outside the math"],
        viva_steps=[
            "Point at the dashed lines: -1 and +1.",
            "Say r = cov / (sx sy), hence the bounds.",
            "Point at the longest teal bar: strongest pair.",
        ],
        extra_meta={"strongest_pair": list(analysis.strongest_pair), "strongest_r": round(analysis.strongest_r, 4)},
        how_graph_made="Horizontal bars of each unique pair's Pearson r. Axis is fixed from -1 to +1.",
    )


def run_q17(analysis):
    blob = analysis.tsne_main()

    def draw(ax):
        tsne_scatter(ax, blob, "TF-IDF (300-D) reduced to 2-D by t-SNE")

    fig_g, ax_g = new_graph_figure("What t-SNE does")
    draw(ax_g)
    fig_c, ax_p, ax_n = new_card_figure(17, "t-SNE scatter")
    draw(ax_p)
    numbered_notes(
        ax_n,
        [
            ("Input", f"Each review → TF-IDF with max_features=300. This run used {blob['n_features']} columns, {blob['n']:,} reviews."),
            ("What t-SNE does", "It places each review as a 2D point so nearby high-D neighbours stay nearby in 2D."),
            ("What it does not do", "It does not predict spoilers. Axes are not interpretable like rating or length."),
            ("Colour", "Red/blue is painted AFTER the embedding. t-SNE did not see has_spoiler."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 17, fig_g, fig_c,
        chart_class="t-SNE scatter",
        graph_structure="2D scatter of reviews; x,y = t-SNE coordinates; colour = has_spoiler (not an input)",
        features=["text (joined sentences)", "TF-IDF", "t-SNE coordinates"],
        metadata_fields=["review_sentences"],
        formulas=["TF-IDF(word, review) = tf × log(N / df)", "t-SNE minimises KL(P_highD || Q_2D)"],
        what_represents="Wording similarity in 2D. Nearby points used similar words. Axes are not rating or length.",
        feature_analysis=(
            "TF-IDF turns wording into numbers. t-SNE only rearranges those numbers for a plot. "
            "Spoiler colour is painted afterwards; t-SNE did not use has_spoiler as an input."
        ),
        explanation=(
            "t-SNE converts each review's high-dimensional TF-IDF vector (up to 300 dimensions) into two "
            "coordinates so that reviews with similar wording stay close together. It is a visualisation "
            "embedding, not a classifier. graph.png is that 2D scatter."
        ),
        how_code=(
            "TfidfVectorizer(max_features=300) on joined sentence text, then sklearn TSNE(n_components=2, "
            "perplexity=30, init='pca') on the dense matrix. has_spoiler is used only to colour points."
        ),
        functions=["TfidfVectorizer", "TSNE", "compute_tsne"],
        safeguards=["Subsample TSNE_SAMPLE reviews", "perplexity capped by sample size"],
        viva_steps=[
            "Say text → 300-D TF-IDF → these 2D points.",
            "Say 'preserves neighbours, not global distances'.",
            "Say axes are not rating or length.",
        ],
        extra_meta={"tsne_n": blob["n"], "tsne_features": blob["n_features"], "perplexity": blob["perplexity"]},
        how_graph_made="sklearn TSNE embedding plotted as a scatter. Colour is has_spoiler, applied after fit.",
    )


def run_q19(analysis):
    panel = analysis.tsne_perplexity_panel()
    fig_g, axes = plt.subplots(1, 3, figsize=(14.5, 5.2), dpi=140)
    fig_g.patch.set_facecolor("white")
    fig_g.suptitle("Same reviews, three perplexity values", color=NAVY, fontweight="bold")
    for ax, p in zip(axes, (5, 30, 100)):
        blob = panel[p]
        tsne_scatter(ax, blob, f"perplexity ≈ {blob['perplexity']}")
    fig_g.tight_layout()

    fig_c = plt.figure(figsize=(18.4, 10.4), dpi=140, facecolor="#F4F6F7")
    gs = fig_c.add_gridspec(2, 3, height_ratios=[1.15, 0.85], left=0.04, right=0.98, top=0.90, bottom=0.08, hspace=0.28, wspace=0.18)
    fig_c.text(0.04, 0.94, "Q19  |  Section H  |  Role of perplexity=30", color="white", fontsize=15,
               fontweight="bold", bbox=dict(facecolor=NAVY, boxstyle="round,pad=0.6"))
    for i, p in enumerate((5, 30, 100)):
        ax = fig_c.add_subplot(gs[0, i])
        blob = panel[p]
        tsne_scatter(ax, blob, f"perplexity ≈ {blob['perplexity']}")
    ax_n = fig_c.add_subplot(gs[1, :])
    ax_n.set_xlim(0, 1)
    ax_n.set_ylim(0, 1)
    ax_n.axis("off")
    numbered_notes(
        ax_n,
        [
            ("Definition", "Perplexity ≈ how many neighbours each point listens to. perplexity=30 ≈ 'about 30 nearby reviews'."),
            ("Too small (5)", "Local specks / many tiny clumps. The map looks dusty."),
            ("Too large (100)", "Neighbourhoods smear together. One or two big blobs."),
            ("Why 30", "A default middle ground for a few hundred to a few thousand points. Changing it changes the STORY the plot tells, not the data."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 19, fig_g, fig_c,
        chart_class="t-SNE perplexity comparison",
        graph_structure="Three 2D scatter panels of the same TF-IDF sample at perplexity 5, 30, 100",
        features=["TF-IDF", "t-SNE"],
        metadata_fields=["review_sentences"],
        formulas=["perplexity ≈ 2^{H(neighbour distribution)}", "effective neighbour count ≈ 30"],
        what_represents="How the same wording vectors look when t-SNE is told to respect few vs many neighbours.",
        feature_analysis=(
            "The points are the same reviews. Only the embedding parameter changes. "
            "If clusters 'appear' or 'vanish' when perplexity moves, they were a visualisation effect."
        ),
        explanation=(
            "perplexity=30 sets the effective number of neighbours t-SNE preserves (about 30). "
            "Lower values make many tiny clusters; higher values melt points into large blobs. "
            "The parameter changes layout, not the underlying TF-IDF."
        ),
        how_code=(
            "A 800-review text sample is vectorized once, then TSNE is fit three times with perplexity "
            "5, 30, and 100 (100 capped by n/4). compute_tsne enforces that cap so sklearn does not error."
        ),
        functions=["compute_tsne", "Analysis.tsne_perplexity_panel"],
        safeguards=["perplexity < n_samples", "shared random_state"],
        viva_steps=[
            "Say perplexity = effective neighbours.",
            "Point at 5 = dust, 30 = default, 100 = smear.",
            "Say we did not change the reviews, only the parameter.",
        ],
        extra_meta={"perplexities": [5, 30, 100], "sample_n": panel[30]["n"]},
    )


def run_q21(analysis):
    gb = analysis.file_bytes / (1024 ** 3)

    def draw(ax):
        labels = ["reviews", "books", "users"]
        sample = [analysis.n, analysis.n_books, analysis.n_users]
        full = [1_380_000, 25_000, 19_000]
        x = range(len(labels))
        w = 0.36
        ax.bar([i - w / 2 for i in x], sample, width=w, color=TEAL, label=f"this run (n={analysis.n:,})", edgecolor="white")
        ax.bar([i + w / 2 for i in x], full, width=w, color=SPOILER, alpha=0.75, label="full UCSD file (published)", edgecolor="white")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_ylabel("count")
        ax.set_yscale("log")
        ax.set_title("Sample vs full corpus (log scale — otherwise 1.38M eats the chart)")
        ax.legend(frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig_g, ax_g = new_graph_figure("Sample vs full UCSD dataset")
    draw(ax_g)
    fig_c, ax_p, ax_n = new_card_figure(21, "comparison board")
    draw(ax_p)
    numbered_notes(
        ax_n,
        [
            ("PDF vs us", "The PDF talks about synthetic data. We used the real file, capped by MAX_ROWS. Schema is the same."),
            ("What can flip", "The high-end rating skew may stay, but the exact mode, medians, r values, top-10 books, and t-SNE clouds will move."),
            ("Sampling bias", "First-N JSONL rows can over-represent early users. Full data is closer to the published 3.22% sentence-spoiler rate."),
            ("Honest viva close", "Directions (spoilers longer, volume ≠ quality) should hold; exact numbers and clean t-SNE clusters should not be over-claimed."),
        ],
        _footer(analysis),
    )
    _finish(
        analysis, 21, fig_g, fig_c,
        chart_class="grouped bar chart (log scale)",
        graph_structure="Grouped bars: reviews / books / users for this sample vs the published full file; y is log so 1.38M does not hide 50k",
        features=["all derived features, as sample estimates"],
        metadata_fields=["full JSONL schema"],
        formulas=["sample estimate ≠ population value"],
        what_represents="Which conclusions are sample-stable and which would likely change on 1.38M reviews.",
        feature_analysis=(
            f"File on disk is {gb:.2f} GB. We analysed {analysis.n:,} reviews "
            f"({100 * analysis.n / 1_380_000:.2f}% of ~1.38M). t-SNE used an even smaller text subset."
        ),
        explanation=(
            "Re-running on the full UCSD set would keep the schema and the same formulas, but counts, "
            "medians, correlations, leaderboards, and especially t-SNE separation would change. Spoilers "
            "are rare (~3.22% of sentences) and wording overlaps, so clusters should look messier than a "
            "small balanced sample. First-N row sampling can also bias users. Directions (spoiler reviews "
            "tend to be longer; most-reviewed is not best) are more trustworthy than exact numbers."
        ),
        how_code=(
            "The same pipeline would run with a larger MAX_ROWS (or reservoir sampling). "
            "Q3's streaming still applies; you still must not json.load the whole file."
        ),
        functions=["load_reviews(max_rows=...)", "build_analysis"],
        safeguards=["Keep streaming even if MAX_ROWS grows", "Do not treat sample t-SNE as the population geometry"],
        viva_steps=[
            "Admit this is a cap, not 1.38M.",
            "List what stays: schema, formulas, likely skew.",
            "List what moves: exact r, top books, t-SNE cleanliness.",
        ],
        extra_meta={"sample_n": analysis.n, "published_reviews": 1_380_000, "file_gb": round(gb, 2)},
        how_graph_made="Grouped bar chart of reviews, books, and users. Sample vs published full-file counts. Log y-axis so 1.38M does not hide 50k.",
    )


def run_map(analysis):
    """Overview poster you open first in viva, plus a 'how to speak / how to run' sheet."""
    gb = analysis.file_bytes / (1024 ** 3)
    unread = max(1_380_000 - analysis.n, 0)

    fig, ax = plt.subplots(figsize=(18.6, 12.2), dpi=140)
    fig.patch.set_facecolor("#F4F6F7")
    concept_axes(ax)
    ax.set_title(
        "Assignment 3 viva map  —  point here first, then open one question card",
        color=NAVY, fontsize=16, fontweight="bold", pad=8,
    )

    # Dataset strip
    box(ax, 0.02, 0.86, 0.96, 0.10, "", "#EAF2F8", NAVY, pad=0.008)
    ax.text(
        0.50, 0.91,
        f"Full file: {gb:.2f} GB  ·  ~1.38 million reviews  ·  we KEEP first {analysis.n:,}  "
        f"(MAX_ROWS)  ·  ~{unread:,} reviews stay UNREAD on disk, not deleted",
        ha="center", va="center", color=NAVY, fontsize=10, fontweight="bold",
        transform=ax.transAxes,
    )

    # Pipeline
    box(ax, 0.02, 0.70, 0.18, 0.12, "1. JSONL file\none review / line", NAVY, NAVY, fs=9)
    box(ax, 0.22, 0.70, 0.18, 0.12, "2. Stream + stop\nQ3  MAX_ROWS", TEAL, TEAL, fs=9)
    box(ax, 0.42, 0.70, 0.18, 0.12, "3. Formulas Q4–5\nlength, k/n", GOLD, GOLD, tc=NAVY, fs=9)
    box(ax, 0.62, 0.70, 0.16, 0.12, "4. Plots\nQ6–Q19", SPOILER, SPOILER, fs=9)
    box(ax, 0.80, 0.70, 0.18, 0.12, "5. Q20–Q21\nspoiler-prone +\nsample vs full", NAVY, NAVY, fs=8)
    arrow(ax, 0.20, 0.76, 0.22, 0.76)
    arrow(ax, 0.40, 0.76, 0.42, 0.76)
    arrow(ax, 0.60, 0.76, 0.62, 0.76)
    arrow(ax, 0.78, 0.76, 0.80, 0.76)

    # Sections — what A means vs all
    tiles = [
        (0.02, 0.52, "A  Q1–Q3\nschema, flags,\nwhy we cap rows", NAVY),
        (0.22, 0.52, "B  Q4–Q5\nlength & k/n\nzero-sentence guard", TEAL),
        (0.42, 0.52, "C  Q6–Q8\nhistogram +\nboxplot / outliers", "#1F6AA5"),
        (0.62, 0.52, "D  Q9–Q10\nscatter, then\ncolour = spoiler", SPOILER),
        (0.82, 0.52, "E  Q11–Q12\nheatmap and\nwhy r ∈ [-1,1]", GOLD),
        (0.02, 0.33, "F  Q13–Q14\nbarh leaderboard\nvolume ≠ quality", TEAL),
        (0.22, 0.33, "G  Q15–Q16\nmin-max radar\nround vs spike", NAVY),
        (0.42, 0.33, "H  Q17–Q19\nTF-IDF → t-SNE\nperplexity=30", SPOILER),
        (0.62, 0.33, "I  Q20–Q21\nspoiler-prone pair\nsample vs 1.38M", GOLD),
        (0.82, 0.33, "CLI reminder\nA ≠ all\nA = section A only", MUTED),
    ]
    for x, y, text, col in tiles:
        tc = NAVY if col in (GOLD, MUTED) else "white"
        box(ax, x, y, 0.16, 0.16, text, col, col, fs=8, tc=tc)

    # Unused data
    box(ax, 0.02, 0.14, 0.47, 0.16, "", "white", NAVY, pad=0.01)
    ax.text(
        0.255, 0.27, "What we did not use — and why",
        ha="center", color=NAVY, fontsize=10, fontweight="bold", transform=ax.transAxes,
    )
    ax.text(
        0.255, 0.20,
        f"timestamp: no time question\n"
        f"user_id: count only ({analysis.n_users:,} users here)\n"
        f"raw sentence text: only t-SNE needs it\n"
        f"book title: field does not exist in this JSON",
        ha="center", va="center", color=INK, fontsize=8.5, transform=ax.transAxes,
    )

    box(ax, 0.51, 0.14, 0.47, 0.16, "", "white", TEAL, pad=0.01)
    ax.text(
        0.745, 0.27, "What to type in the terminal",
        ha="center", color=TEAL, fontsize=10, fontweight="bold", transform=ax.transAxes,
    )
    ax.text(
        0.745, 0.20,
        "4     → only question 4\n"
        "A     → section A  (Q1 Q2 Q3)   [not “all”]\n"
        "all   → questions 1–21 + this map\n"
        "map   → only this poster",
        ha="center", va="center", color=INK, fontsize=8.5, transform=ax.transAxes,
    )

    ax.text(
        0.50, 0.07,
        "Viva order: this map → that question’s bettergraph_viva.png → speak boxes 1–4 "
        "(formula → plug numbers → what the graph shows → edge case).",
        ha="center", color=MUTED, fontsize=9, transform=ax.transAxes,
    )

    out = OUTPUT_DIR / "00_viva_map"
    out.mkdir(parents=True, exist_ok=True)
    save_fig(fig, out / "viva_map.png")

    fig2, ax2 = plt.subplots(figsize=(16.5, 10.8), dpi=140)
    fig2.patch.set_facecolor("#F4F6F7")
    concept_axes(ax2)
    ax2.set_title("How to run the code, and how to talk in viva", color=NAVY, fontsize=16, fontweight="bold")
    box(ax2, 0.05, 0.55, 0.90, 0.38, "", "white", NAVY)
    ax2.text(0.50, 0.88, "VS Code terminal (first time)", ha="center", color=NAVY,
             fontsize=13, fontweight="bold", transform=ax2.transAxes)
    ax2.text(
        0.50, 0.70,
        "1. Terminal → New Terminal\n"
        "2. cd \"C:\\Users\\ASUS\\Desktop\\Prog Lab Assignment\\Assignment 3\\code\"\n"
        "3. python main.py\n"
        "4. When it asks, type  all   the first time (builds every folder).\n"
        "    Later, type  4  or  A  to practise one piece.\n\n"
        "A means Section A of the PDF (Q1–Q3).  all means every question.",
        ha="center", va="center", color=INK, fontsize=11, transform=ax2.transAxes,
    )
    box(ax2, 0.05, 0.08, 0.90, 0.42, "", "white", TEAL)
    ax2.text(0.50, 0.44, "When they ask a question", ha="center", color=TEAL,
             fontsize=13, fontweight="bold", transform=ax2.transAxes)
    ax2.text(
        0.50, 0.24,
        "1. Open that folder’s bettergraph_viva.png — do not improvise the formula.\n"
        "2. Read the formula out loud, then plug the worked numbers on the card.\n"
        "3. Point at the graph: “this axis / colour / bar is that formula.”\n"
        "4. If they ask how code did it → how_code_worked.txt (same folder).\n"
        "5. If they ask “did you use the whole 1.38 million?” → No. MAX_ROWS. Q3 and Q21.",
        ha="center", va="center", color=INK, fontsize=11, transform=ax2.transAxes,
    )
    save_fig(fig2, out / "how_to_speak.png")

    (out / "explanation.txt").write_text(
        f"""# Master viva map

Open `viva_map.png` first. Open `how_to_speak.png` if you need the terminal commands.

## Dataset
Full file ≈ {gb:.2f} GB / 1.38 million reviews. This project kept the first {analysis.n:,} (`MAX_ROWS`).
The rest were not loaded (unread, not deleted).

## CLI (what to type after `python main.py`)
- `4` — only question 4
- `A` — section A only (questions 1, 2, 3). **A is not all.**
- `all` — questions 1–21 plus this map
- `map` — only this poster
- `help` — print the option list again
- `q` — quit

## VS Code
```
cd "C:\\Users\\ASUS\\Desktop\\Prog Lab Assignment\\Assignment 3\\code"
python main.py
```
First time, type `all`.
""",
        encoding="utf-8",
    )
    stale = out / "explanation.md"
    if stale.exists():
        stale.unlink()
    print(f"  saved viva map -> {out}")
