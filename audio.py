from typing import Callable

import numpy as np
import pygame


class Audio:
    max_amp = 32767

    @staticmethod
    def linear_volume(t: np.ndarray) -> np.ndarray:
        return 1 - np.abs(2 * t / t[-1] - 1)

    @staticmethod
    def sin(t: np.ndarray, freq: float, amp: float) -> np.ndarray:
        return amp * np.sin(2 * np.pi * freq * t)

    def __init__(self, sample_rate: int,
                 relative_amp: float) -> None:
        self.sample_rate = sample_rate
        self.relative_amp = relative_amp
        self.t = None
        self.collected_amp = None
        pygame.mixer.init(frequency=sample_rate, buffer=4096)

    def construct_time(self, seconds: float) -> None:
        self.t = np.linspace(0, seconds, self.sample_rate * seconds,
                             dtype=np.float64)
        self.collected_amp = np.zeros_like(self.t)

    def create_amp(self, amp_func: Callable[[np.ndarray, float, float],
                                            np.ndarray],
                   frequency: float,
                   amplitude: float) -> None:
        if self.collected_amp is None:
            raise NotImplementedError("Construct time first with"
                                      "`construct_time` before creating amp.")

        self.collected_amp += amp_func(self.t, frequency, amplitude)

    def play_sound(self, vol_func: Callable[[np.ndarray], np.ndarray]) -> None:
        amp = (self.collected_amp * vol_func(self.t)
               * self.relative_amp
               * self.max_amp
               / np.max(self.collected_amp)).astype(np.int16)

        # reshape to 2 channels because mono is broken
        amp = np.repeat(amp.reshape(amp.size, 1), 2, axis=1)
        sound = pygame.sndarray.make_sound(amp)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.delay(100)
