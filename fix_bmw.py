import os

print("BMW Project - Final Fix Script")
print("="*40)

# Fix test_setup.py
f = 'test_setup.py'
txt = open(f, encoding='utf-8').read()
txt = txt.replace('client.messages.create', 'client.chat.completions.create')
txt = txt.replace('message.content[0].text', 'message.choices[0].message.content')
open(f, 'w', encoding='utf-8').write(txt)
print("Fixed: test_setup.py")

# Fix all pipeline files
files = [
    'pipelines/pipeline_1_llm_only.py',
    'pipelines/pipeline_2_basic_rag.py',
    'pipelines/pipeline_3_graphrag.py'
]

for f in files:
    txt = open(f, encoding='utf-8').read()
    txt = txt.replace('self.client.messages.create', 'self.client.chat.completions.create')
    txt = txt.replace('message.content[0].text', 'message.choices[0].message.content')
    txt = txt.replace('message.usage.input_tokens', 'message.usage.prompt_tokens')
    txt = txt.replace('message.usage.output_tokens', 'message.usage.completion_tokens')
    open(f, 'w', encoding='utf-8').write(txt)
    print(f"Fixed: {f}")

print("="*40)
print("ALL FILES FIXED! Ab test karo:")
print("python test_setup.py")
