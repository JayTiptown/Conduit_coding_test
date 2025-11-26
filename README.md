# Conduit Voice Pipeline

A real-time voice-to-voice conversational AI application that transcribes user speech, generates responses using an LLM, synthesizes speech using a custom voice, and logs all interaction data.

## Project Structure

The source code is located in the `src/` directory:

- **`src/main.py`**: The entry point and orchestrator. It handles the main conversation loop, Voice Activity Detection (VAD) logic to detect when the user stops speaking, and coordinates the flow between transcription, LLM, and TTS.
- **`src/transcription.py`**: Handles real-time speech-to-text using the Deepgram API. It manages the WebSocket connection and streaming audio data.
- **`src/llm.py`**: Client for the Language Model (OpenRouter/OpenAI compatible). It sends the transcribed text to the model and streams back the response.
- **`src/tts.py`**: Handles Text-to-Speech using the ElevenLabs API. It converts the LLM's textual response into audio (using a specific cloned voice) and plays it back to the user.
- **`src/audio.py`**: Manages audio capture from the system microphone using `sounddevice`.
- **`src/storage.py`**: Handles logging of all character-level data (timestamps, confidence, latency, source) to `transcription_log.csv`.

## Prerequisites

- **Python 3.11+**
- **uv**: An extremely fast Python package installer and resolver. [Install uv](https://github.com/astral-sh/uv).
- **API Keys**: You need API keys for the following services set in your environment or `.env` file:
    - `DEEPGRAM_API_KEY`: For transcription.
    - `OPENROUTER_API_KEY`: For LLM generation.
    - `ELEVEN_LABS_API_KEY`: For Text-to-Speech.

## Setup

1.  **Clone the repository** (if applicable).
2.  **Install dependencies**:
    ```bash
    uv sync
    ```
    This will create a virtual environment and install all required packages specified in `pyproject.toml` and `uv.lock`.

## Running the Application

To run the voice pipeline:

```bash
uv run src/main.py
```

### Interaction
1.  The application will connect to Deepgram and start listening.
2.  **Speak naturally**. The system uses a silence detection threshold (default ~0.8s) to determine when you are finished speaking.
3.  Once silence is detected:
    - The system sends your speech to the LLM.
    - The LLM generates a response.
    - The response is spoken back to you using the configured ElevenLabs voice.
    - There is a short "refractory period" after the AI speaks where input is ignored to prevent echo loops.
4.  **Logs**: Check `transcription_log.csv` for detailed timing data of every character spoken and heard.

## Configuration

You can adjust settings in the code (mostly in `src/main.py` and `src/tts.py`):
- **Latency**: VAD silence threshold is set in `conversation_loop` in `src/main.py`.
- **Voice**: The ElevenLabs Voice ID is configured in `src/main.py` when initializing `TTSClient`.
