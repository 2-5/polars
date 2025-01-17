import time
from typing import Any

import numpy as np

import polars as pl
from polars.testing import assert_series_equal


def test_cross_join_stack() -> None:
    a = pl.Series(np.arange(100_000)).to_frame().lazy()
    t0 = time.time()
    # this should be instant if directly pushed into sink
    # if not the cross join will first fill the stack with all matches of a single chunk
    assert a.join(a, how="cross").head().collect(streaming=True).shape == (5, 2)
    t1 = time.time()
    assert (t1 - t0) < 0.5


def test_ooc_sort(monkeypatch: Any) -> None:
    monkeypatch.setenv("POLARS_FORCE_OOC_SORT", "1")

    s = pl.arange(0, 100_000, eager=True).rename("idx")

    df = s.shuffle().to_frame()

    for reverse in [True, False]:
        out = (
            df.lazy().sort("idx", reverse=reverse).collect(streaming=True)
        ).to_series()

        assert_series_equal(out, s.sort(reverse=reverse))
