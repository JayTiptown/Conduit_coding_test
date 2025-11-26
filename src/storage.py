import csv
import os
from datetime import datetime
from typing import Optional

class DataLogger:
    def __init__(self, filename: str = "transcription_log.csv"):
        self.filename = filename
        self.last_end_time = 0.0
        self._initialize_file()

    def _initialize_file(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        # Only write header if file is empty or doesn't exist
        write_header = not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0
        
        if write_header:
            with open(self.filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["char", "start_time", "end_time", "notes"])

    def log_char(self, char: str, start_time: float, end_time: float, notes: str = ""):
        """Log a single character with timestamps."""
        with open(self.filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([char, f"{start_time:.3f}", f"{end_time:.3f}", notes])

    def log_word_chars(self, word: str, start: float, end: float, confidence: float):
        """
        Decompose a word into characters and log them with estimated timestamps.
        Handles inserting a space before the word if applicable.
        """
        if not word:
            return

        # If we have a previous word, log a space between them
        # Use a threshold to avoid spaces if we are just starting or weird overlap
        if self.last_end_time > 0 and start > self.last_end_time:
            self.log_char(" ", self.last_end_time, start, "implied space")

        duration = end - start
        num_chars = len(word)
        char_duration = duration / num_chars if num_chars > 0 else 0
        
        current_time = start
        
        for char in word:
            char_end = current_time + char_duration
            self.log_char(char, current_time, char_end, f"confidence: {confidence:.2f}")
            current_time = char_end
            
        self.last_end_time = end

