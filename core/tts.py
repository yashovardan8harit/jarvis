import subprocess
import uuid
import os
import re
import sounddevice as sd
import soundfile as sf

class TextToSpeech:
    def __init__(self):
        self.voice_path = "voices/en_US-lessac-medium.onnx"

    def clean_text(self, text):
        # Remove markdown symbols
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)   # bold
        text = re.sub(r"\*(.*?)\*", r"\1", text)       # italic
        text = re.sub(r"#+\s*", "", text)              # headers ###
        text = re.sub(r"-\s*", "", text)               # bullet points
        text = re.sub(r"`", "", text)                  # inline code
        text = re.sub(r"\n+", ". ", text)              # newlines → pause
        return text.strip()

    def speak(self, text):
        text = self.clean_text(text)

        temp_file = f"temp_{uuid.uuid4().hex}.wav"

        command = [
            "piper",
            "--model", self.voice_path,
            "--output_file", temp_file
        ]

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(text)

            data, samplerate = sf.read(temp_file, dtype='float32')

            sd.play(data * 0.9, samplerate)
            sd.wait()

            os.remove(temp_file)

        except Exception as e:
            print("TTS Error:", e)
