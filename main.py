import pyaudio
import numpy as np
import pygame

CHUNK = 131072  # Number of audio frames per buffer
RATE = 96000  # Sample rate (Hz)
IN_TUNE_THRESHOLD = 1  # How close (in Hz) to the tuning does it need to be in tune?
STRING_IDENTIFY_THRESHOLD = 10  # How close to the tuning for it to recognize the string?

FORMAT = pyaudio.paInt16  # 16-bit integers
CHANNELS = 1  # Mono audio
STANDARD_TUNING = {82: "Low E", 110: "A", 147: "D", 196: "G", 247: "B", 330: "High E"}
X = np.fft.rfftfreq(CHUNK, 1.0/RATE)
N_MAX_VALUES = 4


def find_closest_string(freq, tuning=STANDARD_TUNING):
    errors = dict.fromkeys(tuning.keys())
    for k in tuning.keys():
        errors[k] = freq - k
    errors_abs = {k: abs(v) for k, v in errors.items()}
    most_likely = min(errors_abs, key=errors_abs.get)
    return most_likely, errors[most_likely]


def get_fundamental(stream):
    data = stream.read(CHUNK)
    # Convert byte data to numpy array
    audio_data = np.frombuffer(data, dtype=np.int16)

    fft_data = np.abs(np.fft.rfft(audio_data))

    # Alejandro's solution
    # max_index = np.argmax(fft_data)
    max_indices = np.argpartition(fft_data, -N_MAX_VALUES)[-N_MAX_VALUES:]
    pairs = {}
    for max_index in max_indices:
        # print("Frequency: "+str(x[max_index])+", Magnitude: "+str(fft_data[max_index]))

        for i in range(2, 5 + 1):
            # print("("+str(i)+"): Frequency: "+str(x[int(max_index/i)])+", Magnitude: "+str(fft_data[int(max_index/i)]))
            # pairs.append([x[int(max_index/i)], fft_data[int(max_index/i)]])
            pairs[X[int(max_index / i)]] = fft_data[int(max_index / i)]
    filtered_pairs = {k: v for k, v in pairs.items() if k > 60}
    if len(filtered_pairs) > 0:
        guessed_fundamental = max(filtered_pairs, key=filtered_pairs.get)
        # print(filtered_pairs)
        return (guessed_fundamental, filtered_pairs[guessed_fundamental])
    else:
        return (-1, 0)


# set up pyaudio
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


# pygame initialization
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 240
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
running = True

font = pygame.font.SysFont(None, 48)


try:
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("white")
        freq_text = ""
        text = ""
        out_of_tune = 0

        guessed_fundamental, mag_fundamental = get_fundamental(stream)
        if guessed_fundamental > 0:

            if mag_fundamental > 6000000:
                print("Guessed Fundamental: " + str(guessed_fundamental) + ", Magnitude: " + str(mag_fundamental))
                c, e = find_closest_string(guessed_fundamental)
                if abs(e) < STRING_IDENTIFY_THRESHOLD:
                    text = STANDARD_TUNING[c]
                    freq_text = f"{guessed_fundamental:.2f}"
                    out_of_tune = e
                else:
                    text = ""
                    freq_text = ""
                # if abs(e) < IN_TUNE_THRESHOLD:
                #     print("Closest String: " + STANDARD_TUNING[c] + ", you're more or less in tune!")
                # elif abs(e) < STRING_IDENTIFY_THRESHOLD:
                #     if e > 0:
                #         print("Closest String: " + STANDARD_TUNING[c] + ", you're a little high!")
                #     if e < 0:
                #         print("Closest String: " + STANDARD_TUNING[c] + ", you're a little low!")

        # render text
        text_box = font.render(text, True, "Black")
        text_rect = text_box.get_rect()
        text_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        screen.blit(text_box, text_rect)

        freq_text_box = font.render(freq_text, True, "Black")
        freq_text_rect = freq_text_box.get_rect()
        freq_text_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30)
        screen.blit(freq_text_box, freq_text_rect)

        # render bars
        pygame.draw.rect(screen, "Red", (SCREEN_WIDTH/2-(STRING_IDENTIFY_THRESHOLD*20), SCREEN_HEIGHT/2-50, (STRING_IDENTIFY_THRESHOLD*40), 10))
        pygame.draw.rect(screen, "Green", (SCREEN_WIDTH / 2 - (IN_TUNE_THRESHOLD*20), SCREEN_HEIGHT / 2 - 50, (IN_TUNE_THRESHOLD*40), 10))
        if text != "":
            pygame.draw.rect(screen, "Black", (SCREEN_WIDTH/2 + out_of_tune*20 - 1, SCREEN_HEIGHT/2 - 55, 2, 20))
        pygame.display.flip()


except KeyboardInterrupt:
    pass

pygame.quit()
stream.stop_stream()
stream.close()
p.terminate()
