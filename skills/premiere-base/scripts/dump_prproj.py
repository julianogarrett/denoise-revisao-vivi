#!/usr/bin/env python3
"""Dump OFFLINE de uma sequência direto do .prproj (sem Premiere, sem Bridge).

Serve para comparar versões: o autosave de quando o Claude parou x o projeto
depois que o Juliano mexeu.

  python3 dump_prproj.py PROJETO.prproj                 -> lista as sequências
  python3 dump_prproj.py PROJETO.prproj "Nome seq" > a.tsv

Saída TSV: faixa, início, fim, in_fonte, nome_da_midia, efeitos, label
(tempos em segundos; efeitos = nomes dos componentes além de Motion/Opacity
padrão). Texto de Graphics/.mogrt não sai aqui: olhe frames.
"""
import sys, gzip, re
import xml.etree.ElementTree as ET

TK = 254016000000.0
raw = gzip.open(sys.argv[1]).read()
root = ET.fromstring(raw)
byid, byuid = {}, {}
for el in root:
    if 'ObjectID' in el.attrib: byid[el.attrib['ObjectID']] = el
    if 'ObjectUID' in el.attrib: byuid[el.attrib['ObjectUID']] = el

def ref(el):
    if el is None: return None
    if 'ObjectRef' in el.attrib: return byid.get(el.attrib['ObjectRef'])
    if 'ObjectURef' in el.attrib: return byuid.get(el.attrib['ObjectURef'])
    return None

def txt(el, path, d=None):
    f = el.find(path) if el is not None else None
    return f.text if f is not None and f.text is not None else d

seqs = [e for e in root if e.tag == 'Sequence']
if len(sys.argv) < 3:
    for s in seqs: print(txt(s, 'Name'))
    sys.exit()
seq = next(s for s in seqs if txt(s, 'Name') == sys.argv[2])

def media_name(sub):
    name = txt(sub, 'Name')
    clip = ref(sub.find('Clip'))
    inpt = 0.0
    if clip is not None:
        inner = clip.find('Clip')
        if inner is not None:
            inpt = int(txt(inner, 'InPoint', '0')) / TK
            src = ref(inner.find('Source'))
            if src is not None:
                ms = src.find('MediaSource')
                m = ref(ms.find('Media')) if ms is not None else None
                if m is not None:
                    p = txt(m, 'ActualMediaFilePath') or txt(m, 'FilePath') or ''
                    if p: name = name or p.split('/')[-1]
                    if not name: name = txt(m, 'Title')
    return name or '?', inpt

def effects(cti):
    co = cti.find('ComponentOwner/Components')
    chain = ref(co)
    out = []
    if chain is None: return out
    for c in chain.iter('Component'):
        comp = ref(c)
        if comp is None: continue
        dn = txt(comp, './/DisplayName') or txt(comp, './/MatchName') or comp.tag
        if dn in ('Motion', 'Opacity', 'Volume', 'Channel Volume', 'Panner', 'AE.ADBE Motion', 'AE.ADBE Opacity'): continue
        out.append(dn)
    return out

rows = []
for kind, tgname in (('V', 'VideoTrackGroup'), ('A', 'AudioTrackGroup')):
    for tg in seq.iter('TrackGroup'):
        g = ref(tg.find('Second')) if tg.find('Second') is not None else ref(tg)
        if g is None or g.tag != tgname: continue
        for t in g.iter('Track'):
            tr = ref(t)
            if tr is None: continue
            idx = int(txt(tr, './/Track/Index', '0'))
            for ti in tr.iter('TrackItem'):
                it = ref(ti)
                if it is None: continue
                cti = it.find('ClipTrackItem')
                if cti is None: continue
                st = int(txt(cti, 'TrackItem/Start', '0')) / TK
                en = int(txt(cti, 'TrackItem/End', '0')) / TK
                sub = ref(cti.find('SubClip'))
                nm, inp = media_name(sub) if sub is not None else ('?', 0)
                rows.append((f'{kind}{idx+1}', st, en, inp, nm, ','.join(effects(cti))))
for r in sorted(rows, key=lambda r: (r[0][0], int(r[0][1:]), r[1])):
    print(f'{r[0]}\t{r[1]:.2f}\t{r[2]:.2f}\t{r[3]:.2f}\t{r[4]}\t{r[5]}')
