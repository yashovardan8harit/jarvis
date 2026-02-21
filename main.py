import sounddevice as sd
import numpy as np
import wave
import time
import sys
import signal

from core.stt import SpeechToText
from core.tts import TextToSpeech
from core.wake_word import WakeWordDetector
from brain.intent_router import IntentRouter
from brain.llm import LocalLLM
from config import PORCUPINE_ACCESS_KEY

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.desktop_ui import JarvisWindow
from threading import Thread


running = True
timer = QTimer()
timer.start(100)
timer.timeout.connect(lambda: None)
ACTIVE_TIMEOUT = 5  # seconds
active_mode = False
last_active_time = 0


# ==============================
# RECORD AUDIO
# ==============================
def record_audio(filename="input.wav"):
    print("🎤 Recording started...")

    SAMPLE_RATE = 16000
    SILENCE_THRESHOLD = 0.005
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

        if speech_started and silence_time >= SILENCE_DURATION:
            break

    if not audio_buffer:
        print("No speech detected.")
        return False

    full_audio = np.concatenate(audio_buffer)

    if np.max(np.abs(full_audio)) > 0:
        full_audio = full_audio / np.max(np.abs(full_audio))

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((full_audio * 32767).astype(np.int16).tobytes())

    print("🛑 Recording finished.")
    return True


# ==============================
# WAKE WORD WORKER
# ==============================
def wake_word_worker(window, stt, tts, router, llm):
    print("Wake word thread started")

    wake_detector = WakeWordDetector(PORCUPINE_ACCESS_KEY)
    print("Wake word initialized")

    global active_mode
    global last_active_time

    while running:

        # ==========================
        # SLEEP MODE
        # ==========================
        if not active_mode:
            wake_detector.listen()
            print("Wake word detected!")

            active_mode = True
            last_active_time = time.time()

        # ==========================
        # LISTEN (like old version)
        # ==========================
        window.showListeningSignal.emit()
        record_audio()

        text = stt.transcribe("input.wav")
        print("You said:", text)

        # ==========================
        # NO SPEECH CASE (timeout logic)
        # ==========================
        if not text.strip():
            if time.time() - last_active_time > ACTIVE_TIMEOUT:
                print("Returning to sleep mode.")
                active_mode = False
            continue

        # Reset timer only when valid speech happens
        last_active_time = time.time()

        window.showResponseSignal.emit("Processing...")
        time.sleep(0.2)

        # ==========================
        # ROUTING
        # ==========================
        intent = router.route(text)

        if intent:
            response = intent["speak"]
            window.showResponseSignal.emit(response)
            tts.speak(response)
            intent["execute"]()
        else:
            response = llm.generate(text)
            window.showResponseSignal.emit(response)
            tts.speak(response)


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print("Starting FULL Jarvis GUI...")

    stt = SpeechToText()
    print("Whisper initialized.")

    tts = TextToSpeech()
    print("TTS initialized.")

    router = IntentRouter()
    llm = LocalLLM()
    print("Brain initialized.")

    app = QApplication(sys.argv)
    window = JarvisWindow()

    # 🔥 ADD THIS
    from PyQt6.QtCore import QTimer
    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    def handle_exit(sig, frame):
        global running
        print("\nShutting down Jarvis...")
        running = False
        app.quit()

    signal.signal(signal.SIGINT, handle_exit)

    thread = Thread(
        target=wake_word_worker,
        args=(window, stt, tts, router, llm),
        daemon=True
    )
    thread.start()

    sys.exit(app.exec())
