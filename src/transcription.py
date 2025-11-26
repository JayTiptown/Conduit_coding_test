import os
import threading
from typing import Callable, Optional
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from dotenv import load_dotenv

load_dotenv()

class TranscriptionService:
    def __init__(self, 
                 callback: Callable[[str, float, float, float], None]):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not set")
        
        # DeepgramClient(api_key=...) is safer with v3+
        self.client = DeepgramClient(api_key=self.api_key)
        self.socket = None
        self.callback = callback
        self._thread = None
        self._stop_event = threading.Event()

    def _on_message(self, result, **kwargs):
        """Handle message from Deepgram."""
        if result is None:
            return
        
        # Result is likely a ListenV1ResultsEvent Pydantic model
        # We access attributes directly
        
        # Check for channel and alternatives
        if hasattr(result, 'channel') and result.channel:
            channel = result.channel
            if hasattr(channel, 'alternatives') and channel.alternatives:
                alternative = channel.alternatives[0]
                if hasattr(alternative, 'words') and alternative.words:
                    for word_info in alternative.words:
                        self.callback(
                            word_info.word,
                            word_info.start,
                            word_info.end,
                            word_info.confidence
                        )

    def _on_error(self, error, **kwargs):
        print(f"Deepgram Error: {error}")

    def _run(self):
        """Run the transcription loop in a thread."""
        # Options as strings for the connect method
        options = {
            "model": "nova-2",
            "language": "en-US",
            "smart_format": "true",
            "interim_results": "false",
            "encoding": "linear16",
            "channels": "1",
            "sample_rate": "16000",
        }

        try:
            # Use the context manager to connect
            with self.client.listen.v1.connect(**options) as socket:
                self.socket = socket
                
                # Register event listeners
                socket.on(EventType.MESSAGE, self._on_message)
                socket.on(EventType.ERROR, self._on_error)
                
                # Start listening (blocks until closed)
                socket.start_listening()
        except Exception as e:
            print(f"Transcription connection failed or closed: {e}")
        finally:
            self.socket = None

    def start(self):
        """Start the transcription service."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def send_audio(self, audio_data: bytes):
        """Send audio data to Deepgram."""
        if self.socket:
            try:
                self.socket.send_media(audio_data)
            except Exception as e:
                print(f"Error sending audio: {e}")

    def stop(self):
        """Stop the connection."""
        self._stop_event.set()
        if self.socket:
            # Attempt to close the socket cleanly
            # There isn't a clean 'close' method exposed on V1SocketClient easily reachable?
            # But accessing _websocket is possible if needed, or sending CloseStream
            try:
                 # Send an empty byte message or specific control message if supported
                 # Deepgram usually treats empty bytes as end of stream, or we can close.
                 if hasattr(self.socket, '_websocket'):
                     self.socket._websocket.close()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=1)
