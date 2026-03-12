# app_structurizer/src/domain/ports.py
"""
Structural subtyping contracts (Interfaces).
These define the boundaries between pure logic and the C-level ML inferencing.
"""

from typing import Protocol
from .models import RawDocument, MarkdownAST

class VisionExtractor(Protocol):
    """
    A Functor mapping the continuous spatial domain (RawDocument)
    to a discrete semantic domain (MarkdownAST).

    Any ML framework (Nougat, Marker, GPT-4V) must satisfy this contract.
    """

    def extract_ast(self, document: RawDocument) -> MarkdownAST:
        """
        Executes the forward pass of the neural network to construct the Markdown string.

        Args:
            document: The unparsed PDF binary reference.

        Returns:
            MarkdownAST: The successfully decoded discrete text representation.
        """
        ...
