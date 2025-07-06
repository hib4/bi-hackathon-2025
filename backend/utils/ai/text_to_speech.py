import azure.cognitiveservices.speech as speechsdk
from utils.azure_blob_storage import upload_file_to_blob
from fastapi.concurrency import run_in_threadpool
from fastapi import HTTPException
from settings import settings
from uuid import uuid4
import base64
import threading
import time

speech_key = settings.MICROSOFT_AZURE_TEXT_TO_SPEECH_RESOURCE_KEY
speech_endpoint = "https://eastasia.api.cognitive.microsoft.com/"
folder_name = "voices"

AVAILABLE_VOICES = {
    "en-US-JennyMultilingualNeural": {
        "name": "Jenny 🌈",
        "description": "Suara manis multi-bahasa seperti guru favorit yang selalu sabar"
    },
    "en-US-AvaMultilingualNeural": {
        "name": "Ava 🎀",
        "description": "Suara modern ala Amerika yang cocok untuk cerita fantasi"
    },
    "en-US-AlloyTurboMultilingualNeural": {
        "name": "Alloy Turbo 🚀",
        "description": "Suara super cepat penuh energi seperti roket!"
    },
    "en-US-NovaTurboMultilingualNeural": {
        "name": "Nova Turbo ✨",
        "description": "Suara ceria yang membuat hari-harimu berkilau"
    },
    # "en-US-CoraMultilingualNeural": {
    #     "name": "Cora 🍭",
    #     "description": "Suara hangat seperti kakak perempuan yang baik hati"
    # },
    # "en-US-ChristopherMultilingualNeural": {
    #     "name": "Christopher 🏆",
    #     "description": "Suara tegas dan heroik untuk cerita petualangan"
    # },
    # "en-US-BrandonMultilingualNeural": {
    #     "name": "Brandon 🎸",
    #     "description": "Suara santai ala anak muda yang asyik diajak ngobrol"
    # },
    # "en-US-SteffanMultilingualNeural": {
    #     "name": "Steffan 🎮",
    #     "description": "Suara seru untuk narasi game dan petualangan digital"
    # },
    # "en-US-AdamMultilingualNeural": {
    #     "name": "Adam 🏡",
    #     "description": "Suara hangat seperti ayah yang pandai bercerita"
    # },
    # "en-US-AmandaMultilingualNeural": {
    #     "name": "Amanda 🌸",
    #     "description": "Suara lembut yang cocok untuk dongeng pengantar tidur"
    # },
    # "en-US-DerekMultilingualNeural": {
    #     "name": "Derek 🎭",
    #     "description": "Suara ekspresif untuk membawakan karakter yang hidup"
    # },
    # "en-US-DustinMultilingualNeural": {
    #     "name": "Dustin 🏄‍♂️",
    #     "description": "Suara santai seperti teman bermain di pantai"
    # },
    # "en-US-LewisMultilingualNeural": {
    #     "name": "Lewis 🎩",
    #     "description": "Suara elegan untuk kisah misteri dan detektif"
    # },
    # "en-GB-AdaMultilingualNeural": {
    #     "name": "Ada 🍵",
    #     "description": "Suara klasik ala Inggris dengan logat British yang elegan"
    # },
    # "en-GB-OllieMultilingualNeural": {
    #     "name": "Ollie ⚽",
    #     "description": "Suara energik khas anak Inggris yang suka petualangan"
    # },
    "zh-CN-XiaoxiaoMultilingualNeural": {
        "name": "Xiaoxiao 🏮",
        "description": "Suara manis yang cocok untuk bercerita"
    }
}

CLIENT_TIMEOUT = 300000000000
SERVICE_TIMEOUT_THRESHOLD = 300000000000

def _synthesize_speech(request) -> str:
    scene_id = request.get("scene_id")
    text_content = request.get("prompt")
    voice_name_code = request.get("voice_name_code")

    if len(text_content) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Text too long. Please limit to 1000 characters per request."
        )

    ssml = f"""
    <speak version='1.0' xml:lang='id-ID'>
        <voice name='{voice_name_code}'>
            <lang xml:lang='id-ID'>{text_content}</lang>
        </voice>
    </speak>
    """

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)
    speech_config.speech_synthesis_voice_name = voice_name_code
    speech_config.set_property(speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceBoundary, "false")

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    class ResultContainer:
        def __init__(self):
            self.result = None
            self.exception = None
            self.start_time = time.time()
            self.audio_size = 0

    container = ResultContainer()

    def audio_chunk_cb(evt):
        container.audio_size += len(evt.audio_data)
        elapsed = time.time() - container.start_time

        if container.audio_size > 0:
            approx_duration = container.audio_size / 32000
            current_rtf = elapsed / approx_duration if approx_duration > 0 else 0
            
            if current_rtf > SERVICE_TIMEOUT_THRESHOLD:
                speech_synthesizer.stop_speaking_async()
                container.exception = HTTPException(
                    status_code=408,
                    detail=f"Service performance threshold exceeded (RTF: {current_rtf:.2f})"
                )

    speech_synthesizer.synthesizing.connect(audio_chunk_cb)

    def worker():
        try:
            container.result = speech_synthesizer.speak_ssml_async(ssml).get()
        except Exception as e:
            container.exception = e

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=CLIENT_TIMEOUT)

    if t.is_alive():
        speech_synthesizer.stop_speaking_async()
        t.join(timeout=2)
        raise HTTPException(
            status_code=408,
            detail=f"Speech synthesis timed out after {CLIENT_TIMEOUT} seconds"
        )

    if container.exception:
        raise container.exception

    result = container.result

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        audio_data = result.audio_data
        base64_audio = base64.b64encode(audio_data).decode("utf-8")
        filename = f"{uuid4()}.wav"

        blob_url = upload_file_to_blob(
            base64_string=base64_audio, 
            folder_name=folder_name,
            blob_filename=filename
        )

        return {
            "scene_id": scene_id,
            "type": "voice",
            "voice": blob_url
        }

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        
        if "Timeout" in cancellation_details.error_details:
            raise HTTPException(
                status_code=408,
                detail="Azure service timeout: " + cancellation_details.error_details
            )
        
        error_msg = f"Speech synthesis canceled: {cancellation_details.reason}"
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            error_msg += f" — {cancellation_details.error_details}"
        
        print(error_msg)
        raise HTTPException(
            status_code=500,
            detail="Speech synthesis was canceled by the service"
        )

async def synthesize_speech(request):
    return await run_in_threadpool(_synthesize_speech, request)