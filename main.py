import sounddevice as sd
import numpy as np
import wave
import noisereduce as nr
import scipy.io.wavfile as wav
import time

from ui.desktop_ui import JarvisWindow
from PyQt6.QtWidgets import QApplication
import sys

from core.stt import SpeechToText
from core.tts import TextToSpeech
from brain.llm import LocalLLM
from brain.intent_router import IntentRouter
from core.wake_word import WakeWordDetector
from config import PORCUPINE_ACCESS_KEY

SAMPLE_RATE = 16000
DURATION = 5

# Initialize components
try:
    stt = SpeechToText()
except Exception as e:
    print("Whisper failed:", e)

tts = TextToSpeech()
llm = LocalLLM()
router = IntentRouter()

# Confirmation state
pending_action = None
awaiting_confirmation = False

ACTIVE_TIMEOUT = 8  # seconds
last_active_time = 0
active_mode = False

def record_audio(filename="input.wav"):
    print("🎤 Listening...")

    SAMPLE_RATE = 16000
    SILENCE_THRESHOLD = 0.0005
    SILENCE_DURATION = 1.5
    CHUNK_DURATION = 0.25

    audio_buffer = []
    silence_time = 0
    speech_started = False

    while True:
        chunk = sd.rec(
            int(CHUNK_DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )
        sd.wait()

        chunk = chunk.flatten()
        volume = np.sqrt(np.mean(chunk**2))

        if volume > SILENCE_THRESHOLD:
            speech_started = True
            silence_time = 0
            audio_buffer.append(chunk)

        elif speech_started:
            audio_buffer.append(chunk)
            silence_time += CHUNK_DURATION

        # Stop only if speech had started AND silence long enough
        if speech_started and silence_time >= SILENCE_DURATION:
            break

    if not audio_buffer:
        return

    full_audio = np.concatenate(audio_buffer)

    # Normalize
    if np.max(np.abs(full_audio)) > 0:
        full_audio = full_audio / np.max(np.abs(full_audio))

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((full_audio * 32767).astype(np.int16).tobytes())

    print("🛑 Speech ended. Processing...")

app = QApplication(sys.argv)
window = JarvisWindow()

def run_jarvis():
    print("Jarvis thread started")
    global pending_action
    global awaiting_confirmation
    global active_mode
    global last_active_time

    wake_detector = WakeWordDetector(PORCUPINE_ACCESS_KEY)

    while True:

        # ==========================
        # If not active → wait wake word
        # ==========================
        if not active_mode:
            wake_detector.listen()
            window.showListeningSignal.emit()
            active_mode = True
            last_active_time = time.time()


        # ==========================
        # If active → listen directly
        # ==========================
        record_audio()

        text = stt.transcribe("input.wav")
        print(f"\nYou said: {text}")

        if not text.strip():
            # If silence, check timeout
            if time.time() - last_active_time > ACTIVE_TIMEOUT:
                print("🟢 Returning to sleep mode.")
                active_mode = False
            continue

        last_active_time = time.time()

        text_lower = text.lower()

        # ==========================
        # Confirmation Handling
        # ==========================
        if awaiting_confirmation:

            if any(word in text_lower for word in ["yes", "confirm", "do it"]):
                tts.speak("Confirmed.")
                if pending_action:
                    pending_action()
                pending_action = None
                awaiting_confirmation = False
                continue

            elif any(word in text_lower for word in ["no", "cancel", "stop"]):
                tts.speak("Cancelled.")
                pending_action = None
                awaiting_confirmation = False
                continue

            else:
                tts.speak("Please say yes or no.")
                continue

        # ==========================
        # Intent Routing
        # ==========================
        intent = router.route(text)

        if intent:

            if intent["execute"].__name__ in ["shutdown", "restart"]:
                tts.speak("Are you sure you want to proceed?")
                pending_action = intent["execute"]
                awaiting_confirmation = True

            else:
                window.showResponseSignal.emit(intent["speak"])
                tts.speak(intent["speak"])
                intent["execute"]()

        else:
            response = llm.generate(text)
            tts.speak(response)

if __name__ == "__main__":
    from threading import Thread

    jarvis_thread = Thread(target=run_jarvis, daemon=True)
    jarvis_thread.start()

    sys.exit(app.exec())