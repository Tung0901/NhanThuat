"""
Nhan Thuat Audio Engine & Speech Normalization Package.
Provides text-to-speech sanitization, sentence chunking, and speech-ready scripts.
"""

from nhan_thuat.audio.speech_normalizer import (
    clean_markdown_for_speech,
    extract_speech_modes,
    split_into_utterance_chunks,
)

__all__ = [
    "clean_markdown_for_speech",
    "extract_speech_modes",
    "split_into_utterance_chunks",
]
