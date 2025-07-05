import azure.cognitiveservices.speech as speechsdk
from utils.azure_blob_storage import upload_file_to_blob
from fastapi.concurrency import run_in_threadpool
from fastapi import HTTPException
from settings import settings
from uuid import uuid4
import base64

speech_key = settings.MICROSOFT_AZURE_TEXT_TO_SPEECH_RESOURCE_KEY
speech_endpoint = "https://eastasia.api.cognitive.microsoft.com/"
speech_voice_name = "id-ID-GadisNeural"
folder_name = "voices"

def _synthesize_speech(request) -> str:
    scene_id = request.get("scene_id")
    text_content = request.get("prompt")
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)
    speech_config.speech_synthesis_voice_name = speech_voice_name

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    result = speech_synthesizer.speak_text_async(text_content).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        audio_data = result.audio_data

        base64_audio = base64.b64encode(audio_data).decode("utf-8")

        filename = f"{uuid4()}.wav"

        blob_url = upload_file_to_blob(
            base64_string=base64_audio, 
            folder_name= folder_name,
            blob_filename=filename
        )

        return {
            "scene_id": scene_id,
            "type": "voice",
            "voice": blob_url
        }

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        error_msg = f"Speech synthesis canceled: {cancellation_details.reason}"
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            error_msg += f" — {cancellation_details.error_details}"
        print(error_msg)
        raise HTTPException(status_code=500, detail="someting went wrong when Synthesizing voice")

async def synthesize_speech(request):
    return await run_in_threadpool(_synthesize_speech, request)