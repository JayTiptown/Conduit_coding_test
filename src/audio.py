import queue
import sounddevice as sd
import sys

class AudioCapture:
    def __init__(self, rate: int = 16000, chunk: int = 1024, channels: int = 1):
        self.rate = rate
        self.chunk = chunk
        self.channels = channels
        self.audio_queue = queue.Queue()
        self.stream = None

    def _callback(self, indata, frames, time, status):
        """Callback for sounddevice InputStream."""
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def start(self):
        """Start the audio stream."""
        self.stream = sd.RawInputStream(
            samplerate=self.rate,
            blocksize=self.chunk,
            dtype='int16',
            channels=self.channels,
            callback=self._callback
        )
        self.stream.start()

    def stop(self):
        """Stop the audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def get_data(self):
        """Generator that yields audio data chunks."""
        while True:
            try:
                # Blocking get with timeout to allow checking for stop signal externally if needed
                yield self.audio_queue.get(timeout=1) 
            except queue.Empty:
                continue
            except GeneratorExit:
                self.stop()
                break

