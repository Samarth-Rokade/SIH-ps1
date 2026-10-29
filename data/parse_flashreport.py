"""
Parse the MoSPI PAIMANA Flash Report (July 2026) PDF into structured project records.

Table 6 -> all ongoing projects
Table 3 -> projects completed / commissioned during the month
"""
import re
import json
import pdfplumber

PDF = "/mnt/user-data/uploads/FlashReport_July_2026.pdf"

# column x-bands (page width 1080pt), taken from the repeated table header
COLS = {
    "slno":     (40, 84),
    "name":     (84, 468),
    "state":    (468, 556),
    "date":     (556, 652),
    "doc":      (652, 752),
    "cost":     (752, 838),
    "exp":      (838, 922),
    "prog":     (922, 1060),
}

FOOTER_PAT = re.compile(r"Project Assessment|PAIMANA|paimana-proj|^Page \d+")
MINISTRY_PAT = re.compile(r"^(Ministry|Department)\b")
TERMINATOR_PAT = re.compile(r"^\((?:-|\d+)\)\s+\((?:-|\d+)\)$")
PAREN_PAT = re.compile(r"^\(.*\)$")
TOTAL_PAT = re.compile(r"^Total\s*\(\d+\)")
MMYYYY = re.compile(r"^\(?(\d{2}/\d{4})\)?$")
NUM = re.compile(r"^\(?-?[\d,]+(?:\.\d+)?\)?$")


def col_of(x_center):
    for name, (a, b) in COLS.items():
        if a <= x_center < b:
            return name
    return None


def page_words(page):
    words = page.extract_words()
    out = []
    for w in words:
        if w["top"] < 250 or w["top"] > 1430:
            continue
        c = col_of((w["x0"] + w["x1"]) / 2)
        if c is None:
            continue
        out.append({"col": c, "top": w["top"], "x0": w["x0"], "text": w["text"]})
    return out


def cluster_lines(words, tol=5):
    """Cluster words of a single column into visual lines."""
    lines = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(w["top"] - lines[-1]["top"]) <= tol:
            lines[-1]["words"].append(w)
            lines[-1]["top"] = min(lines[-1]["top"], w["top"])
        else:
            lines.append({"top": w["top"], "words": [w]})
    for ln in lines:
        ln["text"] = " ".join(x["text"] for x in sorted(ln["words"], key=lambda x: x["x0"]))
    return lines


def clean_num(tok):
    tok = tok.strip("()").replace(",", "")
    if tok in ("-", ""):
        return None
    try:
        return float(tok)
    except ValueError:
        return None


def parse_table(first_page, last_page, has_progress=True):
    """Generic parser for the ongoing (Table 6) / completed (Table 3) layouts."""
    records = []
    ministry, sector = None, None
    expect_heading = True
    pending_name = []          # text lines accumulated for the current project
    seen = set()
    with pdfplumber.open(PDF) as pdf:
        for pno in range(first_page, last_page + 1):
            page = pdf.pages[pno]
            ws = page_words(page)
            by_col = {}
            for w in ws:
                by_col.setdefault(w["col"], []).append(w)

            name_lines = cluster_lines(by_col.get("name", []))
            slnos = cluster_lines(by_col.get("slno", []))
            other = {c: cluster_lines(by_col.get(c, [])) for c in
                     ("state", "date", "doc", "cost", "exp", "prog")}

            # walk the name column top-to-bottom; a project block ends at its
            # "(legacy code) (pmgid)" terminator line
            block_start = 0.0
            for ln in name_lines:
                txt = ln["text"].strip()
                if not txt or FOOTER_PAT.search(txt):
                    continue
                if TOTAL_PAT.match(txt):
                    expect_heading = True
                    continue
                if MINISTRY_PAT.match(txt) and expect_heading:
                    ministry = txt
                    continue
                if expect_heading and not PAREN_PAT.match(txt):
                    sector = txt
                    expect_heading = False
                    continue
                if TERMINATOR_PAT.match(txt):
                    # close the block: find the Sl.No inside [block_start, this line]
                    y_end = ln["top"] + 4
                    hit = [s for s in slnos if block_start <= s["top"] <= y_end
                           and s["text"].strip().isdigit()
                           and int(s["text"]) not in seen]
                    if not hit and pending_name:
                        # wrapped multi-state rows can push the Sl.No outside the
                        # block window; fall back to the next expected serial
                        nxt = (records[-1]["sl_no"] + 1) if records else 1
                        hit = [s for s in slnos if s["text"].strip().isdigit()
                               and int(s["text"]) == nxt]
                    if hit and pending_name:
                        seen.add(int(hit[0]["text"]))
                        y = hit[0]["top"]
                        lo, hi = y - 14, y + 16

                        def grab(col):
                            return [l["text"].strip() for l in other[col]
                                    if lo <= l["top"] <= hi]

                        dates = [MMYYYY.match(t).group(1) for t in grab("date") if MMYYYY.match(t)]
                        docs = [MMYYYY.match(t).group(1) for t in grab("doc") if MMYYYY.match(t)]
                        docs_raw = grab("doc")
                        costs = [clean_num(t) for t in grab("cost") if NUM.match(t)]
                        exps = [clean_num(t) for t in grab("exp") if NUM.match(t)]
                        progs = [clean_num(t) for t in grab("prog") if NUM.match(t)] if has_progress else []
                        state = " ".join(grab("state"))

                        records.append({
                            "sl_no": int(hit[0]["text"]),
                            "project_name": " ".join(pending_name),
                            "ministry": ministry,
                            "sector": sector,
                            "state": state,
                            "approval_date": dates[0] if dates else None,
                            "start_date": dates[1] if len(dates) > 1 else None,
                            "original_doc": docs[0] if docs else None,
                            "revised_doc": docs[1] if len(docs) > 1 else None,
                            "doc_raw": docs_raw,
                            "original_cost": costs[0] if costs else None,
                            "revised_cost": costs[1] if len(costs) > 1 else None,
                            "expenditure": exps[0] if exps else None,
                            "physical_progress": progs[0] if progs else None,
                            "page": pno,
                        })
                    pending_name = []
                    block_start = ln["top"] + 4
                    continue
                if PAREN_PAT.match(txt):
                    continue  # agency / project code lines
                pending_name.append(txt)
    return records


if __name__ == "__main__":
    ongoing = parse_table(54, 151, has_progress=True)
    print("ongoing parsed:", len(ongoing))
    nums = [r["sl_no"] for r in ongoing]
    print("sl_no range:", min(nums), max(nums), "unique:", len(set(nums)))
    missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
    print("missing sl_nos:", missing[:20], "count", len(missing))
    print(json.dumps(ongoing[:2], indent=1)[:1500])
    print("first-25 original cost sum:",
          round(sum(r["original_cost"] or 0 for r in ongoing if r["sl_no"] <= 25), 2), "expect 21345.07")
    with open("ongoing_raw.json", "w") as f:
        json.dump(ongoing, f)
