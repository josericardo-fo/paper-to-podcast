import json
import time
from typing import Any, Dict, Optional

import requests
from config import ELEVEN_LABS_API_KEY, PODCAST_DIR
from utils.text_processor import TextProcessor


class PodcastGenerator:
    """
    Responsável por gerar podcasts a partir de textos usando TTS.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ELEVEN_LABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"

        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")

    def generate_podcast(
        self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    ) -> Dict[str, Any]:
        """
        Gera um arquivo de áudio a partir do texto usando ElevenLabs API.

        Args:
            text: Texto para transformar em áudio
            voice_id: ID da voz a ser usada (padrão é "Rachel")

        Returns:
            Dicionário com informações sobre o podcast gerado
        """

        formatted_text = TextProcessor.format_for_tts(text)

        url = f"{self.base_url}/text-to-speech/{voice_id}/stream"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }

        data = {
            "text": formatted_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }

        start_time = time.time()

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = TextProcessor.sanitize_filename(text[:30])
            audio_path = PODCAST_DIR / f"podcast_{timestamp}_{filename}.mp3"

            with open(audio_path, "wb") as f:
                f.write(response.content)

            duration = time.time() - start_time

            result = {
                "audio_path": str(audio_path),
                "metadata": {
                    "voice_id": voice_id,
                    "text_length": len(text),
                    "duration_seconds": round(duration, 2),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }

            # Salvar metadados
            metadata_path = audio_path.with_suffix(".json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            return result

        except Exception as e:
            error_msg = f"Erro na geração do podcast: {str(e)}"
            print(error_msg)
            return {"error": error_msg}

    def list_available_voices(self) -> list:
        """Retorna lista de vozes disponíveis na ElevenLabs API."""
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["voices"]
        except Exception as e:
            print(f"Erro ao obter vozes disponíveis: {e}")
            return []
