import PyPDF2

pdf_path = "1768227625.pdf"

with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    print(f"Total pages: {len(pdf_reader.pages)}\n")
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        print(f"--- PAGE {page_num + 1} ---")
        print(text)
        print("\n")
