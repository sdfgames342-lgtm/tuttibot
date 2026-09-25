import json
with open('lexico.json', 'r') as f:
    lex = json.load(f)
lex['108'] = {'es': 'pescado', 'en': 'fish', 'pt': 'peixe'}
with open('lexico.json', 'w') as f:
    json.dump(lex, f, indent=2)
print("✅ Palabra 'pescado' añadida al léxico.")