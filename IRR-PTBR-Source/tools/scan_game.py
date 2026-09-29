import repak, os, re, struct, json, time

PAK = r"C:\Games\Incursion.Red.River.v1.3.0.6\Test_C\Content\Paks"
OUT = r"C:\Users\PHILIP~1\AppData\Local\Temp\opencode\corpus_game.json"

# TODAS as pastas com texto do proprio jogo
TARGETS = [
    'Test_C/Content/Blueprints/',
    'Test_C/Content/Characters/',
    'Test_C/Content/ThirdParty/',
    'Test_C/Config/',
]

readers = []
for f in sorted(os.listdir(PAK)):
    if f.lower().endswith('.pak') and 'IRRPTBR' not in f:
        readers.append((f, repak.PakBuilder().reader(os.path.join(PAK, f))))

def texty(name):
    return any(name.startswith(t) for t in TARGETS)

def is_text(s):
    if len(s) < 3 or len(s) > 4000:
        return False
    if not re.search(r'[A-Za-z]{3}', s):
        return False
    for c in s:
        o = ord(c)
        if o < 32 and c not in '\t\r\n':
            return False
    return True

def scan(data):
    out = set()
    n = len(data)
    i = 0
    while i < n - 4:
        L = struct.unpack_from('<i', data, i)[0]
        if 3 < L < 4000 and i + 4 + L <= n:
            chunk = data[i+4:i+4+L]
            if chunk[-1] == 0:
                try:
                    s = chunk[:-1].decode('ascii')
                    if is_text(s):
                        out.add(s)
                except Exception:
                    pass
        elif -4000 < L < -3 and i + 4 + 2*(-L) <= n:
            nb = 2 * (-L)
            if data[i+4+nb-2:i+4+nb] == b'\x00\x00':
                try:
                    s = data[i+4:i+4+nb-2].decode('utf-16-le')
                    if is_text(s):
                        out.add(s)
                except Exception:
                    pass
        i += 1
    return out

strings = {}
t0 = time.time()
count = 0
for pakname, r in readers:
    for name in r.files():
        if not name.endswith('.uexp') or not texty(name):
            continue
        try:
            data = r.get(name)
        except Exception:
            continue
        count += 1
        for s in scan(data):
            strings.setdefault(s, set()).add(name)
    print('  ', pakname, count, len(strings), '%.0fs' % (time.time()-t0), flush=True)

print('scanned', count, 'files;', len(strings), 'unique strings; %.0fs' % (time.time()-t0))
with open(OUT, 'w', encoding='utf-8') as w:
    json.dump({k: sorted(v) for k, v in sorted(strings.items())}, w, ensure_ascii=False, indent=0)
print('wrote', OUT)
