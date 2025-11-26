## Part 1: Create a simple voice-to-text transcription program, where
1. a user can speak, and your program transcribes what the user says in realtime (aim for generally <300ms latency from time a word is spoken -> time data for that word is saved).
2. the transcription should be done through Deepgram (unless you have a good reason to not use Deepgram, in which case trust your judgement). You can use this Deepgram API key:
07101d289c209b4af367aef6c517e640c5493079

3. the data is saved in the following format: char, start-time, end-time, notes or debug info if any. Each char should be one character spoken aloud. For example, if I say 'hello world', then the ds should have eleven entries (or potentially twelve, depending on how you choose to handle spaces in the final position).
4. the word start and end times should come precisely from the transcription API. Depending on how you do it, you may need to estimate char-level timestamps based on the word-level ones. That's fine.

## Part 2: Integrate this transcription program with an LLM respondent, where
1. the transcription of what the person said is sent to an LLM, which should generate a response. (Consider using Groq, Fireworks, or Openrouter, but up to you.)
2. an audio version of that LLM response is spoken to the user, using your own voice (probably with Elevenlabs).
3. the data of all chars that the user hears are saved in the same format as the data in Part 1.

The final product should be a program where the user has a conversation with an LLM (speaking in your voice), where all spoken and heard chars are saved in a single data format.