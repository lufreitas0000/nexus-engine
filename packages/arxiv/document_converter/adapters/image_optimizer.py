import os
from pathlib import Path
from typing import Optional
from PIL import Image
import structlog

logger = structlog.get_logger(__name__)

class ImageOptimizer:
    def __init__(self, max_width: int = 1920, max_height: int = 1080, quality: int = 80):
        self.max_width = max_width
        self.max_height = max_height
        self.quality = quality

    def resolve_image_path(self, source_dir: str, image_ref: str) -> Optional[Path]:
        r"""
        LaTeX often omits the file extension for \includegraphics.
        This function tries to find the actual file in the source_dir.
        """
        base_path = Path(source_dir) / image_ref

        if base_path.exists() and base_path.is_file():
            return base_path

        extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.eps']
        for ext in extensions:
            test_path = base_path.with_suffix(ext)
            if test_path.exists() and test_path.is_file():
                return test_path

        return None

    def optimize(self, source_image_path: str, output_dir: str, output_filename: str) -> Optional[str]:
        """
        Loads the image using Pillow, converts it to RGB, resizes it if needed,
        and saves it as a compressed JPEG in output_dir.
        Returns the relative path to the optimized image from the output_dir.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            # Ensure the output filename ends with .jpg
            if not output_filename.lower().endswith(('.jpg', '.jpeg')):
                output_filename = f"{Path(output_filename).stem}.jpg"

            output_path = Path(output_dir) / output_filename

            # If input is PDF or EPS, Pillow might struggle without Ghostscript/Poppler.
            # We'll try to open it and just skip if it fails.
            with Image.open(source_image_path) as img:
                # Convert to RGB (handles transparency in PNGs by replacing with black/white or just dropping alpha)
                if img.mode in ('RGBA', 'P', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')

                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1]) # Use alpha channel as mask
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if necessary while maintaining aspect ratio
                img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)

                # Save optimized JPEG
                img.save(output_path, "JPEG", quality=self.quality, optimize=True)

            return str(Path(output_filename))

        except Exception as e:
            logger.warning(f"Failed to optimize image {source_image_path}: {e}")
            return None
