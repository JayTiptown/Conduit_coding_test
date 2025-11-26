import re
from typing import Iterator, Generator, List

def stream_sentences(text_stream: Iterator[str]) -> Generator[str, None, None]:
    """
    Consumes a stream of text chunks and yields complete sentences.
    Maintains an internal buffer for partial sentences.
    """
    buffer = []
    
    for chunk in text_stream:
        buffer.append(chunk)
        combined_text = "".join(buffer)
        
        # Split by sentence endings (. ? !), keeping the delimiter
        # This regex looks for .!? followed by space or end of string
        parts = re.split(r'([.!?]+(?:\s+|$))', combined_text)
        
        if len(parts) > 1:
            # We have at least one sentence boundary
            # parts = [sent1, sep1, sent2, sep2, remainder]
            
            i = 0
            while i < len(parts) - 1:
                sentence = parts[i] + parts[i+1]
                yield sentence
                i += 2
            
            # Keep the remainder in the buffer
            if i < len(parts):
                buffer = [parts[i]]
            else:
                buffer = []
                
    # Yield any remaining text in the buffer after stream ends
    if buffer:
        remainder = "".join(buffer).strip()
        if remainder:
            yield remainder

