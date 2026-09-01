"""
Assignment 3 — run this from the VS Code terminal.

First time (builds every output folder):

    cd "C:\\Users\\ASUS\\Desktop\\Prog Lab Assignment\\Assignment 3\\code"
    python main.py
    all

A is Section A (questions 1-3). It is not the same as all.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
os.chdir(CODE_DIR)
sys.path.insert(0, str(CODE_DIR))

import matplotlib

matplotlib.use("Agg")  # save PNGs; no pop-up windows needed in VS Code

from config import MAX_ROWS, QUESTIONS, SECTIONS
from data import build_analysis
from questions import RUNNERS, run_map


HELP = """
------------------------------------------------------------
  What can I type?  (this is the menu)
------------------------------------------------------------
  4          Run ONLY question 4. Use this to practise one answer.
             Any number from 1 to 21 works the same way.

  A          Run Section A of the assignment PDF — questions 1, 2 and 3.
             A is a SECTION LETTER. It does NOT mean "all".

  B          Section B — questions 4 and 5  (the formulas)
  C          Section C — questions 6, 7, 8
  D          Section D — questions 9, 10
  E          Section E — questions 11, 12
  F          Section F — questions 13, 14
  G          Section G — questions 15, 16
  H          Section H — questions 17, 18, 19   (t-SNE, slower)
  I          Section I — questions 20, 21

  all        Run questions 1 through 21, then rebuild the viva map.
             Do this once when you first set the project up.

  map        Rebuild only the overview posters in output\\00_viva_map

  help       Show this list again
  q          Quit

------------------------------------------------------------
  VS Code, first time
------------------------------------------------------------
  1. Terminal → New Terminal
  2. cd "C:\\Users\\ASUS\\Desktop\\Prog Lab Assignment\\Assignment 3\\code"
  3. python main.py
  4. type:  all

  You can also skip the menu:
      python main.py all
      python main.py 4
      python main.py A
      python main.py map
------------------------------------------------------------
"""


def parse_choice(raw: str):
    s = raw.strip()
    if not s:
        return None
    low = s.lower()
    if low in {"q", "quit", "exit"}:
        return "quit"
    if low in {"help", "h", "?"}:
        return "help"
    if low == "all":
        return list(range(1, 22))
    if low == "map":
        return "map"
    if len(s) == 1 and s.upper() in SECTIONS:
        letter = s.upper()
        qids = list(SECTIONS[letter][2])
        name = SECTIONS[letter][1]
        print(f"  Section {letter} = {name} = questions {', '.join(str(q) for q in qids)}")
        print("  (Reminder: A is a section, not 'all'.)")
        return qids
    if s.isdigit():
        qid = int(s)
        if 1 <= qid <= 21:
            return [qid]
        print("  Question numbers are 1 to 21.")
        return None
    print("  I did not understand that.")
    print("  Type a number 1-21, a section letter A-I, all, map, help, or q.")
    return None


def run_ids(analysis, qids: list[int]) -> None:
    for qid in qids:
        title = QUESTIONS[qid]["title"]
        print(f"\n--- Q{qid:02d}  {title} ---")
        RUNNERS[qid](analysis)


def interactive_loop(analysis) -> None:
    print(HELP)
    gb = analysis.file_bytes / (1024 ** 3)
    print(
        f"  Loaded {analysis.n:,} reviews from a {gb:.2f} GB file "
        f"(full set is ~1.38 million). MAX_ROWS={analysis.max_rows:,}."
    )
    print(
        f"  Sample: {analysis.n_books:,} books, {analysis.n_users:,} users. "
        "Everything after MAX_ROWS was not read."
    )
    print("  First time here? type  all")
    while True:
        try:
            raw = input("\nType a question, a section letter, all, map, help, or q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nStopped.")
            return
        choice = parse_choice(raw)
        if choice is None:
            continue
        if choice == "quit":
            print("Stopped.")
            return
        if choice == "help":
            print(HELP)
            continue
        if choice == "map":
            run_map(analysis)
            print("  Open:  ..\\output\\00_viva_map\\viva_map.png")
            continue
        run_ids(analysis, choice)
        if len(choice) > 1:
            run_map(analysis)
        print("  Files are under  ..\\output\\")


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    max_rows = MAX_ROWS
    if "--max-rows" in argv:
        i = argv.index("--max-rows")
        try:
            max_rows = int(argv[i + 1])
        except (IndexError, ValueError):
            print("Usage: python main.py --max-rows 20000")
            sys.exit(2)
        del argv[i : i + 2]
    if any(a in {"-h", "--help", "help"} for a in argv) and len(argv) == 1:
        print(HELP)
        return

    analysis = build_analysis(max_rows)
    if not argv:
        interactive_loop(analysis)
        return

    choice = parse_choice(" ".join(argv))
    if choice is None or choice == "quit":
        sys.exit(1)
    if choice == "help":
        print(HELP)
        return
    if choice == "map":
        run_map(analysis)
        return
    run_ids(analysis, choice)
    if choice == list(range(1, 22)):
        run_map(analysis)


if __name__ == "__main__":
    main()
