"""Icon manager for downloading, caching, and validating custom node icons."""

import hashlib
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from PIL import Image


# Security settings
MAX_ICON_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit
DOWNLOAD_TIMEOUT_SECONDS = 5
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".diagrams_mcp" / "icon_cache"


class IconManager:
    """Manage custom icons from web URLs and local files.

    Features:
    - Download icons from HTTPS URLs
    - Validate local file paths
    - Cache downloaded icons
    - Security: HTTPS only, size limits, format validation
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialise IconManager.

        Args:
            cache_dir: Directory for caching downloaded icons.
                      Defaults to ~/.diagrams_mcp/icon_cache
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _url_to_cache_filename(self, url: str) -> str:
        """Convert URL to cache filename using hash.

        Args:
            url: Icon URL

        Returns:
            Cache filename (hash + extension)
        """
        # Hash the URL to get a unique filename
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]

        # Extract extension from URL
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Try to get extension
        ext = ".png"  # default
        for allowed_ext in ALLOWED_EXTENSIONS:
            if path.endswith(allowed_ext):
                ext = allowed_ext
                break

        return f"{url_hash}{ext}"

    def get_cached_icon(self, url: str) -> Optional[str]:
        """Get cached icon path if it exists.

        Args:
            url: Icon URL

        Returns:
            Path to cached icon file, or None if not cached
        """
        cache_filename = self._url_to_cache_filename(url)
        cache_path = self.cache_dir / cache_filename

        if cache_path.exists():
            return str(cache_path)

        return None

    def download_icon(self, url: str, cache: bool = True) -> str:
        """Download icon from URL and optionally cache it.

        Args:
            url: HTTPS URL to icon image
            cache: Whether to cache the downloaded icon

        Returns:
            Path to downloaded (and optionally cached) icon file

        Raises:
            ValueError: If URL is invalid, download fails, or file is too large
        """
        # Validate HTTPS only
        if not url.startswith("https://"):
            raise ValueError(f"Icon URL must use HTTPS for security. Got: {url}")

        # Check cache first
        if cache:
            cached_path = self.get_cached_icon(url)
            if cached_path:
                return cached_path

        # Download the icon
        try:
            response = requests.get(
                url,
                timeout=DOWNLOAD_TIMEOUT_SECONDS,
                stream=True,  # Stream to check size
                headers={"User-Agent": "diagrams-mcp/1.0"},
            )
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > MAX_ICON_SIZE_BYTES:
                raise ValueError(
                    f"Icon file too large: {int(content_length)} bytes "
                    f"(max: {MAX_ICON_SIZE_BYTES} bytes)"
                )

            # Download content
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > MAX_ICON_SIZE_BYTES:
                    raise ValueError(f"Icon file exceeds maximum size: {MAX_ICON_SIZE_BYTES} bytes")

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to download icon from {url}: {str(e)}")

        # Validate it's actually an image
        try:
            from io import BytesIO

            img = Image.open(BytesIO(content))
            img.verify()  # Verify it's a valid image
        except Exception as e:
            raise ValueError(f"Downloaded file is not a valid image: {str(e)}")

        # Save to cache if requested
        if cache:
            cache_filename = self._url_to_cache_filename(url)
            cache_path = self.cache_dir / cache_filename

            with open(cache_path, "wb") as f:
                f.write(content)

            return str(cache_path)
        else:
            # Save to temporary location
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, suffix=Path(urlparse(url).path).suffix or ".png"
            ) as f:
                f.write(content)
                return f.name

    def validate_local_icon(self, path: str) -> str:
        """Validate that a local icon file exists and is valid.

        Args:
            path: Path to local icon file

        Returns:
            Absolute path to the icon file

        Raises:
            ValueError: If file doesn't exist, isn't an image, or has invalid format
        """
        # Convert to Path object
        icon_path = Path(path)

        # Check if file exists
        if not icon_path.exists():
            raise ValueError(f"Icon file not found: {path}")

        # Check if it's a file (not directory)
        if not icon_path.is_file():
            raise ValueError(f"Icon path is not a file: {path}")

        # Check extension
        if icon_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid icon file extension '{icon_path.suffix}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # Try to validate it's an image
        try:
            img = Image.open(icon_path)
            img.verify()
        except Exception as e:
            raise ValueError(f"File is not a valid image: {str(e)}")

        # Return absolute path
        return str(icon_path.absolute())

    def get_icon_path(
        self,
        icon_source: str,
        icon_path: str,
        cache: bool = True,
    ) -> str:
        """Get icon path, downloading from URL or validating local file.

        This is the main entry point for getting icon paths.

        Args:
            icon_source: Either "url" or "local"
            icon_path: URL or local file path
            cache: Whether to cache downloaded icons

        Returns:
            Absolute path to the icon file

        Raises:
            ValueError: If icon source is invalid or icon cannot be retrieved
        """
        if icon_source == "url":
            return self.download_icon(icon_path, cache=cache)
        elif icon_source == "local":
            return self.validate_local_icon(icon_path)
        else:
            raise ValueError(f"Invalid icon_source '{icon_source}'. Must be 'url' or 'local'")

    def clear_cache(self) -> int:
        """Clear all cached icons.

        Returns:
            Number of files deleted
        """
        count = 0
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
                count += 1
        return count

    def get_cache_size(self) -> int:
        """Get total size of cached icons in bytes.

        Returns:
            Total cache size in bytes
        """
        total_size = 0
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size
