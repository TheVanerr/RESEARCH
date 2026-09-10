#!/usr/bin/env python3
"""Convert WASHING REPORT Excel to a single self-contained HTML file."""

import base64
import html
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

BASE = Path(r"c:\Users\fatih.gural\Desktop\PROJECTS\RESEARCH\Mattheus Washing Report")
EXCEL = BASE / "WASHING REPORT 2.xlsm"
OUT_HTML = BASE / "washing-report.html"
NOTE_PHOTO_GLOB = "IMG_*.jpg"
NOTE_PHOTO_MAX_PX = 480
NOTE_PHOTO_QUALITY = 82

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def col_letters(col: int) -> str:
    s = ""
    while col:
        col, rem = divmod(col - 1, 26)
        s = chr(65 + rem) + s
    return s


def parse_cell_ref(ref: str) -> tuple[int, int]:
    m = re.match(r"([A-Z]+)(\d+)", ref)
    col = 0
    for ch in m.group(1):
        col = col * 26 + (ord(ch) - 64)
    return col, int(m.group(2))


def load_shared_strings(z: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    strings = []
    for si in root.findall(".//m:si", NS):
        parts = [t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")]
        strings.append("".join(parts))
    return strings


def load_vm_to_image(z: zipfile.ZipFile) -> dict[int, str]:
    rels_root = ET.fromstring(z.read("xl/richData/_rels/richValueRel.xml.rels"))
    rid_to_file = {}
    for rel in rels_root.findall("rel:Relationship", NS):
        target = rel.get("Target", "")
        if "media/" in target:
            rid_to_file[rel.get("Id")] = Path(target).name

    rv_root = ET.fromstring(z.read("xl/richData/richValueRel.xml"))
    rel_ids = [
        rel.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        for rel in rv_root.findall(
            "rv:rel",
            {**NS, "rv": "http://schemas.microsoft.com/office/spreadsheetml/2022/richvaluerel"},
        )
    ]

    meta = ET.fromstring(z.read("xl/metadata.xml"))
    vm_map = {}
    for idx, bk in enumerate(meta.findall(".//m:valueMetadata/m:bk", NS), start=1):
        rc = bk.find("m:rc", NS)
        rich_idx = int(rc.get("v"))
        rid = rel_ids[rich_idx]
        vm_map[idx] = rid_to_file[rid]
    return vm_map


def file_to_data_uri(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def compress_jpeg_for_embed(path: Path) -> str:
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((NOTE_PHOTO_MAX_PX, NOTE_PHOTO_MAX_PX), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=NOTE_PHOTO_QUALITY, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"


def load_note_photo_uris() -> list[str]:
    photos = sorted(BASE.glob(NOTE_PHOTO_GLOB))
    if len(photos) != 11:
        raise SystemExit(f"Expected 11 note photos ({NOTE_PHOTO_GLOB}), found {len(photos)}")
    return [compress_jpeg_for_embed(p) for p in photos]


def load_image_data_uris(z: zipfile.ZipFile, vm_map: dict[int, str], vm_cells: dict) -> dict[str, str]:
    cache: dict[str, str] = {}
    cell_images: dict[str, str] = {}

    for ref, vm in vm_cells.items():
        src_name = vm_map.get(vm)
        if not src_name:
            continue
        if src_name not in cache:
            raw = z.read(f"xl/media/{src_name}")
            b64 = base64.b64encode(raw).decode("ascii")
            cache[src_name] = f"data:image/png;base64,{b64}"
        cell_images[ref] = cache[src_name]
    return cell_images


def parse_sheet(z: zipfile.ZipFile, strings: list[str]) -> tuple[dict, dict]:
    root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    cells = {}
    vm_cells = {}
    for row in root.findall(".//m:sheetData/m:row", NS):
        for c in row.findall("m:c", NS):
            ref = c.get("r")
            col, row_num = parse_cell_ref(ref)
            if row_num < 2 or col < 2:
                continue
            vm = c.get("vm")
            if vm:
                vm_cells[ref] = int(vm)
                continue
            t = c.get("t")
            v_el = c.find("m:v", NS)
            if v_el is None or v_el.text is None:
                continue
            val = v_el.text
            if t == "s":
                val = strings[int(val)]
            elif t == "e":
                continue
            cells[ref] = val
    return cells, vm_cells


def img_tag(data_uri: str, alt: str, lazy: bool = False) -> str:
    attrs = f' decoding="async" alt="{html.escape(alt)}"'
    if lazy:
        attrs += ' loading="lazy"'
    return f'<img src="{data_uri}"{attrs}>'


def td_text(value) -> str:
    return f'<td class="text-cell">{html.escape(str(value))}</td>'


def td_photo(data_uri: str | None, alt: str) -> str:
    if not data_uri:
        return "<td class=\"photo-cell\"></td>"
    return f'<td class="photo-cell">{img_tag(data_uri, alt)}</td>'


def build_html(cells: dict, cell_images: dict, note_photo_uris: list[str]) -> str:
    headers = [
        "TEST NO",
        "TEMPERATURE (°C)",
        "CHEMICAL THAT USED",
        "TIME (dk)",
        "PARTS DIRECTION",
        "PARTS DIRECTION PHOTO",
        "PARTS PHOTO",
        "PARTS PHOTO",
        "PARTS PHOTO",
        "PARTS PHOTO",
        "PARTS PHOTO",
    ]
    header_html = "".join(f"<th>{html.escape(h)}</th>" for h in headers)

    rows_html = []
    for row in range(3, 8):
        no = cells.get(f"B{row}", "")
        rows_html.append(
            '<tr class="data-row">'
            + td_text(no)
            + td_text(cells.get(f"C{row}", ""))
            + td_text(cells.get(f"D{row}", ""))
            + td_text(cells.get(f"E{row}", ""))
            + td_text(cells.get(f"F{row}", ""))
            + td_photo(cell_images.get(f"G{row}"), f"Test {no} direction")
            + "".join(
                td_photo(cell_images.get(f"{col_letters(c)}{row}"), f"Test {no} part {c - 7}")
                for c in range(8, 13)
            )
            + "</tr>"
        )

    summary = cells.get("B8", "")
    col_count = len(headers)
    note_text = (
        "Note: After a few days without any processing, the quality of the sample "
        "surfaces remains as shown in the photos below."
    )
    note_photos_html = "".join(
        f'<td class="photo-cell" data-note-photo="{i}"></td>'
        for i in range(len(note_photo_uris))
    )
    note_photos_json = json.dumps(note_photo_uris, separators=(",", ":"))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Washing Report</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 12px;
      font-family: Calibri, "Segoe UI", Arial, sans-serif;
      font-size: 11pt;
      color: #000;
      background: #fff;
    }}
    .sheet-wrap {{
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }}
    table.report {{
      border-collapse: collapse;
      table-layout: fixed;
      width: max-content;
      min-width: 100%;
      background: #fff;
    }}
    table.report th,
    table.report td {{
      border: 1px solid #000;
      padding: 4px 6px;
      vertical-align: middle;
      text-align: center;
      word-wrap: break-word;
    }}
    table.report thead th {{
      background: #d9e1f2;
      font-weight: 700;
      font-size: 10pt;
      line-height: 1.2;
      height: 36px;
    }}
    table.report tbody tr.data-row td {{
      height: 160px;
    }}
    table.report td.text-cell {{
      width: 110px;
      min-width: 90px;
      max-width: 130px;
    }}
    table.report td.photo-cell {{
      width: 180px;
      min-width: 150px;
      padding: 2px;
      vertical-align: middle;
    }}
    table.report td.photo-cell img {{
      display: block;
      width: 100%;
      height: auto;
      max-height: 154px;
      object-fit: contain;
      margin: 0 auto;
      cursor: zoom-in;
    }}
    .lightbox {{
      display: none;
      position: fixed;
      inset: 0;
      z-index: 9999;
      background: rgba(0, 0, 0, 0.9);
      align-items: center;
      justify-content: center;
      padding: 16px;
      cursor: zoom-out;
    }}
    .lightbox.open {{ display: flex; }}
    .lightbox img {{
      max-width: 96vw;
      max-height: 92vh;
      object-fit: contain;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }}
    .lightbox-close {{
      position: absolute;
      top: 12px;
      right: 16px;
      color: #fff;
      font-size: 28px;
      line-height: 1;
      cursor: pointer;
      user-select: none;
    }}
    table.report tr.summary-row td {{
      text-align: left;
      vertical-align: top;
      height: auto;
      padding: 8px 10px;
      font-size: 10pt;
      line-height: 1.45;
      background: #fff;
    }}
    table.report tr.note-row td {{
      text-align: left;
      vertical-align: top;
      height: auto;
      padding: 8px 10px;
      font-size: 10pt;
      line-height: 1.45;
      background: #fff;
      font-style: italic;
    }}
    table.report tr.note-photos-row {{
      content-visibility: auto;
      contain-intrinsic-size: auto 160px;
    }}
    table.report tr.note-photos-row td {{
      height: 160px;
    }}
    /* Excel-like column widths */
    col.c-no {{ width: 80px; }}
    col.c-temp {{ width: 100px; }}
    col.c-chem {{ width: 130px; }}
    col.c-time {{ width: 80px; }}
    col.c-dir {{ width: 110px; }}
    col.c-photo {{ width: 180px; }}
    @media (max-width: 768px) {{
      body {{ padding: 6px; }}
      table.report td.photo-cell {{ width: 140px; min-width: 120px; }}
      table.report td.photo-cell img {{ max-height: 120px; }}
    }}
    @media print {{
      body {{ padding: 0; }}
      .sheet-wrap {{ overflow: visible; }}
      .lightbox {{ display: none !important; }}
    }}
  </style>
</head>
<body>
  <div class="sheet-wrap">
    <table class="report">
      <colgroup>
        <col class="c-no">
        <col class="c-temp">
        <col class="c-chem">
        <col class="c-time">
        <col class="c-dir">
        <col class="c-photo">
        <col class="c-photo">
        <col class="c-photo">
        <col class="c-photo">
        <col class="c-photo">
        <col class="c-photo">
      </colgroup>
      <thead>
        <tr>{header_html}</tr>
      </thead>
      <tbody>
        {''.join(rows_html)}
        <tr class="summary-row">
          <td colspan="{col_count}">{html.escape(summary)}</td>
        </tr>
        <tr class="note-row">
          <td colspan="{col_count}">{html.escape(note_text)}</td>
        </tr>
        <tr class="note-photos-row">
          {note_photos_html}
        </tr>
      </tbody>
    </table>
  </div>

  <div class="lightbox" id="lightbox" aria-hidden="true">
    <span class="lightbox-close" id="lightbox-close">&times;</span>
    <img id="lightbox-img" src="" alt="">
  </div>

  <script>
    (function () {{
      var lb = document.getElementById('lightbox');
      var lbImg = document.getElementById('lightbox-img');
      var lbClose = document.getElementById('lightbox-close');

      function openLightbox(src, alt) {{
        lbImg.src = src;
        lbImg.alt = alt || '';
        lb.classList.add('open');
        lb.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
      }}

      function closeLightbox() {{
        lb.classList.remove('open');
        lb.setAttribute('aria-hidden', 'true');
        lbImg.src = '';
        document.body.style.overflow = '';
      }}

      document.addEventListener('click', function (e) {{
        if (e.target.matches('.photo-cell img')) {{
          e.stopPropagation();
          openLightbox(e.target.src, e.target.alt);
        }}
      }});

      lb.addEventListener('click', closeLightbox);
      lbClose.addEventListener('click', function (e) {{
        e.stopPropagation();
        closeLightbox();
      }});
      lbImg.addEventListener('click', function (e) {{ e.stopPropagation(); }});

      document.addEventListener('keydown', function (e) {{
        if (e.key === 'Escape') closeLightbox();
      }});

      var notePhotos = {note_photos_json};
      document.querySelectorAll('[data-note-photo]').forEach(function (td) {{
        var idx = parseInt(td.getAttribute('data-note-photo'), 10);
        var img = document.createElement('img');
        img.src = notePhotos[idx];
        img.alt = 'Surface quality photo ' + (idx + 1);
        img.loading = 'lazy';
        img.decoding = 'async';
        td.appendChild(img);
      }});
    }})();
  </script>
</body>
</html>"""


def main():
    with zipfile.ZipFile(EXCEL) as z:
        strings = load_shared_strings(z)
        vm_map = load_vm_to_image(z)
        cells, vm_cells = parse_sheet(z, strings)
        cell_images = load_image_data_uris(z, vm_map, vm_cells)

    note_photo_uris = load_note_photo_uris()
    OUT_HTML.write_text(build_html(cells, cell_images, note_photo_uris), encoding="utf-8")
    size_mb = OUT_HTML.stat().st_size / (1024 * 1024)
    print(f"Created: {OUT_HTML}")
    print(f"Size:    {size_mb:.1f} MB ({len(cell_images) + len(note_photo_uris)} embedded images)")


if __name__ == "__main__":
    main()
