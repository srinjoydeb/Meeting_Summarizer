import json
from typing import List, Dict, Any


class ChunkingService:

    def __init__(
        self,
        chunk_duration_seconds: int = 120,
        overlap_seconds: int = 30,
        max_characters: int = 18000
    ):
        """
        Configuration for transcript chunking.

        chunk_duration_seconds:
            Target maximum duration of a chunk.
            120 seconds = 2 minutes.

        overlap_seconds:
            Amount of previous conversation included
            in the next chunk.

        max_characters:
            Safety limit for the amount of text
            contained in a chunk.
        """

        self.chunk_duration_seconds = chunk_duration_seconds
        self.overlap_seconds = overlap_seconds
        self.max_characters = max_characters

    def create_chunks(
        self,
        diarized_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Split a diarized transcript into overlapping chunks.

        Input:
            {
                "segments": [
                    {
                        "start": ...,
                        "end": ...,
                        "speaker": "...",
                        "text": "..."
                    }
                ]
            }

        Output:
            [
                {
                    "chunk_id": 1,
                    "start": ...,
                    "end": ...,
                    "duration": ...,
                    "segment_count": ...,
                    "text": "...",
                    "segments": [...]
                }
            ]
        """

        segments = diarized_data.get("segments", [])

        if not segments:
            return []

        chunks = []

        current_segments = []
        current_start = None
        current_characters = 0

        chunk_id = 1

        for segment in segments:

            text = segment.get("text", "").strip()

            if not text:
                continue

            segment_start = float(segment["start"])
            segment_end = float(segment["end"])

            # Start a new chunk
            if not current_segments:
                current_start = segment_start

            current_duration = (
                segment_end - current_start
            )

            segment_characters = len(text)

            duration_exceeded = (
                current_duration >=
                self.chunk_duration_seconds
            )

            character_limit_exceeded = (
                current_characters +
                segment_characters
                > self.max_characters
            )

            # If the current chunk has data and adding
            # this segment would exceed our limits,
            # finalize the current chunk.
            if current_segments and (
                duration_exceeded
                or character_limit_exceeded
            ):

                chunks.append(
                    self._build_chunk(
                        chunk_id,
                        current_segments
                    )
                )

                chunk_id += 1

                # Keep the last part of the previous
                # chunk for context overlap.
                overlap_start = (
                    segment_start -
                    self.overlap_seconds
                )

                overlap_segments = [
                    previous_segment
                    for previous_segment in current_segments
                    if float(previous_segment["end"])
                    >= overlap_start
                ]

                current_segments = overlap_segments

                if current_segments:

                    current_start = float(
                        current_segments[0]["start"]
                    )

                    current_characters = sum(
                        len(
                            s.get("text", "").strip()
                        )
                        for s in current_segments
                    )

                else:

                    current_start = segment_start
                    current_characters = 0

            current_segments.append(segment)

            current_characters += segment_characters

        # Add the final chunk.
        if current_segments:

            chunks.append(
                self._build_chunk(
                    chunk_id,
                    current_segments
                )
            )

        return chunks

    def _build_chunk(
        self,
        chunk_id: int,
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build the final representation of one chunk.
        """

        start = float(segments[0]["start"])
        end = float(segments[-1]["end"])

        formatted_text = self._format_segments(
            segments
        )

        return {
            "chunk_id": chunk_id,
            "start": start,
            "end": end,
            "duration": round(end - start, 2),
            "segment_count": len(segments),
            "text": formatted_text,
            "segments": segments
        }

    def _format_segments(
        self,
        segments: List[Dict[str, Any]]
    ) -> str:
        """
        Convert structured diarization segments into
        compact conversation text for the LLM.
        """

        lines = []

        for segment in segments:

            speaker = segment.get(
                "speaker",
                "UNKNOWN"
            )

            text = segment.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            start = float(
                segment.get("start", 0)
            )

            end = float(
                segment.get("end", 0)
            )

            lines.append(
                f"[{start:.2f}-{end:.2f}] "
                f"{speaker}: {text}"
            )

        return "\n".join(lines)

    def save_chunks(
        self,
        chunks: List[Dict[str, Any]],
        output_path: str
    ) -> None:
        """
        Save chunks to a JSON file.
        """

        output = {
            "chunk_count": len(chunks),
            "chunks": chunks
        }

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output,
                file,
                indent=4,
                ensure_ascii=False
            )