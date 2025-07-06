from utils.ai.text_to_speech import AVAILABLE_VOICES

def get_available_voice_model(current_user):
    return {
        "data": AVAILABLE_VOICES
    }