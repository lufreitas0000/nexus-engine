"""
Validation suite for the effectful Infrastructure Adapters.
Isolated via execution markers to prevent CI/CD hardware exceptions.
"""

import pytest
import httpx
import respx
from pathlib import Path

from src.domain.models import PhysicalImageReference
from src.adapters.external_api import ExternalAPIAdapter

@pytest.mark.network
@respx.mock
def test_external_api_adapter_deterministic_http(physical_image: PhysicalImageReference) -> None:
    target_url = "https://api.openai.com/v1/chat/completions"
    respx.post(target_url).mock(
        return_value=httpx.Response(200, json={
            "choices": [{"message": {"content": "Semantic decoding of a mathematical plot."}}]
        })
    )
    
    adapter = ExternalAPIAdapter(api_key="sk-synthetic-key")
    result = adapter.encode_manifold(physical_image)
    
    assert result.content == "Semantic decoding of a mathematical plot."
    assert result.metadata["engine"] == "ExternalAPIAdapter"
    assert result.metadata["network_status"] == "200 OK"

@pytest.mark.gpu
def test_local_quantized_adapter_vram_allocation(physical_image: PhysicalImageReference) -> None:
    from src.adapters.local_quantized import LocalQuantizedAdapter
    
    adapter = LocalQuantizedAdapter()
    result = adapter.encode_manifold(physical_image)
    
    assert isinstance(result.content, str)
    assert len(result.content) > 0
    assert result.metadata["engine"] == "LocalQuantizedAdapter"
    assert "4-bit" in result.metadata["quantization"]
