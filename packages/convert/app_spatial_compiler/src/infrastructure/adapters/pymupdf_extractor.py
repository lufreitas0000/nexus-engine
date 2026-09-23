import json
import fitz  # type: ignore
from app_spatial_compiler.src.domain.models import BookmarkNode, DocumentStructure

class PyMuPDFMetadataAdapter:
    """
    Adapter to extract metadata and structure using PyMuPDF (fitz).
    It reads TOCs (bookmarks) and allows compilation to markdown-compatible JSON.
    """

    def extract_structure(self, document_path: str | bytes) -> DocumentStructure:
        """Extracts the DocumentStructure (bookmarks) from a PDF."""
        try:
            if isinstance(document_path, bytes):
                doc = fitz.open(stream=document_path, filetype="pdf")
            else:
                doc = fitz.open(document_path)

            toc = doc.get_toc(simple=False)
            bookmarks = []
            for item in toc:
                # toc item format typically: [level, title, page, dest_dict_or_name]
                level = item[0]
                title = item[1]
                page = item[2]

                # Check if there is a destination name
                dest_name = None
                if len(item) > 3 and isinstance(item[3], dict):
                    dest_name = item[3].get('name')

                bookmarks.append(
                    BookmarkNode(
                        level=level,
                        title=title,
                        page=page,
                        dest_name=dest_name
                    )
                )

            doc.close()
            return DocumentStructure(bookmarks=tuple(bookmarks))
        except Exception as e:
            # Fallback or error logging could be placed here
            # For now, return an empty structure if it fails to parse
            return DocumentStructure(bookmarks=tuple())

    def to_markdown_json(self, structure: DocumentStructure) -> str:
        """
        Serializes the DocumentStructure to a JSON string that might be embedded
        as a metadata block or used by downstream orchestrators.
        """
        data = {
            "bookmarks": [
                {
                    "level": b.level,
                    "title": b.title,
                    "page": b.page,
                    "dest_name": b.dest_name
                }
                for b in structure.bookmarks
            ]
        }
        return json.dumps(data, indent=2)
