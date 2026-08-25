import os

import torch
import soundfile as sf

from dotenv import load_dotenv
from pyannote.audio import Pipeline


load_dotenv()


class DiarizationService:

    def __init__(self):

        hf_token = os.getenv("HF_TOKEN")

        if not hf_token:
            raise ValueError(
                "HF_TOKEN is not configured in the .env file."
            )

        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-community-1",
            token=hf_token
        )

    def load_audio(self, audio_path: str):

        waveform, sample_rate = sf.read(
            audio_path,
            dtype="float32"
        )

        # Convert stereo → mono
        if waveform.ndim == 2:
            waveform = waveform.mean(axis=1)

        # Convert NumPy array → PyTorch tensor
        waveform = torch.from_numpy(waveform)

        # Add channel dimension
        # (samples) → (1, samples)
        waveform = waveform.unsqueeze(0)

        return {
            "waveform": waveform,
            "sample_rate": sample_rate
        }

    def diarize(self, audio_path: str):

        audio = self.load_audio(audio_path)

        output = self.pipeline(audio)

        diarization = output.exclusive_speaker_diarization

        speakers = []

        for turn, speaker in diarization:

            speakers.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

        return speakers

    def assign_speakers(
        self,
        transcript_segments,
        speaker_segments
    ):

        result = []

        for transcript in transcript_segments:

            transcript_start = transcript["start"]
            transcript_end = transcript["end"]

            best_speaker = None
            best_overlap = 0

            for speaker_segment in speaker_segments:

                speaker_start = speaker_segment["start"]
                speaker_end = speaker_segment["end"]

                overlap_start = max(
                    transcript_start,
                    speaker_start
                )

                overlap_end = min(
                    transcript_end,
                    speaker_end
                )

                overlap = max(
                    0,
                    overlap_end - overlap_start
                )

                if overlap > best_overlap:

                    best_overlap = overlap
                    best_speaker = speaker_segment["speaker"]

            result.append({
                "start": transcript_start,
                "end": transcript_end,
                "speaker": best_speaker,
                "text": transcript["text"]
            })

        return result