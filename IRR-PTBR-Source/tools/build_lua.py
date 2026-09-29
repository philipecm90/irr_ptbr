import json, os, importlib.util

W = r'C:\Users\PHILIP~1\AppData\Local\Temp\opencode'
OUT = r'C:\Games\Incursion.Red.River.v1.3.0.6\Test_C\Binaries\Win64\ue4ss\Mods\PTTranslator\Scripts\translations.lua'

kr_keys = json.load(open(os.path.join(W, 'corpus6.json'), encoding='utf-8'))

# base dictionaries
tr = {}
for f in ('tr_ui1.json', 'tr_desc.json', 'tr_extra.json'):
    tr.update(json.load(open(os.path.join(W, f), encoding='utf-8')))

# mission prefix translations
mtr = {}
for mn in ('tr_mission', 'tr_mission2'):
    spec = importlib.util.spec_from_file_location(mn, os.path.join(W, mn + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for attr in ('MISSION_TR', 'MISSION_TR2'):
        d = getattr(m, attr, None)
        if d:
            mtr.update(d)
# UI prefix translations
spec = importlib.util.spec_from_file_location('tr_kr_ui', os.path.join(W, 'tr_kr_ui.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
mtr.update(getattr(m, 'UI_TR', {}))
spec = importlib.util.spec_from_file_location('tr_kr2', os.path.join(W, 'tr_kr2.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
mtr.update(getattr(m, 'UI2', {}))
spec = importlib.util.spec_from_file_location('tr_kr3', os.path.join(W, 'tr_kr3.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
mtr.update(getattr(m, 'UI3', {}))
spec = importlib.util.spec_from_file_location('tr_kr4', os.path.join(W, 'tr_kr4.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
mtr.update(getattr(m, 'NARR', {}))
spec = importlib.util.spec_from_file_location('tr_game', os.path.join(W, 'tr_game.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
mtr.update(getattr(m, 'GAME', {}))
import tr_rules

# also load a manual PT dict for kr keys if present
manual = {}
mp = os.path.join(W, 'tr_kr.json')
if os.path.exists(mp):
    manual = json.load(open(mp, encoding='utf-8'))

import tr_items
out = {}
mmiss = 0
still = []
for k in kr_keys:
    v = manual.get(k) or tr.get(k)
    if v is None:
        cand = [p for p in mtr if k.startswith(p)]
        if cand:
            v = mtr[max(cand, key=len)]
    if v is None:
        v = tr_rules.rule_translate(k)
    if v is None:
        v = tr_items.translate_name(k)
    if v is None and ' for the ' in k:
        v = k.replace(' for the ', ' para a ')
    if v:
        out[k] = v
    else:
        mmiss += 1
        still.append(k)
print('mtr prefixes:', len(mtr), '| kr keys sem traducao:', mmiss)
json.dump(still, open(os.path.join(W, 'kr_still_missing.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# keep only entries that actually differ / are translatable
def esc(s):
    import re as _re
    s = _re.sub(r'</[A-Za-z]+>', '</>', s)   # jogo usa </> como fechamento
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as w:
    w.write('-- Incursion Red River PT-BR runtime translations\n')
    w.write('return {\n')
    for k in sorted(out):
        w.write('["%s"]="%s",\n' % (esc(k), esc(out[k])))
    w.write('}\n')
print('translations.lua entries:', len(out))
