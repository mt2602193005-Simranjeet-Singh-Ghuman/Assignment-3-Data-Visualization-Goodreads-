"""Question function registry."""

from q_charts import (
    run_q06,
    run_q07,
    run_q08,
    run_q09,
    run_q10,
    run_q11,
    run_q13,
    run_q14,
    run_q15,
    run_q16,
    run_q18,
    run_q20,
)
from q_concept import (
    run_map,
    run_q01,
    run_q02,
    run_q03,
    run_q04,
    run_q05,
    run_q12,
    run_q17,
    run_q19,
    run_q21,
)

RUNNERS = {
    1: run_q01,
    2: run_q02,
    3: run_q03,
    4: run_q04,
    5: run_q05,
    6: run_q06,
    7: run_q07,
    8: run_q08,
    9: run_q09,
    10: run_q10,
    11: run_q11,
    12: run_q12,
    13: run_q13,
    14: run_q14,
    15: run_q15,
    16: run_q16,
    17: run_q17,
    18: run_q18,
    19: run_q19,
    20: run_q20,
    21: run_q21,
}

NEEDS_TSNE = {17, 18, 19}
