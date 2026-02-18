import sounddevice as sd
import numpy as np
import wave

DEVICE_INDEX = None
SAMPLE_RATE = 16000
DURATION = 5  # seconds

print("Recording for 5 seconds... Speak now.")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=DEVICE_INDEX
)

sd.wait()

print("Recording complete. Saving file...")

with wave.open("test.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio.tobytes())

print("Saved as test.wav")
