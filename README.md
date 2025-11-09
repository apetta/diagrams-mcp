# Diagrams MCP Server

MCP server for generating infrastructure and architecture diagrams as code using the Python [diagrams](https://diagrams.mingrammer.com/) library.

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
- Graphviz attribute customisation

## Installation

**System Requirements:**

- Graphviz must be installed:
  - macOS: `brew install graphviz`
  - Ubuntu/Debian: `sudo apt-get install graphviz`
  - Windows: Download from https://graphviz.org/download/

### IDEs

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_diagrams-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22diagrams%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22diagrams-mcp%22%5D%7D)

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=diagrams&config=eyJjb21tYW5kIjoidXZ4IGRpYWdyYW1zLW1jcCJ9)

### Claude Desktop

Add to your `claude_desktop_config.json`:

**For published package:**

```json
{
  "mcpServers": {
    "diagrams": {
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
    "diagrams:local": {
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

### Claude Code

**Quick setup (CLI):**

Published package:

```bash
claude mcp add --transport stdio math -- uvx diagrams-mcp
```

Local development:

```bash
claude mcp add --transport stdio math -- uvx --from /absolute/path/to/diagrams-mcp diagrams-mcp
```

**Team setup (project-level):**

Add `.mcp.json` to your project root:

```json
{
  "mcpServers": {
    "diagrams": {
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

## Custom Icons

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

## Development

### Running Tests

```bash
# Run all tests
uv run poe test
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

## License

MIT License. See `LICENSE` file for details.

## Contributing

Contributions welcome via PRs! Please ensure:

1. Tests pass, and new ones are added if applicable
2. Code is linted & formatted
3. Type hints are included
4. Clear, actionable error messages are provided

## Support

For issues and questions, please open an issue on GitHub.
