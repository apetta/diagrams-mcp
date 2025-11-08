"""Node registry for discovering available diagram nodes.

This module provides a catalog of 500+ nodes across 15+ providers.
Nodes are dynamically discovered via introspection.
"""

import inspect
import pkgutil
from functools import lru_cache
from typing import Dict, List, Optional


# Provider → Categories mapping
# This is the lightweight metadata that's always in memory
PROVIDER_CATEGORIES: Dict[str, List[str]] = {
    "aws": [
        "analytics",
        "ar",
        "blockchain",
        "business",
        "compute",
        "cost",
        "database",
        "devtools",
        "enablement",
        "enduser",
        "engagement",
        "game",
        "general",
        "integration",
        "iot",
        "management",
        "media",
        "migration",
        "ml",
        "mobile",
        "network",
        "quantum",
        "robotics",
        "satellite",
        "security",
        "storage",
    ],
    "azure": [
        "analytics",
        "compute",
        "database",
        "devops",
        "general",
        "identity",
        "integration",
        "iot",
        "migration",
        "ml",
        "mobile",
        "monitor",
        "network",
        "security",
        "storage",
        "web",
    ],
    "gcp": [
        "analytics",
        "api",
        "compute",
        "database",
        "devtools",
        "iot",
        "migration",
        "ml",
        "network",
        "operations",
        "security",
        "storage",
    ],
    "k8s": [
        "chaos",
        "clusterconfig",
        "compute",
        "controlplane",
        "ecosystem",
        "group",
        "infra",
        "network",
        "others",
        "podconfig",
        "rbac",
        "storage",
    ],
    "onprem": [
        "aggregator",
        "analytics",
        "auth",
        "cd",
        "certificates",
        "ci",
        "client",
        "compute",
        "container",
        "database",
        "dns",
        "etl",
        "gitops",
        "iac",
        "identity",
        "inmemory",
        "logging",
        "mlops",
        "monitoring",
        "network",
        "queue",
        "registry",
        "search",
        "security",
        "storage",
        "tracing",
        "vcs",
        "workflow",
    ],
    "alibabacloud": [
        "analytics",
        "application",
        "compute",
        "database",
        "network",
        "security",
        "storage",
    ],
    "digitalocean": ["compute", "database", "network", "storage"],
    "elastic": [
        "agent",
        "beats",
        "elasticsearch",
        "enterprisesearch",
        "kibana",
        "logstash",
        "orchestration",
        "saas",
    ],
    "firebase": ["base", "develop", "extentions", "grow", "quality"],
    "generic": [
        "blank",
        "compute",
        "database",
        "device",
        "network",
        "os",
        "place",
        "storage",
        "virtualization",
    ],
    "ibm": [
        "analytics",
        "applications",
        "blockchain",
        "compute",
        "data",
        "devops",
        "infrastructure",
        "management",
        "network",
        "security",
        "social",
        "storage",
    ],
    "oci": ["compute", "connectivity", "database", "monitoring", "network", "storage"],
    "openstack": [
        "apiproxies",
        "applicationlifecycle",
        "applicationserver",
        "billing",
        "compute",
        "database",
        "deployment",
        "monitoring",
        "networking",
        "orchestration",
        "security",
        "sharedservices",
        "storage",
    ],
    "outscale": ["compute", "network", "security", "storage"],
    "programming": ["flowchart", "framework", "language", "runtime"],
    "saas": [
        "alerting",
        "analytics",
        "cdn",
        "chat",
        "communication",
        "filesharing",
        "identity",
        "logging",
        "media",
        "recommendation",
        "social",
    ],
}


# Sample nodes for common providers (lazy-loaded full catalog)
# This is just a subset for quick reference - full catalog loaded on demand
SAMPLE_NODES: Dict[str, Dict[str, List[str]]] = {
    "aws": {
        "compute": ["EC2", "Lambda", "ECS", "EKS", "Fargate", "Batch"],
        "database": ["RDS", "DynamoDB", "ElastiCache", "Neptune", "Redshift"],
        "storage": ["S3", "EBS", "EFS", "Glacier", "Storage_Gateway"],
        "network": ["VPC", "ELB", "CloudFront", "Route53", "API_Gateway"],
    },
    "azure": {
        "compute": ["VM", "Functions", "ContainerInstances", "AKS", "Batch"],
        "database": ["SQL", "Cosmos_DB", "Cache_For_Redis", "Database_For_MySQL"],
        "storage": ["Storage_Accounts", "Blob_Storage", "Disk_Storage", "File_Storage"],
        "network": ["VirtualNetworks", "LoadBalancers", "CDN", "DNS", "Application_Gateway"],
    },
    "gcp": {
        "compute": ["GCE", "Functions", "GKE", "Run", "AppEngine"],
        "database": ["SQL", "Firestore", "Bigtable", "Spanner", "Memorystore"],
        "storage": ["GCS", "Filestore", "PersistentDisk"],
        "network": ["VPC", "LoadBalancing", "CDN", "DNS", "API_Gateway"],
    },
    "k8s": {
        "compute": [
            "Pod",
            "StatefulSet",
            "Deployment",
            "ReplicaSet",
            "DaemonSet",
            "Job",
            "CronJob",
        ],
        "network": ["Service", "Ingress", "NetworkPolicy"],
        "storage": ["PersistentVolume", "PersistentVolumeClaim", "StorageClass"],
    },
    "generic": {
        "compute": ["Rack"],
        "database": ["SQL"],
        "device": ["Mobile", "Tablet"],
        "network": ["Firewall", "Router", "Switch", "VPN", "Subnet"],
        "os": ["Android", "Centos", "Debian", "IOS", "Linux", "Ubuntu", "Windows"],
    },
    "programming": {
        "framework": ["Angular", "Django", "Flask", "React", "Vue", "Spring", "FastAPI"],
        "language": ["Python", "Java", "Go", "Rust", "JavaScript", "TypeScript", "Kotlin"],
        "flowchart": ["StartEnd", "Process", "Decision", "Data", "Document", "Database", "Delay"],
    },
}


def get_node_info(provider: str, category: str, node_type: str) -> Dict[str, str]:
    """Get information about a specific node.

    Args:
        provider: Provider name (e.g., "aws")
        category: Category within provider (e.g., "compute")
        node_type: Node type (e.g., "EC2")

    Returns:
        Dict with node information including import path
    """
    # Construct import path
    # Example: diagrams.aws.compute.EC2
    import_path = f"diagrams.{provider}.{category}.{node_type}"

    return {
        "provider": provider,
        "category": category,
        "type": node_type,
        "import_path": import_path,
    }


@lru_cache(maxsize=1)
def _discover_all_nodes() -> Dict[str, Dict[str, List[str]]]:
    """Dynamically discover all available nodes from diagrams library.

    Results are cached for performance.

    Returns:
        Dict mapping provider -> category -> list of node types
    """
    import diagrams  # noqa: F401

    results = {}

    # Only introspect known providers
    for provider in PROVIDER_CATEGORIES.keys():
        try:
            provider_module = __import__(f"diagrams.{provider}", fromlist=[""])
            results[provider] = {}

            # Get all submodules (categories)
            provider_path = provider_module.__path__
            for _importer, category, _ispkg in pkgutil.iter_modules(provider_path):
                # Skip private/internal modules
                if category.startswith("_"):
                    continue

                try:
                    cat_module = __import__(
                        f"diagrams.{provider}.{category}",
                        fromlist=[""],
                    )
                    nodes = []

                    # Get all classes that don't start with underscore
                    for name, obj in inspect.getmembers(cat_module):
                        if (
                            inspect.isclass(obj)
                            and not name.startswith("_")
                            and hasattr(obj, "_icon")
                        ):  # Ensure it's a node class
                            nodes.append(name)

                    if nodes:
                        results[provider][category] = sorted(nodes)

                except (ImportError, AttributeError):
                    # Skip categories that can't be imported
                    pass

        except ImportError:
            # Skip providers that aren't installed
            pass

    return results


def search_nodes(
    provider: Optional[str] = None,
    category: Optional[str] = None,
    search_term: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, str]]:
    """Search for nodes matching criteria using dynamic discovery.

    Args:
        provider: Optional provider filter
        category: Optional category filter
        search_term: Optional search term for node type
        limit: Maximum number of results to return

    Returns:
        List of matching nodes with their information
    """
    # Get discovered nodes (cached after first call)
    all_nodes = _discover_all_nodes()

    results = []

    # Determine which providers to search
    providers_to_search = [provider] if provider else all_nodes.keys()

    for prov in providers_to_search:
        if prov not in all_nodes:
            continue

        provider_nodes = all_nodes[prov]

        # Determine which categories to search
        categories_to_search = [category] if category else provider_nodes.keys()

        for cat in categories_to_search:
            if cat not in provider_nodes:
                continue

            # Get nodes in this category
            nodes = provider_nodes[cat]

            for node in nodes:
                # Apply search filter if provided
                if search_term and search_term.lower() not in node.lower():
                    continue

                node_info = get_node_info(prov, cat, node)
                results.append(node_info)

                if len(results) >= limit:
                    return results

    return results


def get_all_providers() -> List[str]:
    """Get list of all available providers."""
    return sorted(PROVIDER_CATEGORIES.keys())


def get_provider_categories(provider: str) -> List[str]:
    """Get list of categories for a provider.

    Args:
        provider: Provider name

    Returns:
        List of category names

    Raises:
        ValueError: If provider is unknown
    """
    if provider not in PROVIDER_CATEGORIES:
        available = ", ".join(sorted(PROVIDER_CATEGORIES.keys()))
        raise ValueError(f"Unknown provider '{provider}'. Available providers: {available}")

    return PROVIDER_CATEGORIES[provider]


def validate_node_reference(provider: str, category: str, node_type: str) -> bool:
    """Validate that a node reference is potentially valid.

    This checks that the provider and category exist, but doesn't verify
    the specific node type exists (since we don't load the full catalog).

    Args:
        provider: Provider name
        category: Category name
        node_type: Node type

    Returns:
        True if the reference is potentially valid

    Raises:
        ValueError: If provider or category is invalid
    """
    if provider not in PROVIDER_CATEGORIES:
        available = ", ".join(sorted(PROVIDER_CATEGORIES.keys()))
        raise ValueError(f"Unknown provider '{provider}'. Available providers: {available}")

    if category not in PROVIDER_CATEGORIES[provider]:
        available = ", ".join(sorted(PROVIDER_CATEGORIES[provider]))
        raise ValueError(
            f"Unknown category '{category}' for provider '{provider}'. "
            f"Available categories: {available}"
        )

    # If we got here, provider and category are valid
    # We can't validate the specific node type without loading the full catalog,
    # but that will be validated at diagram generation time by the diagrams library
    return True
