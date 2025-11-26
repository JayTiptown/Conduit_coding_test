## Part 1: Create a simple voice-to-text transcription program, where
1. a user can speak, and your program transcribes what the user says in realtime (aim for generally <300ms latency from time a word is spoken -> time data for that word is saved).
2. the transcription should be done through Deepgram (unless you have a good reason to not use Deepgram, in which case trust your judgement). You can use this Deepgram API key:
07101d289c209b4af367aef6c517e640c5493079

3. the data is saved in the following format: char, start-time, end-time, notes or debug info if any. Each char should be one character spoken aloud. For example, if I say 'hello world', then the ds should have eleven entries (or potentially twelve, depending on how you choose to handle spaces in the final position).
4. the word start and end times should come precisely from the transcription API. Depending on how you do it, you may need to estimate char-level timestamps based on the word-level ones. That's fine.