import sys
import fitz # PyMuPDF
import os

def slice_pdf(input_path, output_path, start_page, end_page):
    # PyMuPDF uses 0-based indexing.
    # The markdown page headers are 1-based internal book pages, 
    # but let's assume they map to the physical PDF pages, or we just extract the range.
    doc = fitz.open(input_path)
    new_doc = fitz.open()
    
    # Ensure bounds
    start = max(0, start_page - 1)
    end = min(len(doc) - 1, end_page - 1)
    
    new_doc.insert_pdf(doc, from_page=start, to_page=end)
    new_doc.save(output_path)
    print(f"Saved {output_path} (Pages {start+1}-{end+1})")

if __name__ == "__main__":
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    start_p = int(sys.argv[3])
    end_p = int(sys.argv[4])
    slice_pdf(input_pdf, output_pdf, start_p, end_p)
