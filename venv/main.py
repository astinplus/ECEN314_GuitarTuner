import pyaudio
import numpy as np
import matplotlib.pyplot as plt

CHUNK = 4096  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit integers
CHANNELS = 1  # Mono audio
RATE = 96000#44100  # Sample rate (Hz)
RECORD_SECONDS = 5  # Duration of recording
STANDARD_TUNING = {82: "Low E", 110: "A", 147: "D", 196: "G", 247: "B", 330: "High E"}

def mag_response_X(f, data):
    result = 0
    for i in range(CHUNK):
        result += data[i] * np.exp(-2j * np.pi * i * f)
    return 20*np.log10(np.abs(result))

def find_closest_string(data, tuning=STANDARD_TUNING):
    errors = dict.fromkeys(tuning.keys())
    for k in tuning.keys():
        errors[k] = sum([abs(float(d)/k - round(d/k)) for d in data])
    # print(errors)
    most_likely = min(errors, key=errors.get)
    return most_likely, errors[most_likely]/len(data)
# set up pyaudio
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

SIZE = int(CHUNK/2+1)
fig, ax = plt.subplots()
# x = np.arange(0, SIZE, 1)  # X-axis for waveform
x = np.fft.rfftfreq(CHUNK, 1.0/RATE)
line, = ax.plot(x, np.random.rand(SIZE), '-')  # Initial empty plot
# ax.set_ylim(-2 ** 15, 2 ** 15)  # Adjust based on your audio format (e.g., int16)
ax.set_ylim(0, 500000)
# ax.set_xlim(0, max(x))
ax.set_xlim(0,800)
plt.show(block=False)  # Non-blocking show

# fig, ax = plt.subplots()
# frequency_values = np.arange(0, 400, 1)
# line, = ax.plot(frequency_values, np.random.rand(len(frequency_values)), '-')  # Initial empty plot
# ax.set_ylim(0, 100)  # Adjust based on your audio format (e.g., int16)
# ax.set_xlim(min(frequency_values), max(frequency_values))
# plt.show(block=False)  # Non-blocking show


# def get_max_freqs(n, data, freqs):
#     max_indices = np.argpartition(data, -n)[-n:]
#     return freqs[max_indices], data[max_indices]


try:
    while True:
        data = stream.read(CHUNK)
        # Convert byte data to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)

        fft_data = np.abs(np.fft.rfft(audio_data))
        # print(fft_data)
        # frequency_data = [None] * len(frequency_values)
        # for i in range(len(frequency_values)):
        #     frequency_data[i] = mag_response_X(frequency_values[i], audio_data)
        #
        # print(frequency_data)
        # print(len(x))
        # print(len(fft_data))
        # print(x[np.argmax(fft_data)])
        max_indices = np.argpartition(fft_data, -5)[-5:]
        # mf, md = get_max_freqs(3, fft_data, x)
        # print(x[max_indices], "max = "+str(x[np.argmax(fft_data)]))
        c, e = find_closest_string(x[max_indices])
        if e < 0.1 and 0 not in x[max_indices]:
            print("This is the "+STANDARD_TUNING[c]+" string with confidence "+str(e))
            # print(c,e)
        # Update the plot
        line.set_ydata(fft_data)
        # line.set_ydata(frequency_data)
        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()

