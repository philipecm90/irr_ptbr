import os, json, re, sys, time
import repak
import patchlib

PAK = r"C:\Games\Incursion.Red.River.v1.3.0.6\Test_C\Content\Paks"
WORK = r"C:\Users\PHILIP~1\AppData\Local\Temp\opencode"
OUTPAK = os.path.join(WORK, "pakchunk999-IRRPTBR_P.pak")

# ---- load translations ----
tr = {}
for f in os.environ.get('IRRDICTS', 'tr_ui1.json,tr_desc.json,tr_extra.json').split(','):
    tr.update(json.load(open(os.path.join(WORK, f), encoding='utf-8')))

# ---- mission prefix-based translations (UTF-16 strings) ----
import importlib.util
_mtr = {}
for _modname in ('tr_mission', 'tr_mission2'):
    _spec = importlib.util.spec_from_file_location(_modname, os.path.join(WORK, _modname + '.py'))
    _m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
    _mtr.update(getattr(_m, 'MISSION_TR', {}) or {})
    _mtr.update(getattr(_m, 'MISSION_TR2', {}) or {})
_c6 = json.load(open(os.path.join(WORK, 'corpus6.json'), encoding='utf-8'))
_c6keys = list(_c6.keys())
_miss = 0
for prefix, pt in _mtr.items():
    matches = [k for k in _c6keys if k.startswith(prefix)]
    if len(matches) != 1:
        matches2 = [k for k in _c6keys if prefix in k]
        if len(matches2) == 1:
            matches = matches2
    if len(matches) == 1:
        tr[matches[0]] = pt
    else:
        _miss += 1
        if _miss <= 30:
            print('  MISS-PREFIX', repr(prefix[:55]), '->', len(matches))
print('mission prefixes aplicados:', len(_mtr) - _miss, 'de', len(_mtr))

# ---- FANG Assignment (formulaico) ----
import re as _re
_fang = _re.compile(r'^FANG Assignment <strong>([A-Z0-9_]+)</>: <italic>(.*)</>$')
_cond = {
    'Eliminate the targets with the assigned condition.': 'Elimine os alvos com a condição atribuída.',
    'Complete the listed operations while in-raid.': 'Conclua as operações listadas durante a raid.',
    'Retrieve all evidence at marked areas and deliver them.': 'Recupere todas as evidências nas áreas marcadas e entregue-as.',
}
_nf = 0
for _k in _c6keys:
    _m = _fang.match(_k)
    if _m:
        tr[_k] = 'Designação da FANG <strong>%s</>: <italic>%s</>' % (_m.group(1), _cond.get(_m.group(2), _m.group(2)))
        _nf += 1
print('FANG assignments:', _nf)

# ---- item name rules ----
def tr_name(name):
    n = name
    for suf, pt in [
        ('Armored Rig', 'Colete tático blindado'),
        ('Plate Carrier', 'Colete balístico'),
        ('Pistol Grip', 'Empunhadura da pistola'),
        ('Vertical Foregrip', 'Empunhadura frontal vertical'),
        ('Vertical Grip', 'Empunhadura vertical'),
        ('Foregrip', 'Empunhadura frontal'),
        ('Flash Hider', 'Apagador de chamas'),
        ('Muzzle Brake', 'Freio de boca'),
        ('Muzzle Device', 'Dispositivo de bocal'),
        ('Gas Block', 'Bloco de gás'),
        ('Gas Tube', 'Tubo de gás'),
        ('Dust Cover', 'Tampa antipoeira'),
        ('Buffer Tube', 'Tubo de recuo'),
        ('Buffertube', 'Tubo de recuo'),
        ('Buttstock', 'Coronha'),
        ('Handguard', 'Guarda-mão'),
        ('Hanguard', 'Guarda-mão'),
        ('Handguard.', 'Guarda-mão.'),
        ('Silencer', 'Supressor'),
        ('Suppressor', 'Supressor'),
        ('Magazine', 'Carregador'),
        ('Receiver', 'Receptor'),
        ('Backpack', 'Mochila'),
        ('Helmet', 'Capacete'),
        ('Chassis', 'Chassi'),
        ('Canteen', 'Cantil'),
        ('Bandage', 'Atadura'),
        ('Compass', 'Bússola'),
        ('Camera', 'Câmera'),
        ('Grenade', 'Granada'),
        ('Safe Key', 'Chave do cofre'),
        ('Key', 'Chave'),
        ('Scope', 'Mira telescópica'),
        ('Sight', 'Mira'),
        ('Slide', 'Corrediça'),
        ('Stock', 'Coronha'),
        ('Barrel', 'Cano'),
        ('Rail', 'Trilho'),
        ('Mount', 'Suporte'),
        ('Grip', 'Empunhadura'),
        ('Mag', 'Carregador'),
        ('Rig', 'Colete tático'),
        ('Book', 'Livro'),
        ('Cigar', 'Charuto'),
        ('Cigarettes', 'Cigarros'),
    ]:
        if n == suf:
            return pt
        if n.endswith(' ' + suf):
            base = n[:-len(suf)-1]
            return f"{pt} {base}"
        if n.endswith(' ' + suf + '.'):
            base = n[:-len(suf)-2]
            return f"{pt} {base}."
    return None

# ---- gather corpus file set ----
corpus = json.load(open(os.path.join(WORK, 'corpus4.json'), encoding='utf-8'))
uexp_paths = set()
for k, fs in corpus.items():
    for f in fs:
        uexp_paths.add(f)
# add all files seen by the utf16 scan (covers files with only UTF-16 text)
ALLOWED_PREFIXES = ('ID_', 'W_', 'WB_', 'DT_', 'DA_', 'BP_', 'E_', 'S_')
def _allowed(name):
    b = name.rsplit('/', 1)[-1]
    return b.startswith(ALLOWED_PREFIXES)
try:
    _c6f = json.load(open(os.path.join(WORK, 'corpus6.json'), encoding='utf-8'))
    for k, fs in _c6f.items():
        for f in fs:
            if _allowed(f):
                uexp_paths.add(f)
except Exception as e:
    print('corpus6 skip', e)

# add item names via rules
idname = json.load(open(os.path.join(WORK, 'work2.json'), encoding='utf-8'))['idname']
for nm in idname:
    t = tr_name(nm)
    if t:
        tr.setdefault(nm, t)

print('translation entries:', len(tr))
matcher = patchlib.Matcher(tr)
print('matcher: ansi=%d utf16=%d' % (matcher.n_ansi, matcher.n_utf16))

# ---- open pak readers ----
readers = {}
for f in sorted(os.listdir(PAK)):
    if f.lower().endswith('.pak') and 'IRRPTBR' not in f:
        readers[f] = repak.PakBuilder().reader(os.path.join(PAK, f))

# map uexp path -> reader
path_reader = {}
for f, r in readers.items():
    for name in r.files():
        if name in uexp_paths:
            path_reader[name] = (f, r)

print('packages to scan:', len(path_reader))

outputs = {}
stats = {'A': 0, 'B': 0}
t0 = time.time()
done = 0
for uexp_path, (pakname, r) in path_reader.items():
    uasset_path = uexp_path[:-5] + '.uasset'
    try:
        uexp = r.get(uexp_path)
        uasset = r.get(uexp_path[:-5] + '.uasset')
    except Exception as e:
        continue
    if len(uexp) > 4_000_000:
        continue
    try:
        res = matcher.patch(uexp, uasset)
    except Exception as e:
        print('  PATCH-ERR', uexp_path, repr(e))
        continue
    if res is None:
        continue
    nua, nuexp, deltas = res
    outputs[uasset_path] = nua
    outputs[uexp_path] = nuexp
    for _, _, pat in deltas:
        stats[pat] = stats.get(pat, 0) + 1
    done += 1
    if done % 200 == 0:
        print('  patched', done, 'pkgs;', len(outputs), 'files; %.0fs' % (time.time()-t0), flush=True)

print('patched packages:', done, 'output files:', len(outputs), 'patterns:', stats, '%.0fs' % (time.time()-t0))

# ---- write mod pak ----
w = repak.PakBuilder().writer(OUTPAK, version=repak.Version.V11, mount_point="../../../")
for path, data in outputs.items():
    w.write_file(path, data, compress=True)
w.write_index()
print('wrote', OUTPAK, os.path.getsize(OUTPAK), 'bytes')
