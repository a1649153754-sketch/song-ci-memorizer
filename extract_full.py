import fitz
import re

def parse_and_extract(pdf_path):
    doc = fitz.open(pdf_path)
    lines = []
    # Add page markers for each page
    for i in range(len(doc)):
        lines.append(f"--- Page {i+1} ---")
        text = doc[i].get_text()
        for ln in text.split('\n'):
            lines.append(ln)
        
    toc_items = []
    
    in_toc = False
    in_body = False
    
    for line in lines:
        stripped = line.strip()
        
        # Detect TOC pages
        if stripped.startswith('--- Page 2 ---'):
            in_toc = True
        if stripped.startswith('--- Page 14 ---'): # End of TOC
            in_toc = False
            in_body = True
            
        if in_toc:
            # Match TOC entries
            match = re.search(r'^(\*?)(.*?)\s*\.{3,}\s*\d+$', stripped)
            if match:
                is_ast = match.group(1) == '*'
                title_full = match.group(2).strip()
                
                # Check if it's a work (has parentheses)
                m2 = re.search(r'^(.*?)（(.*?)）$', title_full)
                if m2:
                    toc_items.append({
                        'type': 'work',
                        'title': m2.group(1).strip(),
                        'first_line': m2.group(2).strip(),
                        'is_asterisk': is_ast,
                        'content': []
                    })
                else:
                    toc_items.append({
                        'type': 'other',
                        'title': title_full
                    })
                    
    print(f"Parsed {len(toc_items)} items from TOC.")
    works_count = sum(1 for x in toc_items if x['type'] == 'work')
    print(f"Of which {works_count} are works.")
    
    # Process body
    # We will join all lines after TOC (page 14 onwards) into a single string
    body_lines = []
    in_body = False
    for line in lines:
        if line.startswith('--- Page 14 ---'):
            in_body = True
        if in_body and not line.startswith('--- Page'):
            body_lines.append(line)
    
    body_text = '\n'.join(body_lines)
    
    # First, find start pos of all works
    for i, item in enumerate(toc_items):
        item['start_pos'] = -1
        if item['type'] == 'work':
            search_key = item['first_line'][:5]
            pos = body_text.find(search_key)
            if pos != -1:
                # the "actual" start is the title, which appears before first_line
                title_pos = body_text.rfind(item['title'], max(0, pos - 80), pos)
                item['start_pos'] = title_pos if title_pos != -1 else pos

    # Now infer the start pos of 'other' items by looking for their title between the known works
    for i, item in enumerate(toc_items):
        if item['type'] == 'other':
            # find previous known pos
            prev_pos = 0
            for j in range(i-1, -1, -1):
                if toc_items[j]['start_pos'] != -1:
                    prev_pos = toc_items[j]['start_pos']
                    break
            # find next known pos
            next_pos = len(body_text)
            for j in range(i+1, len(toc_items)):
                if toc_items[j]['start_pos'] != -1:
                    next_pos = toc_items[j]['start_pos']
                    break
            
            # search for item['title'] strictly between prev_pos and next_pos
            pos = body_text.find(item['title'], prev_pos, next_pos)
            if pos != -1:
                item['start_pos'] = pos

    # Ensure monotonic increasing positions (if any item failed to find or is out of order, filter it out for boundary purposes)
    valid_items = [it for it in toc_items if it['start_pos'] != -1]
    valid_items.sort(key=lambda x: x['start_pos'])
    
    ast_file = open('asterisk_works.txt', 'w', encoding='utf-8')
    nor_file = open('normal_works.txt', 'w', encoding='utf-8')
    
    extracted_count = 0
    for idx, item in enumerate(valid_items):
        if item['type'] == 'work':
            start_pos = item['start_pos']
            end_pos = valid_items[idx+1]['start_pos'] if idx + 1 < len(valid_items) else len(body_text)
            content = body_text[start_pos:end_pos].strip()
            
            if item['is_asterisk']:
                ast_file.write(content + "\n" + "="*40 + "\n")
            else:
                nor_file.write(content + "\n" + "="*40 + "\n")
            extracted_count += 1
            
    ast_file.close()
    nor_file.close()
    
    missing = works_count - extracted_count
    print(f"Extracted {extracted_count} works. Missing {missing}.")

    print("Done writing to files.")

if __name__ == '__main__':
    parse_and_extract('宋词导读作品选（2026年春）.pdf')
