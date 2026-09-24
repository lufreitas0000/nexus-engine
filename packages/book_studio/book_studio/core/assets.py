import re
import shutil
from pathlib import Path
from book_studio.core.schemas import ExtractionResult

class AssetManager:
    """Routes physical image files to the assets directory and injects structured placeholders."""

    def __init__(self, asset_dir: Path):
        self.asset_dir = asset_dir
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        # Matches standard markdown image links output by extraction tools
        self.img_regex = re.compile(r'!\[.*?\]\(([^)]+\.(?:png|jpg|jpeg|webp))\)')

    def process_and_route(self, data: ExtractionResult, source_img_dir: Path) -> ExtractionResult:
        for page in data.pages:
            for block in page.blocks:
                if not block.content:
                    continue

                matches = self.img_regex.findall(block.content)
                for img_rel_path in matches:
                    # Resolve just the filename since OCR tools might prepend directories
                    img_name = Path(img_rel_path).name
                    src_img = source_img_dir / img_name

                    if src_img.exists():
                        dest_img = self.asset_dir / img_name
                        shutil.copy2(src_img, dest_img)

                        # Generate the Obsidian-compatible callout and LaTeX-compatible metadata block
                        placeholder = (
                            f"\n> [!figure] Asset: {img_name}\n"
                            f"> **Caption:** [AGENT_TO_EXTRACT]\n"
                            f"> **Alt-Text:** [AGENT_TO_GENERATE]\n"
                            f"> ![[{img_name}]]\n"
                        )

                        # Deterministically replace the raw OCR image tag with the structured block
                        pattern = rf'!\[.*?\]\({re.escape(img_rel_path)}\)'
                        match = re.search(pattern, block.content)
                        if match:
                            block.content = block.content.replace(match.group(0), placeholder)

        return data
