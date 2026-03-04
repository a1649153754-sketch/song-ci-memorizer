import fitz
import re

def parse_toc(doc):
    asterisk_works = []
    normal_works = []
    
    # TOC seems to be from page 1 to 12 (0-indexed)
    for i in range(1, 13):
        text = doc[i].get_text()
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Match lines like "*望江南（天上月） ............. 2" or "菩萨蛮（平林漠漠烟如织） ........ 3"
            # It might have dots and page numbers at the end.
            if re.search(r'\.{3,}\s*\d+$', line):
                is_asterisk = line.startswith('*')
                # Remove asterisk
                clean_line = line.lstrip('*')
                # Extract title and first line part before dots
                match = re.search(r'^(.*?)\s*\.{3,}', clean_line)
                if match:
                    title_part = match.group(1).replace(' ', '')
                    if is_asterisk:
                        asterisk_works.append(title_part)
                    else:
                        normal_works.append(title_part)
    return asterisk_works, normal_works

if __name__ == "__main__":
    doc = fitz.open('宋词导读作品选（2026年春）.pdf')
    a_works, n_works = parse_toc(doc)
    print(f"Found {len(a_works)} asterisk works and {len(n_works)} normal works.")
    print("Sample asterisk:", a_works[:5])
    print("Sample normal:", n_works[:5])
