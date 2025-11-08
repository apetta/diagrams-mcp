# Diagrams MCP Server

MCP server for generating infrastructure and architecture diagrams as code using the Python diagrams library.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Smithery](https://smithery.ai/badge/@apetta/diagrams-mcp)](https://smithery.ai/server/@apetta/diagrams-mcp)

## Features

**5 Diagram Tools** for infrastructure, architecture, and flowcharts:

- **Infrastructure Diagrams** - 15+ providers (AWS, Azure, GCP, K8s, On-Prem, SaaS)
- **500+ Node Types** - Compute, database, network, storage, security
- **Custom Icons** - Web URLs (HTTPS) and local files
- **Flowcharts** - 24 shapes for process diagrams
- **Validation** - Dry-run before generation

**Advanced Capabilities:**

- Multiple output formats (PNG, PDF, JPG, DOT)
- Cluster grouping with unlimited nesting
- Edge styling (colours, labels, line styles)
- Token efficiency (up to 80% reduction)
- Graphviz attribute customisation

## Installation

### IDEs

_One-click installation badges coming soon for VS Code and Cursor_

### Claude Desktop

Add to your `claude_desktop_config.json`:

**For published package:**

```json
{
  "mcpServers": {
    "Diagrams": {
      "command": "uvx",
      "args": ["diagrams-mcp"]
    }
  }
}
```

**For local development:**

```json
{
  "mcpServers": {
    "Diagrams:local": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/diagrams-mcp",
        "run",
        "diagrams-mcp"
      ]
    }
  }
}
```

**System Requirements:**

- Graphviz must be installed:
  - macOS: `brew install graphviz`
  - Ubuntu/Debian: `sudo apt-get install graphviz`
  - Windows: Download from https://graphviz.org/download/

### Claude Code

**Quick setup (CLI):**

For published package:

```bash
claude mcp add diagrams-mcp --global
```

For local development:

```bash
claude mcp add diagrams-mcp --global \
  --command "uv --directory /ABSOLUTE/PATH/TO/diagrams-mcp run diagrams-mcp"
```

**Team setup (project-level):**

Add `.mcp.json` to your project root:

```json
{
  "mcpServers": {
    "Diagrams": {
      "command": "uvx",
      "args": ["diagrams-mcp"]
    }
  }
}
```

**Verify installation:**

```bash
claude mcp list
```

Or check in IDE: View → MCP Servers, or use `/mcp` command.

**System Requirements:**

- Graphviz: `brew install graphviz` (macOS), `sudo apt-get install graphviz` (Ubuntu)

## Try It

Once installed, try these prompts:

- "Create an AWS 3-tier web application diagram with Route53, ELB, EC2 instances, and RDS"
- "Generate a Kubernetes microservices architecture with ingress, services, and pods"
- "Build a flowchart for a CI/CD pipeline with decision points"
- "Create a diagram using a custom icon from my company logo URL"
- "Show me all available AWS compute nodes"

Map to tools: `create_diagram`, `create_diagram_with_custom_icons`, `create_flowchart`, `list_available_nodes`, `validate_diagram_spec`

## Tool Reference

All tool parameters and descriptions are available in your IDE's autocomplete.

### Diagram Generation (3 tools)

| Tool                               | Description                                                  |
| ---------------------------------- | ------------------------------------------------------------ |
| `create_diagram`                   | Full infrastructure/architecture diagrams with all providers |
| `create_diagram_with_custom_icons` | Diagrams with custom node icons from URLs or local files     |
| `create_flowchart`                 | Simplified flowchart creation with 24 process shapes         |

### Discovery & Validation (2 tools)

| Tool                    | Description                                                   |
| ----------------------- | ------------------------------------------------------------- |
| `list_available_nodes`  | Search 500+ available nodes by provider, category, or keyword |
| `validate_diagram_spec` | Dry-run validation before generation                          |

## Examples

### AWS 3-Tier Architecture

```json
{
  "name": "AWS 3-Tier Web Application",
  "nodes": [
    {
      "id": "r53",
      "provider": "aws",
      "category": "network",
      "type": "Route53",
      "label": "DNS"
    },
    {
      "id": "elb",
      "provider": "aws",
      "category": "network",
      "type": "ELB",
      "label": "Load Balancer"
    },
    {
      "id": "ec2_1",
      "provider": "aws",
      "category": "compute",
      "type": "EC2",
      "label": "Web Server 1"
    },
    {
      "id": "ec2_2",
      "provider": "aws",
      "category": "compute",
      "type": "EC2",
      "label": "Web Server 2"
    },
    {
      "id": "rds",
      "provider": "aws",
      "category": "database",
      "type": "RDS",
      "label": "Database"
    }
  ],
  "connections": [
    { "from_node": "r53", "to_node": "elb" },
    { "from_node": "elb", "to_node": ["ec2_1", "ec2_2"] },
    { "from_node": "ec2_1", "to_node": "rds" },
    { "from_node": "ec2_2", "to_node": "rds" }
  ],
  "direction": "LR",
  "output_format": ["png", "pdf"]
}
```

### Kubernetes Microservices

```json
{
  "name": "K8s Microservices",
  "nodes": [
    {
      "id": "ing",
      "provider": "k8s",
      "category": "network",
      "type": "Ingress",
      "label": "Ingress"
    },
    {
      "id": "svc_a",
      "provider": "k8s",
      "category": "network",
      "type": "Service",
      "label": "Service A"
    },
    {
      "id": "pod_a1",
      "provider": "k8s",
      "category": "compute",
      "type": "Pod",
      "label": "Pod A-1"
    },
    {
      "id": "pod_a2",
      "provider": "k8s",
      "category": "compute",
      "type": "Pod",
      "label": "Pod A-2"
    },
    {
      "id": "pvc",
      "provider": "k8s",
      "category": "storage",
      "type": "PersistentVolumeClaim",
      "label": "Storage"
    }
  ],
  "connections": [
    { "from_node": "ing", "to_node": "svc_a" },
    { "from_node": "svc_a", "to_node": ["pod_a1", "pod_a2"] },
    { "from_node": "pod_a1", "to_node": "pvc" },
    { "from_node": "pod_a2", "to_node": "pvc" }
  ],
  "clusters": [
    {
      "name": "Namespace: production",
      "node_ids": ["svc_a", "pod_a1", "pod_a2", "pvc"]
    }
  ]
}
```

### Custom Icons from Web URLs

```json
{
  "name": "Hybrid Architecture",
  "custom_nodes": [
    {
      "id": "custom_app",
      "label": "My Application",
      "icon_source": "url",
      "icon_path": "https://example.com/logo.png",
      "cache_icons": true
    }
  ],
  "nodes": [
    {
      "id": "s3",
      "provider": "aws",
      "category": "storage",
      "type": "S3",
      "label": "Storage"
    },
    {
      "id": "lambda",
      "provider": "aws",
      "category": "compute",
      "type": "Lambda",
      "label": "Function"
    }
  ],
  "connections": [
    { "from_node": "custom_app", "to_node": "s3" },
    { "from_node": "s3", "to_node": "lambda" }
  ]
}
```

### Custom Icons from Local Files

```json
{
  "name": "Internal Services",
  "custom_nodes": [
    {
      "id": "internal_api",
      "label": "Internal API",
      "icon_source": "local",
      "icon_path": "/path/to/api-icon.png"
    }
  ],
  "connections": [...]
}
```

### Flowchart with Decisions

```json
{
  "name": "CI/CD Pipeline",
  "steps": [
    { "id": "start", "shape": "StartEnd", "label": "Start" },
    { "id": "build", "shape": "Process", "label": "Build Code" },
    { "id": "test", "shape": "Decision", "label": "Tests Pass?" },
    { "id": "deploy", "shape": "Process", "label": "Deploy to Production" },
    { "id": "notify_fail", "shape": "Process", "label": "Notify Team" },
    { "id": "end", "shape": "StartEnd", "label": "End" }
  ],
  "flows": [
    { "from_step": "start", "to_step": "build" },
    { "from_step": "build", "to_step": "test" },
    { "from_step": "test", "to_step": "deploy", "label": "Yes" },
    { "from_step": "test", "to_step": "notify_fail", "label": "No" },
    { "from_step": "deploy", "to_step": "end" },
    { "from_step": "notify_fail", "to_step": "end" }
  ]
}
```

## Security (Custom Icons)

### Web URL Icons

- HTTPS-only (HTTP rejected)
- 5MB file size limit
- 5-second download timeout
- Image format validation (PNG, JPG)
- Automatic caching (~/.diagrams_mcp/icon_cache)

### Local File Icons

- Path validation (file must exist)
- Format validation
- Sandboxed execution

## Advanced Usage

### Clusters with Styling

```json
{
  "clusters": [
    {
      "name": "VPC",
      "node_ids": ["elb", "ec2_1", "ec2_2", "rds"],
      "graph_attr": {
        "bgcolor": "#E5F5FD",
        "pencolor": "#1976D2",
        "fontname": "Arial",
        "fontsize": "14"
      }
    }
  ]
}
```

### Edge Styling

```json
{
  "connections": [
    {
      "from_node": "app",
      "to_node": "db",
      "label": "SQL Query",
      "color": "red",
      "style": "dashed"
    }
  ]
}
```

### Custom Graphviz Attributes

```json
{
  "graph_attr": {
    "layout": "dot",
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.5"
  },
  "node_attr": {
    "fontname": "Helvetica",
    "fontsize": "12"
  }
}
```

### Multiple Output Formats

```json
{
  "output_format": ["png", "pdf"],
  "return_base64": true
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=diagrams_mcp --cov-report=html

# Specific test file
uv run pytest tests/test_create_diagram.py
```

### Development Modes

**STDIO mode** (for Claude Desktop integration):

```bash
uv run diagrams-mcp
```

**HTTP mode** (for containerised deployments):

```bash
uv run diagrams-mcp-http --port 8000
```

### Linting & Formatting

```bash
# Lint
uv run ruff check src/diagrams_mcp

# Format
uv run ruff format src/diagrams_mcp

# Check both
uv run poe check
```

## Docker Deployment

```bash
# Build
docker build -t diagrams-mcp .

# Run (HTTP mode)
docker run -p 8000:8000 diagrams-mcp

# Environment variables
docker run -e PORT=8080 diagrams-mcp
```

## MCP Resources

The server provides built-in documentation resources:

- `docs://quick-start` - Quick start guide with examples
- `docs://custom-icons` - Comprehensive custom icons guide
- `tools://available` - List of all available tools

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Acknowledgements

Built with:

- [diagrams](https://github.com/mingrammer/diagrams) - Diagram generation library
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Graphviz](https://graphviz.org/) - Graph visualisation software
- [Pydantic](https://docs.pydantic.dev/) - Data validation

## Quick Reference

### Common Providers

```
aws, azure, gcp, k8s, onprem, generic, programming, saas
```

### Common AWS Categories

```
compute, database, network, storage, analytics, ml, security
```

### Common Node Types

```
AWS: EC2, Lambda, RDS, S3, ELB, VPC, DynamoDB
Azure: VM, Functions, SQL, BlobStorage, VirtualNetworks
GCP: GCE, Functions, SQL, GCS, VPC
K8s: Pod, Service, Deployment, Ingress, PersistentVolume
```

### Quick Discovery

```bash
# List all AWS compute nodes
list_available_nodes(provider="aws", category="compute")

# Search for databases
list_available_nodes(search_term="database")

# All K8s resources
list_available_nodes(provider="k8s")
```
