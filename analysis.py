import json
import re

def analyze():
    # 1. Parse TOC from inspect_output.txt to get authors and all asterisk works
    with open('inspect_output.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_toc = False
    current_author = "佚名"
    toc_asterisks = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('--- Page 2 ---'):
            in_toc = True
        if stripped.startswith('--- Page 14 ---'):
            break
            
        if in_toc:
            match = re.search(r'^(\*?)(.*?)\s*\.{3,}\s*\d+', stripped)
            if match:
                is_ast = match.group(1) == '*'
                title_full = match.group(2).strip()
                
                m2 = re.search(r'^(.*?)（(.*?)）$', title_full)
                if m2: # It is a work
                    work_title = m2.group(1).strip()
                    first_line = m2.group(2).strip()
                    if is_ast:
                        toc_asterisks.append({
                            'title': work_title,
                            'first_line': first_line,
                            'author': current_author
                        })
                else: # It is an author or category
                    # Exclude categories like "唐五代词选", "两宋词选"
                    if not title_full.endswith("词选") and "曲子词" not in title_full:
                        current_author = title_full
                    elif "曲子词" in title_full:
                        current_author = "敦煌曲子词"
                        
    print(f"Total asterisk works in TOC: {len(toc_asterisks)}")
    
    # 2. Load data.js
    with open('data.js', 'r', encoding='utf-8') as f:
        js_text = f.read()
    match = re.search(r'const asteriskWorks = (\[.*\]);', js_text, flags=re.DOTALL)
    data_works = json.loads(match.group(1))
    
    print(f"Total asterisk works in data.js: {len(data_works)}")
    
    # Check for merged works by length or presence of other titles inside content
    for idx, work in enumerate(data_works):
        content_str = "".join(work['content'])
        print(f"[{idx}] {work['title']}: {len(content_str)} chars")
        if len(content_str) > 200: # usually poems are short, if >200 maybe merged?
            print(f"  --> VERY LONG: {content_str[:50]}...")
            
    print("\n--- TOC vs Data ---")
    data_titles = [w['title'] for w in data_works]
    
    missing_from_data = []
    for toc in toc_asterisks:
        if toc['title'] not in data_titles:
            missing_from_data.append(toc)
            
    with open('out.txt', 'w', encoding='utf-8') as out:
        out.write(f"\nMissing from data.js ({len(missing_from_data)}):\n")
        for m in missing_from_data:
            out.write(f"  {m['title']} ({m['first_line']}) by {m['author']}\n")
            
        # Find merged items (where a title from missing exists inside the content of a data_works item)
        for m in missing_from_data:
            for dw in data_works:
                content_str = "".join(dw['content'])
                if m['title'] in content_str or m['first_line'] in content_str:
                    out.write(f"\nPossible merged: {m['title']} might be inside {dw['title']}\n")

if __name__ == '__main__':
    analyze()
