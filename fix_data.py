import json
import re

def fix():
    with open("data.js", "r", encoding="utf-8") as f:
        text = f.read()

    match = re.search(r'const asteriskWorks = (\[.*\]);', text, flags=re.DOTALL)
    if not match:
        print("Could not find asteriskWorks array")
        return

    data_str = match.group(1)
    works = json.loads(data_str)

    for work in works:
        content = work.get("content", [])
        new_content = []
        for line in content:
            # Ignore standalone numbers (like page numbers)
            if re.match(r'^\d+$', line.strip()):
                continue
            
            # Remove embedded spaces that cause weird formatting
            line = re.sub(r'\s{2,}', '', line)
            # Remove trailing/leading spaces
            line = line.strip()
            if not line:
                continue

            if len(new_content) > 0:
                prev = new_content[-1]
                # If previous string does not end in a sentence-ending punctuation
                if not re.search(r'[。！？】”」]$', prev):
                    new_content[-1] = prev + line
                    continue
            
            new_content.append(line)
        work["content"] = new_content

    new_js = 'const asteriskWorks = ' + json.dumps(works, ensure_ascii=False, indent=2) + ';\n'
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(new_js)

    print("Successfully fixed data.js")

if __name__ == "__main__":
    fix()
