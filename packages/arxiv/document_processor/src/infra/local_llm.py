import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from common.profiler import profile_execution

class QuantizedLocalLLMAdapter:
    """Adapter for running LLM inference within a 6GB VRAM constraint."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._init_model()

    def _init_model(self) -> None:
        """Loads the model using 4-bit quantization to fit local hardware."""
        with profile_execution(f"load_quantized_{self.model_id}"):
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                quantization_config=quantization_config,
                device_map="auto"
            )

    def generate(self, prompts: list[str], max_batch_size: int = 2) -> list[str]:
        """Executes inference using dynamic batching to prevent OOM."""
        results = []

        for i in range(0, len(prompts), max_batch_size):
            batch = prompts[i:i + max_batch_size]
            with profile_execution(f"generate_batch_{len(batch)}"):
                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    padding=True,
                    truncation=True
                ).to(self.device)

                with torch.no_grad():
                    outputs = self.model.generate(**inputs, max_new_tokens=256)

                decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                results.extend(decoded)

                # Deterministic memory reclamation
                del inputs, outputs
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        return results
