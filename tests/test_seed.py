"""Seed reproducibility tests."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
from utils.seed import set_seed, DEFAULT_SEED


def test_seed_sets_numpy_deterministically():
    set_seed(123)
    arr1 = np.random.rand(10).copy()
    set_seed(123)
    arr2 = np.random.rand(10).copy()
    np.testing.assert_array_equal(arr1, arr2)


def test_different_seeds_produce_different_results():
    set_seed(1)
    arr1 = np.random.rand(10).copy()
    set_seed(2)
    arr2 = np.random.rand(10).copy()
    assert not np.array_equal(arr1, arr2)


def test_default_seed_is_42():
    assert DEFAULT_SEED == 42
