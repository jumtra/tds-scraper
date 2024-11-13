import numpy as np


def dots(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """aとbの積.

    Args:
        a (np.ndarray): _description_
        b (np.ndarray): _description_

    Returns
    -------
        np.ndarray: _description_
    """
    return np.dot(a, b)


if __name__ == "__main__":
    a = np.arange(10)
    b = np.arange(10)
    c = dots(a, b)
