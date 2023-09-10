import numpy as np

"""
Volume modulation functions, defines the envelope of the wave.
"""


def constant_envelope(t: np.ndarray) -> np.ndarray:
    """
    No-op, returns array of ones same shape as t.
    :param t: Array of timesteps.
    """
    return np.ones_like(t)


def sym_ramp_envelope(t: np.ndarray) -> np.ndarray:
    """
    Symmetrically ramps up from 0 to 1, then down from 1 to 0.
    :param t: Array of timesteps.
    """
    return 1 - np.abs(2 * t / t[-1] - 1)
