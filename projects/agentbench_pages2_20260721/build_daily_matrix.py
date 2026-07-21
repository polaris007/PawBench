# -*- coding: utf-8 -*-
"""Adjust slide 8 (bridge to daily work) and insert a new slide 9 (daily-capability
matrix) into Agent评测.pptx. Non-destructive: writes Agent评测_v4.pptx."""
import copy
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

ORIG = r"docs\PPT\Agent评测.pptx"
OUT = r"docs\PPT\Agent评测_v4.pptx"

# ---- palette (from identity) ----
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG = RGBColor(0xFF, 0xFF, 0xFF)
PRIMARY = RGBColor(0x1E, 0x3A, 0x8A)
ACCENT = RGBColor(0x25, 0x63, 0xEB)
STRIPE = RGBColor(0xF2, 0xF5, 0xFA)
BODY = RGBColor(0x1A, 0x1A, 0x2E)
SUB = RGBColor(0x64, 0x74, 0x8B)
BORDER = RGBColor(0xE2, 0xE8, 0xF0)
WARN_BG = RGBColor(0xFE, 0xF2, 0xF2)
WARN_TX = RGBColor(0xEF, 0x44, 0x44)
FONT = "Microsoft YaHei"

prs = Presentation(ORIG)
print("original slides:", len(prs.slides._sldIdLst))


def set_run(run, size, bold=False, color=None):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', FONT)
    if color is not None:
        run.font.color.rgb = color


# ============ 1) Adjust slide 8 ============
s8 = prs.slides[7]  # 0-indexed slide 8
for shp in s8.shapes:
    if not shp.has_text_frame:
        continue
    txt = shp.text_frame.text
    # subtitle
    if "用一个真实任务卡" in txt:
        p = shp.text_frame.paragraphs[0]
        # capture original formatting
        old_run = p.runs[0] if p.runs else None
        size = old_run.font.size if old_run else Pt(20)
        color = old_run.font.color.rgb if (old_run and old_run.font.color and old_run.font.color.type is not None) else SUB
        p.text = "借 T053 看清 PawBench「执行 → 采集 → 评分 → 汇总」的评测链路——它同样适用于我们的日常任务（下页对照）"
        set_run(p.runs[0], size.pt if size else 20, bold=False, color=color)
        print("  updated subtitle on slide 8")

# add a forward pointer textbox (bottom-right) on slide 8
from pptx.enum.text import PP_ALIGN
L, T, W, H = Emu(860000), Emu(6700000), Emu(3800000), Emu(360000)
tb = s8.shapes.add_textbox(L, T, W, H)
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.RIGHT
r = p.add_run()
r.text = "↓ 下一页：PawBench 任务 ↔ 我们的 7 类日常能力"
set_run(r, 14, bold=False, color=ACCENT)
print("  added forward pointer on slide 8")

# ============ 2) Build new slide 9 (matrix) ============
def blank_layout(prs):
    for lay in prs.slide_layouts:
        if lay.name.lower() == "blank":
            return lay
    return min(prs.slide_layouts, key=lambda l: len(l.placeholders))

layout = blank_layout(prs)
new_slide = prs.slides.add_slide(layout)
for ph in list(new_slide.placeholders):
    ph._element.getparent().remove(ph._element)
new_slide.background.fill.solid()
new_slide.background.fill.fore_color.rgb = BG

# title
tb = new_slide.shapes.add_textbox(Emu(600000), Emu(380000), Emu(11600000), Emu(560000))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "PawBench 任务 ↔ 我们的日常能力"
set_run(r, 32, bold=True, color=PRIMARY)

# subtitle
tb = new_slide.shapes.add_textbox(Emu(600000), Emu(980000), Emu(11600000), Emu(420000))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "日常 7 类使用场景中，6 类在 PawBench 都有强匹配任务；它们与第 8 页 T053 走完全相同的「执行→采集→评分→汇总」链路"
set_run(r, 15, bold=False, color=SUB)

# matrix data
headers = ["日常能力", "对应任务", "评分方式", "考察核心"]
rows = [
    ["邮件处理", "T016 Email Triage", "hybrid（自动 0.35 / LLM 0.65）", "读收件箱 → 分类(需回复/通知/垃圾) → 结构化输出"],
    ["通讯录 / CRM", "T026 / T027 CRM Export", "hybrid（自动 0.5 / LLM 0.5）", "从 CRM 导出客户与通讯录数据，并做错误恢复"],
    ["内部新闻 / 资讯", "T025 Newsletter Curation", "hybrid（自动 0.4 / LLM 0.6）", "多源 RSS 筛选 → 编辑摘要 → 形成技术简报"],
    ["Excel / 表格", "T019 / T020 Expense Report", "hybrid（自动 0.45 / LLM 0.55）", "原始交易 → 分类汇总 → 生成报销报告"],
    ["文档 (Doc)", "T040 / T041 会议 & 进度", "hybrid（自动 0.2 / LLM 0.8）", "提取会议行动项 / 并行生成多项目进度报告"],
    ["代码处理", "T064 Playwright E2E", "hybrid（自动 0.5 / LLM 0.5）", "编写并调试端到端表单测试代码（真实代码操作）"],
    ["PPT 演示文稿", "— 暂无覆盖", "—", "当前任务体系未覆盖，建议作为扩展方向"],
]

n_rows = len(rows) + 1
n_cols = 4
tbl_left, tbl_top = Emu(600000), Emu(1480000)
tbl_w, tbl_h = Emu(11600000), Emu(5180000)
gtbl = new_slide.shapes.add_table(n_rows, n_cols, tbl_left, tbl_top, tbl_w, tbl_h)
table = gtbl.table
# column widths
cw = [Emu(1650000), Emu(2650000), Emu(3050000), Emu(4250000)]
for i, w in enumerate(cw):
    table.columns[i].width = w
# disable default banding style by setting each cell explicitly
for r_i in range(n_rows):
    table.rows[r_i].height = Emu(int(tbl_h / n_rows))

# header
for c_i, htext in enumerate(headers):
    cell = table.cell(0, c_i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = PRIMARY
    cell.margin_left = Emu(120000)
    cell.margin_right = Emu(120000)
    cell.margin_top = Emu(60000)
    cell.margin_bottom = Emu(60000)
    cell.vertical_anchor = 1  # middle
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = htext
    set_run(r, 14, bold=True, color=WHITE)

# body
for i, row in enumerate(rows):
    is_gap = (i == len(rows) - 1)
    for c_i, val in enumerate(row):
        cell = table.cell(i + 1, c_i)
        cell.fill.solid()
        if is_gap:
            cell.fill.fore_color.rgb = WARN_BG
        else:
            cell.fill.fore_color.rgb = WHITE if (i % 2 == 0) else STRIPE
        cell.margin_left = Emu(120000)
        cell.margin_right = Emu(120000)
        cell.margin_top = Emu(60000)
        cell.margin_bottom = Emu(60000)
        cell.vertical_anchor = 1
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = val
        if is_gap:
            set_run(r, 13, bold=(c_i == 0), color=WARN_TX)
        else:
            set_run(r, 13, bold=(c_i == 0), color=BODY)

# borders (python-pptx has no cell.border; set via tcPr XML)
def set_cell_border(cell, color, width_pt):
    tcPr = cell._tc.get_or_add_tcPr()
    for edge in ("L", "R", "T", "B"):
        tag = "a:ln" + edge
        ln = tcPr.find(qn(tag))
        if ln is None:
            ln = tcPr.makeelement(qn(tag), {})
            tcPr.append(ln)
        ln.set("w", str(int(width_pt * 12700)))
        ln.set("cap", "flat")
        fill = ln.find(qn("a:solidFill"))
        if fill is None:
            fill = ln.makeelement(qn("a:solidFill"), {})
            ln.append(fill)
        clr = fill.find(qn("a:srgbClr"))
        if clr is None:
            clr = fill.makeelement(qn("a:srgbClr"), {})
            fill.append(clr)
        clr.set("val", "%02X%02X%02X" % (color[0], color[1], color[2]))

for r_i in range(n_rows):
    for c_i in range(n_cols):
        set_cell_border(table.cell(r_i, c_i), BORDER, 0.75)

# bottom note
tb = new_slide.shapes.add_textbox(Emu(600000), Emu(6760000), Emu(11600000), Emu(340000))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "注：上述任务均为 hybrid 评分（自动检查 + LLM 评判），与你们日常使用 OpenClaw 处理邮件 / 表格 / 文档 / 代码的能力高度对应。"
set_run(r, 12, bold=False, color=SUB)

print("  built new slide (matrix), total shapes:", len(new_slide.shapes))

# ============ 3) Reorder: move new slide to position 8 (0-indexed) ============
sldIdLst = prs.slides._sldIdLst
new_el = list(sldIdLst)[-1]  # it was appended last
sldIdLst.remove(new_el)
sldIdLst.insert(8, new_el)
print("  reordered; final slides:", len(prs.slides._sldIdLst))

# ============ 4) Fix page numbers (were hardcoded "NN / 10") ============
import re as _re

def find_pagenum(shapes):
    for shp in shapes:
        if shp.has_text_frame and _re.match(r'^\s*\d{2} / \d{2}\s*$', shp.text_frame.text):
            return shp
    return None

# capture slide 8 page-number geometry to replicate on the new matrix slide
s8_pn = find_pagenum(prs.slides[7].shapes)
pn_left = pn_top = pn_w = pn_h = None
pn_size = 12
pn_color = SUB
if s8_pn:
    pn_left, pn_top, pn_w, pn_h = s8_pn.left, s8_pn.top, s8_pn.width, s8_pn.height
    run = s8_pn.text_frame.paragraphs[0].runs[0]
    pn_size = run.font.size.pt if run.font.size else 12
    if run.font.color is not None and run.font.color.type is not None:
        pn_color = run.font.color.rgb

for i, sl in enumerate(prs.slides):
    pn = find_pagenum(sl.shapes)
    if pn is not None:
        pn.text_frame.paragraphs[0].text = "%02d / 11" % (i + 1)
        set_run(pn.text_frame.paragraphs[0].runs[0], pn_size, bold=False, color=pn_color)
    elif i == 8 and pn_left is not None:  # matrix slide: add page number
        tb = sl.shapes.add_textbox(pn_left, pn_top, pn_w, pn_h)
        tf = tb.text_frame
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = "09 / 11"
        set_run(r, pn_size, bold=False, color=pn_color)
        print("  added page number on matrix slide")
print("  renumbered page numbers to /11")

prs.save(OUT)
print("saved:", OUT)
