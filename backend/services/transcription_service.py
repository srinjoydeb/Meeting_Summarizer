from faster_whisper import WhisperModel
from pathlib import Path


class TranscriptionService:

    def __init__(self):
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path: str):

        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5
        )

        transcript_segments = []

        for segment in segments:
            transcript_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })

        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": transcript_segments
        }