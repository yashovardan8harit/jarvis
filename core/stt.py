from faster_whisper import WhisperModel
import os

class SpeechToText:
    def __init__(self):
        print("Loading Whisper model...")
        self.model = WhisperModel(
            "medium.en",
            device="cpu",
            compute_type="float32"
        )
        print("Whisper loaded successfully.")

    def transcribe(self, audio_path):
        segments, info = self.model.transcribe(
            audio_path,
            language="en",
            beam_size=5,
            vad_filter=True
        )

        text = ""
        for segment in segments:
            text += segment.text + " "

        return text.strip()
