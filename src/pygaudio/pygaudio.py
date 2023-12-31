from typing import Callable, Optional

import numpy as np
import pygame


class PygAudio:
    max_amp = 32767

    def __init__(self, num_channels: Optional[int] = None,
                 sample_rate: Optional[int] = None,
                 relative_amp: Optional[float] = None) -> None:
        """
        :param num_channels: Mono (1) or stereo (2). Defaults to mono.
        :param sample_rate: Sample rate of audio engine. Defaults to 44100.
        :param relative_amp: Relative amplitude of final audio (0 to 1).
            Defaults to 0.5.
        """
        if num_channels is None:
            num_channels = 1
        elif num_channels not in (1, 2):
            raise ValueError(f"{num_channels=} needs to be 1 or 2.")
        if sample_rate is None:
            sample_rate = 44100
        if relative_amp is None:
            relative_amp = 0.5

        self.num_channels = num_channels
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
        self.t = np.linspace(0, seconds, int(self.sample_rate * seconds),
                             dtype=np.float64)

        self.collected_amp = np.zeros((len(self.t), self.num_channels),
                                      dtype=np.float64)
        self.timestep = self.t[1] - self.t[0]
        return self.timestep

    def create_wave(self, wave_func: Callable[[np.ndarray,
                                               float,
                                               float,
                                               Optional[float]],
                                              np.ndarray],
                    vol_func: Callable[[np.ndarray, Optional[float]],
                                       np.ndarray],
                    frequency: float,
                    amplitude: float,
                    phase: Optional[float] = None,
                    scale: Optional[float] = None,
                    start_offset: Optional[float] = None,
                    stop_offset: Optional[float] = None,
                    channel: Optional[str] = None) -> None:
        """
        Create audio based on a defined wavefunction and volume function.
        :param wave_func: Function that takes in time array and returns array
            of amplitudes.
        :param vol_func: Function that takes in time array and returns array
            of modulation coefficients.
        :param frequency: Frequency of wave.
        :param amplitude: Amplitude of wave.
        :param phase: (Optional) Phase of wave. 0 if None.
        :param scale: (Optional) Scale for vol_func. 1 if None.
        :param start_offset: (Optional) Starting index of time array to play
            wave at. Starts at 0 if None.
        :param stop_offset: (Optional) Stopping index of time array to play
            wave at. Stops at last index if None.
        :param channel: Audio channel to create audio in.
            ("left", "right", "both"). Defaults to "both".
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
        if scale is None:
            scale = 1

        # attempt to convert channel value to something logical
        if channel is None:
            channel = "both" if self.num_channels == 2 else "left"
        if channel not in ("left", "right", "both"):
            raise ValueError(f"{channel=} has to be 'left' or 'right' or"
                             " 'both'")
        if channel != "left" and self.num_channels == 1:
            channel = "left"

        # segment of time array the wave lasts for
        wave_time = self.t[start_offset:stop_offset+1]
        # modulation starts relative to t=offset
        modulation = vol_func(wave_time - wave_time[0], scale)
        # wave starts relative to t=0
        wave = wave_func(wave_time, frequency, amplitude, phase)
        # modulated wave
        mod_audio = modulation * wave

        # add audio to relevant channels
        if channel == "left" or channel == "both":
            amp_segment = self.collected_amp[start_offset:stop_offset+1, 0]
            amp_segment += mod_audio
        if channel == "right" or channel == "both":
            amp_segment = self.collected_amp[start_offset:stop_offset+1, 1]
            amp_segment += mod_audio

    def insert_audio(self, audio: np.ndarray,
                     scale: Optional[float] = None,
                     start_offset: Optional[float] = None,
                     stop_offset: Optional[float] = None,
                     channel: Optional[str] = None,
                     vol_func: Optional[Callable[[np.ndarray, Optional[float]],
                                                 np.ndarray]] = None) -> None:
        """
        Add raw audio in the form of a numpy array. If length of audio
            provided does not match the offsets or exceeds the time array,
            audio is repeated/truncated to match.
        :param audio: Numpy array with raw amplitudes of wave.
        :param scale: (Optional) Scale for vol_func. 1 if None.
        :param start_offset: (Optional) Starting index of time array to play
            wave at. Starts at 0 if None.
        :param stop_offset: (Optional) Stopping index of time array to play
            wave at. Stops at start_offset + len(audio) - 1 if None.
        :param channel: Audio channel to insert audio in.
            ("left", "right", "both"). Defaults to "both".
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

        if scale is None:
            scale = 1

        # attempt to convert channel value to something logical
        if channel is None:
            channel = "both" if self.num_channels == 2 else "left"
        if channel not in ("left", "right", "both"):
            raise ValueError(f"{channel=} has to be 'left' or 'right' or"
                             " 'both'")
        if channel != "left" and self.num_channels == 1:
            channel = "left"

        # force length
        audio = np.resize(audio, stop_offset - start_offset + 1)

        if vol_func is None:
            vol_func = self.constant_volume

        # segment of time array the wave lasts for
        wave_time = self.t[start_offset:stop_offset+1]
        # modulation starts relative to t=offset
        modulation = vol_func(wave_time - wave_time[0], scale)
        # modulated audio
        mod_audio = modulation * audio

        # add audio to relevant channels
        if channel == "left" or channel == "both":
            amp_segment = self.collected_amp[start_offset:stop_offset+1, 0]
            amp_segment += mod_audio
        if channel == "right" or channel == "both":
            amp_segment = self.collected_amp[start_offset:stop_offset+1, 1]
            amp_segment += mod_audio

    def play_sound(self) -> None:
        amp = (self.collected_amp
               * self.relative_amp
               * self.max_amp
               / np.max(self.collected_amp)).astype(np.int16)

        if self.num_channels == 1:
            # reshape to 2 channels because mono is broken
            amp = np.repeat(amp, 2, axis=1)

        sound = pygame.sndarray.make_sound(amp)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.delay(100)

    def time_to_offset(self, time: float) -> int:
        """
        Converts a timestamp to offset for methods that require offset.
        :param time: Time to convert to offset.
        """
        return int(time * self.sample_rate)
