import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv("GOOGLE_API_KEY")
        model = os.getenv("GEMINI_MODEL")

        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not configured"
            )

        if not model:
            raise ValueError(
                "GEMINI_MODEL is not configured"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def generate_mom(self, diarized_transcript):

        prompt = f"""
You are an expert meeting analyst.

You are given a diarized meeting transcript.

The speakers are anonymous labels such as:

SPEAKER_00
SPEAKER_01
SPEAKER_02

Do NOT try to identify their real names.

Your job is to analyze the COMPLETE meeting transcript
and generate accurate Minutes of Meeting (MoM).

IMPORTANT RULES:

1. Use ONLY information present in the transcript.
2. Do NOT invent facts.
3. Preserve speaker labels exactly.
4. Identify important discussion points.
5. Identify decisions that were actually made.
6. Identify action items.
7. Identify who owns an action item when the transcript
   clearly indicates the speaker.
8. Identify deadlines when explicitly mentioned.
9. If there is no deadline, use null.
10. If there are no decisions, return [].
11. If there are no action items, return [].
12. If there are no open questions, return [].
13. Return ONLY valid JSON.
14. Do NOT return Markdown.
15. Do NOT include ```json or ``` around the response.

Return exactly this structure:

{{
    "title": "Meeting title",

    "summary": "Concise summary of the meeting",

    "key_discussion_points": [
        "Discussion point 1",
        "Discussion point 2"
    ],

    "decisions": [
        {{
            "decision": "What was decided",
            "made_by": "SPEAKER_00"
        }}
    ],

    "action_items": [
        {{
            "task": "Task that needs to be completed",
            "owner": "SPEAKER_01",
            "deadline": null
        }}
    ],

    "open_questions": [
        "Unresolved question"
    ]
}}

Here is the complete diarized meeting transcript:

{json.dumps(diarized_transcript, indent=2, ensure_ascii=False)}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text