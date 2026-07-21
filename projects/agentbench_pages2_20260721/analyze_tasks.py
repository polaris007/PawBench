import os, re, glob, json

TASK_DIR = r"d:\workplace\github\PawBench\data\pawbench-v1.0\tasks"

def parse_frontmatter(text):
    m = re.match(r"^---\s*(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    block = m.group(1)
    data = {}
    # simple key: value, and nested under labels:
    cur = data
    stack = []
    for line in block.splitlines():
        if not line.strip():
            continue
        if re.match(r"^\s+", line):
            # nested - handle under labels
            pass
        mm = re.match(r"^([A-Za-z_\-]+):\s*(.*)$", line)
        if mm:
            k, v = mm.group(1), mm.group(2).strip()
            data[k] = v
    return data

def get_field(fm, *keys):
    # try top-level then labels.* 
    for k in keys:
        if k in fm and fm[k]:
            return fm[k]
    return ""

rows = []
for fp in sorted(glob.glob(os.path.join(TASK_DIR, "*.md"))):
    text = open(fp, encoding="utf-8").read()
    fm = parse_frontmatter(text)
    # scenario may be under labels:
    scen = ""
    m = re.search(r"scenario:\s*([A-Za-z_/]+)", text)
    if m: scen = m.group(1)
    caps = ""
    m = re.search(r"capabilities:\s*(.*?)(?:\n\w|\n---|\Z)", text, re.S)
    name = get_field(fm, "name")
    cat = get_field(fm, "category")
    rows.append({
        "file": os.path.basename(fp),
        "id": get_field(fm, "id"),
        "name": name,
        "category": cat,
        "scenario": scen,
        "raw": text[:600],
    })

# User usage dimensions
dims = {
    "PPT": ["ppt", "presentation", "slide", "幻灯片", "deck"],
    "Excel": ["excel", "xlsx", "csv", "spreadsheet", "表格", "workbook", "reconcili", "expense", "报销", "financial", "finance"],
    "Word/Doc/PDF": ["doc", "word", "pdf", "document", "report", "whitepaper", "合同", "contract", "memo", "summary", "extract"],
    "Code": ["code", "coding", "program", "dev", "github", "git ", "shell", "cicd", "api", "schema", "migration", "debug", "pipeline", "software", "script", "backtest", "algorithm", "svpwm", "sparql", "sql"],
    "Email": ["email", "邮件", "gmail", "mailbox", "inbox"],
    "Contacts/CRM": ["crm", "contact", "通讯录", "directory", "customer", "account", "通讯"],
    "Internal News": ["news", "newsletter", "新闻", "kb_search", "knowledge", "ticker", "ticket", "announce", "internal"],
}

def matches(r):
    blob = (r["file"] + " " + r["name"] + " " + r["category"] + " " + r["scenario"] + " " + r["raw"]).lower()
    hit = {}
    for dim, kws in dims.items():
        if any(k in blob for k in kws):
            hit[dim] = True
    return hit

result = {d: [] for d in dims}
for r in rows:
    hits = matches(r)
    for d in hits:
        result[d].append(r)

for d in dims:
    print(f"\n===== {d}  ({len(result[d])} 个) =====")
    for r in result[d]:
        print(f"  - {r['file']}  | {r['name']}  | cat={r['category']}  | scen={r['scenario']}")

# save json
json.dump(result, open(r"d:\workplace\github\PawBench\projects\agentbench_pages2_20260721\task_match.json","w"), ensure_ascii=False, indent=1)
print("\nTOTAL tasks:", len(rows))
