from typing import Callable, Optional

import numpy as np
import pygame


class PygAudio:
    max_amp = 32767

    """
    Volume modulation methods.
    """
    @staticmethod
    def constant_volume(t: np.ndarray) -> np.ndarray:
        """
        No-op, returns array of ones same shape as t.
        :param t: Array of timesteps.
        """
        return np.ones_like(t)

    @staticmethod
    def sym_ramp_volume(t: np.ndarray) -> np.ndarray:
        """
        Symmetrically ramps up from 0 to 1, then down from 1 to 0.
        :param t: Array of timesteps.
        """
        return 1 - np.abs(2 * t / t[-1] - 1)

    """
    Common waveform methods.
    """
    @staticmethod
    def sin(t: np.ndarray,
            freq: float,
            amp: float,
            phi: Optional[float] = None) -> np.ndarray:
        """
        Standard sine waveform.
        :param t: Array of timesteps.
        :param freq: Frequency of wave.
        :param phi: Phase of wave in radians. Defaults to 0.
        """
        if phi is None:
            phi = 0
        return amp * np.sin(2 * np.pi * freq * t + phi)

    """
    Begin instance methods.
    """
    def __init__(self, sample_rate: int,
                 relative_amp: float) -> None:
        self.sample_rate = sample_rate
        self.relative_amp = relative_amp
        self.t = None
        self.collected_amp = None
        pygame.mixer.init(frequency=sample_rate, buffer=4096)

    def construct_time(self, seconds: float) -> float:
        self.t = np.linspace(0, seconds, self.sample_rate * seconds,
                             dtype=np.float64)
        self.collected_amp = np.zeros_like(self.t)
        self.timestep = self.t[1] - self.t[0]
        return self.timestep

    def create_wave(self, wave_func: Callable[[np.ndarray,
                                               float,
                                               float,
                                               Optional[float]],
                                              np.ndarray],
                    frequency: float,
                    amplitude: float,
                    vol_func: Callable[[np.ndarray], np.ndarray],
                    start_offset: Optional[float] = None,
                    stop_offset: Optional[float] = None,
                    phase: Optional[float] = 0) -> None:
        if self.collected_amp is None:
            raise UnboundLocalError("Construct time first with"
                                    "`construct_time` before creating"
                                    "waves.")

        # offset checks
        if start_offset is None or stop_offset is None:
            # Both offsets have to be specified or wave will last for entire
            # audio
            start_offset = 0
            stop_offset = (len(self.t) - 1)
        elif stop_offset <= start_offset:
            raise ValueError("Stop offset has to be greater than start"
                             " offset.")
        else:  # check values
            if start_offset < 0:
                print(f"{start_offset=} set to invalid value, setting to 0.")
                start_offset = 0
            if stop_offset > (len(self.t) - 1):
                print(f"{stop_offset=} set to invalid value, setting to final"
                      " timestep.")
                stop_offset = (len(self.t) - 1)

        # segment of time array the wave lasts for
        wave_time = self.collected_amp[start_offset:stop_offset+1]
        wave_time += (vol_func(wave_time)
                      * wave_func(wave_time, frequency, amplitude, phase))

    def play_sound(self) -> None:
        amp = (self.collected_amp
               * self.relative_amp
               * self.max_amp
               / np.max(self.collected_amp)).astype(np.int16)

        # reshape to 2 channels because mono is broken
        amp = np.repeat(amp.reshape(amp.size, 1), 2, axis=1)
        sound = pygame.sndarray.make_sound(amp)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.delay(100)
