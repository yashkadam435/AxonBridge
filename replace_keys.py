import os, re
key_regex = re.compile(r'gsk_[A-Za-z0-9]+')
for root, _, files in os.walk('.'):
    if '.git' in root: continue
    for f in files:
        if f.endswith(('.py', '.yml')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                new_content = key_regex.sub('your_groq_api_key_here', content)
                if content != new_content:
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    print(f'Replaced in {path}')
            except Exception as e:
                pass
