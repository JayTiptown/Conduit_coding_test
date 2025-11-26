import os
import queue
import threading
import time
from typing import Iterator, Optional, Generator
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import sounddevice as sd
import numpy as np

class TTSClient:
    def __init__(self, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"): # Default voice (e.g. George)
        api_key = os.getenv("ELEVEN_LABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVEN_LABS_API_KEY not set")
        
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.sample_rate = 44100 # MP3 decoding usually results in 44.1k or 24k depending on model

    def generate_audio_for_text(self, text: str) -> bytes:
        """Generate audio bytes for a specific text chunk."""
        # Request MP3, we'll assume we can decode it or play it.
        # Actually sounddevice works with raw PCM (numpy arrays).
        # Decoding MP3 in python without ffmpeg/pydub is hard.
        # Let's try to request PCM if possible.
        # 'output_format' parameter in generate.
        # ElevenLabs supports 'pcm_16000', 'pcm_22050', 'pcm_24000', 'pcm_44100'.
        
        audio_stream = self.client.text_to_speech.convert(
            text=text,
            voice_id=self.voice_id,
            model_id="eleven_turbo_v2_5",
            output_format="pcm_24000" 
        )
        return b"".join(audio_stream)

    def play_audio(self, audio_data: bytes, text: str, logger):
        """
        Play audio data and log characters.
        """
        if not audio_data:
            return

        # Convert bytes to numpy array for sounddevice
        # PCM 16-bit int
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        sample_rate = 24000 # Matches pcm_24000
        duration = len(audio_np) / sample_rate
        
        start_time = time.time()
        
        # Non-blocking play? No, we want to block to log accurately or use a callback.
        # Blocking play is easiest for sync logging.
        sd.play(audio_np, sample_rate, blocking=True)
        
        end_time = time.time() # Should be start_time + duration roughly
        
        # Log characters distributed over duration
        logger.log_word_chars(text, start_time, end_time, confidence=1.0, source="llm")
        
