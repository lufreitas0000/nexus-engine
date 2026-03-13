# app_vision_encoder/src/adapters/external_api.py
import base64
import httpx
from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

class ExternalAPIAdapter:
    """
    Satisfies VisionEncoderPort by delegating tensor inference to an external HTTP endpoint.
    """
    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://api.openai.com/v1/chat/completions",
        model: str = "gpt-4o"
    ):
        self._api_key = api_key
        self._endpoint = endpoint
        self._model = model

    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription:
        # Map physical bytes to Base64 discrete string representation
        image_bytes = image.file_path.read_bytes()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Provide a concise academic description of this mathematical plot or diagram."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 300
        }

        # Execute blocking socket operation
        with httpx.Client() as client:
            response = client.post(self._endpoint, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()

        semantic_content = data["choices"][0]["message"]["content"]

        return SemanticDescription(
            content=semantic_content,
            metadata={
                "engine": "ExternalAPIAdapter",
                "network_status": f"{response.status_code} {response.reason_phrase}",
                "model": self._model
            }
        )
