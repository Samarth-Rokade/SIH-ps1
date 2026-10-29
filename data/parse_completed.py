"""Parse Table 3 (projects commissioned during the month) from the Flash Report."""
import re, json
import pdfplumber

PDF = "/mnt/user-data/uploads/FlashReport_July_2026.pdf"
COLS = {"slno": (45, 88), "name": (88, 470), "state": (470, 570),
        "date": (570, 670), "doc": (670, 800), "cost": (800, 912), "exp": (912, 1060)}

FOOTER = re.compile(r"Project Assessment|PAIMANA|paimana-proj|^Page \d+|^Note:")
MIN_PAT = re.compile(r"^(Ministry|Department)\b")
TOTAL = re.compile(r"^Total\s*\(\d+\)")
CODE = re.compile(r"^\d{6}$")
PAREN = re.compile(r"^\(.*\)$")
MMYYYY = re.compile(r"^\(?(\d{2}/\d{4})\)?$")
NUM = re.compile(r"^\(?-?[\d,]+(?:\.\d+)?\)?$")


def col_of(x):
    for n, (a, b) in COLS.items():
        if a <= x < b:
            return n


def cluster(words, tol=5):
    lines = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(w["top"] - lines[-1]["top"]) <= tol:
            lines[-1]["words"].append(w); lines[-1]["top"] = min(lines[-1]["top"], w["top"])
        else:
            lines.append({"top": w["top"], "words": [w]})
    for l in lines:
        l["text"] = " ".join(x["text"] for x in sorted(l["words"], key=lambda x: x["x0"]))
    return lines


def num(t):
    t = t.strip("()").replace(",", "")
    if t in ("-", ""): return None
    try: return float(t)
    except ValueError: return None


def parse(pages):
    recs, ministry, sector, expect, name_buf, seen = [], None, None, True, [], set()
    with pdfplumber.open(PDF) as pdf:
        for pno in pages:
            ws = []
            for w in pdf.pages[pno].extract_words():
                if w["top"] < 250 or w["top"] > 1430: continue
                c = col_of((w["x0"] + w["x1"]) / 2)
                if c: ws.append({"col": c, **w})
            by = {}
            for w in ws: by.setdefault(w["col"], []).append(w)
            names = cluster(by.get("name", []))
            slnos = cluster(by.get("slno", []))
            other = {c: cluster(by.get(c, [])) for c in ("state", "date", "doc", "cost", "exp")}
            start = 0.0
            for ln in names:
                t = ln["text"].strip()
                if not t or FOOTER.search(t): continue
                if TOTAL.match(t): expect = True; continue
                if MIN_PAT.match(t) and expect: ministry = t; continue
                if expect and not PAREN.match(t): sector = t; expect = False; continue
                if CODE.match(t):
                    hit = [s for s in slnos if start <= s["top"] <= ln["top"] + 6
                           and s["text"].isdigit() and int(s["text"]) not in seen]
                    if hit and name_buf:
                        seen.add(int(hit[0]["text"])); y = hit[0]["top"]
                        g = lambda c: [l["text"].strip() for l in other[c] if y - 15 <= l["top"] <= y + 15]
                        d = [MMYYYY.match(x).group(1) for x in g("date") if MMYYYY.match(x)]
                        dc = [MMYYYY.match(x).group(1) for x in g("doc") if MMYYYY.match(x)]
                        cs = [num(x) for x in g("cost") if NUM.match(x)]
                        ex = [num(x) for x in g("exp") if NUM.match(x)]
                        recs.append({"sl_no": int(hit[0]["text"]), "project_name": " ".join(name_buf),
                                     "ministry": ministry, "sector": sector, "state": " ".join(g("state")),
                                     "approval_date": d[0] if d else None,
                                     "start_date": d[1] if len(d) > 1 else None,
                                     "actual_doc": dc[0] if dc else None,
                                     "original_doc": dc[1] if len(dc) > 1 else None,
                                     "revised_doc": dc[2] if len(dc) > 2 else None,
                                     "original_cost": cs[0] if cs else None,
                                     "revised_cost": cs[1] if len(cs) > 1 else None,
                                     "expenditure": ex[0] if ex else None})
                    name_buf = []; start = ln["top"] + 6; continue
                if PAREN.match(t): continue
                name_buf.append(t)
    return recs


if __name__ == "__main__":
    r = parse([35, 36])
    print(len(r), "completed records")
    for x in r[:3]: print(x)
    print("cost sum", sum(v["original_cost"] or 0 for v in r))
    json.dump(r, open("completed_raw.json", "w"))
