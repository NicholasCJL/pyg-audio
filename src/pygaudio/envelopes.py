from typing import Optional

import numpy as np

"""
Volume modulation functions, defines the envelope of the wave.
"""


def constant_envelope(t: np.ndarray,
                      scale: Optional[float] = None) -> np.ndarray:
    """
    No-op, returns array of ones same shape as t.
    :param t: Array of timesteps.
    :param scale: Not used.
    """
    return np.ones_like(t)


def sym_ramp_envelope(t: np.ndarray,
                      scale: Optional[float] = None) -> np.ndarray:
    """
    Symmetrically ramps up from 0 to 1, then down from 1 to 0.
    :param t: Array of timesteps.
    :param scale: Not used.
    """
    return 1 - np.abs(2 * t / t[-1] - 1)


def linear_exp_envelope(t: np.ndarray,
                        scale: Optional[float] = None) -> np.ndarray:
    """
    Quick ramp up from 0 then decay. f(t, scale) = t*exp(1-t/scale)/scale.
    Max amplitude of 1.
    :param t: Array of timesteps.
    :param scale: "Sharpness" of "hump". Larger scale corresponds to faster
        ramp up and decay. Defaults to 1.
    """
    if scale is None:
        scale = 1
    return (t / scale) * np.exp(1 - t / scale)
