"""Shared test fixtures for diagrams-mcp."""

from typing import AsyncGenerator

import pytest
from fastmcp import Client
from diagrams_mcp.server import mcp


@pytest.fixture
async def mcp_client() -> AsyncGenerator[Client, None]:
    """Create in-memory MCP client for testing."""
    async with Client(mcp) as client:
        yield client


@pytest.fixture
def sample_nodes():
    """Sample valid nodes for testing."""
    return [
        {
            "id": "s3",
            "provider": "aws",
            "category": "storage",
            "type": "S3",
            "label": "Storage",
        },
        {
            "id": "lambda",
            "provider": "aws",
            "category": "compute",
            "type": "Lambda",
            "label": "Function",
        },
        {
            "id": "rds",
            "provider": "aws",
            "category": "database",
            "type": "RDS",
            "label": "Database",
        },
    ]


@pytest.fixture
def sample_connections():
    """Sample connections for testing."""
    return [
        {"from_node": "s3", "to_node": "lambda"},
        {"from_node": "lambda", "to_node": "rds"},
    ]


@pytest.fixture
def sample_cluster():
    """Sample cluster for testing."""
    return {
        "name": "VPC",
        "node_ids": ["s3", "lambda", "rds"],
        "graph_attr": {"bgcolor": "#E5F5FD"},
    }


@pytest.fixture
def mock_icon_response(requests_mock):
    """Mock HTTP icon download with valid PNG data."""
    # PNG magic bytes + minimal valid PNG data
    png_data = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    requests_mock.get(
        "https://example.com/icon.png",
        content=png_data,
        headers={"Content-Type": "image/png"},
    )

    return requests_mock


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Temporary directory for diagram outputs."""
    output_dir = tmp_path / "diagrams"
    output_dir.mkdir()
    return output_dir
