import pdfplumber
import docx


def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def parse_docx(file):

    doc = docx.Document(file)

    text = "\n".join([p.text for p in doc.paragraphs])

    return text
