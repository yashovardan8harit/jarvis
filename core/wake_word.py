import pvporcupine
import pyaudio
import struct

class WakeWordDetector:
    def __init__(self, access_key):
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["jarvis"]
        )

        self.pa = pyaudio.PyAudio()

        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def listen(self):
        print("🟢 Jarvis is sleeping... Say 'Jarvis' to wake.")

        while True:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            keyword_index = self.porcupine.process(pcm)

            if keyword_index >= 0:
                print("🔵 Wake word detected!")
                return True

    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        self.porcupine.delete()
