from nexus_schema.models import Document, Section, Paragraph, Metadata

def markdown_to_document(markdown: str) -> Document:
    sections = []
    current_section = Section(title=None, content=[])
    
    lines = markdown.split('\n')
    buffer = []

    def flush_buffer():
        if buffer:
            text = " ".join(buffer).strip()
            if text:
                current_section.content.append(Paragraph(text=text))
            buffer.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            flush_buffer()
            # If the current section has content or a title, save it
            if current_section.title is not None or current_section.content:
                sections.append(current_section)
            
            # Start new section
            # remove all leading '#' and spaces
            title = stripped.lstrip('#').strip()
            current_section = Section(title=title, content=[])
        elif not stripped:
            # empty line means paragraph break
            flush_buffer()
        else:
            buffer.append(stripped)
            
    flush_buffer()
    if current_section.title is not None or current_section.content:
        sections.append(current_section)
        
    return Document(metadata=Metadata(), sections=sections)


def document_to_markdown(doc: Document) -> str:
    lines = []
    
    # Optional YAML frontmatter from metadata could go here
    # lines.append(f"# {doc.metadata.title}") ...
    
    for section in doc.sections:
        if section.title:
            lines.append(f"# {section.title}")
            lines.append("")
            
        for p in section.content:
            lines.append(p.text)
            lines.append("")
            
    return "\n".join(lines)
