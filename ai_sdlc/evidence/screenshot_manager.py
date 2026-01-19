"""
Screenshot Manager

Manages screenshot evidence from QA testing.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """
    Manages screenshot evidence.

    Organizes, validates, and prepares screenshots for upload and presentation.
    """

    def __init__(self, work_item_id: str, base_path: str):
        """
        Initialize screenshot manager.

        Args:
            work_item_id: The work item ID
            base_path: Base path for screenshots
        """
        self.work_item_id = work_item_id
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Supported image formats
        self.supported_formats = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

    def collect_screenshots(self, directory: str) -> List[Dict[str, Any]]:
        """
        Collect all screenshots from a directory.

        Args:
            directory: Directory to scan

        Returns:
            List of screenshot metadata dictionaries
        """
        screenshots = []
        dir_path = Path(directory)

        if not dir_path.exists():
            self.logger.warning(f"Directory not found: {directory}")
            return screenshots

        # Find all image files
        for file_path in dir_path.rglob("*"):
            if file_path.suffix.lower() in self.supported_formats:
                metadata = self._extract_metadata(file_path)
                screenshots.append(metadata)

        self.logger.info(f"Collected {len(screenshots)} screenshots from {directory}")
        return screenshots

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from a screenshot file.

        Args:
            file_path: Path to screenshot file

        Returns:
            Metadata dictionary
        """
        stat = file_path.stat()

        return {
            "path": str(file_path),
            "filename": file_path.name,
            "size_bytes": stat.st_size,
            "format": file_path.suffix.lower().lstrip("."),
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "description": self._infer_description(file_path.name),
        }

    def _infer_description(self, filename: str) -> str:
        """
        Infer description from filename.

        Args:
            filename: Screenshot filename

        Returns:
            Human-readable description
        """
        # Remove extension
        name = Path(filename).stem

        # Replace separators with spaces
        name = name.replace("-", " ").replace("_", " ")

        # Capitalize words
        return name.title()

    def select_top_screenshots(
        self, screenshots: List[Dict[str, Any]], max_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select top screenshots for ADO attachment.

        Selects the most important screenshots based on naming and size.

        Args:
            screenshots: List of screenshot metadata
            max_count: Maximum number to select (default: 3)

        Returns:
            Selected screenshots
        """
        if len(screenshots) <= max_count:
            return screenshots

        # Priority keywords in filename
        priority_keywords = [
            "dashboard",
            "home",
            "main",
            "overview",
            "error",
            "result",
            "summary",
        ]

        # Score each screenshot
        scored = []
        for screenshot in screenshots:
            filename = screenshot["filename"].lower()
            score = 0

            # Higher score for priority keywords
            for keyword in priority_keywords:
                if keyword in filename:
                    score += 10

            # Slightly favor larger files (more content)
            score += min(screenshot["size_bytes"] / 10000, 5)

            scored.append((score, screenshot))

        # Sort by score descending and take top N
        scored.sort(reverse=True, key=lambda x: x[0])
        return [s[1] for s in scored[:max_count]]

    def validate_screenshot(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a screenshot file.

        Args:
            file_path: Path to screenshot file

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            return False, "File does not exist"

        # Check file format
        if path.suffix.lower() not in self.supported_formats:
            return False, f"Unsupported format: {path.suffix}"

        # Check file size (warn if > 5MB)
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 5:
            self.logger.warning(
                f"Screenshot {path.name} is large ({size_mb:.1f}MB). Consider compressing."
            )

        # Try to validate as image (optional, requires PIL)
        try:
            from PIL import Image

            with Image.open(path) as img:
                # Check if image can be loaded
                img.verify()

            return True, None

        except ImportError:
            # PIL not available, skip validation
            return True, None
        except Exception as e:
            return False, f"Invalid image file: {e}"

    def create_screenshot_index(
        self, screenshots: List[Dict[str, Any]]
    ) -> str:
        """
        Create an index document for screenshots.

        Args:
            screenshots: List of screenshot metadata

        Returns:
            Markdown index content
        """
        md = f"""# Screenshots - Work Item {self.work_item_id}

**Total Screenshots:** {len(screenshots)}
**Generated:** {Path.cwd()}

---

## Screenshots

"""

        for i, screenshot in enumerate(screenshots, 1):
            md += f"""### {i}. {screenshot['description']}

- **Filename:** `{screenshot['filename']}`
- **Size:** {screenshot['size_bytes'] / 1024:.1f} KB
- **Format:** {screenshot['format'].upper()}

"""

        md += """
---

*Generated by AI-SDLC Screenshot Manager*
"""

        return md

    def compress_screenshot(
        self, file_path: str, max_width: int = 1920, quality: int = 85
    ) -> Optional[str]:
        """
        Compress a screenshot to reduce file size.

        Args:
            file_path: Path to screenshot file
            max_width: Maximum width in pixels (default: 1920)
            quality: JPEG quality 1-100 (default: 85)

        Returns:
            Path to compressed file or None if failed
        """
        try:
            from PIL import Image

            path = Path(file_path)

            # Open image
            with Image.open(path) as img:
                # Calculate new size if needed
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                # Save compressed
                compressed_path = path.with_stem(path.stem + "_compressed")

                # Convert RGBA to RGB if saving as JPEG
                if compressed_path.suffix.lower() in [".jpg", ".jpeg"] and img.mode == "RGBA":
                    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img

                img.save(compressed_path, quality=quality, optimize=True)

            self.logger.info(f"Compressed {path.name} -> {compressed_path.name}")
            return str(compressed_path)

        except ImportError:
            self.logger.error("PIL not installed. Cannot compress screenshots.")
            return None
        except Exception as e:
            self.logger.error(f"Failed to compress {file_path}: {e}")
            return None
