import json
import re

def fix_data():
    # 1. Parse TOC to get authors
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
                if m2:
                    if is_ast:
                        toc_asterisks.append({
                            'title': m2.group(1).strip(),
                            'first_line': m2.group(2).strip(),
                            'author': current_author
                        })
                else:
                    if not title_full.endswith("词选") and "曲子词" not in title_full:
                        current_author = title_full
                    elif "曲子词" in title_full:
                        current_author = "敦煌曲子词"

    # 2. Extract normal_works text for 满庭芳 (山抹微云)
    with open('normal_works.txt', 'r', encoding='utf-8') as f:
        normal_text = f.read()
    
    man_ting_fang_idx = normal_text.find("山抹微云，天连衰草")
    end_idx = normal_text.find("【附录】", man_ting_fang_idx) if "【附录】" in normal_text[man_ting_fang_idx:man_ting_fang_idx+500] else normal_text.find("=====", man_ting_fang_idx)
    raw_content = normal_text[man_ting_fang_idx:end_idx].strip()
    
    # split into content array
    mtf_lines = [c.strip() for c in re.split(r'\s{2,}|\n', raw_content) if c.strip()]
    if not mtf_lines:
        mtf_lines = ["山抹微云，天连衰草，画角声断谯门。暂停征棹，聊共引离尊。多少蓬莱旧事，空回首、烟霭纷纷。斜阳外，寒鸦数点，流水绕孤村。", "销魂。当此际，香囊暗解，罗带轻分。谩赢得、青楼薄幸名存。此去何时见也，襟袖上、空惹啼痕。伤情处，高城望断，灯火已黄昏。"]

    # 3. Load data.js
    with open('data.js', 'r', encoding='utf-8') as f:
        js_text = f.read()
        
    match = re.search(r'const asteriskWorks = (\[.*?\]);(.*?)$', js_text, flags=re.DOTALL)
    data_works = json.loads(match.group(1))
    rest_of_file = match.group(2)
    
    # 4. Process and Fix
    # Fuzzy match function for assigning authors
    def get_author(work):
        t = work['title']
        if "半死桐" in t: return "贺铸"
        if "横塘路" in t: return "贺铸"
        if "暗香" in t: return "姜夔"
        if "一丛花令" in t: return "张先"
        
        # Exact match or substring matching first_line
        content_str = "".join(work['content'])
        for item in toc_asterisks:
            if item['title'] == t or item['title'] in t:
                return item['author']
            if item['first_line'] in content_str:
                return item['author']
        return "佚名"

    new_works = []
    
    for w in data_works:
        w['author'] = get_author(w)
        
        if "暗香" in w['title'] and "疏影" in w['title']:
            w['title'] = "暗香"
            w['author'] = "姜夔"
            new_works.append(w)
            
        elif w['title'] == "一丛花令":
            # Need to split out 天仙子
            content_list = []
            tian_content = []
            found_tian = False
            for line in w['content']:
                if '天仙子' in line or '水调' in line:
                    found_tian = True
                    # Clean up the line:
                    if line.startswith("天仙子"):
                        tian_content.append(line.replace("天仙子", "").strip())
                    else:
                        tian_content.append(line)
                else:
                    if found_tian:
                        tian_content.append(line)
                    else:
                        content_list.append(line)
                        
            w['content'] = [x for x in content_list if x.strip()]
            new_works.append(w)
            
            # create 天仙子
            new_works.append({
                'title': '天仙子',
                'author': '张先',
                'content': [x for x in tian_content if x.strip()]
            })
            print(f"Split 天仙子 with content {tian_content}")
            
        else:
            new_works.append(w)
            
    # Add 满庭芳
    new_works.append({
        'title': '满庭芳',
        'author': '秦观',
        'content': mtf_lines
    })
    
    # Check if we have 88 works now (86 + Tianxianzi + Mantingfang = 88 items)
    print(f"Total new works count: {len(new_works)}")

    # 5. Write out
    new_js = f"const asteriskWorks = {json.dumps(new_works, ensure_ascii=False, indent=2)};\n{rest_of_file}"
    with open('data_new.js', 'w', encoding='utf-8') as f:
        f.write(new_js)

if __name__ == '__main__':
    fix_data()
