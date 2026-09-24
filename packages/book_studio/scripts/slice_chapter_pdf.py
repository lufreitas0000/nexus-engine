import os
import glob
import subprocess
import sys

def get_chapter_pages(chapter_num):
    md_files = glob.glob(f"data/06_final_md/{chapter_num}_*.md")
    if not md_files:
        return None, None
    
    pages = []
    for f in md_files:
        with open(f, 'r') as file:
            for line in file:
                if line.startswith("page:"):
                    try:
                        pages.append(int(line.split(":")[1].strip()))
                    except:
                        pass
                    break
    if not pages:
        return None, None
    
    # Internal book pages map to physical PDF pages by an offset. 
    # From previous subagents, physical page = internal page + 12 (roughly).
    # Let's extract exactly the range in the metadata + a small buffer.
    start_page = min(pages) + 12
    end_page = max(pages) + 12 + 10 # Buffer of 10 pages to be safe
    return start_page, end_page

def main():
    chapter_num = sys.argv[1].zfill(2)
    start_p, end_p = get_chapter_pages(chapter_num)
    
    if start_p is None:
        print(f"No pages found for chapter {chapter_num}")
        return
        
    input_pdf = "data/01_raw/gordon_baym_qm.pdf"
    output_pdf = f"data/01_raw/chapter_{chapter_num}_sliced.pdf"
    
    cmd = f"qpdf --empty --pages {input_pdf} {start_p}-{end_p} -- {output_pdf}"
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)
    print(f"Created {output_pdf}")

if __name__ == "__main__":
    main()
