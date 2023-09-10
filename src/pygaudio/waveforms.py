from typing import Optional
import numpy as np

"""
Common waveform methods.
"""


def sin(t: np.ndarray,
        freq: float,
        amp: float,
        phi: Optional[float] = None) -> np.ndarray:
    """
    Standard sine waveform.
    :param t: Array of timesteps.
    :param freq: Frequency of wave.
    :param phi: (Optional) Phase of wave in radians. Defaults to 0.
    """
    if phi is None:
        phi = 0
    return amp * np.sin(2 * np.pi * freq * t + phi)


def saw(t: np.ndarray,
        freq: float,
        amp: float,
        phi: Optional[float] = None) -> np.ndarray:
    """
    Standard sawtooth waveform.
    :param t: Array of timesteps.
    :param freq: Frequency of wave.
    :param phi: (Optional) Phase of wave in radians. Defaults to 0.
    """
    if phi is None:
        phi = 0

    # trigonometric form is ~2x as fast as remainder form
    return ((2 * amp / np.pi)
            * np.arctan(np.tan(np.pi * freq * t + phi / 2)))


def square(t: np.ndarray,
           freq: float,
           amp: float,
           phi: Optional[float] = None) -> np.ndarray:
    """
    Standard square waveform.
    :param t: Array of timesteps.
    :param freq: Frequency of wave.
    :param phi: (Optional) Phase of wave in radians. Defaults to 0.
    """
    if phi is None:
        phi = 0
    return amp * np.sign(np.sin(2 * np.pi * freq * t + phi))


def triangle(t: np.ndarray,
             freq: float,
             amp: float,
             phi: Optional[float] = None) -> np.ndarray:
    """
    Standard triangle waveform.
    :param t: Array of timesteps.
    :param freq: Frequency of wave.
    :param phi: (Optional) Phase of wave in radians. Defaults to 0.
    """
    if phi is None:
        phi = 0

    # trigonometric form is ~2x as fast as remainder form
    return ((2 * amp / np.pi)
            * np.arcsin(np.sin(2 * np.pi * freq * t + phi)))
