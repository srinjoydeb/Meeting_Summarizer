from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import json

from backend.services.transcription_service import TranscriptionService
from backend.services.diarization_service import DiarizationService


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
TRANSCRIPT_DIR = BASE_DIR / "transcripts"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".ogg"
}


transcription_service = TranscriptionService()


@router.post("/upload")
async def upload_meeting(audio: UploadFile = File(...)):

    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="No audio file provided"
        )

    extension = Path(audio.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {extension}"
        )

    meeting_id = str(uuid.uuid4())

    filename = f"{meeting_id}{extension}"

    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        while chunk := await audio.read(1024 * 1024):
            buffer.write(chunk)

    return {
        "message": "Meeting audio uploaded successfully",
        "meeting_id": meeting_id,
        "filename": filename
    }


@router.post("/{meeting_id}/transcribe")
async def transcribe_meeting(meeting_id: str):

    # Find the uploaded audio file
    audio_files = list(UPLOAD_DIR.glob(f"{meeting_id}.*"))

    if not audio_files:
        raise HTTPException(
            status_code=404,
            detail="Meeting audio not found"
        )

    audio_path = audio_files[0]

    # Transcribe audio
    result = transcription_service.transcribe(
        str(audio_path)
    )

    # Save transcript
    transcript_path = TRANSCRIPT_DIR / f"{meeting_id}.json"

    with open(transcript_path, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    return {
        "message": "Meeting transcribed successfully",
        "meeting_id": meeting_id,
        "transcript_file": str(transcript_path),
        "transcript": result
    }

diarization_service = DiarizationService()
 
@router.post("/{meeting_id}/diarize")
async def diarize_meeting(meeting_id: str):

    try:

        print("\n==============================")
        print("STARTING DIARIZATION")
        print("Meeting ID:", meeting_id)
        print("==============================")

        # -----------------------------------
        # 1. Find audio
        # -----------------------------------

        audio_files = list(
            UPLOAD_DIR.glob(f"{meeting_id}.*")
        )

        print("Audio files found:", audio_files)

        if not audio_files:
            raise HTTPException(
                status_code=404,
                detail="Meeting audio not found"
            )

        audio_path = audio_files[0]

        print("Audio path:", audio_path)

        # -----------------------------------
        # 2. Find transcript
        # -----------------------------------

        transcript_path = (
            TRANSCRIPT_DIR / f"{meeting_id}.json"
        )

        print("Transcript path:", transcript_path)

        if not transcript_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Transcript not found"
            )

        # -----------------------------------
        # 3. Load transcript
        # -----------------------------------

        with open(
            transcript_path,
            "r",
            encoding="utf-8"
        ) as file:

            transcript_data = json.load(file)

        print(
            "Transcript segments:",
            len(transcript_data["segments"])
        )

        # -----------------------------------
        # 4. Run diarization
        # -----------------------------------

        print("\nRunning pyannote diarization...")

        speaker_segments = (
            diarization_service.diarize(
                str(audio_path)
            )
        )

        print("\nDiarization completed!")

        print(
            "Speaker segments:",
            len(speaker_segments)
        )

        print(
            "First speaker segment:",
            speaker_segments[0]
            if speaker_segments
            else "NONE"
        )

        # -----------------------------------
        # 5. Assign speakers
        # -----------------------------------

        print("\nAssigning speakers to transcript...")

        final_segments = (
            diarization_service.assign_speakers(
                transcript_data["segments"],
                speaker_segments
            )
        )

        print("Speaker assignment completed!")

        # -----------------------------------
        # 6. Create result
        # -----------------------------------

        result = {
            "meeting_id": meeting_id,
            "segments": final_segments
        }

        # -----------------------------------
        # 7. Save result
        # -----------------------------------

        output_path = (
            TRANSCRIPT_DIR /
            f"{meeting_id}_diarized.json"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nDiarized transcript saved:")
        print(output_path)

        print("\n==============================")
        print("DIARIZATION SUCCESS")
        print("==============================\n")

        return result

    except HTTPException:
        raise

    except Exception as e:

        import traceback

        print("\n\n==============================")
        print("DIARIZATION FAILED")
        print("==============================")

        print("Exception type:", type(e).__name__)
        print("Exception:", str(e))

        print("\nFULL TRACEBACK:")
        traceback.print_exc()

        print("==============================\n")

        raise HTTPException(
            status_code=500,
            detail=f"Diarization failed: {type(e).__name__}: {str(e)}"
        )