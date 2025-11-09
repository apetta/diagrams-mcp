"""Simplified tests for MCP tool functions - pragmatic coverage."""

import json
import pytest


@pytest.mark.asyncio
async def test_create_diagram_works(mcp_client, sample_nodes, sample_connections, tmp_output_dir):
    """Test basic diagram generation."""
    result = await mcp_client.call_tool(
        "create_diagram",
        {
            "name": "Test",
            "nodes": sample_nodes[:2],
            "connections": [sample_connections[0]],
            "output_dir": str(tmp_output_dir),
        },
    )
    data = json.loads(result.content[0].text)
    assert "file_paths" in data


@pytest.mark.asyncio
async def test_list_nodes_works(mcp_client):
    """Test listing nodes."""
    result = await mcp_client.call_tool("list_available_nodes", {"provider": "aws", "limit": 5})
    data = json.loads(result.content[0].text)
    assert "nodes" in data
    assert len(data["nodes"]) > 0


@pytest.mark.asyncio
async def test_validate_spec_works(mcp_client, sample_nodes, sample_connections):
    """Test spec validation."""
    result = await mcp_client.call_tool(
        "validate_diagram_spec",
        {"nodes": sample_nodes, "connections": sample_connections},
    )
    data = json.loads(result.content[0].text)
    assert data["valid"] is True
