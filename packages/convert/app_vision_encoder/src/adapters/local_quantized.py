from typing import Any, Optional
from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

class LocalQuantizedAdapter:
    """
    Satisfies VisionEncoderPort utilizing local 4-bit quantized VRAM allocation.
    """
    def __init__(self, model_id: str = "llava-hf/llava-1.5-7b-hf"):
        self._model_id = model_id
        self._processor: Optional[Any] = None
        self._model: Optional[Any] = None

    def _load_models_lazily(self) -> None:
        if self._model is None:
            import torch
            from transformers import AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig
            
            # Explicitly suppress mypy on untyped library functions
            quantization_config = BitsAndBytesConfig(  # type: ignore[no-untyped-call]
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            
            self._processor = AutoProcessor.from_pretrained(self._model_id)  # type: ignore[no-untyped-call]
            self._model = LlavaForConditionalGeneration.from_pretrained(
                self._model_id,
                quantization_config=quantization_config,
                device_map="auto"
            )

    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription:
        from PIL import Image
        
        self._load_models_lazily()
        
        raw_image = Image.open(image.file_path).convert("RGB")
        prompt = "USER: <image>\nProvide a concise academic description of this image.\nASSISTANT:"
        
        inputs = self._processor(prompt, raw_image, return_tensors='pt').to("cuda") # type: ignore
        output_tensor = self._model.generate(**inputs, max_new_tokens=200) # type: ignore
        
        decoded_output = self._processor.decode(output_tensor[0], skip_special_tokens=True) # type: ignore
        semantic_content = decoded_output.split("ASSISTANT:")[-1].strip()
        
        return SemanticDescription(
            content=semantic_content,
            metadata={
                "engine": "LocalQuantizedAdapter",
                "quantization": "4-bit",
                "model_id": self._model_id
            }
        )
