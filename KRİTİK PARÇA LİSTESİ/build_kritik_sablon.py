# -*- coding: utf-8 -*-
"""Boş kritik parça şablonu — Excel + HTML (ürün ağacı doldurma yok)."""
from __future__ import annotations

import base64
import io
import json
import os
import re
from collections import defaultdict
from datetime import date

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image

FOLDER = os.path.dirname(os.path.abspath(__file__))
VERI_PATH = os.path.join(FOLDER, "kritik-parca-veri.json")
PHOTOS_DIR = os.path.join(FOLDER, "photos")
CEVIRI_PATH = os.path.join(FOLDER, "kritik-parca-ceviri.json")
_PHOTO_PREF = {".jpg": 0, ".jpeg": 1, ".png": 2, ".webp": 3, ".jfif": 4}


def norm_siparis(raw) -> str | None:
    if raw is None:
        return None
    compact = re.sub(r"\s+", "", str(raw).strip())
    m = re.match(r"^(\d{2})(\d{5})(\d{2})$", compact)  # ekli kod: '10 00694 12'
    if m:
        return " ".join(m.groups())
    m = re.match(r"^(\d{2})(\d{3,6})$", compact)
    if m:
        return f"{m.group(1)} {m.group(2).zfill(5)}"
    return None


def photo_map() -> dict[str, str]:
    """Sipariş kodu -> photos/… (aynı seride jpg tercih)."""
    if not os.path.isdir(PHOTOS_DIR):
        return {}
    by: dict[str, list[str]] = defaultdict(list)
    for name in os.listdir(PHOTOS_DIR):
        code = norm_siparis(os.path.splitext(name)[0])
        if code:
            by[code].append(name)
    out: dict[str, str] = {}
    for code, files in by.items():
        files.sort(key=lambda n: _PHOTO_PREF.get(os.path.splitext(n)[1].lower(), 99))
        out[code] = f"photos/{files[0]}"
    return out


# Aynı görünen seriler: ailenin tüm satırları tek referans fotoğrafı kullanır.
# (parça adı regex'i, referans sipariş kodu) — yeni aile eklemek için satır ekleyin.
FOTO_AILELERI = [
    (r"^TERMİK RÖLESİ ", "10 00249"),        # Schneider LR2K serisi
    (r"^KONTAKTÖR ", "10 01331"),            # Schneider LC1K serisi
    (r"^AMORTİSÖR ", "10 12433"),            # gazlı amortisör (175N–1400N aynı görünüm)
    (r"^NOZZLE ", "07 00253"),               # 1/4" yassı huzme nozzle
    (r"^TERMOKUPU?L ETB30F06", "10 01343"),
    (r"^ÖN FİLTRE ", "07 10214"),            # paslanmaz sepet ön filtre (çizim)   # Enda ETB30F06 (kablo boyu farklı)
]


def apply_photos(data: dict[str, list[dict]]) -> int:
    """Fotoğraf sırası: 1) aile kuralı  2) kendi sipariş kodu."""
    photos = photo_map()
    n = 0
    for rows in data.values():
        for r in rows:
            name = str(r.get("Parça adı", ""))
            fam = next((photos.get(ref) for pat, ref in FOTO_AILELERI if re.search(pat, name)), None)
            photo = fam or photos.get(norm_siparis(r.get("Sipariş kodu", "")) or "")
            if photo and r.get("Fotoğraf") != photo:
                r["Fotoğraf"] = photo
                n += 1
    return n


# Önerilen stok formülü: adet yalnızca Önem + Aşınma + Ulaşılabilirlik'e bağlıdır,
# aynı sınıftaki iki parça her zaman aynı adedi alır. Aşınma belirleyicidir:
# sık (1) ≥ 2  >  orta (2) = 1  ≥  seyrek (3) ≤ 1 — nadir bozulan parça, sık bozulandan fazla stok almaz.
# Ulaşılabilirlik yalnızca seyrek+kritik parçada "1 emniyet yedeği mi, liste mi" kararını verir.
# (etiket, önem, aşınma, ulaş, adet, tr, en, de) — boş küme = hepsi; ilk eşleşen kural uygulanır.
STOK_KURALLARI = [
    ("C+1", "C", "1", "", 3, "sık aşınma, kritik — depo seti",
     "frequent wear, critical — store set", "häufiger Verschleiß, kritisch — Lagersatz"),
    ("A/B+1", "AB", "1", "", 2, "sık aşınma — depo seti",
     "frequent wear — store set", "häufiger Verschleiß — Lagersatz"),
    ("2", "", "2", "", 1, "orta aşınma — 1 yedek",
     "medium wear — 1 spare", "mittlerer Verschleiß — 1 Ersatz"),
    ("C+3+K/O", "C", "3", "KO", 1, "kritik ama seyrek — 1 emniyet yedeği",
     "critical but rare — 1 safety spare", "kritisch, aber selten — 1 Sicherheitsreserve"),
    ("C+3+Z", "C", "3", "Z", 0, "kritik, seyrek, imalat / uzun termin — listede tut, siparişle",
     "critical, rare, manufactured / long lead time — keep on list, order when needed",
     "kritisch, selten, Fertigung / lange Lieferzeit — auf Liste, bei Bedarf bestellen"),
    ("A/B+3", "AB", "3", "", 0, "seyrek arıza — listede tut, siparişle",
     "rare failure — keep on list, order when needed", "seltener Ausfall — auf Liste, bei Bedarf bestellen"),
]
STOK_EKSIK = ("sınıf eksik — önce Önem/Aşınma/Ulaşılabilirlik girin",
              "class incomplete — enter criticality/wear/availability first",
              "Klasse unvollständig — zuerst Kritikalität/Verschleiß/Verfügbarkeit eintragen")
# Set olarak gönderilen parçalar: formül stok veriyorsa 1 set (= makinedeki takım) önerilir.
SET_BIRIMLI = re.compile(r"^NOZZLE ")
SET_GEREKCE = ("makinedeki nozzle takımı kadar — 1 set",
               "full nozzle set as fitted on the machine — 1 set",
               "kompletter Düsensatz wie an der Maschine — 1 Satz")
BIRIM_YAZI = {"adet": ("adet", "pcs", "Stk."), "set": ("set", "set", "Satz")}


def stok_kurali(o: str, a: str, u: str) -> tuple | None:
    if not (o in "ABC" and o and a in "123" and a and u in "KOZ" and u):
        return None
    for k in STOK_KURALLARI:
        if (not k[1] or o in k[1]) and k[2] == a and (not k[3] or u in k[3]):
            return k
    return None


def birim(r: dict) -> str:
    return "set" if SET_BIRIMLI.search(str(r.get("Parça adı", ""))) else "adet"


def stok_hesapla(r: dict) -> tuple[int, str, str, str]:
    """(miktar, gerekçe tr, en, de) — gerekçe '<Ö+A+U> → <miktar> <birim> · <kural>' biçimindedir."""
    o = str(r.get("Önem (A/B/C)", "")).strip().upper()
    a = str(r.get("Aşınma (1/2/3)", "")).strip()
    u = str(r.get("Ulaşılabilirlik (K/O/Z)", "")).strip().upper()
    combo = f"{o or '?'}+{a or '?'}+{u or '?'}"
    k = stok_kurali(o, a, u)
    n, txt = (k[4], k[5:8]) if k else (0, STOK_EKSIK)
    unit = birim(r)
    if unit == "set" and n > 0:
        n, txt = 1, SET_GEREKCE
    return (n, *(f"{combo} → {n} {w} · {t}" for w, t in zip(BIRIM_YAZI[unit], txt)))


def normalize_row(r: dict) -> dict:
    r.setdefault("Fotoğraf", "")
    n, ger, _, _ = stok_hesapla(r)
    r["Önerilen stok (adet)"] = str(n)
    r["Birim"] = birim(r)
    r["Stok gerekçesi"] = ger
    if not str(r.get("Not", "")).strip():
        r["Not"] = "Teknik / kullanım notu ekleyin."
    return r


def load_data() -> dict[str, list[dict]]:
    if not os.path.isfile(VERI_PATH):
        return {"LYM": [], "VDL": [], "KBN": []}
    with open(VERI_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    data = {
        k: [normalize_row(dict(row)) for row in raw.get(k, [])]
        for k in ("LYM", "VDL", "KBN")
    }
    apply_photos(data)
    return data


def row_to_list(r: dict) -> list:
    return [r.get(c, "") for c in COLS]

COLS = [
    "Sipariş kodu",
    "Parça adı",
    "Fotoğraf",
    "Varyant / makine",
    "Önem (A/B/C)",
    "Aşınma (1/2/3)",
    "Ulaşılabilirlik (K/O/Z)",
    "Önerilen stok (adet)",
    "Birim",
    "Stok gerekçesi",
    "Not",
]

LEGEND_ROWS = [
    ("Önem C", "Arızada makine çalışmaz veya emniyet onayı yok"),
    ("Önem B", "Kısıtlı çalışma / kısa sürede duruş riski"),
    ("Önem A", "Makine çalışır; ikincil etki"),
    ("Aşınma 1", "Sık tüketim/aşınma (bakım periyodunda)"),
    ("Aşınma 2", "Orta vadeli (yıllar)"),
    ("Aşınma 3", "Seyrek; olay bazlı (darbe, kaza)"),
    ("Ulaş. K", "Kolay tedarik (piyasa, hızlı)"),
    ("Ulaş. O", "Orta termin (bayi, 1–3 hafta)"),
    ("Ulaş. Z", "Zor / tek kaynak / imalat"),
]
LEGEND_ROWS += [(f"Stok {k[0]}", f"{k[4]} adet — {k[5]}") for k in STOK_KURALLARI]


def write_excel(path: str, data: dict[str, list[dict]]) -> None:
    wb = openpyxl.Workbook()
    hdr_fill = PatternFill("solid", fgColor="1E3A5F")
    hdr_font = Font(color="FFFFFF", bold=True)
    legend_fill = PatternFill("solid", fgColor="F1F5F9")

    ws0 = wb.active
    ws0.title = "Sınıflandırma"
    ws0["A1"] = "Kritik parça — sınıflandırma kriterleri"
    ws0["A1"].font = Font(bold=True, size=14)
    ws0.append([])
    ws0.append(["Kod", "Açıklama"])
    for a, b in LEGEND_ROWS:
        ws0.append([a, b])
    ws0.append([])
    ws0.append(["Güncelleme", date.today().isoformat()])
    ws0.column_dimensions["A"].width = 18
    ws0.column_dimensions["B"].width = 72

    widths = (14, 40, 22, 22, 14, 14, 18, 16, 8, 28, 24)
    for sheet in ("LYM", "VDL", "KBN"):
        ws = wb.create_sheet(sheet)
        ws.append(COLS)
        for i, cell in enumerate(ws[1], start=1):
            cell.fill = hdr_fill
            cell.font = hdr_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = "A2"
        for col in ("E", "F", "G"):
            for r in range(2, 502):
                ws[f"{col}{r}"].fill = legend_fill
        rows = data.get(sheet, [])
        if rows:
            for r in rows:
                ws.append(row_to_list(r))
        else:
            ws["A2"] = ""
            ws["B2"] = "← Satırları doldurun"
            ws["B2"].font = Font(italic=True, color="64748B")

    wb.save(path)


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Kritik Parça Listesi</title>
  <style>
    :root {
      --bg:#f4f5f7; --surface:#ffffff; --surface-2:#f0f2f5; --line:#e4e7ec;
      --text:#101828; --muted:#667085; --faint:#98a2b3;
      --accent:#2f5bea; --accent-soft:#eaf0ff;
      --c:#d92d20; --c-soft:#fee4e2; --b:#dc6803; --b-soft:#fef0c7; --a:#079455; --a-soft:#dcfae6;
      --z:#c11574; --z-soft:#fce7f6;
      --shadow:0 1px 2px rgba(16,24,40,.05), 0 1px 3px rgba(16,24,40,.06);
      --shadow-lg:0 12px 32px rgba(16,24,40,.14);
      color-scheme:light;
    }
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) {
        --bg:#0c111d; --surface:#161b26; --surface-2:#1f242f; --line:#2a313e;
        --text:#f5f5f6; --muted:#94969c; --faint:#61646c;
        --accent:#7b9bff; --accent-soft:#1c2a52;
        --c:#f97066; --c-soft:#3d1714; --b:#fdb022; --b-soft:#3a2a0a; --a:#47cd89; --a-soft:#0d2f1f;
        --z:#f670c7; --z-soft:#3a1230;
        --shadow:0 1px 2px rgba(0,0,0,.4); --shadow-lg:0 12px 32px rgba(0,0,0,.5);
        color-scheme:dark;
      }
    }
    :root[data-theme="dark"] {
      --bg:#0c111d; --surface:#161b26; --surface-2:#1f242f; --line:#2a313e;
      --text:#f5f5f6; --muted:#94969c; --faint:#61646c;
      --accent:#7b9bff; --accent-soft:#1c2a52;
      --c:#f97066; --c-soft:#3d1714; --b:#fdb022; --b-soft:#3a2a0a; --a:#47cd89; --a-soft:#0d2f1f;
      --z:#f670c7; --z-soft:#3a1230;
      --shadow:0 1px 2px rgba(0,0,0,.4); --shadow-lg:0 12px 32px rgba(0,0,0,.5);
      color-scheme:dark;
    }
    * { box-sizing:border-box; }
    html, body { margin:0; }
    body {
      background:var(--bg); color:var(--text);
      font:14px/1.45 "Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,sans-serif;
      -webkit-font-smoothing:antialiased;
    }
    button { font:inherit; color:inherit; cursor:pointer; }
    .mono { font-family:"Cascadia Mono",Consolas,ui-monospace,monospace; }

    /* Üst bar */
    .top {
      position:sticky; top:0; z-index:20; display:flex; align-items:center; gap:12px 16px; flex-wrap:wrap;
      padding:12px 24px; background:color-mix(in srgb, var(--surface) 88%, transparent);
      backdrop-filter:blur(10px); border-bottom:1px solid var(--line);
    }
    .brand { display:flex; align-items:center; gap:10px; margin-right:8px; }
    .logo {
      width:34px; height:34px; border-radius:10px; display:grid; place-items:center;
      background:var(--accent); color:#fff; font-weight:800; font-size:13px; letter-spacing:.02em;
    }
    .brand h1 { margin:0; font-size:15px; font-weight:700; letter-spacing:-.01em; }
    .brand small { display:block; color:var(--muted); font-size:12px; }
    .seg { display:inline-flex; padding:3px; background:var(--surface-2); border-radius:10px; gap:2px; }
    .seg button {
      border:0; background:transparent; padding:6px 14px; border-radius:8px; font-weight:600; color:var(--muted);
      display:inline-flex; align-items:center; gap:6px;
    }
    .seg button .n { font-size:11px; font-weight:700; color:var(--faint); }
    .seg button.on { background:var(--surface); color:var(--text); box-shadow:var(--shadow); }
    .seg button.on .n { color:var(--accent); }
    .search { flex:1; min-width:180px; max-width:360px; margin-left:auto; position:relative; }
    .search svg { position:absolute; left:11px; top:50%; transform:translateY(-50%); color:var(--faint); }
    .search input {
      width:100%; height:36px; padding:0 12px 0 34px; border-radius:10px; border:1px solid var(--line);
      background:var(--surface); color:var(--text); font:inherit;
    }
    .search input:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft); }
    .icon-btn {
      width:36px; height:36px; border-radius:10px; border:1px solid var(--line); background:var(--surface);
      display:grid; place-items:center; color:var(--muted);
    }
    .tools { display:flex; gap:8px; }
    .icon-btn:hover { color:var(--text); border-color:var(--faint); }

    main { padding:20px 24px 40px; max-width:1600px; margin:0 auto; }

    /* KPI */
    .kpis { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:18px; }
    .kpi { background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:14px 16px; box-shadow:var(--shadow); }
    .kpi .lbl { color:var(--muted); font-size:12px; font-weight:600; display:flex; align-items:center; gap:6px; }
    .kpi .val { font-size:26px; font-weight:700; letter-spacing:-.02em; margin-top:2px; font-variant-numeric:tabular-nums; }
    .kpi .val small { font-size:13px; color:var(--faint); font-weight:600; margin-left:4px; }
    .dot { width:8px; height:8px; border-radius:50%; display:inline-block; }

    /* Filtre çubuğu */
    .bar { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:14px; }
    .chips { display:flex; gap:6px; flex-wrap:wrap; }
    .chip {
      border:1px solid var(--line); background:var(--surface); border-radius:999px; padding:5px 12px;
      font-size:13px; font-weight:600; color:var(--muted); display:inline-flex; align-items:center; gap:6px;
    }
    .chip:hover { color:var(--text); }
    .chip.on { background:var(--text); color:var(--surface); border-color:var(--text); }
    .chip .cnt { font-size:11px; opacity:.7; }
    .bar .right { margin-left:auto; display:flex; gap:8px; align-items:center; }
    .bar select {
      height:32px; border-radius:8px; border:1px solid var(--line); background:var(--surface); color:var(--text);
      font:inherit; font-size:13px; padding:0 8px;
    }
    .seg.sm button { padding:4px 10px; }
    .result { color:var(--faint); font-size:12px; }

    /* Kartlar */
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:12px; }
    .card {
      background:var(--surface); border:1px solid var(--line); border-radius:14px; overflow:hidden;
      box-shadow:var(--shadow); cursor:pointer; display:flex; flex-direction:column; text-align:left; padding:0; min-width:0;
      transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease; position:relative;
    }
    .card:hover { transform:translateY(-2px); box-shadow:var(--shadow-lg); border-color:var(--faint); }
    .card:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
    .card::before { content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--sev, var(--line)); z-index:1; }
    .card .row { display:flex; gap:12px; padding:14px 14px 0 18px; min-width:0; }
    .card .tn { width:64px; height:64px; flex-shrink:0; border-radius:10px; overflow:hidden; background:var(--surface-2); display:grid; place-items:center; color:var(--faint); }
    .card .tn img { width:100%; height:100%; object-fit:cover; display:block; }
    .card .info { min-width:0; display:flex; flex-direction:column; gap:3px; }
    .sev-C { --sev:var(--c); --sev-soft:var(--c-soft); }
    .sev-B { --sev:var(--b); --sev-soft:var(--b-soft); }
    .sev-A { --sev:var(--a); --sev-soft:var(--a-soft); }
    .ph { aspect-ratio:16/10; background:var(--surface-2); display:grid; place-items:center; overflow:hidden; }
    .ph img { width:100%; height:100%; object-fit:cover; display:block; }
    .ph .none { color:var(--faint); display:flex; flex-direction:column; align-items:center; gap:4px; font-size:11px; }
    .cb { padding:0 14px 12px 18px; display:flex; flex-direction:column; flex:1; }
    .code { font-size:12px; color:var(--accent); font-weight:600; }
    .card .ttl { margin:0; font-size:14px; font-weight:600; line-height:1.3; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
    .mach { color:var(--muted); font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .foot { display:flex; align-items:flex-end; justify-content:space-between; margin-top:auto; padding-top:12px; }

    .badges { display:flex; gap:4px; }
    .bd {
      min-width:26px; height:24px; padding:0 7px; border-radius:7px; display:inline-grid; place-items:center;
      font-size:12px; font-weight:700; border:1px solid var(--line); color:var(--muted); background:var(--surface);
    }
    .bd.o-C { background:var(--c-soft); color:var(--c); border-color:transparent; }
    .bd.o-B { background:var(--b-soft); color:var(--b); border-color:transparent; }
    .bd.o-A { background:var(--a-soft); color:var(--a); border-color:transparent; }
    .bd.w-1 { color:var(--text); border-color:var(--faint); }
    .bd.u-O { color:var(--b); border-color:color-mix(in srgb, var(--b) 45%, transparent); }
    .bd.u-Z { color:var(--z); border-color:color-mix(in srgb, var(--z) 45%, transparent); background:var(--z-soft); }
    .bd.u-none { border-style:dashed; color:var(--faint); }

    .stk { text-align:right; line-height:1; }
    .stk b { font-size:22px; font-weight:700; font-variant-numeric:tabular-nums; }
    .stk small { display:block; font-size:10px; color:var(--faint); text-transform:uppercase; letter-spacing:.06em; margin-top:3px; }
    .stk.zero b { color:var(--faint); }

    /* Liste */
    .list { background:var(--surface); border:1px solid var(--line); border-radius:14px; overflow:auto; box-shadow:var(--shadow); }
    .list table { width:100%; border-collapse:collapse; }
    .list th {
      position:sticky; top:0; background:var(--surface-2); color:var(--muted); font-size:11px; font-weight:700;
      text-transform:uppercase; letter-spacing:.05em; text-align:left; padding:10px 12px; white-space:nowrap;
    }
    .list td { padding:8px 12px; border-top:1px solid var(--line); vertical-align:middle; }
    .list tr.r { cursor:pointer; }
    .list tr.r:hover td { background:var(--surface-2); }
    .list td.sev { width:4px; padding:0; background:var(--sev); }
    .list .thumb { width:40px; height:40px; border-radius:8px; object-fit:cover; display:block; background:var(--surface-2); }
    .list .thumb.none { display:grid; place-items:center; color:var(--faint); }
    .list td.num { text-align:right; font-weight:700; font-variant-numeric:tabular-nums; }
    .list td.num.zero { color:var(--faint); }
    .list .mach { max-width:220px; }

    .empty { text-align:center; padding:60px 20px; color:var(--muted); background:var(--surface); border:1px dashed var(--line); border-radius:14px; }

    /* Detay paneli */
    .scrim { position:fixed; inset:0; background:rgba(12,17,29,.45); opacity:0; pointer-events:none; transition:opacity .18s; z-index:40; }
    .scrim.on { opacity:1; pointer-events:auto; }
    .drawer {
      position:fixed; top:0; right:0; bottom:0; width:min(440px,100%); background:var(--surface); z-index:41;
      transform:translateX(100%); transition:transform .22s ease; box-shadow:var(--shadow-lg);
      display:flex; flex-direction:column; border-left:1px solid var(--line);
    }
    .drawer.on { transform:none; }
    .drawer .ph { aspect-ratio:4/3; flex-shrink:0; }
    .drawer .ph img { object-fit:contain; background:#fff; }
    .drawer .x { position:absolute; top:12px; right:12px; z-index:2; background:var(--surface); }
    .dbody { padding:18px 22px 28px; overflow:auto; display:flex; flex-direction:column; gap:16px; }
    .dbody h2 { margin:2px 0 0; font-size:19px; line-height:1.3; letter-spacing:-.01em; }
    .copy { border:0; background:var(--accent-soft); color:var(--accent); border-radius:6px; padding:2px 8px; font-size:12px; font-weight:600; margin-left:6px; }
    .facts { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
    .fact { background:var(--surface-2); border-radius:10px; padding:10px; }
    .fact .k { font-size:11px; color:var(--muted); font-weight:600; }
    .fact .v { display:flex; align-items:center; gap:6px; margin-top:4px; font-weight:600; font-size:13px; }
    .stockbox { display:flex; align-items:center; gap:14px; padding:14px; border-radius:12px; border:1px solid var(--line); }
    .stockbox b { font-size:32px; line-height:1; font-variant-numeric:tabular-nums; }
    .stockbox .t { font-size:12px; color:var(--muted); }
    .stockbox .t strong { display:block; color:var(--text); font-size:13px; }
    .sec .k { font-size:11px; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; }
    .sec p { margin:0; }

    /* Yardım */
    dialog {
      border:1px solid var(--line); border-radius:16px; padding:0; width:min(760px,calc(100% - 32px));
      background:var(--surface); color:var(--text); box-shadow:var(--shadow-lg);
    }
    dialog::backdrop { background:rgba(12,17,29,.45); }
    .hd { display:flex; align-items:center; justify-content:space-between; padding:16px 20px; border-bottom:1px solid var(--line); }
    .hd h2 { margin:0; font-size:16px; }
    .hb { padding:18px 20px 22px; display:grid; gap:18px; }
    .axes { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
    .axis h4 { margin:0 0 8px; font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; }
    .axis div { display:flex; gap:8px; align-items:center; margin-bottom:6px; font-size:13px; }
    .rules { width:100%; border-collapse:collapse; font-size:13px; }
    .rules td { padding:7px 8px; border-top:1px solid var(--line); }
    .rules td:last-child { text-align:right; font-weight:700; white-space:nowrap; }
    .rules caption { text-align:left; font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; font-weight:700; padding-bottom:6px; }

    @media (max-width:900px) {
      .kpis { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .axes { grid-template-columns:1fr; }
    }
    @media (max-width:640px) {
      .top { padding:10px 16px; }
      .tools { margin-left:auto; }
      .seg#tabs { order:4; flex-basis:100%; }
      .seg#tabs button { flex:1; justify-content:center; }
      .search { order:5; max-width:none; flex-basis:100%; }
      .kpi .val { font-size:22px; }
      main { padding:16px 16px 32px; }
      .grid { grid-template-columns:1fr; gap:10px; }
      .list .hide-sm { display:none; }
      .bar .right { margin-left:0; }
    }
    @media print {
      .top .search, .top .icon-btn, .bar, .drawer, .scrim { display:none !important; }
      .top { position:static; backdrop-filter:none; }
      #grid { display:none !important; } #list { display:block !important; box-shadow:none; }
      body { background:#fff; }
    }
    /* Dil seçimi */
    .lang { position:relative; }
    .lang-btn {
      height:36px; border-radius:10px; border:1px solid var(--line); background:var(--surface);
      display:inline-flex; align-items:center; gap:7px; padding:0 9px 0 10px; font-weight:600; font-size:13px;
    }
    .lang-btn:hover { border-color:var(--faint); }
    .lang-btn .chev { color:var(--faint); transition:transform .15s; }
    .lang-btn[aria-expanded="true"] .chev { transform:rotate(180deg); }
    .flag { width:20px; height:14px; border-radius:3px; display:block; flex-shrink:0; box-shadow:0 0 0 1px rgba(16,24,40,.12); overflow:hidden; }
    .lang-menu {
      position:absolute; right:0; top:calc(100% + 6px); min-width:168px; margin:0; padding:4px; list-style:none; z-index:30;
      background:var(--surface); border:1px solid var(--line); border-radius:12px; box-shadow:var(--shadow-lg);
    }
    .lang-menu li {
      display:flex; align-items:center; gap:10px; padding:8px 10px; border-radius:8px; cursor:pointer; font-size:13px;
    }
    .lang-menu li:hover, .lang-menu li.focus { background:var(--surface-2); }
    .lang-menu li b { font-weight:700; min-width:22px; }
    .lang-menu li span.nm { color:var(--muted); flex:1; }
    .lang-menu li .ck { color:var(--accent); visibility:hidden; }
    .lang-menu li[aria-selected="true"] .ck { visibility:visible; }
  </style>
</head>
<body>
  <header class="top">
    <div class="brand">
      <div class="logo">KP</div>
      <div><h1 data-i="title"></h1><small data-i="subtitle"></small></div>
    </div>
    <nav class="seg" id="tabs"></nav>
    <label class="search">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input type="search" id="q" autocomplete="off"/>
    </label>
    <div class="tools">
    <div class="lang" id="lang">
      <button class="lang-btn" id="langBtn" aria-haspopup="listbox" aria-expanded="false"></button>
      <ul class="lang-menu" id="langMenu" role="listbox" tabindex="-1" hidden></ul>
    </div>
    <button class="icon-btn" id="helpBtn">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14"/><circle cx="12" cy="17.5" r=".6" fill="currentColor"/></svg>
    </button>
    <button class="icon-btn" id="themeBtn">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>
    </button>
    </div>
  </header>

  <main>
    <section class="kpis" id="kpis"></section>
    <div class="bar">
      <div class="chips" id="chips"></div>
      <div class="right">
        <span class="result" id="result"></span>
        <select id="sort">
          <option value="sev" data-i="sortSev"></option>
          <option value="stock" data-i="sortStock"></option>
          <option value="code" data-i="sortCode"></option>
          <option value="name" data-i="sortName"></option>
        </select>
        <div class="seg sm" id="viewSeg">
          <button data-v="grid"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg></button>
          <button data-v="list"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01"/></svg></button>
        </div>
      </div>
    </div>
    <section class="grid" id="grid"></section>
    <section class="list" id="list" hidden></section>
  </main>

  <div class="scrim" id="scrim"></div>
  <aside class="drawer" id="drawer" aria-hidden="true">
    <button class="icon-btn x" id="dClose"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg></button>
    <div id="dContent" style="display:flex;flex-direction:column;min-height:0;flex:1"></div>
  </aside>

  <dialog id="help">
    <div class="hd"><h2 data-i="helpTitle"></h2><button class="icon-btn" id="helpClose"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg></button></div>
    <div class="hb" id="helpBody"></div>
  </dialog>

  <script>
    const COLS = __COLS__;
    const DATA = __DATA__;
    const DATA_I18N = __I18N__;
    const K = { kod:"Sipariş kodu", ad:"Parça adı", foto:"Fotoğraf", mak:"Varyant / makine",
      o:"Önem (A/B/C)", a:"Aşınma (1/2/3)", u:"Ulaşılabilirlik (K/O/Z)", s:"Önerilen stok (adet)",
      g:"Stok gerekçesi", n:"Not", unit:"Birim" };

    const FLAGS = {
      tr: '<svg class="flag" viewBox="0 0 30 20"><rect width="30" height="20" fill="#E30A17"/><circle cx="11" cy="10" r="5" fill="#fff"/><circle cx="12.25" cy="10" r="4" fill="#E30A17"/><polygon fill="#fff" points="13.90,10.00 15.59,9.41 15.63,7.62 16.71,9.05 18.42,8.53 17.40,10.00 18.42,11.47 16.71,10.95 15.63,12.38 15.59,10.59"/></svg>',
      en: '<svg class="flag" viewBox="0 0 60 40" preserveAspectRatio="xMidYMid slice"><rect width="60" height="40" fill="#012169"/><path d="M0 0 60 40M60 0 0 40" stroke="#fff" stroke-width="8"/><path d="M0 0 60 40M60 0 0 40" stroke="#C8102E" stroke-width="3"/><path d="M30 0v40M0 20h60" stroke="#fff" stroke-width="12"/><path d="M30 0v40M0 20h60" stroke="#C8102E" stroke-width="7"/></svg>',
      de: '<svg class="flag" viewBox="0 0 30 20"><rect width="30" height="7" fill="#000"/><rect y="6.67" width="30" height="6.67" fill="#DD0000"/><rect y="13.33" width="30" height="6.67" fill="#FFCE00"/></svg>'
    };
    const LANGS = [
      { id:'tr', code:'TR', name:'Türkçe', locale:'tr' },
      { id:'en', code:'EN', name:'English', locale:'en' },
      { id:'de', code:'DE', name:'Deutsch', locale:'de' }
    ];
    const UI = {
      tr: {
        title:'Kritik Parça Listesi', subtitle:'Yedek parça · stok önerisi', search:'Kod, parça veya makine ara',
        groups:'Makine grubu', help:'Sınıflandırma rehberi', helpTitle:'Sınıflandırma rehberi', theme:'Temayı değiştir', lang:'Dil',
        kParts:'Parça', kCrit:'Kritik (C)', kStocked:'Stokta tutulacak', kItems:'kalem', kTotal:'Toplam yedek', kPcs:'adet',
        all:'Tümü', keep:'Stokta tut', results:'{n} sonuç', sort:'Sıralama',
        sortSev:'Önem sırası', sortStock:'Stok adedi', sortCode:'Sipariş kodu', sortName:'Parça adı',
        cards:'Kart görünümü', listView:'Liste görünümü',
        hCode:'Kod', hPart:'Parça', hMachine:'Makine', hClass:'Sınıf', hStock:'Stok', stock:'stok',
        noMatch:'Eşleşen parça yok.', noRows:'{g} için henüz satır yok.', noPhoto:'Fotoğraf yok',
        crit:'Önem', wear:'Aşınma', avail:'Ulaşılabilirlik', availShort:'Ulaşım', unassigned:'Atanmadı', availUnassigned:'Ulaşılabilirlik henüz atanmadı',
        copy:'Kopyala', copied:'Kopyalandı', recQty:'Önerilen yedek adet', recSet:'Önerilen yedek set', unitSet:'set', setNote:'Nozzle\'lar adet değil set olarak önerilir: 1 set = makinedeki nozzle takımı.', notStocked:'Depoda tutulmaz', note:'Not', close:'Kapat',
        o:{ C:'Kritik', B:'Kısıtlı', A:'İkincil' }, a:{ '1':'Sık', '2':'Orta', '3':'Seyrek' }, u:{ K:'Kolay', O:'Orta', Z:'Zor' },
        oD:{ C:'makine durur / emniyet', B:'kapasite, kalite düşer', A:'makine çalışır' },
        aD:{ '1':'bakımda değişir', '2':'birkaç yıl ömür', '3':'hasar / kaza' },
        uD:{ K:'piyasa, günler', O:'bayi, haftalar', Z:'imalat, tek kaynak' },
        rules:'Stok kuralı',
      },
      en: {
        title:'Critical Parts List', subtitle:'Spare parts · stock recommendation', search:'Search code, part or machine',
        groups:'Machine group', help:'Classification guide', helpTitle:'Classification guide', theme:'Toggle theme', lang:'Language',
        kParts:'Parts', kCrit:'Critical (C)', kStocked:'To keep in stock', kItems:'items', kTotal:'Total spares', kPcs:'pcs',
        all:'All', keep:'Keep in stock', results:'{n} results', sort:'Sort',
        sortSev:'By criticality', sortStock:'Stock quantity', sortCode:'Order code', sortName:'Part name',
        cards:'Card view', listView:'List view',
        hCode:'Code', hPart:'Part', hMachine:'Machine', hClass:'Class', hStock:'Stock', stock:'stock',
        noMatch:'No matching parts.', noRows:'No rows for {g} yet.', noPhoto:'No photo',
        crit:'Criticality', wear:'Wear', avail:'Availability', availShort:'Availability', unassigned:'Not assigned', availUnassigned:'Availability not assigned yet',
        copy:'Copy', copied:'Copied', recQty:'Recommended spare quantity', recSet:'Recommended spare sets', unitSet:'set', setNote:'Nozzles are recommended in sets, not pieces: 1 set = the full nozzle set fitted on the machine.', notStocked:'Not kept in stock', note:'Note', close:'Close',
        o:{ C:'Critical', B:'Limited', A:'Secondary' }, a:{ '1':'Frequent', '2':'Medium', '3':'Rare' }, u:{ K:'Easy', O:'Medium', Z:'Hard' },
        oD:{ C:'machine stops / safety', B:'capacity or quality drops', A:'machine keeps running' },
        aD:{ '1':'replaced at service', '2':'lasts a few years', '3':'damage / accident' },
        uD:{ K:'market, days', O:'dealer, weeks', Z:'manufactured, single source' },
        rules:'Stock rule',
      },
      de: {
        title:'Liste kritischer Teile', subtitle:'Ersatzteile · Bestandsempfehlung', search:'Code, Teil oder Maschine suchen',
        groups:'Maschinengruppe', help:'Klassifizierungsleitfaden', helpTitle:'Klassifizierungsleitfaden', theme:'Design wechseln', lang:'Sprache',
        kParts:'Teile', kCrit:'Kritisch (C)', kStocked:'Zu bevorraten', kItems:'Positionen', kTotal:'Ersatzteile gesamt', kPcs:'Stk.',
        all:'Alle', keep:'Bevorraten', results:'{n} Ergebnisse', sort:'Sortierung',
        sortSev:'Nach Kritikalität', sortStock:'Bestandsmenge', sortCode:'Bestellnummer', sortName:'Teilename',
        cards:'Kartenansicht', listView:'Listenansicht',
        hCode:'Code', hPart:'Teil', hMachine:'Maschine', hClass:'Klasse', hStock:'Bestand', stock:'Bestand',
        noMatch:'Keine passenden Teile.', noRows:'Noch keine Einträge für {g}.', noPhoto:'Kein Foto',
        crit:'Kritikalität', wear:'Verschleiß', avail:'Verfügbarkeit', availShort:'Verfügbarkeit', unassigned:'Nicht zugewiesen', availUnassigned:'Verfügbarkeit noch nicht zugewiesen',
        copy:'Kopieren', copied:'Kopiert', recQty:'Empfohlene Ersatzmenge', recSet:'Empfohlene Ersatzsätze', unitSet:'Satz', setNote:'Düsen werden als Satz empfohlen, nicht stückweise: 1 Satz = kompletter Düsensatz der Maschine.', notStocked:'Nicht bevorratet', note:'Hinweis', close:'Schließen',
        o:{ C:'Kritisch', B:'Eingeschränkt', A:'Sekundär' }, a:{ '1':'Häufig', '2':'Mittel', '3':'Selten' }, u:{ K:'Leicht', O:'Mittel', Z:'Schwer' },
        oD:{ C:'Maschine steht / Sicherheit', B:'Kapazität, Qualität sinkt', A:'Maschine läuft weiter' },
        aD:{ '1':'bei Wartung getauscht', '2':'einige Jahre Lebensdauer', '3':'Schaden / Unfall' },
        uD:{ K:'Markt, Tage', O:'Händler, Wochen', Z:'Fertigung, einzige Quelle' },
        rules:'Bestandsregel',
      }
    };
    const RULES = __RULES__;
    const IMGS = __IMGS__;
    const NOTE_PLACEHOLDER = "Teknik / kullanım notu ekleyin.";
    const GROUPS = Object.keys(DATA);
    const SEV_ORDER = { C:0, B:1, A:2 };
    const IMG_NONE = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/></svg>';

    const store = {
      get(k, d) { try { return localStorage.getItem('kp.' + k) ?? d; } catch (e) { return d; } },
      set(k, v) { try { localStorage.setItem('kp.' + k, v); } catch (e) {} }
    };
    const st = { g: GROUPS.includes(store.get('g')) ? store.get('g') : GROUPS[0], q:'', sev:'', stockOnly:false,
      view: store.get('view', 'grid'), sort:'sev', lang: UI[store.get('lang')] ? store.get('lang') : 'tr' };
    let shown = [];
    let drawerRow = null;

    const $ = id => document.getElementById(id);
    const esc = s => String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const up = v => String(v ?? '').trim().toUpperCase();
    const stockOf = r => { const n = parseInt(r[K.s], 10); return isNaN(n) ? 0 : n; };
    const isSet = r => r[K.unit] === 'set';
    const isImg = v => !!IMGS[v] || /^https?:\/\//i.test(v) || /\.(jpe?g|jfif|png|webp|gif|svg)$/i.test(v);
    // Arayüz metni
    const t = (key, vars) => {
      let s = UI[st.lang][key] ?? UI.tr[key] ?? key;
      if (vars) for (const k in vars) s = s.replace('{' + k + '}', vars[k]);
      return s;
    };
    // Veri metni (makine, gerekçe, not). Parça adı ve sipariş kodu hiç çevrilmez.
    const td = v => { const s = String(v ?? ''); return st.lang === 'tr' ? s : ((DATA_I18N[st.lang] || {})[s] ?? s); };
    const locale = () => LANGS.find(l => l.id === st.lang).locale;

    function badges(r) {
      const o = up(r[K.o]), a = up(r[K.a]), u = up(r[K.u]), L = UI[st.lang];
      return '<span class="badges">' +
        '<span class="bd o-' + esc(o) + '" title="' + esc(t('crit') + ': ' + (L.o[o] || '—')) + '">' + esc(o || '—') + '</span>' +
        '<span class="bd w-' + esc(a) + '" title="' + esc(t('wear') + ': ' + (L.a[a] || '—')) + '">' + esc(a || '—') + '</span>' +
        (u ? '<span class="bd u-' + esc(u) + '" title="' + esc(t('avail') + ': ' + (L.u[u] || u)) + '">' + esc(u) + '</span>'
           : '<span class="bd u-none" title="' + esc(t('availUnassigned')) + '">?</span>') +
        '</span>';
    }
    function photo(r, cls) {
      const v = String(r[K.foto] ?? '').trim();
      if (v && isImg(v)) return '<img class="' + (cls || '') + '" src="' + esc(IMGS[v] || v) + '" alt="" loading="lazy" onerror="this.outerHTML=IMG_NONE"/>';
      return cls ? '<span class="' + cls + ' none">' + IMG_NONE + '</span>' : '<span class="none">' + IMG_NONE + esc(t('noPhoto')) + '</span>';
    }

    function filtered() {
      const q = st.q.toLocaleLowerCase(locale());
      const qc = q.replace(/\s+/g, '');
      let rows = (DATA[st.g] || []).filter(r => {
        if (st.sev && up(r[K.o]) !== st.sev) return false;
        if (st.stockOnly && stockOf(r) <= 0) return false;
        if (!q) return true;
        const hay = (r[K.kod] + ' ' + r[K.ad] + ' ' + (r[K.mak] || '') + ' ' + td(r[K.mak])).toLocaleLowerCase(locale());
        return hay.includes(q) || String(r[K.kod]).replace(/\s+/g, '').includes(qc);
      });
      const by = {
        sev: (x, y) => (SEV_ORDER[up(x[K.o])] ?? 9) - (SEV_ORDER[up(y[K.o])] ?? 9) || stockOf(y) - stockOf(x),
        stock: (x, y) => stockOf(y) - stockOf(x) || (SEV_ORDER[up(x[K.o])] ?? 9) - (SEV_ORDER[up(y[K.o])] ?? 9),
        code: (x, y) => String(x[K.kod]).localeCompare(String(y[K.kod]), 'tr'),
        name: (x, y) => String(x[K.ad]).localeCompare(String(y[K.ad]), 'tr')
      }[st.sort];
      return rows.slice().sort(by);
    }

    function renderStatic() {
      document.documentElement.lang = st.lang;
      document.title = t('title');
      document.querySelectorAll('[data-i]').forEach(el => { el.textContent = t(el.dataset.i); });
      $('q').placeholder = t('search');
      $('tabs').setAttribute('aria-label', t('groups'));
      $('sort').setAttribute('aria-label', t('sort'));
      const setLbl = (el, key) => { el.title = t(key); el.setAttribute('aria-label', t(key)); };
      setLbl($('helpBtn'), 'help'); setLbl($('themeBtn'), 'theme');
      setLbl($('dClose'), 'close'); setLbl($('helpClose'), 'close');
      setLbl($('viewSeg').children[0], 'cards'); setLbl($('viewSeg').children[1], 'listView');
      const cur = LANGS.find(l => l.id === st.lang);
      $('langBtn').innerHTML = FLAGS[cur.id] + '<span>' + cur.code + '</span>' +
        '<svg class="chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="m6 9 6 6 6-6"/></svg>';
      setLbl($('langBtn'), 'lang');
      $('langMenu').setAttribute('aria-label', t('lang'));
      $('langMenu').innerHTML = LANGS.map(l =>
        '<li role="option" data-l="' + l.id + '" aria-selected="' + (l.id === st.lang) + '">' + FLAGS[l.id] +
        '<b>' + l.code + '</b><span class="nm">' + l.name + '</span>' +
        '<svg class="ck" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="m5 12 5 5 9-10"/></svg></li>').join('');
      renderHelp();
    }
    function renderHelp() {
      const L = UI[st.lang];
      const axis = (title, keys, lbl, desc, cls) => '<div class="axis"><h4>' + esc(title) + '</h4>' +
        keys.map(k => '<div><span class="bd ' + cls(k) + '">' + k + '</span> ' + esc(lbl[k] + ': ' + desc[k]) + '</div>').join('') + '</div>';
      $('helpBody').innerHTML =
        '<div class="axes">' +
          axis(t('crit'), ['C','B','A'], L.o, L.oD, k => 'o-' + k) +
          axis(t('wear'), ['1','2','3'], L.a, L.aD, k => k === '1' ? 'w-1' : '') +
          axis(t('avail'), ['K','O','Z'], L.u, L.uD, k => k === 'K' ? '' : 'u-' + k) +
        '</div>' +
        '<table class="rules"><caption>' + esc(t('rules')) + '</caption>' +
        RULES.map(r => '<tr><td><span class="mono">' + esc(r.k) + '</span></td><td>' + esc(r.t[st.lang] || r.t.tr) + '</td><td>' + r.n + '</td></tr>').join('') +
        '</table>' +
        '<p style="margin:0;color:var(--muted);font-size:12px">' + esc(t('setNote')) + '</p>';
    }
    function renderTabs() {
      $('tabs').innerHTML = GROUPS.map(g =>
        '<button class="' + (g === st.g ? 'on' : '') + '" data-g="' + esc(g) + '">' + esc(g) +
        '<span class="n">' + (DATA[g] || []).length + '</span></button>').join('');
    }
    function renderKpis() {
      const all = DATA[st.g] || [];
      const crit = all.filter(r => up(r[K.o]) === 'C').length;
      const stocked = all.filter(r => stockOf(r) > 0);
      const total = stocked.filter(r => !isSet(r)).reduce((s, r) => s + stockOf(r), 0);
      const sets = stocked.filter(isSet).reduce((s, r) => s + stockOf(r), 0);
      const pct = all.length ? Math.round(crit * 100 / all.length) : 0;
      const tile = (lbl, val, extra, dot) => '<div class="kpi"><div class="lbl">' +
        (dot ? '<span class="dot" style="background:' + dot + '"></span>' : '') + esc(lbl) +
        '</div><div class="val">' + val + (extra ? '<small>' + esc(extra) + '</small>' : '') + '</div></div>';
      $('kpis').innerHTML =
        tile(t('kParts'), all.length, '', '') +
        tile(t('kCrit'), crit, all.length ? (st.lang === 'tr' ? '%' + pct : pct + ' %') : '', 'var(--c)') +
        tile(t('kStocked'), stocked.length, t('kItems'), 'var(--a)') +
        tile(t('kTotal'), total, t('kPcs') + (sets ? ' + ' + sets + ' ' + t('unitSet') : ''), '');
    }
    function renderChips() {
      const all = DATA[st.g] || [], L = UI[st.lang];
      const n = s => all.filter(r => up(r[K.o]) === s).length;
      const chip = (key, label, cnt, on, dot) => '<button class="chip' + (on ? ' on' : '') + '" data-c="' + key + '">' +
        (dot ? '<span class="dot" style="background:' + dot + '"></span>' : '') + esc(label) +
        '<span class="cnt">' + cnt + '</span></button>';
      $('chips').innerHTML =
        chip('', t('all'), all.length, !st.sev, '') +
        chip('C', L.o.C, n('C'), st.sev === 'C', 'var(--c)') +
        chip('B', L.o.B, n('B'), st.sev === 'B', 'var(--b)') +
        chip('A', L.o.A, n('A'), st.sev === 'A', 'var(--a)') +
        chip('stock', t('keep'), all.filter(r => stockOf(r) > 0).length, st.stockOnly, '');
    }
    function renderBody() {
      shown = filtered();
      $('result').textContent = t('results', { n: shown.length });
      [...$('viewSeg').children].forEach(b => b.classList.toggle('on', b.dataset.v === st.view));
      const grid = $('grid'), list = $('list');
      grid.hidden = st.view !== 'grid';
      list.hidden = st.view !== 'list';
      if (!shown.length) {
        const msg = '<div class="empty">' + esc(st.q || st.sev || st.stockOnly ? t('noMatch') : t('noRows', { g: st.g })) + '</div>';
        grid.innerHTML = msg; list.innerHTML = msg; grid.style.display = 'block'; return;
      }
      grid.style.display = '';
      grid.innerHTML = shown.map((r, i) => {
        const s = stockOf(r);
        return '<button class="card sev-' + esc(up(r[K.o])) + '" data-i="' + i + '">' +
          '<div class="row"><div class="tn">' + photo(r, 'img') + '</div>' +
          '<div class="info"><div class="code mono">' + esc(r[K.kod]) + '</div>' +
          '<div class="ttl">' + esc(r[K.ad]) + '</div>' +
          '<div class="mach">' + esc(td(r[K.mak])) + '</div></div></div>' +
          '<div class="cb"><div class="foot">' + badges(r) +
          '<div class="stk' + (s ? '' : ' zero') + '"><b>' + s + '</b><small>' + esc(isSet(r) ? t('unitSet') : t('stock')) + '</small></div></div></div></button>';
      }).join('');
      list.innerHTML = '<table><thead><tr><th></th><th></th><th>' + esc(t('hCode')) + '</th><th>' + esc(t('hPart')) +
        '</th><th class="hide-sm">' + esc(t('hMachine')) + '</th><th>' + esc(t('hClass')) + '</th><th style="text-align:right">' + esc(t('hStock')) + '</th></tr></thead><tbody>' +
        shown.map((r, i) => {
          const s = stockOf(r);
          return '<tr class="r sev-' + esc(up(r[K.o])) + '" data-i="' + i + '"><td class="sev"></td>' +
            '<td>' + photo(r, 'thumb') + '</td>' +
            '<td class="mono code" style="white-space:nowrap">' + esc(r[K.kod]) + '</td>' +
            '<td>' + esc(r[K.ad]) + '</td>' +
            '<td class="hide-sm"><div class="mach">' + esc(td(r[K.mak])) + '</div></td>' +
            '<td>' + badges(r) + '</td>' +
            '<td class="num' + (s ? '' : ' zero') + '">' + s + (isSet(r) ? ' ' + esc(t('unitSet')) : '') + '</td></tr>';
        }).join('') + '</tbody></table>';
    }
    function render() { renderStatic(); renderTabs(); renderKpis(); renderChips(); renderBody(); }

    function openDrawer(r, keepFocus) {
      drawerRow = r;
      const o = up(r[K.o]), a = up(r[K.a]), u = up(r[K.u]), s = stockOf(r), L = UI[st.lang];
      const note = String(r[K.n] || '').trim();
      const fact = (k, badge, txt) => '<div class="fact"><div class="k">' + esc(k) + '</div><div class="v">' + badge + esc(txt) + '</div></div>';
      $('dContent').innerHTML =
        '<div class="ph sev-' + esc(o) + '">' + photo(r) + '</div>' +
        '<div class="dbody">' +
          '<div><span class="code mono">' + esc(r[K.kod]) + '</span><button class="copy" id="copyBtn">' + esc(t('copy')) + '</button>' +
          '<h2>' + esc(r[K.ad]) + '</h2><div class="mach" style="white-space:normal;margin-top:4px">' + esc(td(r[K.mak])) + '</div></div>' +
          '<div class="facts">' +
            fact(t('crit'), '<span class="bd o-' + esc(o) + '">' + esc(o || '—') + '</span>', L.o[o] || '—') +
            fact(t('wear'), '<span class="bd w-' + esc(a) + '">' + esc(a || '—') + '</span>', L.a[a] || '—') +
            fact(t('availShort'), u ? '<span class="bd u-' + esc(u) + '">' + esc(u) + '</span>' : '<span class="bd u-none">?</span>', L.u[u] || t('unassigned')) +
          '</div>' +
          '<div class="stockbox"><b style="color:' + (s ? 'var(--a)' : 'var(--faint)') + '">' + s + '</b>' +
            '<div class="t"><strong>' + esc(s ? (isSet(r) ? t('recSet') : t('recQty')) : t('notStocked')) + '</strong>' + esc(td(r[K.g] || '')) + '</div></div>' +
          (note && note !== NOTE_PLACEHOLDER ? '<div class="sec"><div class="k">' + esc(t('note')) + '</div><p>' + esc(td(note)) + '</p></div>' : '') +
        '</div>';
      $('copyBtn').onclick = e => {
        e.stopPropagation();
        const btn = e.currentTarget;
        const done = () => { btn.textContent = t('copied'); setTimeout(() => btn.textContent = t('copy'), 1200); };
        try { navigator.clipboard.writeText(String(r[K.kod])).then(done, () => {}); } catch (err) {}
      };
      $('drawer').classList.add('on'); $('drawer').setAttribute('aria-hidden', 'false');
      $('scrim').classList.add('on');
      if (!keepFocus) $('dClose').focus();
    }
    function closeDrawer() {
      drawerRow = null;
      $('drawer').classList.remove('on'); $('drawer').setAttribute('aria-hidden', 'true');
      $('scrim').classList.remove('on');
    }

    // Dil menüsü
    function setLang(id) {
      st.lang = id; store.set('lang', id);
      render();
      if (drawerRow) openDrawer(drawerRow, true);
    }
    function toggleLang(open) {
      const menu = $('langMenu');
      open = open ?? menu.hidden;
      menu.hidden = !open;
      $('langBtn').setAttribute('aria-expanded', String(open));
      if (open) {
        const items = [...menu.children];
        items.forEach(li => li.classList.toggle('focus', li.dataset.l === st.lang));
        menu.focus();
      }
    }
    $('langBtn').onclick = e => { e.stopPropagation(); toggleLang(); };
    $('langMenu').onclick = e => {
      const li = e.target.closest('li'); if (!li) return;
      toggleLang(false); setLang(li.dataset.l); $('langBtn').focus();
    };
    $('langMenu').onkeydown = e => {
      const items = [...$('langMenu').children];
      let i = items.findIndex(li => li.classList.contains('focus'));
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        i = (i + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length;
        items.forEach((li, j) => li.classList.toggle('focus', j === i));
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault(); if (i >= 0) { toggleLang(false); setLang(items[i].dataset.l); $('langBtn').focus(); }
      } else if (e.key === 'Escape' || e.key === 'Tab') {
        toggleLang(false); $('langBtn').focus();
      }
    };
    document.addEventListener('click', e => { if (!$('lang').contains(e.target)) toggleLang(false); });

    $('tabs').onclick = e => { const b = e.target.closest('button'); if (!b) return; st.g = b.dataset.g; st.sev = ''; st.stockOnly = false; store.set('g', st.g); render(); };
    $('chips').onclick = e => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.c === 'stock') st.stockOnly = !st.stockOnly; else st.sev = b.dataset.c;
      renderChips(); renderBody();
    };
    $('q').oninput = e => { st.q = e.target.value.trim(); renderBody(); };
    $('sort').onchange = e => { st.sort = e.target.value; renderBody(); };
    $('viewSeg').onclick = e => { const b = e.target.closest('button'); if (!b) return; st.view = b.dataset.v; store.set('view', st.view); renderBody(); };
    const pick = e => { const el = e.target.closest('[data-i]'); if (el) openDrawer(shown[+el.dataset.i]); };
    $('grid').onclick = pick; $('list').onclick = pick;
    $('scrim').onclick = closeDrawer; $('dClose').onclick = closeDrawer;
    $('helpBtn').onclick = () => $('help').showModal();
    $('helpClose').onclick = () => $('help').close();
    $('help').onclick = e => { if (e.target === $('help')) $('help').close(); };
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeDrawer();
      if (e.key === '/' && !/^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName)) { e.preventDefault(); $('q').focus(); }
    });

    const theme = store.get('theme');
    if (theme) document.documentElement.dataset.theme = theme;
    $('themeBtn').onclick = () => {
      const dark = document.documentElement.dataset.theme
        ? document.documentElement.dataset.theme === 'dark'
        : matchMedia('(prefers-color-scheme: dark)').matches;
      const next = dark ? 'light' : 'dark';
      document.documentElement.dataset.theme = next; store.set('theme', next);
    };

    render();
  </script>
</body>
</html>
'''


def load_ceviri() -> dict[str, dict[str, str]]:
    """Veri metni çevirileri: {"en": {tr: en}, "de": {tr: de}}."""
    if not os.path.isfile(CEVIRI_PATH):
        return {}
    with open(CEVIRI_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def missing_translations(data: dict[str, list[dict]], i18n: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    """Çevirisi olmayan Türkçe metinler (küçük harf içerenler; 'LYM 950' gibi model adları çevrilmez)."""
    texts = {
        str(r.get(c, "")).strip()
        for rows in data.values() for r in rows
        for c in ("Varyant / makine", "Not")  # stok gerekçesi formülden çevrilir
    }
    texts = {t for t in texts if re.search(r"[a-zçğıöşü]", t)}
    return {lang: sorted(t for t in texts if t not in tr) for lang, tr in i18n.items()}


def embed_photos(data: dict[str, list[dict]], max_side: int = 640) -> dict[str, str]:
    """Kullanılan her fotoğrafı küçültüp data URI yapar; HTML tek başına gönderilse de fotoğraflar görünür."""
    out: dict[str, str] = {}
    for rows in data.values():
        for r in rows:
            rel = str(r.get("Fotoğraf", "")).strip()
            src = os.path.join(FOLDER, rel)
            if not rel or rel in out or not os.path.isfile(src):
                continue
            with Image.open(src) as im:
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, "white")
                bg.paste(im, mask=im.split()[3])
                bg.thumbnail((max_side, max_side))
                buf = io.BytesIO()
                bg.save(buf, "JPEG", quality=82, optimize=True)
            out[rel] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    return out


def write_html(path: str, data: dict[str, list[dict]]) -> None:
    cols_json = json.dumps(COLS, ensure_ascii=False)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    i18n = load_ceviri()
    # Stok gerekçeleri formülden üretildiği için çevirileri de buradan eklenir.
    for rows in data.values():
        for r in rows:
            _, tr, en, de = stok_hesapla(r)
            i18n.setdefault("en", {})[tr] = en
            i18n.setdefault("de", {})[tr] = de
    i18n_json = json.dumps(i18n, ensure_ascii=False).replace("</", "<\\/")
    rules = [{"k": k[0], "n": k[4], "t": {"tr": k[5], "en": k[6], "de": k[7]}} for k in STOK_KURALLARI]
    html = (
        HTML_TEMPLATE.replace("__COLS__", cols_json)
        .replace("__DATA__", payload)
        .replace("__I18N__", i18n_json)
        .replace("__RULES__", json.dumps(rules, ensure_ascii=False))
        .replace("__IMGS__", json.dumps(embed_photos(data)))
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main() -> None:
    data = load_data()
    with open(VERI_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    write_excel(os.path.join(FOLDER, "Kritik-Parca-Listeleri.xlsx"), data)
    write_html(os.path.join(FOLDER, "kritik-parca-listeleri.html"), data)
    for lang, miss in missing_translations(data, load_ceviri()).items():
        if miss:
            print(f"Çeviri eksik ({lang}): {len(miss)} metin Türkçe gösterilecek")
    linked = sum(1 for rows in data.values() for r in rows if r.get("Fotoğraf"))
    print("Sablon OK:", date.today().isoformat(), f"| foto bağlı: {linked}")


if __name__ == "__main__":
    main()
