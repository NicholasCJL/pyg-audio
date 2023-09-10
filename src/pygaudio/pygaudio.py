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
        :param phi: (Optional) Phase of wave in radians. Defaults to 0.
        """
        if phi is None:
            phi = 0
        return amp * np.sin(2 * np.pi * freq * t + phi)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
        return (2 * amp / np.pi) * np.arcsin(np.sin(2 * np.pi * freq * t + phi))

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
        """
        Create time array based on total number of seconds.
        :param seconds: Total number of seconds to play audio for.
        :return: Length of each timestep (between samples).
        """
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
                    vol_func: Callable[[np.ndarray], np.ndarray],
                    frequency: float,
                    amplitude: float,
                    phase: Optional[float] = None,
                    start_offset: Optional[float] = None,
                    stop_offset: Optional[float] = None) -> None:
        """
        Create audio based on a defined wavefunction and volume function.
        :param wave_func: Function that takes in time array and returns array
            of amplitudes.
        :param vol_func: Function that takes in time array and returns array
            of modulation coefficients.
        :param frequency: Frequency of wave.
        :param amplitude: Amplitude of wave.
        :param phase: (Optional) Phase of wave. 0 if None.
        :param start_offset: (Optional) Starting index of time array to play
            wave at. Starts at 0 if None.
        :param stop_offset: (Optional) Stopping index of time array to play
            wave at. Stops at last index if None.
        """
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

        if phase is None:
            phase = 0

        # segment of time array the wave lasts for
        wave_time = self.t[start_offset:stop_offset+1]
        # segment of collected amplitude the wave lasts for
        amp_segment = self.collected_amp[start_offset:stop_offset+1]
        # modulation starts relative to t=offset
        modulation = vol_func(wave_time - wave_time[0])
        # wave starts relative to t=0
        wave = wave_func(wave_time, frequency, amplitude, phase)
        amp_segment += modulation * wave

    def insert_audio(self, audio: np.ndarray,
                     start_offset: Optional[float] = None,
                     stop_offset: Optional[float] = None,
                     vol_func: Optional[Callable[[np.ndarray],
                                                 np.ndarray]] = None) -> None:
        """
        Add raw audio in the form of a numpy array. If length of audio
            provided does not match the offsets or exceeds the time array,
            audio is repeated/truncated to match.
        :param audio: Numpy array with raw amplitudes of wave.
        :param start_offset: (Optional) Starting index of time array to play
            wave at. Starts at 0 if None.
        :param stop_offset: (Optional) Stopping index of time array to play
            wave at. Stops at start_offset + len(audio) - 1 if None.
        :param vol_func: (Optional) Function that takes in time array and
            returns array of modulation coefficients. No modulation if None.
        """
        # offset checks
        if start_offset is None:
            start_offset = 0
        if stop_offset is None:
            stop_offset = start_offset + len(audio) - 1

        # force within bounds
        if start_offset < 0:
            print(f"{start_offset=} set to invalid value, setting to 0.")
            start_offset = 0
        if stop_offset > (len(self.t) - 1):
            print(f"{stop_offset=} set to invalid value, setting to final"
                  " timestep.")
            stop_offset = (len(self.t) - 1)

        if stop_offset <= start_offset:
            raise ValueError("Stop offset has to be greater than start"
                             " offset.")

        # force length
        audio = np.resize(audio, stop_offset - start_offset + 1)

        if vol_func is None:
            vol_func = self.constant_volume

        # segment of time array the wave lasts for
        wave_time = self.t[start_offset:stop_offset+1]
        # segment of collected amplitude the wave lasts for
        amp_segment = self.collected_amp[start_offset:stop_offset+1]
        # modulation starts relative to t=offset
        modulation = vol_func(wave_time - wave_time[0])
        amp_segment += modulation * audio

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
