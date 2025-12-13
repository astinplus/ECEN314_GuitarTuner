HOWDY!

This is my final project for my signals and systems class at Texas A&M University, ECEN-314!

It is a simple guitar tuner application written in python. Every loop of the program, it runs through these steps to determine how in-tune the guitar is:
1. It reads input from an audio stream using the [pyaudio](https://pypi.org/project/PyAudio/) library.
2. Using that audio data, it takes an FFT (from the [numpy](https://numpy.org/)) library to get the frequency content.
3. Use [numpy](https://numpy.org/) functions to locate the maximum peaks of the frequency content (these are the harmonics of the signal). These are multiples of the fundamental frequency we are trying to find.
4. Divide each max by a sequence of constants (e.g. 2,3,4,5) and find the frequency there with the highest magnitude. It will only look at frequencies higher than 60Hz, to account for noise.
5. Then it is a simple process of finding which string is closest and how far off it is.

It is very easy to adjust certain settings within the tuner, such as the range for string detection or the range for being roughly in-tune. You can also change how many data points are collected, which will affect the resolution and, therefore, accuracy of the tuner.
There is a simple graphical interface using [pygame](https://www.pygame.org/) to know how to tune your guitar. 

NOTE: I used a Blue Yeti USB microphone for developing this tuner. There is no guarantee this will work flawlessly on your system.
