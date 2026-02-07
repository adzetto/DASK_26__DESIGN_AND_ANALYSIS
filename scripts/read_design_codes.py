"""
Read and extract text from design code PDFs
"""
import pdfplumber
import os
import sys
from pathlib import Path

# Set UTF-8 encoding for console output
sys.stdout.reconfigure(encoding='utf-8')

WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

pdf_dir = 'design_codes'
files = sorted(os.listdir(pdf_dir))

# Also save to file for review
output_file = open('results/design_codes_extracted.txt', 'w', encoding='utf-8')

def output(text):
    print(text)
    output_file.write(text + '\n')

for f in files:
    if f.endswith('.pdf'):
        path = os.path.join(pdf_dir, f)
        output("\n" + "=" * 80)
        output(f"FILE: {f}")
        output("=" * 80)
        
        try:
            with pdfplumber.open(path) as pdf:
                output(f"Page count: {len(pdf.pages)}")
                
                # Extract first pages to understand structure
                max_pages = min(20, len(pdf.pages))
                for i in range(max_pages):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text:
                        output(f"\n--- Page {i+1} ---")
                        # Limit output per page
                        if len(text) > 5000:
                            output(text[:5000] + "\n... [truncated]")
                        else:
                            output(text)
        except Exception as e:
            output(f"Error reading {f}: {e}")

print("\n" + "=" * 80)
print("PDF EXTRACTION COMPLETE")
print("=" * 80)
