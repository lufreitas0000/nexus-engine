import pytest
import httpx
from research_graph.src.infra.external_apis import ColabComputeAdapter, RemoteComputeUnavailableError
import respx

@pytest.mark.asyncio
async def test_colab_adapter_success():
    adapter = ColabComputeAdapter("http://test-tunnel")

    with respx.mock:
        route = respx.post("http://test-tunnel/api/v1/compute").respond(
            json={"status": "completed", "result": {"output": "success"}}
        )
        response = await adapter.execute_remote_task("api/v1/compute", {"task_id": "123"})
        assert response["status"] == "completed"
        assert route.called

@pytest.mark.asyncio
async def test_colab_adapter_502_error():
    adapter = ColabComputeAdapter("http://test-tunnel")

    with respx.mock:
        respx.post("http://test-tunnel/api/v1/compute").respond(status_code=502)
        with pytest.raises(RemoteComputeUnavailableError):
            await adapter.execute_remote_task("api/v1/compute", {"task_id": "123"})
