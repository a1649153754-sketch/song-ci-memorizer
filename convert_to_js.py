import json

def convert_to_js(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Works are separated by '========================================'
    raw_works = content.split('========================================')
    
    works_data = []
    
    for raw in raw_works:
        lines = [line.strip() for line in raw.strip().split('\n') if line.strip()]
        if not lines:
            continue
            
        # First line is usually the title.
        title = lines[0]
        # The rest is the content.
        body = lines[1:]
        
        # Sometimes there might be a subtitle or author mixed in if our extraction wasn't perfect,
        # but the simple structure is title + body.
        works_data.append({
            'title': title,
            'content': body
        })

    # Write as a JavaScript file that assigns this to a global variable
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("const asteriskWorks = ")
        json.dump(works_data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
        
    print(f"Converted {len(works_data)} works to JS.")

if __name__ == "__main__":
    convert_to_js('asterisk_works.txt', 'data.js')
