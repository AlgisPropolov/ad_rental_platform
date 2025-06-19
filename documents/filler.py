from docx import Document

def fill_template(template_path, output_path, data: dict):
    doc = Document(template_path)
    for p in doc.paragraphs:
        for key, value in data.items():
            p.text = p.text.replace(f"{{{{{key}}}}}", str(value))
    doc.save(output_path)
