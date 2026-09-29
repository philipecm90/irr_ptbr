import struct
import ahocorasick

def rfstring(d, o):
    n = struct.unpack_from('<i', d, o)[0]; o += 4
    if n == 0: return '', o
    if n < 0:
        n = -n
        return d[o:o+2*(n-1)].decode('utf-16-le', 'replace'), o + 2*n
    return d[o:o+(n-1)].decode('latin1'), o + n

def parse_uasset(d):
    totalheader = struct.unpack_from('<I', d, 44)[0]
    _, o = rfstring(d, 52)
    o += 4
    namecount = struct.unpack_from('<i', d, o)[0]; o += 4
    nameoffset = struct.unpack_from('<i', d, o)[0]; o += 4
    o += 16
    exportcount = struct.unpack_from('<i', d, o)[0]; o += 4
    exportoffset = struct.unpack_from('<i', d, o)[0]; o += 4
    return totalheader, exportcount, exportoffset

def parse_exports(d, exportoffset, exportcount):
    ex = []
    o = exportoffset
    for _ in range(exportcount):
        st = o
        o += 16 + 8 + 4
        ss = struct.unpack_from('<q', d, o)[0]; sspos = o; o += 8
        so = struct.unpack_from('<q', d, o)[0]; sopos = o; o += 8
        o = st + 96
        ex.append(dict(serialsize=ss, serialoffset=so, sspos=sspos, sopos=sopos))
    return ex

def encode_fstring(s):
    if all(ord(c) < 0x80 for c in s):
        b = s.encode('latin1')
        return struct.pack('<i', len(b)+1) + b + b'\x00'
    b = s.encode('utf-16-le')
    return struct.pack('<i', -(len(s)+1)) + b + b'\x00\x00'

def encode_utf16(s):
    return struct.pack('<i', -(len(s)+1)) + s.encode('utf-16-le') + b'\x00\x00'


class Matcher:
    def __init__(self, translations):
        self.tr = translations
        self.ansi = ahocorasick.Automaton()
        self.utf16 = ahocorasick.Automaton()
        n_ansi = n_u = 0
        for k in translations:
            try:
                kb = k.encode('latin1')
            except UnicodeEncodeError:
                kb = None
            if kb:
                self.ansi.add_word(kb.decode('latin1'), k); n_ansi += 1
            pat = struct.pack('<i', -(len(k)+1)) + k.encode('utf-16-le') + b'\x00\x00'
            self.utf16.add_word(pat.decode('latin1'), k); n_u += 1
        if n_ansi:
            self.ansi.make_automaton()
        if n_u:
            self.utf16.make_automaton()
        self.n_ansi = n_ansi; self.n_utf16 = n_u

    def spans(self, uexp):
        n = len(uexp)
        text = uexp.decode('latin1')
        cand = []  # (s0, s1, pattern, key)
        # UTF-16 (full pattern, unambiguous)
        if self.n_utf16:
            for end, k in self.utf16.iter(text):
                patlen = 4 + len(k) * 2 + 2
                s0 = end - patlen + 1
                cand.append((s0, s0 + patlen, 'U', k))
        # ANSI / ambiguous
        if self.n_ansi:
            for end, k in self.ansi.iter(text):
                kb = k.encode('latin1'); L = len(kb)
                i = end - L + 1
                if i + L >= n or uexp[i+L] != 0:
                    continue
                if i >= 4 and struct.unpack_from('<i', uexp, i-4)[0] == L + 1:
                    cand.append((i-4, i+L+1, 'A', k))
                elif i == 0 or not chr(uexp[i-1]).isalnum():
                    cand.append((i, i+L, 'B', k))
        if not cand:
            return []
        # longest key first; for ties, earlier position first
        cand.sort(key=lambda c: (-len(c[3]), c[0]))
        taken = bytearray(n)
        spans = []
        for s0, s1, pattern, k in cand:
            if s0 < 0 or s1 > n:
                continue
            if any(taken[s0:s1]):
                continue
            if pattern == 'B':
                import unicodedata as _ud
                tb = _ud.normalize('NFKD', self.tr[k]).encode('ascii', 'ignore')
                if len(tb) > (s1 - s0):
                    continue
            for p in range(s0, s1):
                taken[p] = 1
            spans.append((s0, s1, pattern, k))
        spans.sort()
        return spans

    def patch(self, uexp, uasset):
        spans = self.spans(uexp)
        if not spans:
            return None
        out = bytearray()
        prev = 0
        deltas = []
        for s0, s1, pattern, k in spans:
            out += uexp[prev:s0]
            tr = self.tr[k]
            if pattern == 'A':
                rep = encode_fstring(tr)
            elif pattern == 'U':
                rep = encode_utf16(tr)
            else:
                import unicodedata as _ud
                span = s1 - s0
                tb = _ud.normalize('NFKD', tr).encode('ascii', 'ignore')
                if len(tb) > span:
                    tb = tb[:span]
                tb = tb + b' ' * (span - len(tb))
                rep = tb
            out += rep
            deltas.append((s0, len(rep) - (s1 - s0), pattern))
            prev = s1
        out += uexp[prev:]
        new_uexp = bytes(out)

        totalheader, exportcount, exportoffset = parse_uasset(uasset)
        exports = parse_exports(uasset, exportoffset, exportcount)
        ua = bytearray(uasset)
        for e in exports:
            so = e['serialoffset']; ss = e['serialsize']
            before = sum(d for pos, d, _ in deltas if totalheader + pos < so)
            inside = sum(d for pos, d, _ in deltas if so <= totalheader + pos < so + ss)
            struct.pack_into('<q', ua, e['sopos'], so + before)
            struct.pack_into('<q', ua, e['sspos'], ss + inside)
        return bytes(ua), new_uexp, deltas
