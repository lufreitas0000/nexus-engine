import pytest
from book_studio.tools.compiler import TectonicCompiler

@pytest.fixture
def compiler():
    return TectonicCompiler()

def test_successful_compilation(compiler):
    valid_latex = r"""
    \documentclass{article}
    \begin{document}
    This is a valid test $E = mc^2$.
    \end{document}
    """
    result = compiler.compile(valid_latex)
    assert result.success is True
    assert result.log == ""

def test_failed_compilation(compiler):
    invalid_latex = r"""
    \documentclass{article}
    \begin{document}
    This is missing a dollar sign E = mc^2$.
    \end{document}
    """
    result = compiler.compile(invalid_latex)
    assert result.success is False
    assert "error:" in result.log.lower()
