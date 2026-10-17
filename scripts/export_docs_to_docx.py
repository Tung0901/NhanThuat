"""
Script to convert docs/HUONG_DAN_SU_DUNG.md into a beautifully formatted Word (.docx) document.
"""

import re
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
MD_FILE = DOCS_DIR / "HUONG_DAN_SU_DUNG.md"
DOCX_FILE = DOCS_DIR / "HUONG_DAN_SU_DUNG.docx"

# Color Palette
COLOR_PRIMARY_NAVY = RGBColor(15, 23, 42)      # #0F172A
COLOR_GOLD = RGBColor(180, 83, 9)              # #B45309
COLOR_TEXT_MAIN = RGBColor(30, 41, 59)         # #1E293B
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)     # #64748B
COLOR_EMERALD = RGBColor(5, 150, 105)          # #059669
HEX_TABLE_HEADER_BG = "0F172A"
HEX_ROW_ALT_BG = "F8FAFC"
HEX_BORDER = "CBD5E1"
HEX_CALLOUT_BG = "FFFBEB"
HEX_CODE_BG = "F1F5F9"


def set_cell_background(cell, fill_hex: str):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, border_hex="CBD5E1"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="{border_hex}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="94A3B8"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_formatted_runs(paragraph, text: str, default_font_size=11, default_color=COLOR_TEXT_MAIN):
    """Parse Markdown bold (**text**), italic (*text*), inline code (`code`) and add runs."""
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**') and len(token) >= 4:
            run = paragraph.add_run(token[2:-2])
            run.bold = True
            run.font.size = Pt(default_font_size)
            run.font.color.rgb = default_color
        elif token.startswith('*') and token.endswith('*') and len(token) >= 2:
            run = paragraph.add_run(token[1:-1])
            run.italic = True
            run.font.size = Pt(default_font_size)
            run.font.color.rgb = default_color
        elif token.startswith('`') and token.endswith('`') and len(token) >= 2:
            run = paragraph.add_run(f" {token[1:-1]} ")
            run.font.name = "Consolas"
            run.font.size = Pt(default_font_size * 0.9)
            run.font.color.rgb = RGBColor(194, 65, 12)  # orange-red
            rPr = run._r.get_or_add_rPr()
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F3F4F6"/>')
            rPr.append(shd)
        else:
            run = paragraph.add_run(token)
            run.font.size = Pt(default_font_size)
            run.font.color.rgb = default_color


def build_docx():
    doc = docx.Document()

    # 1. Page Setup: A4, 2.54 cm margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

        # Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("NHÂN THUẬT EXECUTIVE STUDIO • HƯỚNG DẪN SỬ DỤNG HỆ THỐNG")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = COLOR_TEXT_MUTED

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Tài liệu lưu hành nội bộ — Dự án Nhân Thuật • BusinessOS Architecture")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = COLOR_TEXT_MUTED

    # Set normal style font
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_TEXT_MAIN

    lines = MD_FILE.read_text(encoding="utf-8").splitlines()

    i = 0
    in_code_block = False
    code_lines = []
    in_mermaid = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle fenced code block
        if stripped.startswith("```"):
            if in_code_block:
                # Flush code block
                table = doc.add_table(rows=1, cols=1)
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                table.autofit = False
                cell = table.cell(0, 0)
                cell.width = Inches(6.47)
                set_cell_background(cell, HEX_CODE_BG)
                set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

                # Set border
                tcPr = cell._tc.get_or_add_tcPr()
                borders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:top w:val="single" w:sz="4" w:color="CBD5E1"/>'
                    f'<w:left w:val="single" w:sz="16" w:color="94A3B8"/>'
                    f'<w:bottom w:val="single" w:sz="4" w:color="CBD5E1"/>'
                    f'<w:right w:val="single" w:sz="4" w:color="CBD5E1"/>'
                    f'</w:tcBorders>'
                )
                tcPr.append(borders)

                cp = cell.paragraphs[0]
                cp.paragraph_format.space_before = Pt(0)
                cp.paragraph_format.space_after = Pt(0)
                c_run = cp.add_run("\n".join(code_lines))
                c_run.font.name = "Consolas"
                c_run.font.size = Pt(9.5)
                c_run.font.color.rgb = RGBColor(30, 41, 59)

                doc.add_paragraph().paragraph_format.space_after = Pt(4)
                code_lines = []
                in_code_block = False
            elif stripped.startswith("```mermaid"):
                in_mermaid = True
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_mermaid:
            if stripped == "```":
                # End mermaid, output stylized workflow box
                in_mermaid = False
                table = doc.add_table(rows=1, cols=1)
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = table.cell(0, 0)
                cell.width = Inches(6.47)
                set_cell_background(cell, "F8FAFC")
                set_cell_margins(cell, top=160, bottom=160, left=220, right=220)
                tcPr = cell._tc.get_or_add_tcPr()
                borders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:top w:val="single" w:sz="4" w:color="CBD5E1"/>'
                    f'<w:left w:val="single" w:sz="18" w:color="B45309"/>'
                    f'<w:bottom w:val="single" w:sz="4" w:color="CBD5E1"/>'
                    f'<w:right w:val="single" w:sz="4" w:color="CBD5E1"/>'
                    f'</w:tcBorders>'
                )
                tcPr.append(borders)

                cp = cell.paragraphs[0]
                cp.paragraph_format.space_before = Pt(0)
                cp.paragraph_format.space_after = Pt(2)
                t_run = cp.add_run("🗺️ LUỒNG VẬN HÀNH 6 PHÂN HỆ:")
                t_run.bold = True
                t_run.font.size = Pt(10.5)
                t_run.font.color.rgb = COLOR_GOLD

                steps = [
                    "Bối cảnh / Tình thế phát sinh ngoài thực tế",
                    "➔ 01. Tham Mưu Quyết Định (Bóc tách dữ kiện, điểm mù & lập kế hoạch 3 bước)",
                    "➔ 02. Chẩn Đoán Nhân Sự & Tổ Chức (Đánh giá người - việc & radar hành vi)",
                    "➔ 03. Hội Đồng Cố Vấn 5 Triết Phái (Đối chiếu phản biện đa chiều)",
                    "➔ 04. Phòng Đấu Trí Giả Lập (Thử nghiệm đòn đối đáp & đàm phán 1-1)",
                    "➔ 05. Sa Bàn Tình Thế War Room (Mô phỏng liên minh phe phái & can thiệp)",
                    "➔ 06. Tủ Sách & Nguồn Tri Thức Codex (Đối chiếu căn cứ pháp lý & cẩm nang)"
                ]
                for st in steps:
                    sp = cell.add_paragraph()
                    sp.paragraph_format.space_before = Pt(1)
                    sp.paragraph_format.space_after = Pt(1)
                    r = sp.add_run(st)
                    r.font.size = Pt(9.5)
                    r.font.color.rgb = COLOR_TEXT_MAIN
                    if st.startswith("➔"):
                        r.bold = True
                doc.add_paragraph().paragraph_format.space_after = Pt(4)
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Document Title (# HƯỚNG DẪN SỬ DỤNG...)
        if stripped.startswith("# "):
            title_text = stripped[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(title_text)
            run.font.name = "Calibri"
            run.font.size = Pt(20)
            run.bold = True
            run.font.color.rgb = COLOR_PRIMARY_NAVY
            i += 1
            continue

        # Subtitle (*Cẩm nang vận hành...*)
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            sub_text = stripped.strip("*")
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(14)
            run = p.add_run(sub_text)
            run.font.name = "Calibri"
            run.font.size = Pt(12)
            run.italic = True
            run.font.color.rgb = COLOR_GOLD
            i += 1
            continue

        # Horizontal Rule (---)
        if stripped in ("---", "***", "___"):
            # Subtle divider
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="E2E8F0"/></w:pBdr>')
            p._p.get_or_add_pPr().append(p_border)
            i += 1
            continue

        # Heading 1 (## ...)
        if stripped.startswith("## "):
            h_text = stripped[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True

            # Underline bar via paragraph bottom border
            p_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="B45309"/></w:pBdr>')
            p._p.get_or_add_pPr().append(p_border)

            run = p.add_run(h_text)
            run.font.name = "Calibri"
            run.font.size = Pt(14.5)
            run.bold = True
            run.font.color.rgb = COLOR_PRIMARY_NAVY
            i += 1
            continue

        # Heading 2 (### ...)
        if stripped.startswith("### "):
            h_text = stripped[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = "Calibri"
            run.font.size = Pt(12.5)
            run.bold = True
            run.font.color.rgb = COLOR_GOLD if "PHÂN HỆ" in h_text else COLOR_TEXT_MAIN
            i += 1
            continue

        # Heading 3 (#### ...)
        if stripped.startswith("#### "):
            h_text = stripped[5:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = "Calibri"
            run.font.size = Pt(11)
            run.bold = True
            run.font.color.rgb = COLOR_TEXT_MAIN
            i += 1
            continue

        # Blockquote (> ...)
        if stripped.startswith("> "):
            bq_text = stripped[2:].strip()
            table = doc.add_table(rows=1, cols=1)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = table.cell(0, 0)
            cell.width = Inches(6.47)
            set_cell_background(cell, HEX_CALLOUT_BG)
            set_cell_margins(cell, top=100, bottom=100, left=180, right=180)

            tcPr = cell._tc.get_or_add_tcPr()
            borders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>'
                f'<w:top w:val="none"/>'
                f'<w:left w:val="single" w:sz="18" w:color="D97706"/>'
                f'<w:bottom w:val="none"/>'
                f'<w:right w:val="none"/>'
                f'</w:tcBorders>'
            )
            tcPr.append(borders)

            cp = cell.paragraphs[0]
            cp.paragraph_format.space_before = Pt(0)
            cp.paragraph_format.space_after = Pt(0)
            add_formatted_runs(cp, bq_text, default_font_size=10.5, default_color=RGBColor(146, 64, 14))

            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            i += 1
            continue

        # Table detection
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            if len(table_lines) >= 2:
                # Parse markdown table
                headers = [c.strip() for c in table_lines[0].strip("|").split("|")]
                rows = []
                for tl in table_lines[2:]:
                    cols = [c.strip() for c in tl.strip("|").split("|")]
                    rows.append(cols)

                doc_table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
                doc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                set_table_borders(doc_table)

                # Format Header
                hdr_cells = doc_table.rows[0].cells
                for idx, h_text in enumerate(headers):
                    cell = hdr_cells[idx]
                    set_cell_background(cell, HEX_TABLE_HEADER_BG)
                    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                    hp = cell.paragraphs[0]
                    hp.paragraph_format.space_before = Pt(0)
                    hp.paragraph_format.space_after = Pt(0)
                    hrun = hp.add_run(h_text)
                    hrun.bold = True
                    hrun.font.size = Pt(10)
                    hrun.font.color.rgb = RGBColor(255, 255, 255)

                # Repeat header on every page
                trPr = doc_table.rows[0]._tr.get_or_add_trPr()
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

                # Format Rows
                for r_idx, r_data in enumerate(rows):
                    row_cells = doc_table.rows[r_idx + 1].cells
                    bg = HEX_ROW_ALT_BG if (r_idx % 2 == 1) else "FFFFFF"
                    for c_idx, cell_value in enumerate(r_data):
                        if c_idx < len(row_cells):
                            cell = row_cells[c_idx]
                            if bg != "FFFFFF":
                                set_cell_background(cell, bg)
                            set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
                            rp = cell.paragraphs[0]
                            rp.paragraph_format.space_before = Pt(0)
                            rp.paragraph_format.space_after = Pt(0)
                            add_formatted_runs(rp, cell_value, default_font_size=10, default_color=COLOR_TEXT_MAIN)

                doc.add_paragraph().paragraph_format.space_after = Pt(6)
            continue

        # Bullet list item (- ... or * ...)
        if re.match(r"^[-*]\s+", stripped):
            item_text = re.sub(r"^[-*]\s+", "", stripped)
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, item_text, default_font_size=11, default_color=COLOR_TEXT_MAIN)
            i += 1
            continue

        # Numbered list item (1. ... or 2. ...)
        if re.match(r"^\d+\.\s+", stripped):
            item_text = re.sub(r"^\d+\.\s+", "", stripped)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, item_text, default_font_size=11, default_color=COLOR_TEXT_MAIN)
            i += 1
            continue

        # Regular Paragraph
        if stripped:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(p, stripped, default_font_size=11, default_color=COLOR_TEXT_MAIN)

        i += 1

    doc.save(str(DOCX_FILE))
    print(f"Successfully generated Word document: {DOCX_FILE}")


if __name__ == "__main__":
    build_docx()
