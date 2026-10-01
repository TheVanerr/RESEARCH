# -*- coding: utf-8 -*-
"""Boş kritik parça şablonu — Excel + HTML (ürün ağacı doldurma yok)."""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from datetime import date

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

FOLDER = os.path.dirname(os.path.abspath(__file__))
VERI_PATH = os.path.join(FOLDER, "kritik-parca-veri.json")
PHOTOS_DIR = os.path.join(FOLDER, "photos")
_PHOTO_PREF = {".jpg": 0, ".jpeg": 1, ".png": 2, ".webp": 3, ".jfif": 4}


def norm_siparis(raw) -> str | None:
    if raw is None:
        return None
    compact = re.sub(r"\s+", "", str(raw).strip())
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


def apply_photos(data: dict[str, list[dict]]) -> int:
    photos = photo_map()
    n = 0
    for rows in data.values():
        for r in rows:
            code = norm_siparis(r.get("Sipariş kodu", ""))
            if code and code in photos:
                if r.get("Fotoğraf") != photos[code]:
                    r["Fotoğraf"] = photos[code]
                    n += 1
    return n


def normalize_row(r: dict) -> dict:
    r.setdefault("Fotoğraf", "")
    stok = str(r.get("Önerilen stok (adet)", "")).strip()
    if stok == "":
        r["Önerilen stok (adet)"] = "0"
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
    ("Stok ipucu", "C+3 → genelde stok 0, listede kalsın | 1+K → depo stoku adayı"),
]


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

    widths = (14, 40, 22, 22, 14, 14, 18, 16, 28, 24)
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


def write_html(path: str, data: dict[str, list[dict]]) -> None:
    cols_json = json.dumps(COLS, ensure_ascii=False)
    payload = json.dumps(data, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Kritik parça listesi</title>
  <style>
    :root {{
      --bg:#0b1220; --bg2:#111827; --surface:#ffffff; --surface2:#f8fafc;
      --border:#e2e8f0; --text:#0f172a; --muted:#64748b;
      --accent:#3b82f6; --accent2:#6366f1;
      --c-bg:#fef2f2; --c-fg:#b91c1c; --c-bar:#ef4444;
      --b-bg:#fff7ed; --b-fg:#c2410c; --b-bar:#f97316;
      --a-bg:#ecfdf5; --a-fg:#047857; --a-bar:#10b981;
      --wear1:#dbeafe; --wear2:#e0e7ff; --wear3:#f1f5f9;
      --k-bg:#dcfce7; --k-fg:#166534;
      --o-bg:#fef9c3; --o-fg:#a16207;
      --z-bg:#fce7f3; --z-fg:#be185d;
      --stock-yes:#059669; --stock-no:#94a3b8;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0; font-family:"Segoe UI",system-ui,-apple-system,sans-serif;
      background:linear-gradient(160deg,#0b1220 0%,#1e293b 45%,#eef2ff 45%,#eef2ff 100%);
      color:var(--text); min-height:100vh;
    }}
    header {{
      background:linear-gradient(135deg,#0f172a 0%,#1d4ed8 55%,#4f46e5 100%);
      color:#fff; padding:1.5rem 1.75rem 1.75rem;
      box-shadow:0 8px 32px rgba(15,23,42,.35);
    }}
    header h1 {{ margin:0 0 .4rem; font-size:1.5rem; font-weight:700; letter-spacing:-.02em; }}
    header p {{ margin:0; opacity:.92; font-size:.9rem; line-height:1.45; }}
    main {{ width:100%; max-width:none; margin:0; padding:1rem 1.25rem 2rem; }}
    .guide-bar {{
      display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.85rem 1.25rem;
      padding:1rem 1.15rem; border-bottom:1px solid var(--border);
      background:linear-gradient(180deg,#f8fafc,#fff); font-size:.78rem; line-height:1.45;
    }}
    @media (max-width:1100px) {{ .guide-bar {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
    @media (max-width:640px) {{ .guide-bar {{ grid-template-columns:1fr; }} }}
    .guide-bar h2 {{ margin:0 0 .25rem; font-size:.9rem; color:#1e293b; grid-column:1/-1; font-weight:800; }}
    .guide-bar .block {{ min-width:0; }}
    .guide-bar .block-wide {{ grid-column:1/-1; background:#f1f5f9; border-radius:10px; padding:.75rem .9rem; border:1px solid #e2e8f0; }}
    .guide-bar .matrix {{ width:100%; border-collapse:collapse; font-size:.72rem; margin-top:.35rem; }}
    .guide-bar .matrix th {{ background:#334155; color:#e2e8f0; padding:.35rem .5rem; text-align:left; font-weight:700; }}
    .guide-bar .matrix td {{ padding:.35rem .5rem; border-bottom:1px solid #e2e8f0; vertical-align:top; background:#fff; }}
    .guide-bar .matrix code {{ background:#e2e8f0; color:#0f172a; }}
    .guide-bar .block strong {{ display:block; margin-bottom:.35rem; color:#334155; font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; }}
    .guide-bar dl {{ margin:0; }}
    .guide-bar dt {{ font-weight:700; margin-top:.25rem; display:flex; align-items:center; gap:.35rem; }}
    .guide-bar dd {{ margin:.1rem 0 0; color:var(--muted); font-size:.75rem; }}
    .guide-bar p {{ margin:0; color:var(--muted); font-size:.75rem; }}
    .tag {{ display:inline-flex; align-items:center; justify-content:center; min-width:1.5rem;
      padding:.15rem .45rem; border-radius:6px; font-size:.72rem; font-weight:800; letter-spacing:.04em; }}
    .tag-c {{ background:var(--c-bg); color:var(--c-fg); }}
    .tag-b {{ background:var(--b-bg); color:var(--b-fg); }}
    .tag-a {{ background:var(--a-bg); color:var(--a-fg); }}
    .panel {{
      background:var(--surface); border:1px solid var(--border); border-radius:16px;
      overflow:hidden; box-shadow:0 8px 40px rgba(15,23,42,.1);
    }}
    .toolbar {{
      display:flex; flex-wrap:wrap; align-items:center; gap:.75rem 1rem;
      padding:.85rem 1.1rem; border-bottom:1px solid var(--border);
      background:linear-gradient(180deg,#fafbff,#fff);
    }}
    .tabs {{ display:flex; gap:.45rem; flex-wrap:wrap; }}
    .tabs button {{
      border:1px solid var(--border); background:#fff; padding:.45rem 1rem;
      border-radius:10px; font-weight:700; font-size:.82rem; cursor:pointer;
      transition:all .15s ease; color:#334155;
    }}
    .tabs button:hover {{ border-color:#93c5fd; background:#eff6ff; }}
    .tabs button.active {{
      background:linear-gradient(135deg,var(--accent),var(--accent2));
      color:#fff; border-color:transparent; box-shadow:0 4px 14px rgba(59,130,246,.35);
    }}
    .stats {{ display:flex; flex-wrap:wrap; gap:.5rem; margin-left:auto; }}
    .stat {{
      display:inline-flex; align-items:center; gap:.35rem; padding:.35rem .65rem;
      border-radius:999px; font-size:.72rem; font-weight:700; border:1px solid var(--border);
      background:#fff;
    }}
    .stat-c {{ border-color:#fecaca; background:var(--c-bg); color:var(--c-fg); }}
    .stat-b {{ border-color:#fed7aa; background:var(--b-bg); color:var(--b-fg); }}
    .stat-a {{ border-color:#a7f3d0; background:var(--a-bg); color:var(--a-fg); }}
    .stat-n {{ color:var(--muted); font-weight:600; }}
    .search-wrap {{ flex:1; min-width:180px; max-width:280px; }}
    .search-wrap input {{
      width:100%; padding:.5rem .75rem .5rem 2.1rem; border:1px solid var(--border);
      border-radius:10px; font-size:.85rem; background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%2394a3b8' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85zm-5.242 1.156a5 5 0 1 1 0-10 5 5 0 0 1 0 10z'/%3E%3C/svg%3E") no-repeat .65rem center;
    }}
    .search-wrap input:focus {{ outline:2px solid #bfdbfe; border-color:#93c5fd; }}
    .table-wrap {{ overflow:auto; max-height:calc(100vh - 280px); width:100%; }}
    table {{ width:100%; border-collapse:separate; border-spacing:0; font-size:.8125rem; }}
    th {{
      background:#1e293b; color:#e2e8f0; text-align:left; padding:.65rem .7rem; font-size:.68rem;
      text-transform:uppercase; letter-spacing:.06em; font-weight:700;
      position:sticky; top:0; z-index:2; border-bottom:2px solid #334155;
    }}
    th:first-child {{ border-radius:0; left:0; z-index:3; }}
    td {{ padding:.55rem .7rem; border-bottom:1px solid #f1f5f9; vertical-align:middle; background:#fff; }}
    tr.data-row {{ transition:background .12s ease; }}
    tr.data-row:hover td {{ background:#f8fafc; }}
    tr.row-c td {{ box-shadow:inset 4px 0 0 var(--c-bar); }}
    tr.row-b td {{ box-shadow:inset 4px 0 0 var(--b-bar); }}
    tr.row-a td {{ box-shadow:inset 4px 0 0 var(--a-bar); }}
    tr.row-c td:first-child {{ background:linear-gradient(90deg,#fff5f5,#fff); }}
    tr.row-b td:first-child {{ background:linear-gradient(90deg,#fffaf5,#fff); }}
    tr.row-a td:first-child {{ background:linear-gradient(90deg,#f0fdf9,#fff); }}
    td.col-kod {{ font-family:Consolas,"Cascadia Mono",monospace; font-weight:600; font-size:.78rem;
      color:#1e40af; white-space:nowrap; position:sticky; left:0; z-index:1;
      box-shadow:2px 0 6px rgba(15,23,42,.04);
    }}
    td.col-ad {{ font-weight:500; color:#0f172a; max-width:280px; }}
    td.col-variant {{ color:var(--muted); font-size:.78rem; max-width:200px; }}
    td.col-foto {{ width:72px; text-align:center; padding:.4rem .35rem; }}
    .photo-ph {{
      width:56px; height:56px; margin:0 auto; border-radius:10px; border:2px dashed #cbd5e1;
      background:#f8fafc; display:flex; align-items:center; justify-content:center;
      color:#94a3b8; font-size:.62rem; font-weight:700; text-transform:uppercase;
    }}
    .photo-thumb {{
      width:56px; height:56px; object-fit:cover; border-radius:10px; border:1px solid var(--border);
      display:block; margin:0 auto; box-shadow:0 2px 8px rgba(15,23,42,.08);
    }}
    .photo-path {{ font-size:.68rem; color:var(--muted); word-break:break-all; max-width:90px; display:inline-block; }}
    .pill {{
      display:inline-flex; align-items:center; justify-content:center; min-width:1.75rem;
      padding:.2rem .55rem; border-radius:8px; font-size:.75rem; font-weight:800;
      letter-spacing:.03em; line-height:1.2;
    }}
    .pill-onem-C {{ background:var(--c-bg); color:var(--c-fg); box-shadow:0 0 0 1px #fecaca inset; }}
    .pill-onem-B {{ background:var(--b-bg); color:var(--b-fg); box-shadow:0 0 0 1px #fed7aa inset; }}
    .pill-onem-A {{ background:var(--a-bg); color:var(--a-fg); box-shadow:0 0 0 1px #a7f3d0 inset; }}
    .pill-wear-1 {{ background:var(--wear1); color:#1d4ed8; }}
    .pill-wear-2 {{ background:var(--wear2); color:#4338ca; }}
    .pill-wear-3 {{ background:var(--wear3); color:#475569; }}
    .pill-ul-K {{ background:var(--k-bg); color:var(--k-fg); }}
    .pill-ul-O {{ background:var(--o-bg); color:var(--o-fg); }}
    .pill-ul-Z {{ background:var(--z-bg); color:var(--z-fg); }}
    .pill-ul-empty {{ background:#f1f5f9; color:#94a3b8; box-shadow:0 0 0 1px #e2e8f0 inset; }}
    .stock-hint {{ display:block; font-size:.62rem; color:#94a3b8; font-weight:600; margin-top:.2rem; }}
    .stock {{
      display:inline-flex; align-items:center; justify-content:center; min-width:2rem;
      padding:.25rem .5rem; border-radius:8px; font-weight:800; font-size:.85rem;
    }}
    .stock-pos {{ background:#ecfdf5; color:var(--stock-yes); box-shadow:0 0 0 1px #a7f3d0 inset; }}
    .stock-zero {{ background:#f1f5f9; color:var(--stock-no); }}
    .stock-empty {{ color:#cbd5e1; font-weight:600; }}
    .note {{ font-size:.75rem; color:var(--muted); font-style:italic; }}
    .empty {{ padding:3rem 1rem; text-align:center; color:var(--muted); }}
    code {{ font-family:Consolas,monospace; font-size:.78rem; background:rgba(255,255,255,.15);
      padding:.12rem .4rem; border-radius:4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Kritik parça listesi · LYM · VDL · KBN</h1>
    <p>Önem <strong>A / B / C</strong> · Aşınma <strong>1 / 2 / 3</strong> · Ulaşılabilirlik <strong>K / O / Z</strong> — kaynak: <code>kritik-parca-veri.json</code></p>
  </header>
  <main>
    <div class="panel">
      <div class="toolbar">
        <div class="tabs" id="tabs"></div>
        <div class="search-wrap"><input type="search" id="q" placeholder="Kod veya parça ara…" autocomplete="off"/></div>
        <div class="stats" id="stats"></div>
      </div>
      <div class="guide-bar">
        <h2>Sınıflandırma ve önerilen stok</h2>
        <div class="block">
          <strong>Önem · A / B / C</strong>
          <dl>
            <dt><span class="tag tag-c">C</span> Kritik</dt>
            <dd>Arızada makine <em>çalışmaz</em> veya emniyet onayı yok (PLC, seviye, kapak). Satır: <strong>kırmızı</strong> sol çubuk.</dd>
            <dt><span class="tag tag-b">B</span> Kısıtlı</dt>
            <dd>Kısa sürede duruş, kapasite veya kalite ciddi düşer. <strong>Turuncu</strong> çubuk.</dd>
            <dt><span class="tag tag-a">A</span> İkincil</dt>
            <dd>Makine çalışır; konfor/kalite etkisi. <strong>Yeşil</strong> çubuk. Tabloda renkli pill.</dd>
          </dl>
        </div>
        <div class="block">
          <strong>Aşınma · 1 / 2 / 3</strong>
          <dl>
            <dt><span class="pill pill-wear-1">1</span> Sık</dt>
            <dd>Bakımda, aylık–yıllık değişim (kontaktör, filtre, teker).</dd>
            <dt><span class="pill pill-wear-2">2</span> Orta</dt>
            <dd>Birkaç yıl / planlı ömür (nozzle, termik, rezistans).</dd>
            <dt><span class="pill pill-wear-3">3</span> Seyrek</dt>
            <dd>Normalde arıza yok; darbe, kaza, yaşlanma olayı.</dd>
          </dl>
        </div>
        <div class="block">
          <strong>Ulaşılabilirlik · K / O / Z</strong>
          <dl>
            <dt><span class="pill pill-ul-K">K</span> Kolay</dt>
            <dd>Piyasa, günler (kontaktör, termik).</dd>
            <dt><span class="pill pill-ul-O">O</span> Orta</dt>
            <dd>Bayi / ithalat, haftalar (sensör, termokupl).</dd>
            <dt><span class="pill pill-ul-Z">Z</span> Zor</dt>
            <dd>ÇNK imalat, tek kaynak (amortisör, özel sac). <strong>—</strong> = henüz atanmadı.</dd>
          </dl>
        </div>
        <div class="block">
          <strong>Tablo okuma</strong>
          <p>Önerilen stok: yeşil kutu = adet &gt; 0, gri <strong>0</strong> = listede tut, depoda tutma. Alt satırda <code>Ö+B+U</code> birleşimi (ör. <code>A+2+K</code>). Ayrıntı: <strong>Stok gerekçesi</strong> sütunu. Fotoğraf: dosya yolu veya URL.</p>
        </div>
        <div class="block block-wide">
          <strong>Önerilen stok nasıl belirlenir? (Önem + Aşınma + Ulaşılabilirlik)</strong>
          <table class="matrix">
            <thead><tr><th>Birleşim</th><th>Tipik anlam</th><th>Önerilen stok</th></tr></thead>
            <tbody>
              <tr><td><code>C + 3</code> (+ Z/O)</td><td>Liste zorunlu; seyrek arıza</td><td><strong>0</strong> — siparişle (termokupl istisna: O ise 1–2)</td></tr>
              <tr><td><code>C + 3 + K</code></td><td>Kritik ama ucuz/hızlı (switch)</td><td><strong>1–3</strong> — emniyet yedek</td></tr>
              <tr><td><code>1 + K</code></td><td>Sık tüketim, piyasa</td><td><strong>2+</strong> — depo seti</td></tr>
              <tr><td><code>A + 2 + K</code></td><td>Orta aşınma, kolay tedarik</td><td><strong>1–2</strong> (termik set: bandı başına 2)</td></tr>
              <tr><td><code>A/B + 2 + Z</code></td><td>İmalat / uzun termin</td><td><strong>1</strong> komple veya hat yedek</td></tr>
              <tr><td><code>B + 3 + K</code></td><td>Olay bazlı, tedarik kolay</td><td><strong>0–1</strong></td></tr>
              <tr><td><code>A + 2</code> (Ulaş. <strong>—</strong>)</td><td>Üçüncü eksen henüz yok</td><td>Geçici adet + not; <strong>K/O/Z</strong> girilince satır güncellenir</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr id="thead"></tr></thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>
  </main>
  <script>
    const COLS = {cols_json};
    const DATA = {payload};
    const KEY_ONEM = "Önem (A/B/C)";
    const KEY_ASINMA = "Aşınma (1/2/3)";
    const KEY_ULAS = "Ulaşılabilirlik (K/O/Z)";
    const KEY_STOK = "Önerilen stok (adet)";
    const KEY_KOD = "Sipariş kodu";
    const KEY_AD = "Parça adı";
    const KEY_FOTO = "Fotoğraf";

    let active = 'LYM';
    let filter = '';
    const tabs = document.getElementById('tabs');
    const thead = document.getElementById('thead');
    const tbody = document.getElementById('tbody');
    const statsEl = document.getElementById('stats');
    document.getElementById('q').oninput = e => {{ filter = e.target.value.trim().toLowerCase(); render(); }};

    ['LYM','VDL','KBN'].forEach(g => {{
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = g;
      b.onclick = () => {{ active = g; render(); }};
      tabs.appendChild(b);
    }});

    function esc(s) {{
      return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }}

    function stockCombo(row) {{
      const o = String(row[KEY_ONEM] ?? '').trim().toUpperCase() || '?';
      const a = String(row[KEY_ASINMA] ?? '').trim() || '?';
      const u = String(row[KEY_ULAS] ?? '').trim().toUpperCase();
      return o + '+' + a + (u ? '+' + u : '+—');
    }}

    function cellHtml(col, val, row) {{
      const v = String(val ?? '').trim();
      if (col === KEY_ONEM && /^[ABC]$/i.test(v)) {{
        const x = v.toUpperCase();
        return '<span class="pill pill-onem-' + x + '">' + x + '</span>';
      }}
      if (col === KEY_ASINMA && /^[123]$/.test(v)) {{
        return '<span class="pill pill-wear-' + v + '">' + v + '</span>';
      }}
      if (col === KEY_ULAS) {{
        if (!v) return '<span class="pill pill-ul-empty" title="Henüz atanmadı">—</span>';
        if (/^[KOZ]$/i.test(v)) {{
          const x = v.toUpperCase();
          return '<span class="pill pill-ul-' + x + '">' + x + '</span>';
        }}
        return esc(v);
      }}
      if (col === KEY_STOK) {{
        const combo = stockCombo(row);
        if (v === '' || v === '—') return '<span class="stock stock-empty">—</span>';
        const n = parseInt(v, 10);
        let inner = '';
        if (n === 0) inner = '<span class="stock stock-zero">0</span>';
        else if (!isNaN(n) && n > 0) inner = '<span class="stock stock-pos">' + n + '</span>';
        else inner = esc(v);
        return inner + '<span class="stock-hint">' + esc(combo) + '</span>';
      }}
      if (col === KEY_FOTO) {{
        if (!v) return '<div class="photo-ph"><span>Foto</span></div>';
        if (/^https?:\\/\\//i.test(v) || /\\.(jpe?g|png|webp|gif|svg)$/i.test(v))
          return '<img class="photo-thumb" src="' + esc(v) + '" alt="" loading="lazy"/>';
        return '<span class="photo-path">' + esc(v) + '</span>';
      }}
      if (col === KEY_KOD) return esc(v);
      if (col === KEY_AD) return esc(v);
      if (col === 'Not') return v ? '<span class="note">' + esc(v) + '</span>' : '<span class="note note-missing">—</span>';
      return esc(v);
    }}

    function rowClass(row) {{
      const o = String(row[KEY_ONEM] ?? '').trim().toUpperCase();
      if (o === 'C') return 'row-c';
      if (o === 'B') return 'row-b';
      if (o === 'A') return 'row-a';
      return '';
    }}

    function colClass(col) {{
      if (col === KEY_KOD) return 'col-kod';
      if (col === KEY_AD) return 'col-ad';
      if (col === KEY_FOTO) return 'col-foto';
      if (col === 'Varyant / makine') return 'col-variant';
      return '';
    }}

    function render() {{
      [...tabs.children].forEach(b => b.classList.toggle('active', b.textContent === active));
      thead.innerHTML = COLS.map(c => '<th>' + esc(c) + '</th>').join('');
      let rows = DATA[active] || [];
      if (filter) {{
        rows = rows.filter(r => {{
          const hay = (r[KEY_KOD] + ' ' + r[KEY_AD] + ' ' + (r['Varyant / makine']||'')).toLowerCase();
          return hay.includes(filter);
        }});
      }}
      const all = DATA[active] || [];
      const c = all.filter(r => String(r[KEY_ONEM]).toUpperCase() === 'C').length;
      const b = all.filter(r => String(r[KEY_ONEM]).toUpperCase() === 'B').length;
      const a = all.filter(r => String(r[KEY_ONEM]).toUpperCase() === 'A').length;
      statsEl.innerHTML =
        '<span class="stat stat-c">C <span class="stat-n">' + c + '</span></span>' +
        '<span class="stat stat-b">B <span class="stat-n">' + b + '</span></span>' +
        '<span class="stat stat-a">A <span class="stat-n">' + a + '</span></span>' +
        '<span class="stat"><span class="stat-n">' + all.length + ' satır</span></span>';

      if (!rows.length) {{
        tbody.innerHTML = '<tr><td colspan="' + COLS.length + '" class="empty">' +
          '<p><strong>' + esc(active) + '</strong> — ' + (filter ? 'eşleşme yok.' : 'henüz satır yok.') + '</p></td></tr>';
        return;
      }}
      tbody.innerHTML = rows.map(r => {{
        const rc = rowClass(r);
        return '<tr class="data-row ' + rc + '">' + COLS.map(c =>
          '<td class="' + colClass(c) + '">' + cellHtml(c, r[c], r) + '</td>'
        ).join('') + '</tr>';
      }}).join('');
    }}
    render();
  </script>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main() -> None:
    data = load_data()
    with open(VERI_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    write_excel(os.path.join(FOLDER, "Kritik-Parca-Listeleri.xlsx"), data)
    write_html(os.path.join(FOLDER, "kritik-parca-listeleri.html"), data)
    linked = sum(1 for rows in data.values() for r in rows if r.get("Fotoğraf"))
    print("Sablon OK:", date.today().isoformat(), f"| foto bağlı: {linked}")


if __name__ == "__main__":
    main()
