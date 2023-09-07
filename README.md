Extensible template for basic audio creation and playback using python with `pygame`.

Requires `pygame` and any version of python that supports type hints.

In `audio.py`, the class `Audio` provides an easy way to create audio with different waveforms and modulation functions, and is extensible with any custom functions. Basic waveforms and modulation functions come with the class. The class also allows for playback using `pygame`.


### Minimal code to play a single 200 Hz sine wave at constant volume for 10 seconds:

```
from audio import Audio

rel_amp = 0.4  # relative limit on amplitude
sample_rate = 44100  # number of samples per second
seconds = 10  # playback length
f = 200  # frequency of sine wave
r_f = 1  # relative amplitude of sine wave

audio = Audio(sample_rate=sample_rate, relative_amp=rel_amp)
audio.construct_time(seconds=seconds)
audio.create_wave(wave_func=Audio.sin, frequency=f, amplitude=r_f)

audio.play_sound(vol_func=Audio.constant_volume)
```


### Code to play a 300 Hz sine wave in addition to the 200 Hz wave at half its volume

```
from audio import Audio

rel_amp = 0.4  # relative limit on amplitude
sample_rate = 44100  # number of samples per second
seconds = 10  # playback length
fs = [200, 300]  # frequencies of sine wave
r_fs = [1, 0.5]  # relative amplitudes of sine waves

audio = Audio(sample_rate=sample_rate, relative_amp=rel_amp)
audio.construct_time(seconds=seconds)
for f, r_f in zip(fs, r_fs):
    audio.create_wave(wave_func=Audio.sin, frequency=f, amplitude=r_f)

audio.play_sound(vol_func=Audio.constant_volume)
```

### Code to modulate the above waves with a linearly increasing then decreasing volume

```
from audio import Audio

rel_amp = 0.4  # relative limit on amplitude
sample_rate = 44100  # number of samples per second
seconds = 10  # playback length
fs = [200, 300]  # frequencies of sine wave
r_fs = [1, 0.5]  # relative amplitudes of sine waves

audio = Audio(sample_rate=sample_rate, relative_amp=rel_amp)
audio.construct_time(seconds=seconds)
for f, r_f in zip(fs, r_fs):
    audio.create_wave(wave_func=Audio.sin, frequency=f, amplitude=r_f)

audio.play_sound(vol_func=Audio.linear_volume)
```

### Extensible functions

The functions `wave_func` and `vol_func` are extensible as long as they follow the template defined in their corresponding type hints.

`wave_func`: Vectorized mapping from time to amplitude. Converts an array of time values `t` into a corresponding amplitude array. E.g. `lambda t, f, A: A * np.sin(2 * np.pi * f * t)` representing a sine wave.

`vol_func`: Vectorized mapping from time to volume modulation (from 0 to 1). 1 corresponds to no change in volume, 0 corresponds to 0 volume. Converts an array of time values `t` into a corresponding modulation array that will be element-wise multiplied with the overall array containing the amplitudes.


### Contact
[contact@nicholascjl.dev](mailto:contact@nicholascjl.dev)