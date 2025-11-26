import sys
import signal
import time
import threading
from audio import AudioCapture
from transcription import TranscriptionService
from storage import DataLogger
from llm import LLMClient
from tts import TTSClient
from utils import stream_sentences

def main():
    # Initialize Components
    logger = DataLogger()
    print(f"Logging to {logger.filename}")

    llm = LLMClient()
    # Using custom voice ID -- this is supposed to be my voice
    tts = TTSClient(voice_id="mJ4Z2GugAkYk7kSHBhiO") 
    
    # State
    user_transcript_buffer = []
    last_word_time = time.time()
    is_processing = False
    processing_lock = threading.Lock()
    ai_finish_time = 0.0 # Timestamp when AI finished speaking
    
    # Events
    new_word_event = threading.Event()
    
    def handle_word(word, start, end, confidence):
        nonlocal last_word_time
        
        # Filter out empty or very low confidence if needed
        if not word.strip():
            return

        delay = 1.0 # 1.0s delay after AI speaks

        with processing_lock:
            # Ignore input if we are processing OR if we are in the "deaf period" after AI speech
            if is_processing or (time.time() < ai_finish_time + delay): 
                return
            
            print(f"User: {word}")
            user_transcript_buffer.append(word)
            last_word_time = time.time()
            new_word_event.set()

        latency = 0.0
        if transcriber and transcriber.stream_start_time > 0:
            estimated_spoken_time = transcriber.stream_start_time + end
            latency = time.time() - estimated_spoken_time
            
        print(f"Transcript: {word} ({start}-{end}) Latency: {latency*1000:.1f}ms")
        logger.log_word_chars(word, start, end, confidence, source="user", latency=latency)

    try:
        transcriber = TranscriptionService(callback=handle_word)
        transcriber.start()
        print("Connected to Deepgram")
    except Exception as e:
        print(f"Failed to init Deepgram: {e}")
        return

    audio = AudioCapture()
    
    # Turn-taking Logic Loop
    def conversation_loop():
        nonlocal is_processing, user_transcript_buffer, last_word_time, ai_finish_time
        
        while True:
            new_word_event.wait()
            
            time_since_last = time.time() - last_word_time
            if time_since_last > 3: # adjust if response is too fast or too slow
                with processing_lock:
                    if not user_transcript_buffer:
                        new_word_event.clear()
                        continue
                        
                    full_text = " ".join(user_transcript_buffer)
                    user_transcript_buffer = []
                    is_processing = True
                    new_word_event.clear()
                
                print(f"\nProcessing: {full_text}...")
                
                # 1. Send to LLM
                response_stream = llm.generate_response(full_text)
                
                # Optional delay before speaking the response
                time.sleep(1) 
                
                # 2. Stream to TTS and Play (using utility for clean sentence splitting)
                for sentence in stream_sentences(response_stream):
                    print(sentence, end="", flush=True)
                    try:
                        audio_bytes = tts.generate_audio_for_text(sentence)
                        tts.play_audio(audio_bytes, sentence, logger)
                    except Exception as e:
                        print(f"Playback error: {e}")
                
                print("\nDone speaking.\n")
                with processing_lock:
                    is_processing = False
                    ai_finish_time = time.time() 
                    last_word_time = time.time() 
            else:
                time.sleep(0.1)

    conversation_thread = threading.Thread(target=conversation_loop, daemon=True)
    conversation_thread.start()

    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\nStopping...")
        audio.stop()
        transcriber.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("Starting audio capture. Speak naturally... (Silence > 1.5s triggers response)")
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
