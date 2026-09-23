import ast
import argparse
import sys

def summarize_python_file(filepath: str) -> str:
    """
    Reads a Python file and returns a summarized AST string representation
    containing only classes, function signatures, and docstrings.
    This saves token context for agents when full implementation details are not needed.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        return f"Error reading file {filepath}: {e}"

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return f"Syntax error in {filepath}: {e}"

    summary = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            summary.append(f"class {node.name}:")
            docstring = ast.get_docstring(node)
            if docstring:
                summary.append(f'    """{docstring}"""')
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [a.arg for a in item.args.args]
                    summary.append(f"    def {item.name}({', '.join(args)}): ...")
        elif isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            summary.append(f"def {node.name}({', '.join(args)}):")
            docstring = ast.get_docstring(node)
            if docstring:
                summary.append(f'    """{docstring}"""')
            else:
                summary.append("    ...")

    return "\n".join(summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize Python files for token efficiency.")
    parser.add_argument("filepath", help="Path to the Python file to summarize.")
    args = parser.parse_args()

    result = summarize_python_file(args.filepath)
    print(result)
