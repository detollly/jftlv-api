import pdfplumber

input_file = "JFTLV.pdf"
output_file = "JFTLVraw.txt"

with pdfplumber.open(input_file) as pdf:
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Saved extracted text to {output_file}")