# Markdown to EPUB Conversion Specifications

## 1. Pre-processing: Obsidian Wikilink Resolution
The Obsidian structure utilizes non-standard Wikilinks of the form `[[Target]]` or `[[Target|Alias]]`. Before passing the input to Pandoc, a regex substitution must execute to map these internal references to standard Markdown hyperlinks.

Let $S$ be the input string. The transformation applies the following regex patterns sequentially:
1. Aliased links: `\[\[(.*?)\|(.*?)\]\]` $\to$ `[$2]($1.md)`
2. Standard links: `\[\[(.*?)\]\]` $\to$ `[$1]($1.md)`

## 2. Pandoc AST Compilation Pipeline
Pandoc operates by parsing the input text into a unified Abstract Syntax Tree (AST) before generating the output format. The system process invocation will execute the following command structure:

`pandoc {input} -f markdown -t epub3 --mathml -o {output}`

The execution pipeline consists of three fundamental phases:
1. **Reader (`-f markdown`)**: Parses the pre-processed input string into the intermediate Pandoc AST.
2. **Filter (`--mathml`)**: Traverses the AST and maps LaTeX mathematical environments into MathML nodes, ensuring valid mathematical rendering within the strict EPUB3 standard.
3. **Writer (`-t epub3`)**: Serializes the AST into the final EPUB3 container structure.
