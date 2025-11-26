import sys
import signal
import time
from audio import AudioCapture
from transcription import TranscriptionService
from storage import DataLogger

def main():
    # Initialize Logger
    logger = DataLogger()
    print(f"Logging to {logger.filename}")

    # Initialize Transcription Service
    def handle_word(word, start, end, confidence):
        print(f"Transcript: {word} ({start}-{end})")
        logger.log_word_chars(word, start, end, confidence)

    try:
        transcriber = TranscriptionService(callback=handle_word)
        transcriber.start()
        print("Connected to Deepgram")
    except Exception as e:
        print(f"Failed to init Deepgram: {e}")
        return

    # Initialize Audio
    audio = AudioCapture()
    
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\nStopping...")
        audio.stop()
        transcriber.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("Starting audio capture. Speak now... (Press Ctrl+C to stop)")
    audio.start()

    try:
        for chunk in audio.get_data():
            transcriber.send_audio(chunk)
    except Exception as e:
        print(f"Error in audio loop: {e}")
    finally:
        audio.stop()
        transcriber.stop()

if __name__ == "__main__":
    main()

