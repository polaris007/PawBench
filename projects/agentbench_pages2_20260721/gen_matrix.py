# Generate the Model x Harness scoring matrix SVG (data-driven).

DATA = [
    # (model_name, is_new, hermes, openclaw, qwenpaw, avg)
    ("claude-opus-4.6", False, 78.4, 76.1, 78.3, 77.6),
    ("deepseek-v4-pro", False, 72.1, 75.4, 75.6, 74.4),
    ("qwen3.7-max", True, 72.3, 72.5, 77.6, 74.1),
    ("qwen3.6-max-preview", True, 68.1, 75.1, 78.3, 73.9),
    ("qwen3.6-plus", False, 70.4, 73.6, 75.0, 73.0),
    ("qwen3.6-27b", False, 68.2, 72.9, 72.7, 71.3),
    ("glm-5.1", True, 63.2, 68.5, 71.1, 67.6),
    ("kimi-k2.6", False, 66.4, 66.6, 66.6, 66.5),
    ("qwen3.6-35b-a3b", False, 56.7, 67.6, 68.3, 64.3),
]
AVG_ROW = (68.4, 72.1, 73.7, 71.4)

HARNESSES = [
    ("Hermes", "v2026.4.23"),
    ("OpenClaw", "v2026.4.24"),
    ("QwenPaw", "v1.1.3"),
]


def cell_color(score):
    if score >= 76:
        return "#047857"
    if score >= 73:
        return "#059669"
    if score >= 70:
        return "#10B981"
    if score >= 67:
        return "#34D399"
    if score >= 64:
        return "#6EE7B7"
    if score >= 60:
        return "#A7F3D0"
    return "#D1FAE5"


def text_color(score):
    return "#FFFFFF" if score >= 73 else "#1A1A2E"


parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">')
parts.append('  <defs><style>text{font-family:"Microsoft YaHei",Arial,sans-serif}</style></defs>')
parts.append('  <rect x="0" y="0" width="1280" height="720" fill="#FFFFFF"/>')
parts.append('  <rect x="0" y="0" width="1280" height="5" fill="#1E3A8A"/>')

# Title
parts.append('  <text x="80" y="78" font-size="32" font-weight="bold" fill="#1E3A8A">PawBench 评测结果 · Model × Harness 评分矩阵</text>')
parts.append('  <rect x="80" y="95" width="100" height="4" fill="#2563EB"/>')
parts.append('  <text x="80" y="130" font-size="15" fill="#64748B">全景 150 个任务（文本 + 多模态） · 9 模型 × 3 Harness · Overall 综合得分</text>')

# Tabs (static)
parts.append('  <rect x="80" y="150" width="110" height="32" rx="16" fill="#1E3A8A"/>')
parts.append('  <text x="135" y="171" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">Overall · 110</text>')
parts.append('  <rect x="200" y="150" width="90" height="32" rx="16" fill="#F2F5FA"/>')
parts.append('  <text x="245" y="171" font-size="13" fill="#64748B" text-anchor="middle">Text 24+</text>')
parts.append('  <rect x="300" y="150" width="130" height="32" rx="16" fill="#F2F5FA"/>')
parts.append('  <text x="365" y="171" font-size="13" fill="#64748B" text-anchor="middle">Multimodal · 24</text>')

# Table
x0 = 80
y0 = 200
col_widths = [240, 220, 220, 220, 220]
header_h = 50
row_h = 32

col_x = []
acc = x0
for w in col_widths:
    col_x.append(acc)
    acc += w

# Header row
parts.append(f'  <rect x="{x0}" y="{y0}" width="1120" height="{header_h}" fill="#1E3A8A"/>')
parts.append(f'  <text x="{col_x[0]+20}" y="{y0+31}" font-size="14" font-weight="bold" fill="#FFFFFF">MODEL</text>')
for i, (name, ver) in enumerate(HARNESSES):
    cx = col_x[i + 1] + col_widths[i + 1] / 2
    parts.append(f'  <text x="{cx}" y="{y0+23}" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{name}</text>')
    parts.append(f'  <text x="{cx}" y="{y0+41}" font-size="10" fill="#93C5FD" text-anchor="middle">{ver}</text>')
parts.append(f'  <text x="{col_x[4]+col_widths[4]/2}" y="{y0+32}" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">平均</text>')

# Data rows
for ri, (model, is_new, hermes, openclaw, qwenpaw, avg) in enumerate(DATA):
    ry = y0 + header_h + ri * row_h
    if ri % 2 == 0:
        parts.append(f'  <rect x="{x0}" y="{ry}" width="1120" height="{row_h}" fill="#F8FAFC"/>')
    # model name
    name_x = col_x[0] + 20
    parts.append(f'  <text x="{name_x}" y="{ry+22}" font-size="15" fill="#1A1A2E">{model}</text>')
    if is_new:
        badge_x = col_x[0] + 180
        parts.append(f'  <rect x="{badge_x}" y="{ry+8}" width="48" height="18" rx="3" fill="#F59E0B"/>')
        parts.append(f'  <text x="{badge_x+24}" y="{ry+21}" font-size="11" font-weight="bold" fill="#FFFFFF" text-anchor="middle">新文本</text>')
    # cells
    for ci, score in enumerate([hermes, openclaw, qwenpaw, avg]):
        cx = col_x[ci + 1]
        color = cell_color(score)
        parts.append(f'  <rect x="{cx}" y="{ry}" width="{col_widths[ci + 1]}" height="{row_h}" fill="{color}"/>')
        text_c = text_color(score)
        text_x = cx + col_widths[ci + 1] / 2
        parts.append(f'  <text x="{text_x}" y="{ry+22}" font-size="16" font-weight="bold" fill="{text_c}" text-anchor="middle">{score:.1f}</text>')
    # subtle dividers
    for ci in range(1, 5):
        parts.append(f'  <line x1="{col_x[ci]}" y1="{ry}" x2="{col_x[ci]}" y2="{ry+row_h}" stroke="#FFFFFF" stroke-width="1"/>')

# Average row
ri = len(DATA)
ry = y0 + header_h + ri * row_h
parts.append(f'  <rect x="{x0}" y="{ry}" width="1120" height="{row_h}" fill="#E2E8F0"/>')
parts.append(f'  <text x="{col_x[0]+20}" y="{ry+22}" font-size="15" font-weight="bold" fill="#1E3A8A">平均</text>')
for ci, score in enumerate(AVG_ROW):
    cx = col_x[ci + 1]
    text_x = cx + col_widths[ci + 1] / 2
    parts.append(f'  <text x="{text_x}" y="{ry+22}" font-size="16" font-weight="bold" fill="#1E3A8A" text-anchor="middle">{score:.1f}</text>')

# Footnote
parts.append('  <text x="80" y="610" font-size="12" fill="#94A3B8">数据来源：PawBench OpenJudge 评测引擎 · 截至 2025 年 7 月 · 平均分 = 跨 harness 加权 · 单元格颜色深浅代表分数高低</text>')

parts.append('</svg>')

out = "\n".join(parts) + "\n"
out_path = r"projects\agentbench_pages2_20260721\svg_output\02_matrix.svg"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(out)
print("written:", out_path, len(out), "chars")
