import PyPDF2

def process_file(file):
    if file and file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    elif file:
        return file.read().decode("utf-8").strip()
    return ""