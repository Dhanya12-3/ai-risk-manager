import numpy as np
import pandas as pd
from src.ml.pipeline import metrics_at_threshold, split_data

def test_split_is_chronological():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=100),
        "label": np.zeros(100)
    })
    a, b, c = split_data(df)
    assert len(a) == 70
    assert len(b) == 15
    assert len(c) == 15
    assert a.timestamp.max() < b.timestamp.min() < c.timestamp.min()

def test_cost_calculation():
    y = np.array([0,0,0,1,1])
    p = np.array([.1,.2,.8,.9,.95])
    m = metrics_at_threshold(y, p, .5, fp_cost=100, fn_cost=2500)
    assert m["false_positives"] == 1
    assert m["false_negatives"] == 0
    assert m["total_cost"] == 100

def test_metric_output_is_real_numbers():
    y = np.array([0,1,0,1])
    p = np.array([.1,.8,.3,.9])
    m = metrics_at_threshold(y, p, .5)
    assert 0 <= m["precision"] <= 1
    assert 0 <= m["recall"] <= 1
    assert 0 <= m["f1"] <= 1
