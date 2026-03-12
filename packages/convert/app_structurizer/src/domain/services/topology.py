"""
Domain Service for Mathematical PDF Topology Analysis.
Classifies the memory layout using Shannon Entropy H(X) bounds on the discrete text manifold.
"""

import math
from collections import Counter
import fitz  # type: ignore
from src.domain.models import RawDocument

class PdfTopologyAnalyzer:
    """
    Analyzes the discrete text state space of a PDF.
    Calculates the Shannon Entropy of the extracted string manifold.
    """

    # Theoretical entropy bounds for structured natural language (bits/char)
    H_LOWER_BOUND = 3.5
    H_UPPER_BOUND = 5.0

    def analyze(self, document: RawDocument) -> float:
        """
        Calculates the continuous Quality Factor Q in [0, 1] based on
        the zeroth-order Shannon Entropy of the vector text manifold.

        Args:
            document: Validated pointer to the PDF file.

        Returns:
            float: Quality Factor Q. 1.0 implies perfect mathematical vector text.
                   0.0 implies a raster manifold (image-only) or complete noise.
        """
        doc = fitz.open(str(document.file_path))

        try:
            if doc.page_count == 0:
                return 0.0

            # O(1) sampling: Extract the first accessible text manifold
            page = doc[0]
            extracted_string = page.get_text()

        finally:
            doc.close()

        if not extracted_string or len(extracted_string.strip()) < 10:
            return 0.0

        h_x = self._calculate_shannon_entropy(extracted_string)
        return self._map_entropy_to_q_factor(h_x)

    def _calculate_shannon_entropy(self, string_manifold: str) -> float:
        r"""
        Computes H(X) = - \sum P(x) \log_2 P(x) for the discrete character sequence.
        """
        manifold_length = len(string_manifold)
        if manifold_length == 0:
            return 0.0

        counts = Counter(string_manifold)
        entropy = 0.0

        for count in counts.values():
            p_x = count / manifold_length
            entropy -= p_x * math.log2(p_x)

        return entropy

    def _map_entropy_to_q_factor(self, h_x: float) -> float:
        """
        Maps the empirical entropy H(X) to a continuous Quality Factor.
        Topological validity peaks when H(X) is within the [3.5, 5.0] bound.
        """
        if self.H_LOWER_BOUND <= h_x <= self.H_UPPER_BOUND:
            return 1.0

        if h_x < self.H_LOWER_BOUND:
            # Degenerate extraction (e.g., repeated characters, empty spaces)
            return max(0.0, h_x / self.H_LOWER_BOUND)

        # High entropy regime (pseudo-random noise, encrypted streams, raw rasters)
        # Decay the Q factor as entropy approaches maximum 8-bit noise.
        return max(0.0, 1.0 - ((h_x - self.H_UPPER_BOUND) / 3.0))
