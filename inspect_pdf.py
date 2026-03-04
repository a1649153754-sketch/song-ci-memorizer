import fitz

def inspect_pdf(pdf_path, out_path, num_pages=20):
    try:
        doc = fitz.open(pdf_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"Total pages: {len(doc)}\n")
            for i in range(min(num_pages, len(doc))):
                page_text = doc[i].get_text()
                f.write(f"--- Page {i+1} ---\n")
                f.write(page_text)
                f.write("\n" + "-" * 40 + "\n")
        print(f"Output written to {out_path}")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    inspect_pdf('宋词导读作品选（2026年春）.pdf', 'inspect_output.txt')
