import sounddevice as sd
import numpy as np
import wave
from core.stt import SpeechToText

SAMPLE_RATE = 16000
DURATION = 5

import noisereduce as nr
import scipy.io.wavfile as wav

def record_audio(filename="test.wav"):
    print("Recording for 5 seconds... Speak clearly.")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    # Flatten audio
    audio = audio.flatten()

    # Normalize
    audio = audio / np.max(np.abs(audio))

    # Noise reduction
    reduced_noise = nr.reduce_noise(
        y=audio,
        sr=SAMPLE_RATE,
        prop_decrease=0.8
    )

    # Save cleaned audio
    wav.write(
        filename,
        SAMPLE_RATE,
        (reduced_noise * 32767).astype(np.int16)
    )

    print("Recording saved.")



if __name__ == "__main__":
    record_audio()

    stt = SpeechToText()
    result = stt.transcribe("test.wav")

    print("\nTranscribed Text:")
    print(result)
