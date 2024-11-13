from typing import Any

import numpy as np
import pytest

from python_rye_template.hoge import dots

# テストケースの辞書
test_cases = {
    "scalar_multiplication": {
        "a": np.array([2]),
        "b": np.array([3]),
        "expected": np.array(6),
    },
    "vector_dot_product": {
        "a": np.array([1, 2, 3]),
        "b": np.array([4, 5, 6]),
        "expected": np.int64(32),
    },
    "matrix_multiplication": {
        "a": np.array([[1, 2], [3, 4]]),
        "b": np.array([[5, 6], [7, 8]]),
        "expected": np.array([[19, 22], [43, 50]]),
    },
}


# テスト関数
@pytest.mark.parametrize("case", list(test_cases.values()), ids=list(test_cases.keys()))
def test_dots(case: dict[str, Any]) -> None:
    """a.

    Args:
        case (dict_items[str, dict[str, Any]]): _description_
    """
    a = case["a"]
    b = case["b"]
    expected = case["expected"]

    result = dots(a, b)
    np.testing.assert_array_equal(result, expected)
