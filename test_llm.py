import json

from backend.services.llm_service import LLMService


INPUT_FILE = "backend/transcripts/61ff20f1-26de-4e57-b7bf-99cc04a413aa_diarized.json"


def main():

    print("Loading diarized transcript...")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        diarized_data = json.load(file)

    print("Transcript loaded.")

    print(
        f"Number of segments: "
        f"{len(diarized_data.get('segments', []))}"
    )

    print("\nSending transcript to Gemini...")

    llm = LLMService()

    result = llm.generate_mom(
        diarized_data
    )

    print("\n" + "=" * 70)
    print("GEMINI RESPONSE")
    print("=" * 70)

    print(result)

    print("=" * 70)


if __name__ == "__main__":
    main()